# utility.py
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os



DB_USER ="postgres"
DB_PASSWORD ="statefarm"
DB_NAME = "postgres"
DB_HOST = "35.222.41.70"  # <- Public IP of your Cloud SQL instance
DB_PORT =  "5432"

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# ✅ Test block to check connection when script is run directly
if __name__ == "__main__":
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Successfully connected to the database.")
            print("Query result:", result.scalar())
    except Exception as e:
        print("❌ Failed to connect to the database.")
        print("Error:", e)
