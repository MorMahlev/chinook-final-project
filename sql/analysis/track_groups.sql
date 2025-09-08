with track_units as (
 select
	t.track_key,
    coalesce(sum(l.quantity),0) as units_sold
 from dwh2.dim_track t
 left join dwh2.fact_invoiceline l on l.track_key = t.track_key
 group by t.track_key
),
bucketed as (
 select
	CASE
    WHEN units_sold = 0 THEN '0'
    WHEN units_sold between 1 and 5 THEN '1-5'
    WHEN units_sold between 6 and 10 THEN '5-10'
    ELSE '10+'
    END as sales_bucket
 from track_units
)
 select
 	CASE 
	WHEN sales_bucket ='10+' THEN 'A'
	WHEN sales_bucket ='5-10' THEN 'B'
	WHEN sales_bucket = '1-5' THEN 'C'
	ELSE 'D'
	END as rank_by_sales,
 	sales_bucket,
	count(*) as tracks_count
 from bucketed
 group by  sales_bucket
 order by 
	CASE sales_bucket
  	WHEN '10+' THEN 1
  	WHEN '5-10' THEN 2
  	WHEN '1-5' THEN 3
  	ELSE 4
  	END
;
