from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import os

# Load .env from project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
database = os.getenv("POSTGRES_DB")
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")

connection_url = (
    f"postgresql+psycopg2://{user}:{password}"
    f"@{host}:{port}/{database}"
)

engine = create_engine(connection_url)

with engine.connect() as connection:
    result = connection.execute(text("SELECT version();"))
    print("Connected successfully!")
    print(result.fetchone()[0])