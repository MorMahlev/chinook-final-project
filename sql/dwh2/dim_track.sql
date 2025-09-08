-- DROP TABLE IF EXISTS dwh2.dim_track;

CREATE TABLE dwh2.dim_track as
with base as (
select
  t.trackid as track_key,
  t.name as track_name,
  t.albumid, 
  t.mediatypeid, 
  t.genreid,
  t.composer, 
  t.milliseconds, 
  t.bytes, 
  t.unitprice
from stg.track t
)
select
  b.track_key, 
  b.track_name,
  a.title as album_title, 
  ar.name as artist_name, 
  mt.name as media_type, 
  g.name  as genre,
  b.composer, 
  b.milliseconds,
  round(b.milliseconds::numeric/1000, 5) as duration_seconds,
  to_char((b.milliseconds/1000)::int*interval'1 second', 'MI:SS') as duration_mmss,
  b.bytes, b.unitprice
from base b
left join stg.album a on a.albumid = b.albumid
left join stg.artist ar on ar.artistid = a.artistid
left join stg.mediatype mt on mt.mediatypeid = b.mediatypeid
left join stg.genre g on g.genreid = b.genreid
;


