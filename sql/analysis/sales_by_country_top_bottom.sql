with country_totals as (
 select
   	f.billing_country as country,
	sum(l.unitprice * l.quantity) as amount_usd
 from dwh2.fact_invoice f
 join dwh2.fact_invoiceline l on l.invoice_key = f.invoice_key
 group by f.billing_country
),
ranked as (
 select
	country,
   	amount_usd,
   	dense_rank() over(order by amount_usd DESC) as r_top,
   	dense_rank() over(order by amount_usd ASC) as r_bottom
 from country_totals
),
selected_countries as (
 select 
	country, 
	amount_usd
 from ranked
 where r_top <= 5 OR r_bottom <= 5
),
country_genre as (
 select
	f.billing_country as country,
	t.genre as genre,
    sum(l.unitprice * l.quantity) as amount_usd
 from dwh2.fact_invoice f
 join dwh2.fact_invoiceline l on l.invoice_key = f.invoice_key
 join dwh2.dim_track t on t.track_key = l.track_key
 where f.billing_country in (
 	select country 
	from selected_countries
)
 group by f.billing_country,
 		  t.genre
),
country_sums as (
 select
	country, 
	sum(amount_usd) as sum_in_country
 from country_genre
 group by country
)
 select 'A) TOP/BOTTOM 5 countries by total' as section,
		*
 from selected_countries
 order by amount_usd DESC
;