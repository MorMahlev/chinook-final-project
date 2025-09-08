CREATE SCHEMA IF NOT EXISTS dwh2;

select nspname as schema_name
from pg_namespace
where nspname IN ('dwh2');
