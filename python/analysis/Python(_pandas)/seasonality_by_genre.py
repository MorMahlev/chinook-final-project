import os
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DB_URL")
if not DB_URL:
    raise RuntimeError("DB_URL is not set in .env")

engine = create_engine(DB_URL)

SQL = """select
    i.invoice_date::date as invoice_date,
    t.genre,
    il.line_total as amount_usd
from dwh2.fact_invoiceline il
join dwh2.fact_invoice i on i.invoice_key = il.invoice_key
join dwh2.dim_track t on t.track_key = il.track_key;
"""
df = pd.read_sql(SQL, engine)
if df.empty:
    raise RuntimeError("DWH2 returned no rows. Check your ETL / tables.")

df["invoice_date"] = pd.to_datetime(df["invoice_date"])
df["month"] = df["invoice_date"].dt.month

agg = (df.groupby(["month", "genre"], as_index=False)["amount_usd"].sum().rename(columns={"amount_usd": "total_usd"}))
top5 = (agg.groupby("genre")["total_usd"]
       .sum()
       .sort_values(ascending=False)
       .head(5)
       .index
       .tolist())
preferred = ["Alternative & Punk", "Jazz", "Latin", "Metal", "Rock"]
order = [g for g in preferred if g in top5] + [g for g in top5 if g not in preferred]
agg_top = agg[agg["genre"].isin(order)].copy()

pivot = (agg_top.pivot_table(
        index= "month", columns="genre", values="total_usd", aggfunc="sum")
         .reindex(range(1, 13))
           .fillna(0.0))

pivot = pivot[[c for c in order if c in pivot.columns]]

pastel_colors = [
    "#d8cfc2",
    "#c0c8bf",
    "#aebfc7",
    "#d6bda9",
    "#e3b7b3",
    "#b5cbb7",
]

fig, ax = plt.subplots(figsize=(16, 6))

months = pivot.index.to_list()
genres = list(pivot.columns)
n_groups = len(months)
n_bars   = max(len(genres), 1)
bar_width = 0.8 / n_bars
x_base = pd.Series(range(n_groups), index=months)

for i, g in enumerate(genres):
    x = x_base + (i - (n_bars - 1) / 2) * bar_width
    bars = ax.bar(
        x,
        pivot[g].values,
        width=bar_width,
        label=g,
        color=pastel_colors[i % len(pastel_colors)],  
        edgecolor="#666", linewidth=0.5)
    
    for b, val in zip(bars, pivot[g].values):
        ax.text(
            b.get_x() + b.get_width()/2, b.get_height()+2,
            f"{int(round(val))}",
            ha="center", va="bottom", fontsize=9, color="#444")
        
ax.set_title("Seasonality by Genre — Grouped Monthly Sales (Top 5 Genres)")
ax.set_xlabel("Month")
ax.set_ylabel("Total (USD)")
ax.set_xticks(range(n_groups))
ax.set_xticklabels(months)
ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.25),
          ncol= min(len(genres), 5),
          frameon=False,
          fontsize= 10)
ax.margins(x=0.01)
ax.set_facecolor("#faf7f2") 
fig.patch.set_facecolor("#faf7f2")
ax.grid(axis="y", linestyle=":", linewidth=0.6, color="#cfc8bc")
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
plt.tight_layout()


fig.savefig("seasonality_by_genre.png", dpi=160)
plt.show()