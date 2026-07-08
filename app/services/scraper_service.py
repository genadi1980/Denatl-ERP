import os
import re
import traceback
from decimal import Decimal
from playwright.sync_api import sync_playwright

# Ensure these imports align with your repository paths
from app.database import SessionLocal
from models.models import ProductDB, PriceHistoryDB


def parse_decimal(raw_text: str) -> Decimal:
    """Robustly extract a price from messy text. Returns 0 on failure."""
    if not raw_text:
        return Decimal("0")

    # 1. Clean up non-breaking spaces, zero-width spaces
    text = (
        raw_text.replace("\u00a0", " ")
        .replace("\xa0", " ")
        .replace("\u202f", " ")
        .replace("\u200b", "")
        .strip()
    )

    # 2. Handle dual currency strings (e.g. "2 760,00 €/5 398,09 лв.")
    # Prioritize BGN if both are present
    if "€" in text and ("лв" in text or "bgn" in text.lower()):
        parts = text.split("/")
        for p in parts:
            if "лв" in p or "bgn" in p.lower():
                text = p
                break

    lowered = text.lower()

    # 3. Check for freebies
    if any(word in lowered for word in ["free", "безплатно", "подарък"]):
        return Decimal("0")

    # 4. Strip out common language prefixes
    for prefix in ["from", "от", "starting at"]:
        if lowered.startswith(prefix):
            text = text[len(prefix) :].strip()
            break

    # 5. Clean up currency tokens before using RegEx
    text = (
        text.replace("€", "")
        .replace("лв.", "")
        .replace("лв", "")
        .replace("bgn", "")
        .replace("BGN", "")
        .strip()
    )

    # 6. Extract numbers
    numbers = re.findall(r"\d+[\s.,]?\d*[\s.,]?\d*", text)
    if not numbers:
        return Decimal("0")

    # Extract the first matching block and normalize decimal separators
    val_str = numbers[0].replace(" ", "").strip()
    
    # Handle European decimal formatting (e.g. "1.234,56" or "1 234,56" or "1234,56")
    if "," in val_str:
        if "." in val_str:
            val_str = val_str.replace(".", "")
        val_str = val_str.replace(",", ".")
    elif val_str.count(".") > 1:
        # e.g., "1.234.56" -> "1234.56"
        parts = val_str.split(".")
        val_str = "".join(parts[:-1]) + "." + parts[-1]

    try:
        return Decimal(val_str)
    except Exception:
        return Decimal("0")


def find_cards(page, site_name, selectors, expected_min=1):
    """Safely returns elements for card selectors."""
    for sel in selectors:
        cards = page.query_selector_all(sel)
        if len(cards) >= expected_min:
            return cards
    return []


def matches_target_materials(product_name: str):
    """
    Checks if a product name matches any of our target materials.
    Returns (matched_category_name, brand) or (None, None)
    """
    name_lower = product_name.lower()
    
    # 1. everX Flow - GC марка (Dentin, Shade, Bulk Shade)
    if "everx" in name_lower and "flow" in name_lower:
        if "dentin" in name_lower:
            return "everX Flow Dentin", "GC"
        elif "bulk" in name_lower or "shade" in name_lower:
            return "everX Flow Bulk", "GC"
        else:
            return "everX Flow", "GC"
            
    # 2. G-aenial Posterior - A2, A3, A3.5
    if "posterior" in name_lower and ("g-aenial" in name_lower or "gaenial" in name_lower or "gc" in name_lower):
        if "a2" in name_lower:
            return "G-aenial Posterior A2", "GC"
        elif "a3.5" in name_lower or "a3,5" in name_lower:
            return "G-aenial Posterior A3.5", "GC"
        elif "a3" in name_lower:
            return "G-aenial Posterior A3", "GC"
        else:
            return "G-aenial Posterior", "GC"
            
    # 3. G-aenial Universal Injectable A2 / A3
    if ("g-aenial" in name_lower or "gaenial" in name_lower) and "injectable" in name_lower:
        if "a2" in name_lower:
            return "G-aenial Universal Injectable A2", "GC"
        elif "a3" in name_lower:
            return "G-aenial Universal Injectable A3", "GC"
        else:
            return "G-aenial Universal Injectable", "GC"
            
    # 4. G-Premio Bond
    if ("g-premio" in name_lower or "gpremio" in name_lower) and "bond" in name_lower:
        return "G-Premio Bond", "GC"
        
    # 5. C-Pilot files 25 mm V 04 0368 025 006 / 008 / 010 / 015
    if "c-pilot" in name_lower or ("c" in name_lower and "pilot" in name_lower and "vdw" in name_lower):
        # We also check if it contains 25mm
        if "25" in name_lower:
            if "006" in name_lower or name_lower.endswith("06") or " 06" in name_lower or "size 6" in name_lower or "размер 6" in name_lower:
                return "C-Pilot files 25 mm V 04 0368 025 006", "VDW"
            elif "008" in name_lower or name_lower.endswith("08") or " 08" in name_lower or "size 8" in name_lower or "размер 8" in name_lower:
                return "C-Pilot files 25 mm V 04 0368 025 008", "VDW"
            elif "010" in name_lower or name_lower.endswith("10") or " 10" in name_lower or "size 10" in name_lower or "размер 10" in name_lower:
                return "C-Pilot files 25 mm V 04 0368 025 010", "VDW"
            elif "015" in name_lower or name_lower.endswith("15") or " 15" in name_lower or "size 15" in name_lower or "размер 15" in name_lower:
                return "C-Pilot files 25 mm V 04 0368 025 015", "VDW"
            else:
                return "C-Pilot files 25 mm", "VDW"
        elif "21" in name_lower:
            return "C-Pilot files 21 mm", "VDW"
        elif "19" in name_lower:
            return "C-Pilot files 19 mm", "VDW"
        else:
            return "C-Pilot files", "VDW"
            
    return None, None


