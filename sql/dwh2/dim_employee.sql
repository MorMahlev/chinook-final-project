-- DROP TABLE IF EXISTS dwh2.dim_employee;

CREATE TABLE dwh2.dim_employee as
WITH mgr as (
select e.employeeid,
       INITCAP(e.firstname)||' '||INITCAP(e.lastname) as manager_name
from stg.employee e
)
select
  e.employeeid as employee_key,
  INITCAP(e.firstname) as first_name,
  INITCAP(e.lastname) as last_name,
  e.title,
  e.reportsto as manager_id,
  m.manager_name,
  e.hiredate,
  date_part('year', AGE(current_date, e.hiredate))::int as tenure_years,
  e.address, e.city, e.state, e.country, e.postalcode,
  e.phone, e.fax, lower (e.email) as email,
  e.departmentid,
  d.department_name,
  dbf.budget,
  CASE 
  WHEN EXISTS (
select 1 
from stg.employee x 
where x.reportsto = e.employeeid
 )
  THEN 1 
  ELSE 0 
  END as is_manager
from stg.employee e
left join mgr m on m.employeeid = e.reportsto
left join stg.department d on d.department_id = e.departmentid
left join stg.department_budget_full dbf on dbf.department_id = e.departmentid
;

--שאילתות לבדיקה
select count(*) as rows_loaded,
       sum(is_manager) as managers_count
from dwh2.dim_employee
;

select *
from dwh2.dim_employee
;