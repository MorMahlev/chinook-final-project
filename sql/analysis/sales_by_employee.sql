with employees_dtls_per_year as (
  select
    e.employee_key,
    e.first_name|| ' ' ||e.last_name as employee_name,
    extract(year from f.invoice_date)::int as year_,
    count(distinct f.customer_key) as customers_served,
    coalesce(sum(f.total_usd), 0) as sales_usd
 from dwh2.dim_employee e
 join dwh2.dim_customer c on c.support_rep_id = e.employee_key
 join dwh2.fact_invoice f on f.customer_key = c.customer_key
 group by e.employee_key,
 		  employee_name,
		  extract(year from f.invoice_date)
),
tenure as (
 select
	employee_key,
	date_part('year', age(current_date, hiredate))::int as tenure_years
 from dwh2.dim_employee
),
percent_growth_compared_prev_year as (
 select
    edpy.*,
    t.tenure_years,
    lag(edpy.sales_usd) over(partition by edpy.employee_key order by edpy.year_) as prev_year_sales
 from employees_dtls_per_year edpy
 left join tenure t on edpy.employee_key = t.employee_key
)
select
  employee_key,
  employee_name,
  year_,
  tenure_years,
  customers_served,
  sales_usd,
  CASE
  WHEN prev_year_sales IS NULL OR prev_year_sales = 0 
  THEN NULL
  ELSE round(100.0 * (sales_usd - prev_year_sales) / prev_year_sales, 2)
  END as sales_growth_percent
from percent_growth_compared_prev_year
order by employee_name,
		 year_
;