DROP TABLE IF EXISTS dwh2.dim_playlist;

CREATE TABLE dwh2.dim_playlist as
select
  p.playlistid as playlist_key,
  p.name as playlist_name,
  count(pt.trackid) as tracks_count
from stg.playlist p
inner join stg.playlisttrack pt on pt.playlistid = p.playlistid
group by p.playlistid, p.name
;

--בדיקות
select *
from dwh2.dim_playlist
;

select count(*) as loaded_rows
from dwh2.dim_playlist
;