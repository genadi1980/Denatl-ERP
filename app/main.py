import os
import subprocess
import sys
import json
from datetime import datetime
from urllib import request

# Resolve project root path and ensure it's in sys.path so app and models modules can be imported
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text, func

from app.database import engine, get_db, Base
from models.models import ProductDB, PriceHistoryDB
from app.services.ai_service import generate_ai_report, OLLAMA_HOST, OLLAMA_MODEL
from app.services.scraper_service import run_dental_scraper_task
from app.dependencies import verify_supabase_jwt

app = FastAPI(title="Dental Promo Tracker")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all origins
    allow_credentials=False, # Must be False when using wildcard allow_origins with Authorization header
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
def global_exception_handler(request, exc: Exception):
    """
    Global fallback exception handler to capture server errors, 
    print trace logs, and return responses with CORS headers.
    """
    import traceback
    error_details = traceback.format_exc()
    print(f"CRITICAL SYSTEM EXCEPTION:\n{error_details}")
    
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "*",
        "Access-Control-Allow-Headers": "*",
    }
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error occurred on the backend.",
            "error": str(exc)
        },
        headers=headers
    )


@app.on_event("startup")
def _init_app():
    """Initialize database tables and log status."""
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print("Failed to create database tables:", type(e).__name__, e)

    print(f"Ollama host: {OLLAMA_HOST}, model: {OLLAMA_MODEL}")
    print("Gemini Serverless AI engine active")


# --- Endpoints ---


@app.post("/scraper/run")
def trigger_scraper(background_tasks: BackgroundTasks, current_user: dict = Depends(verify_supabase_jwt)):
    """Triggers the scraper engine as a clean background task in the thread pool"""
    background_tasks.add_task(run_dental_scraper_task)
    return {
        "status": "Scraper task successfully queued to the background worker pool.",
        "timestamp": datetime.now().isoformat(),
        "triggered_by": current_user.get("email")
    }


@app.get("/promotions/analyze")
def analyze_promotions_endpoint(provider: str = None, db: Session = Depends(get_db), current_user: dict = Depends(verify_supabase_jwt)):
    """Pulls only the cleanest, high-value promo prices per product for the AI."""

    # 1. FIXED: Normalize provider parameter case to resolve the routing failure
    if provider:
        provider = provider.lower().strip()

    # 2. Subquery: get the latest price_history id per product
    latest_per_product = (
        db.query(
            PriceHistoryDB.product_id, func.max(PriceHistoryDB.id).label("latest_id")
        )
        .group_by(PriceHistoryDB.product_id)
        .subquery()
    )

    # 3. HIGH-PERFORMANCE: Let the DB calculate the discount percent and sort natively
    # Added filters to drop negative balances and ignore anomalies above 80%
    recent_promos = (
        db.query(
            ProductDB.name,
            ProductDB.source_site,
            PriceHistoryDB.old_price,
            PriceHistoryDB.new_price,
            PriceHistoryDB.scrapped_at,
            (
                (PriceHistoryDB.old_price - PriceHistoryDB.new_price)
                / PriceHistoryDB.old_price
                * 100
            ).label("discount_calculation"),
        )
        .join(latest_per_product, PriceHistoryDB.id == latest_per_product.c.latest_id)
        .join(ProductDB, ProductDB.id == PriceHistoryDB.product_id)
        .filter(PriceHistoryDB.is_promotion == True)
        .filter(PriceHistoryDB.old_price > PriceHistoryDB.new_price)
        .filter(
            (
                (PriceHistoryDB.old_price - PriceHistoryDB.new_price)
                / PriceHistoryDB.old_price
                * 100
            )
            <= 80.0
        )
        .order_by(text("discount_calculation DESC"))
        .limit(25)  # Strict constraint payload to keep processing extremely fast
        .all()
    )

    if not recent_promos:
        # Fallback: Извличане на всички следени продукти с техните настоящи цени
        all_latest = (
            db.query(
                ProductDB.name,
                ProductDB.source_site,
                PriceHistoryDB.old_price,
                PriceHistoryDB.new_price,
                PriceHistoryDB.scrapped_at,
            )
            .join(latest_per_product, PriceHistoryDB.id == latest_per_product.c.latest_id)
            .join(ProductDB, ProductDB.id == PriceHistoryDB.product_id)
            .all()
        )
        
        if not all_latest:
            return {
                "message": "Няма активни промоции или продукти в базата данни в момента."
            }
            
        data_for_ai = [
            {
                "product": row[0],
                "site": row[1],
                "price": float(row[3]),
            }
            for row in all_latest
        ]
        
        timestamp = all_latest[0][4].strftime("%Y-%m-%d %H:%M") if all_latest[0][4] else "неизвестно"
        
        prompt = f"""Ти си безкомпромисен дентален анализатор. В момента няма активни промоции в базата данни. Направи стегнат ценови преглед на настоящите редовни цени за дентални клиники към {timestamp}:

{data_for_ai}

ПРАВИЛА ЗА ДОКЛАД:
1. Изведи съобщение най-отгоре: "⚠️ Няма активни промоции в момента. Показва се списък с настоящите редовни цени на следените материали:"
2. Кратък списък във формат: Продукт | Сайт | Настояща Цена лв.
3. Сгрупирай продуктите логически по марки или приложения (напр. Ендодонтия, Анестетици, Композити), за да бъде лесно за четене.
4. Пиши директно на български, без уводни изречения и празни приказки."""

        try:
            ai_text, backend = generate_ai_report(prompt, provider=provider)
        except RuntimeError as e:
            raise HTTPException(status_code=503, detail=str(e))

        return {
            "ai_report": ai_text,
            "products_analyzed": len(data_for_ai),
            "timestamp": timestamp,
            "backend": backend,
        }

    # 4. Map query records safely into structured payload dictionaries
    data_for_ai = [
        {
            "product": row[0],
            "site": row[1],
            "old_price": float(row[2]),
            "deal_price": float(row[3]),
            "discount_pct": round(float(row[5]), 1),
        }
        for row in recent_promos
    ]

    timestamp = (
        recent_promos[0][4].strftime("%Y-%m-%d %H:%M")
        if recent_promos[0][4]
        else "unknown"
    )

    # 5. Optimized Prompt: Direct, clear, and highly constrained
    prompt = f"""Ти си безкомпромисен дентален анализатор. Направи стегнат ценови преглед за дентални клиники въз основа на тези ТОП 25 промоции към {timestamp}:

{data_for_ai}

ПРАВИЛА ЗА ДОКЛАД:
1. Кратък списък във формат: Продукт | Сайт | Актуална Цена | Отстъпка%.
2. Сгрупирай продуктите логически по марки или приложения (напр. Ендодонтия, Анестетици, Композити), за да бъде лесно за четене.
3. Накрая изведи ТОП 3 задължителни покупки ("МЕГА СДЕЛКИ") с най-голямо реално спестяване в лева.
4. Пиши директно, без уводни изречения и празни приказки."""

    try:
        ai_text, backend = generate_ai_report(prompt, provider=provider)
        
        # Calculate exact total potential savings in Python for 100% mathematical accuracy
        # (This prevents LLM hallucination and guarantees correct math at the top of the report!)
        try:
            from app.services.ai_service import sanitize_dental_data
            sanitized = sanitize_dental_data(recent_promos)
            valid_items = [p for p in sanitized if p.get("discount_percent", 0) >= 15.0]
            total_savings = sum(max(p.get("old_price", 0) - p.get("promo_price", 0), 0) for p in valid_items)
            
            # Prepend a premium, styled markdown banner showing the exact calculated total savings
            if total_savings > 0 and backend != "error_fallback":
                savings_banner = f"## 🎁 **Общо спестена сума от текущите отстъпки: {total_savings:.2f} лв.**\n*(Сумата представлява потенциалното Ви спестяване при закупуване на един брой от всеки намален продукт спрямо редовните пазарни цени).*\n\n---\n\n"
                ai_text = savings_banner + ai_text
        except Exception as math_err:
            print(f"Failed to prepend exact savings math: {math_err}")
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return {
        "ai_report": ai_text,
        "products_analyzed": len(data_for_ai),
        "timestamp": timestamp,
        "backend": backend,
    }


