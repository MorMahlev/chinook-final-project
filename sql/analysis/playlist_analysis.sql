-- א. הפלייליסט עם הכי הרבה שירים
select playlist_key, 
       playlist_name, 
	   tracks_count
from dwh2.dim_playlist
order by tracks_count DESC, 
         playlist_name
limit 1
;

-- ב. הפלייליסט עם הכי מעט שירים
select playlist_key, 
	   playlist_name,
	   tracks_count
from dwh2.dim_playlist
order by tracks_count ASC, 
	     playlist_name
limit 1
;

-- ג. ממוצע שירים לפלייליסט
select avg (tracks_count)::numeric(10,2) as avg_tracks_per_playlist
from dwh2.dim_playlist
;

