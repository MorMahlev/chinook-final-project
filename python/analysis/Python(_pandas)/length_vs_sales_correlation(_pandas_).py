import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from sqlalchemy import create_engine
from getpass import getpass

user = "postgres"
password = getpass("Enter DB password: ")
host = "localhost"
port = "5432"
database = "chinook"

engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}")


PALETTE = {
    "points":    "#8fa99a",  
    "points_ec": "#333333",  
    "line":      "#5f4d3e",  
    "highlight": "#8c6a5d",  
    "text":      "#966d5c",
    "grid":      "#e6e6e6",
}

plt.rcParams.update({
    "axes.facecolor":  "white",
    "figure.facecolor":"white",
    "axes.edgecolor":  "#888888",
    "grid.color":      PALETTE["grid"],
})

sql = """
with line_sales as (
  select il.track_key as track_id,
         sum(il.unitprice * il.quantity) as total_usd
  from dwh2.fact_invoiceline il
  group by il.track_key
),
track_len as (
  select t.track_key as track_id,
         t.track_name,
         (t.milliseconds/1000.0) as duration_sec
  from dwh2.dim_track t
),
joined as (
  select tl.track_name,
         tl.duration_sec,
         ls.total_usd
  from track_len tl
  join line_sales ls on tl.track_id = ls.track_id
  where tl.duration_sec is not null
)
select *
from joined
;
"""

df = pd.read_sql(sql, engine)


pearson = df["duration_sec"].corr(df["total_usd"])
fit = np.polyfit(df["duration_sec"], df["total_usd"], 1)
line = np.poly1d(fit)


fig, ax = plt.subplots(figsize=(10, 6), dpi=150)


ax.scatter(
    df["duration_sec"], df["total_usd"],
    s=35, alpha=0.7,
    color=PALETTE["points"],
    edgecolor=PALETTE["points_ec"], linewidth=0.6,
    label="Tracks" , zorder=1
)


x_line = np.linspace(df["duration_sec"].min(), df["duration_sec"].max(), 300)
ax.plot(x_line, line(x_line), color=PALETTE["line"], linewidth=1.5, zorder=1, label="Regression")


top_sales = df.nlargest(5, "total_usd")
top_len   = df.nlargest(5, "duration_sec")
hi = pd.concat([top_sales, top_len]).drop_duplicates()

ax.scatter(
    hi["duration_sec"], hi["total_usd"],
    s=40 , color=PALETTE["highlight"], zorder=3,
    edgecolor="#5a4036", linewidth=0.6,
    label="Top sales/length"
)

offsets = [(8,8), (8,-8), (-8,8), (-8,-8), (12,0)]
for i, (_, r) in enumerate(hi.iterrows()):
    ax.annotate(
        r["track_name"][:20],
        (r["duration_sec"], r["total_usd"]),
        textcoords="offset points", xytext=offsets[i % len(offsets)],
        fontsize=8, color=PALETTE["text"],
        bbox=dict(boxstyle="round,pad=0.22", facecolor="white", alpha=0.85, linewidth=0),
        arrowprops=dict(arrowstyle="-", color=PALETTE["highlight"], lw=0.6, alpha=0.9)
    )

ax.set_title("Track Length vs. Total (USD)", color=PALETTE["text"])
ax.set_xlabel("Length (seconds)", color=PALETTE["text"])
ax.set_ylabel("Total (USD)", color=PALETTE["text"])
ax.grid(axis="both", linestyle="--", alpha=0.5)

ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v):,}"))

ax.text(
    0.02, 0.812,
    f"Pearson r = {pearson:.3f}\nRegression: y = {fit[0]:.4f}x + {fit[1]:.2f}",
    transform=ax.transAxes, ha="left", va="top",
    color=PALETTE["text"],
    bbox=dict(boxstyle="round,pad=0.25", facecolor="white", alpha=0.9, linewidth=0.5)
)

ax.legend(frameon=False, loc="upper left")

plt.tight_layout()
plt.savefig("length_vs_sales_correlation.png", dpi=220)
plt.show()