@app.get("/health")
def health_check():
    """Simple health check for DB and Gemini services."""
    db_ok = False
    gemini_ok = bool(os.getenv("GEMINI_API_KEY"))

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_ok = True
    except Exception:
        db_ok = False

    return {"db": db_ok, "gemini": gemini_ok}


class InventoryUpdateSchema(BaseModel):
    quantity: int
    max_quantity: int


@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    """Retrieve all products with their latest price using an efficient subquery join."""
    # Create subquery to get the absolute latest entry ID per product_id
    latest_price_sub = (
        db.query(
            PriceHistoryDB.product_id, func.max(PriceHistoryDB.id).label("latest_id")
        )
        .group_by(PriceHistoryDB.product_id)
        .subquery()
    )

    # Single-step efficient join execution (Fixes the N+1 loop issue entirely)
    records = (
        db.query(ProductDB, PriceHistoryDB)
        .outerjoin(latest_price_sub, ProductDB.id == latest_price_sub.c.product_id)
        .outerjoin(PriceHistoryDB, PriceHistoryDB.id == latest_price_sub.c.latest_id)
        .all()
    )

    result = []
    for product, price in records:
        low_stock_alert = product.quantity <= 0.2 * product.max_quantity if product.max_quantity > 0 else False
        result.append(
            {
                "id": product.id,
                "name": product.name,
                "url": product.url,
                "brand": product.brand,
                "source": product.source_site,
                "latest_price": float(price.new_price) if price else None,
                "old_price": float(price.old_price) if price else None,
                "is_promotion": price.is_promotion if price else False,
                "last_updated": price.scrapped_at.isoformat() if price else None,
                "quantity": product.quantity,
                "max_quantity": product.max_quantity,
                "low_stock_alert": low_stock_alert
            }
        )
    return result


@app.put("/products/{product_id}/inventory")
def update_product_inventory(product_id: int, data: InventoryUpdateSchema, db: Session = Depends(get_db), current_user: dict = Depends(verify_supabase_jwt)):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    product.quantity = data.quantity
    product.max_quantity = data.max_quantity
    db.commit()
    return {
        "id": product.id,
        "name": product.name,
        "quantity": product.quantity,
        "max_quantity": product.max_quantity,
        "low_stock_alert": product.quantity <= 0.2 * product.max_quantity if product.max_quantity > 0 else False
    }


# --- Mount frontend static files safely at the very bottom ---
# For Vite + React compiled static assets in production, mount the 'dist' subdirectory if available
frontend_dir = os.path.join(_parent_dir, "frontend", "dist")
if not os.path.exists(frontend_dir):
    frontend_dir = os.path.join(_parent_dir, "frontend")

if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
