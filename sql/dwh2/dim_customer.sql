-- DROP TABLE IF EXISTS dwh2.dim_customer;

CREATE TABLE dwh2.dim_customer as
select
  c.customerid as customer_key,
  INITCAP(c.firstname) as first_name,
  INITCAP(c.lastname) as last_name,
  lower(c.email) as email,
  split_part(lower(c.email),'@',2) as email_domain,
  c.company,
  c.address,
  c.city,
  c.state,
  c.country,
  c.postalcode,
  c.supportrepid as support_rep_id
from stg.customer c
;

--הרצה לצורך בדיקת נתונים
-- select count(*) as rows_loaded 
-- from dwh2.dim_customer
-- ;
