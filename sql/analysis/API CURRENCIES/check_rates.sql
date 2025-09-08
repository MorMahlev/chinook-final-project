--בדיקה 1:
select i.invoicedate::date as d
from stg.invoice i
left join stg.usd_ils_rates r on r.rate_date = i.invoicedate::date
where r.rate_date IS NULL
group by 1
order by 1
;  

--בדיקה 2:
select *
from stg.usd_ils_rates
where usd_ils_rate IS NULL OR usd_ils_rate <= 0
;

--בדיקה 3:
select count(*) as rows_loaded,
       min(rate_date) as min_date,
       max(rate_date) as max_date
from stg.usd_ils_rates
;
