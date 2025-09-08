import os
import requests
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()
DB_URL = os.getenv("DB_URL")
if not DB_URL:
    raise RuntimeError("missing DB_URL in .env")

TARGET_SCHEMA = "stg"
TARGET_TABLE = "usd_ils_rates"
DRY_RUN = True

def find_date_range(engine):
    with engine.connect() as conn:
        row = conn.execute(text("""
            select min(invoicedate)::date, max(invoicedate)::date
            from stg.invoice
        """)).fetchone()
    return row[0], row[1]

def fetch_rates(start_date, end_date):
    url = "https://api.exchangerate.host/timeseries"
    params = {"start_date": str(start_date), "end_date": str(end_date),
              "base": "USD", "symbols": "ILS"}
    r = requests.get(url, params=params, timeout=30)
    data = r.json()
    if "rates" not in data:
        raise RuntimeError("api error")
    rows = []
    for d, obj in sorted(data["rates"].items()):
        rows.append({"rate_date": d, "usd_ils_rate": obj["ILS"]})
    return pd.DataFrame(rows)

def load_to_db(engine, df):
    with engine.begin() as conn:
        df.to_sql(TARGET_TABLE, engine, schema=TARGET_SCHEMA, if_exists="append", index=False)

def main():
    engine = create_engine(DB_URL)
    s, e = find_date_range(engine)
    print(f"[range] {s} -> {e} (origin: stg.invoice)")
    df = fetch_rates(s, e)
    print(f"[api] fetched {len(df)} rows, sample:")
    print(df.head())
    if DRY_RUN:
        print("[dry-run] no db writes")
        return
    load_to_db(engine, df)
    with engine.connect() as conn:
        cnt, mn, mx = conn.execute(
            text(f"select count(*), min(rate_date), max(rate_date) from {TARGET_SCHEMA}.{TARGET_TABLE}")
        ).fetchone()
    print(f"[done] {TARGET_SCHEMA}.{TARGET_TABLE} rows={cnt}, range {mn}..{mx}")

if __name__ == "__main__":
    main()