def run_dental_scraper_task():
    db = SessionLocal()
    browser = None

    # We perform search-based scraping for our specific queries
    queries = ["everX", "G-aenial", "G-Premio", "C-Pilot"]
    
    sites = [
        {
            "name": "dentstore.bg", 
            "search_url_template": "https://dentstore.bg/search?controller=search&s={query}",
            "card_selectors": [".product-miniature", ".product-item", "[data-id-product]"]
        },
        {
            "name": "belvezar.com", 
            "search_url_template": "https://belvezar.com/search.html?q={query}",
            "card_selectors": [".gs-grid-item", ".product-item, .product-card"]
        },
        {
            "name": "patricia.bg", 
            "search_url_template": "https://patricia.bg/catalogsearch/result/?q={query}",
            "card_selectors": [".product-item", ".product-thumb", ".product-layout", "li.item.product-item"]
        },
    ]

    try:
        if os.name == "nt":
            try:
                import asyncio
                loop = asyncio.ProactorEventLoop()
                asyncio.set_event_loop(loop)
            except Exception:
                pass

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            for site in sites:
                print(f"Scraping site: {site['name']}...")
                page = browser.new_page()
                
                # High-Performance Network Asset Interception (300% Speedup & Bandwidth Savings)
                try:
                    def intercept_assets(route):
                        resource_type = route.request.resource_type
                        # Abort heavy rendering assets (images, stylesheets, fonts, media)
                        if resource_type in ["image", "stylesheet", "font", "media"]:
                            return route.abort()
                        
                        # Block tracking script domains and marketing tags
                        url = route.request.url.lower()
                        if any(term in url for term in ["analytics", "pixel", "facebook", "doubleclick", "hotjar", "gtm.js"]):
                            return route.abort()
                            
                        return route.continue_()
                    
                    page.route("**/*", intercept_assets)
                except Exception as route_err:
                    print(f"    Failed to register network interceptor: {route_err}")
                
                try:
                    for query in queries:
                        target_url = site["search_url_template"].format(query=query)
                        print(f"  Searching for '{query}' -> {target_url}")
                        
                        try:
                            page.goto(target_url, wait_until="networkidle", timeout=60000)
                        except Exception as e:
                            print(f"    Timeout or error navigating to {target_url}: {e}")
                            continue

                        # --- Extract product cards ---
                        product_cards = find_cards(
                            page,
                            site["name"],
                            site["card_selectors"],
                        )
                        
                        if not product_cards:
                            print(f"    No cards found for query '{query}' on {site['name']}")
                            continue

                        print(f"    Found {len(product_cards)} product cards for '{query}'")
                        
                        for card in product_cards:
                            # --- Parse site-specific card elements ---
                            name, link, p_new, p_old, is_promo = None, None, None, None, False
                            
                            try:
                                if site["name"] == "dentstore.bg":
                                    name_elem = card.query_selector(".product-title") or card.query_selector("a[title]")
                                    link_elem = card.query_selector("a.thumbnail.product-thumbnail") or card.query_selector("a.product-link") or card.query_selector("a")
                                    price_elem = card.query_selector(".product-price-and-shipping .price") or card.query_selector(".price")
                                    old_price_elem = card.query_selector(".product-price-and-shipping .regular-price") or card.query_selector(".regular-price")

                                    if name_elem and link_elem and price_elem:
                                        name = (name_elem.inner_text() or "").strip()
                                        raw_link = link_elem.get_attribute("href") or ""
                                        link = raw_link.strip()
                                        p_new = parse_decimal(price_elem.inner_text())
                                        
                                        old_price_text = (old_price_elem.inner_text() or "").strip() if old_price_elem else ""
                                        p_old = parse_decimal(old_price_text) if old_price_text else p_new
                                        is_promo = bool(old_price_text)

                                elif site["name"] == "belvezar.com":
                                    name_elem = card.query_selector(".gs-item-title") or card.query_selector("a.product-name, .product-title")
                                    price_elem = card.query_selector(".gs-new-price") or card.query_selector(".price, .new-price")
                                    old_price_elem = card.query_selector(".gs-old-price") or card.query_selector(".old-price")

                                    if name_elem and price_elem:
                                        name = (name_elem.inner_text() or "").strip()
                                        raw_link = name_elem.get_attribute("href") or ""
                                        link = raw_link.strip()
                                        if link and not link.startswith("http"):
                                            link = "https://belvezar.com" + link
                                            
                                        p_new = parse_decimal(price_elem.inner_text())
                                        old_price_text = (old_price_elem.inner_text() or "").strip() if old_price_elem else ""
                                        p_old = parse_decimal(old_price_text) if old_price_text else p_new
                                        is_promo = bool(old_price_text)

                                elif site["name"] == "patricia.bg":
                                    name_elem = (
                                        card.query_selector(".product-name a")
                                        or card.query_selector(".name a")
                                        or card.query_selector("strong.product-name a")
                                        or card.query_selector("a.product-item-link")
                                    )
                                    price_elem = (
                                        card.query_selector(".price-new")
                                        or card.query_selector(".special")
                                        or card.query_selector("[data-price-type='finalPrice'] .price")
                                        or card.query_selector(".price")
                                    )
                                    old_price_elem = (
                                        card.query_selector(".price-old")
                                        or card.query_selector(".old-price")
                                        or card.query_selector("[data-price-type='oldPrice'] .price")
                                    )

                                    if name_elem and price_elem:
                                        name = (name_elem.inner_text() or "").strip()
                                        raw_link = name_elem.get_attribute("href") or ""
                                        link = raw_link.strip()
                                        if link and not link.startswith("http"):
                                            link = "https://patricia.bg" + link
                                            
                                        p_new = parse_decimal(price_elem.inner_text())
                                        old_price_text = (old_price_elem.inner_text() or "").strip() if old_price_elem else ""
                                        p_old = parse_decimal(old_price_text) if old_price_text else p_new
                                        is_promo = bool(old_price_text and p_old > p_new)

                            except Exception as card_err:
                                print(f"      Error parsing card: {card_err}")
                                continue

                            # --- Process and save if matches target materials ---
                            if name and link and p_new is not None:
                                matched_name, brand = matches_target_materials(name)
                                if matched_name:
                                    save_product(
                                        db, name, link, p_old, p_new, is_promo, site["name"], brand=brand
                                    )
                                    
                except Exception as site_err:
                    print(f"  Error scraping site {site['name']}: {site_err}")
                    traceback.print_exc()
                finally:
                    page.close()

    except Exception as global_err:
        print(f"Global execution error: {global_err}")
    finally:
        if browser:
            try:
                browser.close()
            except Exception:
                pass
        db.close()


