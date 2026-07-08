import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

sys.path.insert(0, os.getcwd())

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def update_schema():
    print("Checking and updating database schema...")
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        try:
            # Add quantity and max_quantity columns if they don't exist
            conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS quantity INT DEFAULT 10;"))
            conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS max_quantity INT DEFAULT 10;"))
            conn.commit()
            print("Successfully updated schema: added 'quantity' and 'max_quantity' columns.")
        except Exception as e:
            print(f"Error updating database schema: {e}")

if __name__ == "__main__":
    update_schema()
