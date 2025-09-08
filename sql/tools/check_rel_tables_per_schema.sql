-- מה יש לי כבר? סקירה מהירה של טבלאות רלוונטיות
WITH tables AS (
  SELECT table_schema, table_name
  FROM information_schema.tables
  WHERE table_type = 'BASE TABLE'
    AND table_schema IN ('stg','dwh','public')
),
marks AS (
  SELECT
    t.table_schema,
    t.table_name,
    CASE
      WHEN t.table_name ILIKE 'dim_%' THEN 'DIM'
      WHEN t.table_name ILIKE 'fact_%' THEN 'FACT'
      WHEN t.table_schema = 'stg' AND t.table_name ILIKE '%rate%' THEN 'RATES'
      WHEN t.table_schema = 'stg' AND t.table_name IN ('invoice','invoiceline','track','customer','employee','playlist','playlisttrack') THEN 'STG_BASE'
      ELSE ''
    END AS kind
  FROM tables t
)
SELECT
  m.table_schema AS schema,
  m.table_name   AS table,
  m.kind         AS tag,
  obj_description((quote_ident(m.table_schema)||'.'||quote_ident(m.table_name))::regclass) AS comment
FROM marks m
ORDER BY
  CASE m.table_schema WHEN 'dwh' THEN 1 WHEN 'stg' THEN 2 ELSE 3 END,
  m.kind DESC,
  m.table_name;
