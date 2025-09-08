import os
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
OUT  = ROOT / "data" / "outputs"

CSV = OUT / "department_budget.csv"

if not CSV.exists():
    raise SystemExit(f"Output file not found: {CSV}")

load_dotenv(ROOT / ".env")
DB_URL = os.getenv("DB_URL")
if not DB_URL:
    raise SystemExit("DB_URL is missing in .env")

engine = create_engine(DB_URL)

df = pd.read_csv(CSV)

with engine.begin() as conn:
    user = conn.execute(text("select current_user")).scalar()
    conn.execute(text(f"create schema if not exists stg authorization {user}"))
    df.to_sql("department_budget", con=conn, schema="stg",
              if_exists="replace", index=False)

print("Loaded stg.department_budget successfully.")
