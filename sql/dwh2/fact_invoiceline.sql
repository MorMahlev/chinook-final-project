-- DROP TABLE IF EXISTS dwh2.fact_invoiceline;

CREATE TABLE dwh2.fact_invoiceline as
select
  il.invoicelineid as invoiceline_key,
  il.invoiceid  as invoice_key,
  il.trackid as track_key,
  il.unitprice,
  il.quantity,
  (il.unitprice * il.quantity)::numeric(18,4) as line_total
from stg.invoiceline il
;

--בדיקה
select count(*) as loaded_rows,
       sum(line_total) as sum_lines
from dwh2.fact_invoiceline
;
