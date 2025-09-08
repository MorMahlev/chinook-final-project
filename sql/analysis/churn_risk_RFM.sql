with base as (
 select
	c.customer_key,
 	c.first_name || ' ' || c.last_name as customer_name,
    count(i.invoice_key) as num_invoices,      
    sum(i.total_usd) as total_spent,      
    max(i.invoice_date) as last_purchase,   
    (current_date - max(i.invoice_date))::int as days_since_last
 from dwh2.fact_invoice i
 join dwh2.dim_customer c on c.customer_key = i.customer_key
 group by c.customer_key, customer_name
),
rfm_rank as (
 select
	b.*,
    ntile(5) over ( order by days_since_last ASC) as r_tile_asc, 
    ntile(5) over (order by num_invoices DESC) as f_tile,
    ntile(5) over (order by total_spent DESC) as m_tile
 from base b
),
scored as (
 select
    customer_key,
    customer_name,
    num_invoices,
    total_spent,
    last_purchase,
    days_since_last,
    (6 - r_tile_asc) as r_tile,
    f_tile,
    m_tile
 from rfm_rank
)
 select
  customer_key as customer_id,
  customer_name,
  num_invoices,
  total_spent,
  last_purchase,
  days_since_last,
  r_tile, 
  f_tile, 
  m_tile,
  CASE
    WHEN r_tile <= 2 AND (f_tile <= 2 OR m_tile <= 2) THEN 'High Risk'
    WHEN r_tile = 3 OR (f_tile between 2 and 3) OR (m_tile between 2 and 3) THEN 'Medium Risk'
    ELSE 'Loyal'
  	END as  churn_flag
from scored
order by churn_flag DESC, 
	 	 days_since_last DESC
;
