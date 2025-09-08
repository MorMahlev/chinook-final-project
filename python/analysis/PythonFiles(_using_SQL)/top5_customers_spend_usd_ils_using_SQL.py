HIGHLIGHT_THRESHOLD = 0.25
PALETTE = {
    "usd":     "#d9d9d9",   
    "ils":     "#b9b2a3",   
    "accent":  "#8c6b4f",   
    "grid":    "#eaeaea"    
}

plt.rcParams.update({
    "axes.facecolor": "white",
    "figure.facecolor": "white",
    "axes.edgecolor": "#aaaaaa",
    "grid.color": PALETTE["grid"],
    "axes.labelcolor": "#333333",
    "xtick.color": "#333333",
    "ytick.color": "#333333",
    "font.size": 10
})


engine = create_engine(DB_URL)

sql = """
with inv as (
 select
	invoice_key as invoice_id,
	customer_key as customer_id,
	invoice_date::date as invoice_date
 from dwh2.fact_invoice
),
sum_per_inv as (
 select 
 	il.invoice_key as invoice_id, 
 	sum(il.unitprice * il.quantity) as inv_total_usd
 from dwh2.fact_invoiceline il
 group by il.invoice_key
),
inv_with_rate as (
 select 
    i.customer_id,
    i.invoice_date,
    s.inv_total_usd,
	c.usd_ils_rate
 from inv i
 join sum_per_inv s on  s.invoice_id = i.invoice_id
 left join dwh2.dim_currency c on c.rate_date = i.invoice_date
)
 select customer_id,
    sum(inv_total_usd) as total_usd,
	sum(inv_total_usd * coalesce(usd_ils_rate, 3.5)) as total_ils
 from inv_with_rate
 group by customer_id
 order by total_usd DESC
 limit 5
;
"""

df = pd.read_sql(sql, engine)
df["customer_id"] = df["customer_id"].astype(str)

fig, ax = plt.subplots(figsize=(8, 5))
x = range(len(df))
bars_usd = ax.bar([i - 0.2 for i in x], df["total_usd"], width=0.4, label="USD", color=PALETTE["usd"])
bars_ils = ax.bar([i + 0.2 for i in x], df["total_ils"], width=0.4, label="ILS", color=PALETTE["ils"])

ax.set_xticks(list(x))
ax.set_xticklabels(df["customer_id"], rotation=0)
ax.set_title("Top-5 Customers by Spend (USD & ILS)")
ax.set_ylabel("Amount")
ax.grid(axis="y", linestyle="--", alpha=0.5)
ax.legend()

def label_bars(bars):
    for b in bars:
        val = b.get_height()
        ax.text(b.get_x() + b.get_width()/2, val, f"{val:,.0f}", ha="center", va="bottom", fontsize=9.5)

label_bars(bars_usd)
label_bars(bars_ils)

plt.tight_layout()
plt.savefig("top5_customers_spend_usd_ils_using_SQL.png", dpi=180)
plt.show()