import os
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DB_URL")
if not DB_URL:
    raise ValueError("STOP! DB_URL not found!")
engine = create_engine(DB_URL)

df_inv = pd.read_sql("select invoice_key as invoice_id, invoice_date from dwh2.fact_invoice", engine)
df_line = pd.read_sql("select invoice_key as invoice_id, line_total as line_total_usd from dwh2.fact_invoiceline", engine)


sum_per_inv = (df_line.groupby("invoice_id", as_index=False)["line_total_usd"].sum())
inv_with_sum = df_inv.merge(sum_per_inv, on= "invoice_id", how= "inner")
inv_with_sum["invoice_date"] = pd.to_datetime(inv_with_sum["invoice_date"])
inv_with_sum["year_"]  = inv_with_sum["invoice_date"].dt.year.astype(int)
inv_with_sum["month_"] = inv_with_sum["invoice_date"].dt.month.astype(int)

df = (inv_with_sum.groupby(["year_", "month_"], as_index=False)["line_total_usd"].sum().rename(columns={"line_total_usd": "total_usd"}))
pvt = (df.pivot(index="month_", columns="year_", values="total_usd").fillna(0).sort_index())
months  = pvt.index.tolist()
years   = pvt.columns.tolist()
n_years = len(years)


PALETTE = ["#d8cfc2", "#c0c8bf", "#aebfc7", "#d6bda9", "#c7d2cc", "#bfc7d9"]
colors  = [PALETTE[i % len(PALETTE)] for i in range(n_years)]

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
    offsets = [i - 0.4 + bar_width/2 + idx * bar_width for i in x]
    bars = ax.bar(offsets, pvt[yr].values,
                  width=bar_width, label=str(yr), color=colors[idx])
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
            ax.text(b.get_x() + b.get_width()/2, v, f"{v:,.0f}",
                    ha="center", va="bottom", fontsize=6)

plt.tight_layout()
plt.savefig("monthly_sales_trend_bars.png", dpi=180)
plt.show()
