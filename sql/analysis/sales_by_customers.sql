with cust_details as (
 select
	c.customer_key,
    c.country,
    count(distinct f.invoice_key) as orders_count,
    coalesce(sum(f.total_usd), 0) as revenue_usd
 from dwh2.dim_customer c
 left join dwh2.fact_invoice f on f.customer_key = c.customer_key
 group by c.customer_key,
		  c.country
),
customer_counts_per_country as (
 select country,
 		count(*) as total_customers
 from cust_details
 group by country
),
label_others as (
 select
    cd.customer_key,
    CASE 
	WHEN ccpc.total_customers = 1 THEN 'Other' 
	ELSE cd.country 
	END as country_group,
    cd.orders_count,
    cd.revenue_usd
 from cust_details cd
 join customer_counts_per_country ccpc on ccpc.country = cd.country
)
select
  country_group as country,
  count(*) as totat_customers,
  round(avg(orders_count)::numeric, 2) as avg_orders_per_customer,
  round(avg(revenue_usd)::numeric, 2) as avg_revenue_per_customer_usd
from label_others
group by country_group
order by
  CASE
  WHEN country_group = 'Other' THEN 2 
  ELSE 1 
  END,
  country_group
;
