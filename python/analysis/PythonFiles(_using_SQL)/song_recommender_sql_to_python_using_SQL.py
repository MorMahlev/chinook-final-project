engine = create_engine(DB_URL)

sql_top_genres = """
with cust_track as (
 select fi.customer_key,
 		il.track_key 
 from dwh2.fact_invoiceline il
  join dwh2.fact_invoice fi on il.invoice_key = fi.invoice_key
),
cust_genre as (
 select c.customer_key,
		dt.genre,
		count(*) as cnt
 from cust_track c
 join dwh2.dim_track dt on c.track_key = dt.track_key 
 where dt.genre IS NOT NULL
 group by c.customer_key,
 		  dt.genre
),
ranked as (
 select 
	customer_key, 
	genre, 
	cnt,
    dense_rank() over(partition by customer_key order by cnt DESC, genre) as rnk
 from cust_genre
)
 select
	customer_key as customer_id,
	genre as genre_name
 from ranked
 where rnk <= 2
 order by customer_key,
 		  rnk, 
		  genre
;
"""
# שלב 2: כל השירים שהלקוח כבר רכש
sql_purchased = """
select
	fi.customer_key as customer_id, 
	il.track_key as track_id
from dwh2.fact_invoiceline il
join dwh2.fact_invoice fi on il.invoice_key = fi.invoice_key
;
"""
# שלב 3: פופולריות כללית של שירים לפי ז'אנר 
sql_popularity = """
with pop as (
 select dt.track_key,
 		dt.genre, 
		count(*) as purchases
 from dwh2.fact_invoiceline il
 join dwh2.dim_track dt on il.track_key = dt.track_key
 where dt.genre IS NOT NULL
 group by dt.track_key, 
 		  dt.genre
)
 select 
	tracK_key as track_id,
	genre as genre_name, 
	purchases
 from pop
;
"""

top_genres = pd.read_sql(sql_top_genres, engine)
purchased = pd.read_sql(sql_purchased, engine)
pop = pd.read_sql(sql_popularity, engine)

purchased_set = (
    purchased.groupby("customer_id")["track_id"]
    .apply(set)
    .to_dict()
)

pop_by_genre = (
    pop.sort_values(["genre_name", "purchases"], ascending=[True, False])
        .groupby("genre_name")["track_id"]
        .apply(list)
        .to_dict()
)

recs = []
for cust, sub in top_genres.groupby("customer_id"):
    owned = purchased_set.get(cust, set())
    for genre in sub["genre_name"].tolist():
        candidates = [t for t in pop_by_genre.get(genre, []) if t not in owned]
        chosen = candidates[:3] 
        recs.append({"customer_id ": cust, " genre_name ": genre, " recommended_track_ids": chosen})

df_recs = pd.DataFrame(recs)

df_recs.to_csv("recommendations_(using_SQL).csv", index=False)
print("PREVIEW:")
print("\n", df_recs.head(10))
print("\nSAVED: recommendations_(using_SQL).csv")