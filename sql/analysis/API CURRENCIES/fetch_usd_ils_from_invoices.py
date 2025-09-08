import requests
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DB_URL")
if not DB_URL:
    raise ValueError("STOP! DB_URL not found!")
engine = create_engine(DB_URL)

API_BASE = "https://api.frankfurter.app" 
BASE = "USD"
TO   = "ILS"
TIMEOUT = 30

def get_invoice_date_range(conn):
    with conn.cursor() as cur:
        try:
            cur.execute("""
                select min(invoicedate)::date, max(invoicedate)::date
                from stg.invoice
            """)
            row = cur.fetchone()
            if row and row[0] and row[1]:
                return row[0].isoformat(), row[1].isoformat()
        except psycopg2.errors.UndefinedTable:
            conn.rollback()

        cur.execute("""
            select min(invoicedate)::date, max(invoicedate)::date
            from public.invoice
        """)
        row = cur.fetchone()
        if not row or not row[0] or not row[1]:
            raise RuntimeError("Could not determine invoice date range from STG or PUBLIC.")
        return row[0].isoformat(), row[1].isoformat()

def fetch_series(start, end):
    url = f"{API_BASE}/{start}..{end}?from={BASE}&to={TO}"
    resp = requests.get(url, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    if "rates" not in data or not isinstance(data["rates"], dict):
        raise ValueError(f"Unexpected API response: {data}")
    rows = []
    for d, obj in sorted(data["rates"].items()):
        rate = obj.get(TO)
        if rate is None:
            continue
        rows.append((d, rate, "frankfurter.app"))
    return rows

def ensure_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
        create schema if not exists stg;
        create table if not exists stg.usd_ils_rates(
            rate_date   date primary key,
            usd_ils_rate numeric(18,8) not null,
            source      text not null default 'frankfurter.app',
            loaded_at   timestamptz not null default now()
        );
        """)
    conn.commit()

def upsert_rates(conn, rows):
    if not rows:
        return 0
    with conn.cursor() as cur:
        execute_values(cur, """
            insert into stg.usd_ils_rates(rate_date, usd_ils_rate, source)
            values %s
            on conflict (rate_date) do update
              set usd_ils_rate = excluded.usd_ils_rate,
                  source      = excluded.source,
                  loaded_at   = now()
        """, rows)
    conn.commit()
    return len(rows)

def main():
    conn = psycopg2.connect(DB_URL)
    try:
        ensure_table(conn)
        start, end = get_invoice_date_range(conn)
        print(f"Invoice date range (source): {start}..{end}")
        rows = fetch_series(start, end)
        n = upsert_rates(conn, rows)
        print(f"Done. Rows upserted into stg.usd_ils_rates: {n}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()