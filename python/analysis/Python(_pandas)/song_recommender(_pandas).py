import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DB_URL")
if not DB_URL:
    raise ValueError("STOP! DB_URL not found!")
engine = create_engine(DB_URL)

df_il = pd.read_sql("select invoice_key as invoice_id, track_key from dwh2.fact_invoiceline", engine)
df_i = pd.read_sql("select invoice_key as invoice_id, customer_key as customer_id from dwh2.fact_invoice", engine)
df_t = pd.read_sql("select track_key, genre from dwh2.dim_track", engine)

cust_track = df_il.merge(df_i, on="invoice_id", how="inner")[["customer_id", "track_key"]]
cust_track = cust_track.merge(df_t, on="track_key", how="left")
cust_track = cust_track.dropna(subset=["genre"])

cust_genre = (cust_track
              .groupby(["customer_id", "genre"], as_index=False)
              .size()
              .rename(columns={"size": "cnt"}))

cust_genre = cust_genre.sort_values(["customer_id", "cnt", "genre"],
                                    ascending=[True, False, True])
cust_genre["rnk"] = (cust_genre
                     .groupby("customer_id")["cnt"]
                     .rank(method="dense", ascending=False))

top_genres = (cust_genre[cust_genre["rnk"] <= 2]
              .loc[:, ["customer_id", "genre"]]
              .rename(columns={"genre": "genre_name"})
              .sort_values(["customer_id", "genre_name"])
              .reset_index(drop=True))

purchased = cust_track[["customer_id", "track_key"]].drop_duplicates()
purchased_set = (purchased
                 .groupby("customer_id")["track_key"]
                 .apply(set)
                 .to_dict())

pop = (df_il.merge(df_t, on="track_key", how="left")
           .dropna(subset=["genre"]))
pop = (pop
       .groupby(["track_key", "genre"], as_index=False)
       .size()
       .rename(columns={"size": "purchases",
                        "track_key": "track_id",
                        "genre": "genre_name"}))

pop = pop.sort_values(["genre_name", "purchases"], ascending=[True, False])
pop_by_genre = (pop
                .groupby("genre_name")["track_id"]
                .apply(list)
                .to_dict())

recs = []
for cust, sub in top_genres.groupby("customer_id"):
    owned = purchased_set.get(cust, set())
    for genre in sub["genre_name"].tolist():
        candidates = [t for t in pop_by_genre.get(genre, []) if t not in owned]
        chosen = candidates[:3]
        recs.append({
            "customer_id": cust,
            "genre_name": genre,
            "recommended_track_ids": chosen
})

df_recs = pd.DataFrame(recs)

df_recs.to_csv("recommendations(_pandas).csv", index=False)
print("PREVIEW:")
print("\n", df_recs.head(10))
print("\nSAVED: recommendations.csv")