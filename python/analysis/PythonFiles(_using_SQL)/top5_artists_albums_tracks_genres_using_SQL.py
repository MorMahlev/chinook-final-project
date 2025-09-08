import pandas as pd
import matplotlib.pyplot as plt
import psycopg2
from sqlalchemy import create_engine
from getpass import getpass

user = "postgres"
password = getpass("Enter DB password: ")
host = "localhost"
port = "5432"
database = "chinook"

HIGHLIGHT_THRESHOLD = 0.25  
PALETTE = {
    "base": ["#d8d2c4", "#c9c3b6", "#b9b2a3", "#a89f8d", "#978c77"],  
    "accent": "#6f6a62", 
}
plt.rcParams.update({
    "axes.facecolor": "white",
    "figure.facecolor": "white",
    "axes.edgecolor": "#888888",
    "grid.color": "#e6e6e6",
    "axes.titleweight": "bold",
    "axes.titlepad": 12,
})

engine = create_engine(DB_URL)

sql_top5_artists_albums = """
with x as (
 select 
     artist_name, 
     count(distinct album_title) as albums_cnt
 from dwh2.dim_track
 where artist_name IS NOT NULL AND album_title IS NOT NULL
 group by artist_name
)
select 
    artist_name,
    albums_cnt
from x
order by albums_cnt DESC,
         artist_name
limit 5
;
"""

sql_top5_artists_tracks = """
with x as (
 select 
    artist_name, 
    count(*) as tracks_cnt
 from dwh2.dim_track
 where artist_name IS NOT NULL
 group by artist_name
)
 select 
    artist_name, 
    tracks_cnt
 from x
 order by tracks_cnt DESC, 
          artist_name
limit 5
;
"""

sql_top5_genres_tracks = """
with  x as (
 select
    genre as genre_name, 
    count(*) as tracks_cnt
 from dwh2.dim_track
 where genre IS NOT NULL
 group by genre
)
 select
   genre_name,
   tracks_cnt
 from x
 order by tracks_cnt DESC,
          genre_name
limit
5
;
"""

df_albums = pd.read_sql(sql_top5_artists_albums, engine)
df_tracks = pd.read_sql(sql_top5_artists_tracks, engine)
df_genres = pd.read_sql(sql_top5_genres_tracks, engine)

def bar_with_highlights(ax, categories, values, title):
    avg = values.mean()
    colors = []
    base = PALETTE["base"]
    for i, v in enumerate(values):
        if v >= avg * (1 + HIGHLIGHT_THRESHOLD):
            colors.append(PALETTE["accent"])
        else:
            colors.append(base[i % len(base)])
    bars = ax.bar(categories, values, color=colors)
    ax.set_title(title)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    ax.set_ylabel("Count")
    ax.set_xticklabels(categories, rotation=20, ha='right')
    
    for b in bars:
        ax.text(b.get_x() + b.get_width()/2, b.get_height(),
                f'{int(b.get_height())}', ha='center', va='bottom', fontsize=9)

fig, axes = plt.subplots(1, 3, figsize=(16, 5))

bar_with_highlights(axes[0], df_albums["artist_name"], df_albums["albums_cnt"],
                    "Top-5 Artists by #Albums")
bar_with_highlights(axes[1], df_tracks["artist_name"], df_tracks["tracks_cnt"],
                    "Top-5 Artists by #Tracks")
bar_with_highlights(axes[2], df_genres["genre_name"], df_genres["tracks_cnt"],
                    "Top-5 Genres by #Tracks")

plt.tight_layout()
plt.savefig("top5_artists_alboms_tracks_genres_using_SQL.png", dpi=180)
plt.show()
