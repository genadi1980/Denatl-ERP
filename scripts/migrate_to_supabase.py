import os
import sys
import sqlite3
from sqlalchemy import create_engine, Table, MetaData
from dotenv import load_dotenv

sys.path.insert(0, os.getcwd())

load_dotenv()

SQLITE_DB_PATH = "dental_tracker.db"
DATABASE_URL = os.getenv("DATABASE_URL")

def migrate():
    """Copies all products and price history from SQLite to Supabase Postgres."""
    if not DATABASE_URL:
        print("Error: DATABASE_URL is not set in your .env file!")
        return
        
    if "sqlite" in DATABASE_URL:
        print("Error: Your DATABASE_URL is still pointing to SQLite! Update it to your Supabase PostgreSQL connection string.")
        return

    if not os.path.exists(SQLITE_DB_PATH):
        print(f"No local SQLite database found at {SQLITE_DB_PATH} to migrate. Skipping data copy.")
        return

    print("Connecting to Supabase PostgreSQL database...")
    postgres_engine = create_engine(DATABASE_URL)
    
    # 1. Initialize Postgres Schema dynamically
    from app.database import Base
    print("Deploying schema tables 'products' and 'price_history' to Supabase...")
    Base.metadata.create_all(bind=postgres_engine)
    print("Schema successfully deployed!")

    # 2. Extract SQLite data
    print(f"Extracting local records from {SQLITE_DB_PATH}...")
    sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
    sqlite_cursor = sqlite_conn.cursor()

    try:
        sqlite_cursor.execute("SELECT id, name, url, brand, source_site, quantity, max_quantity FROM products")
        local_products = sqlite_cursor.fetchall()
        print(f"Found {len(local_products)} products in SQLite.")
    except Exception as e:
        print(f"Could not read products from SQLite: {e}")
        local_products = []

    try:
        sqlite_cursor.execute("SELECT id, product_id, old_price, new_price, is_promotion, scrapped_at FROM price_history")
        local_prices = sqlite_cursor.fetchall()
        print(f"Found {len(local_prices)} price history entries in SQLite.")
    except Exception as e:
        print(f"Could not read price history from SQLite: {e}")
        local_prices = []

    if not local_products:
        print("No local data found. Migration complete.")
        return

    # 3. Seed Supabase PostgreSQL
    meta = MetaData()
    products_table = Table("products", meta, autoload_with=postgres_engine)
    price_history_table = Table("price_history", meta, autoload_with=postgres_engine)

    with postgres_engine.connect() as pg_conn:
        # Copy products
        print("Migrating products to Supabase...")
        product_id_map = {} # Maps SQLite IDs to Postgres IDs if they change
        
        for row in local_products:
            sql_id, name, url, brand, source_site, quantity, max_quantity = row
            try:
                # Check if already exists in PG
                stmt = products_table.select().where(products_table.c.url == url)
                existing = pg_conn.execute(stmt).fetchone()
                
                if not existing:
                    ins_stmt = products_table.insert().values(
                        name=name,
                        url=url,
                        brand=brand,
                        source_site=source_site,
                        quantity=quantity,
                        max_quantity=max_quantity
                    )
                    res = pg_conn.execute(ins_stmt)
                    pg_id = res.inserted_primary_key[0]
                    product_id_map[sql_id] = pg_id
                else:
                    product_id_map[sql_id] = existing[0] # existing.id
            except Exception as ins_err:
                print(f"  Failed to migrate product '{name}': {ins_err}")

        pg_conn.commit()
        print(f"Successfully migrated product definitions.")

        # Copy price history
        print("Migrating price history entries to Supabase...")
        inserted_prices = 0
        for row in local_prices:
            sql_price_id, sql_prod_id, old_price, new_price, is_promotion, scrapped_at = row
            
            # Map SQLite product ID to Supabase product ID
            pg_prod_id = product_id_map.get(sql_prod_id)
            if not pg_prod_id:
                continue
                
            try:
                # Insert price history entry
                ins_stmt = price_history_table.insert().values(
                    product_id=pg_prod_id,
                    old_price=old_price,
                    new_price=new_price,
                    is_promotion=bool(is_promotion),
                    scrapped_at=scrapped_at
                )
                pg_conn.execute(ins_stmt)
                inserted_prices += 1
            except Exception as price_err:
                pass
                
        pg_conn.commit()
        print(f"Successfully migrated {inserted_prices} historical price records to Supabase!")

    sqlite_conn.close()
    print("Migration finished successfully!")

if __name__ == "__main__":
    migrate()
