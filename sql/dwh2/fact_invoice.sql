-- DROP TABLE IF EXISTS dwh2.fact_invoice;

CREATE TABLE dwh2.fact_invoice as
select
  i.invoiceid as invoice_key,
  i.customerid as customer_key,
  i.invoiceDate::date as invoice_date,
  i.billingcountry as billing_country,
  i.total as total_usd
from stg.invoice i
;

--בדיקה
select count(*) as loaded_rows,
        min(invoice_date) as min_date,
		max(invoice_date) as max_date
from dwh2.fact_invoice
;

