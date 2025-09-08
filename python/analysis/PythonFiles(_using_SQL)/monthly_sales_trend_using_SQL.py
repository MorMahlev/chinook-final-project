import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DB_URL")
if not DB_URL:
    raise ValueError("STOP! DB_URL not found!")
engine = create_engine(DB_URL)

sql = """
select 
  extract(year from i.invoice_date)::int  as year_,
  extract(month from i.invoice_date)::int as month_,
  sum(il.unitprice * il.quantity) as total_usd
from dwh2.fact_invoiceline il
join dwh2.fact_invoice i on i.invoice_key = il.invoice_key
group by 1,2
order by 1,2
;
"""
df = pd.read_sql(sql, engine)

pvt = df.pivot(index="month_", columns="year_", values="total_usd").fillna(0).sort_index()
months = pvt.index.tolist()
years  = pvt.columns.tolist()
n_years = len(years)


PALETTE = ["#d8cfc2", "#c0c8bf", "#aebfc7", "#d6bda9", "#c7d2cc", "#bfc7d9"]  
colors = [PALETTE[i % len(PALETTE)] for i in range(n_years)]

plt.rcParams.update({
    "axes.facecolor": "white",
    "figure.facecolor": "white",
    "axes.edgecolor": "#888888",
    "grid.color": "#e6e6e6",
})

fig, ax = plt.subplots(figsize=(12, 6))
x = range(len(months))
bar_width = 0.8 / max(n_years, 1) 

bars_per_year = []
for idx, yr in enumerate(years):
    offsets = [i - 0.4 + bar_width/2 + idx*bar_width for i in x]
    bars = ax.bar(offsets, pvt[yr].values, width=bar_width, label=str(yr), color=colors[idx])
    bars_per_year.append(bars)


ax.set_title("Monthly Sales Trend by Year (USD) — Grouped Bars", pad=12, fontsize=12)
ax.set_xlabel("Month")
ax.set_ylabel("Total (USD)")
ax.set_xticks(list(x))
ax.set_xticklabels(months)
ax.grid(axis="y", linestyle="--", alpha=0.5)
ax.legend(title="Year", ncol=min(3, n_years), frameon=True)


for bars in bars_per_year:
    for b in bars:
        v = b.get_height()
        if v > 0:
            ax.text(b.get_x() + b.get_width()/2, v, f"{v:,.0f}", ha="center", va="bottom", fontsize=6)

plt.tight_layout()
plt.savefig("monthly_sales_trend_bars_using_SQL.png", dpi=180)
plt.show()
