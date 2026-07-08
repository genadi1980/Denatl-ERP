import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("SELECT source_site, count(*) FROM products GROUP BY source_site"))
    for row in result:
        print(f"Site: {row[0]} | Count: {row[1]}")
