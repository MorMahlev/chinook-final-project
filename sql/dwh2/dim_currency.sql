CREATE TABLE IF NOT EXISTS dwh2.dim_currency as
select
  rate_date,
  usd_ils_rate,
  source,
  loaded_at
from stg.usd_ils_rates;

--API -בדיקת נתונים בהשוואה לנתונים שקיבלנו בשלבי ה
select count(*) as rows_loaded,
       min(rate_date) as min_date,
       max(rate_date) as max_date
from dwh2.dim_currency;