def sanitize_dental_data(products):
    for p in products:
        # Normalize and safely handle raw data conversion
        base = (
            float(re.sub(r"[^\d.]", "", str(p.get("base_price", 0)).replace(",", ".")))
            if p.get("base_price")
            else 0.0
        )
        promo = (
            float(re.sub(r"[^\d.]", "", str(p.get("promo_price", 0)).replace(",", ".")))
            if p.get("promo_price")
            else 0.0
        )

        # Correct flipped entry bugs
        if base < promo and base > 0:
            base, promo = promo, base

        p["base_price"] = base
        p["promo_price"] = promo
        p["discount_percent"] = (
            round(((base - promo) / base) * 100, 1) if base > 0 else 0.0
        )
    return products


def save_product(db, name, link, p_old, p_new, is_promo, site_name, brand=None):
    """Saves or updates product in DB, and adds an entry in the price history."""
    print(
        f"Saving [{site_name}] {name} - New: {p_new}, Old: {p_old}, Promo: {is_promo}, Brand: {brand}"
    )
    try:
        # Clean values to avoid None values or float types
        old_price_val = Decimal(str(p_old)) if p_old is not None else Decimal(str(p_new))
        new_price_val = Decimal(str(p_new))

        # Check if product already exists by URL
        product = db.query(ProductDB).filter(ProductDB.url == link).first()
        if not product:
            product = ProductDB(
                name=name,
                url=link,
                brand=brand,
                source_site=site_name
            )
            db.add(product)
            db.commit()
            db.refresh(product)
        else:
            # Update name and brand if they changed
            product.name = name
            if brand:
                product.brand = brand
            db.commit()
            
        # Add price history entry
        price_history = PriceHistoryDB(
            product_id=product.id,
            old_price=old_price_val,
            new_price=new_price_val,
            is_promotion=is_promo
        )
        db.add(price_history)
        db.commit()
    except Exception as e:
        print(f"Error saving product to DB: {e}")
        db.rollback()
