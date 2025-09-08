select 
min(invoicedate)::date as start_date,
max(invoicedate)::date as end_date
from stg.invoice
;