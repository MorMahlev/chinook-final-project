# Chinook Data Warehouse & Analytics Project

This project was built as part of my Data Analyst training.  
It demonstrates how to design a data warehouse (DWH), implement ETL processes, and perform advanced analytics with SQL and Python.

## Data Model

The Chinook database was transformed into a **star-schema** (`dwh2`) design:

- **Dimensions:** customer, employee, track, playlist, currency, etc.  
- **Facts:** invoices and invoice lines.

This structure enables efficient analytical queries across multiple business questions.

![Star Schema](images/star_schema.png)

## ETL Process

A full ETL (Extract, Transform, Load) pipeline was implemented:

- **Extract:** Pull raw data from the Chinook database and an external currency API.  
- **Transform:** Clean and standardize the data, convert currency values, and apply business rules.  
- **Load:** Save the processed data into the `dwh2` schema (dimension & fact tables).

This ensures reliable, clean, and business-ready data for analysis.

## Analytical Results

Examples of visual outputs (Pandas implementation):

1. **Monthly Sales Trend**  
   Identify seasonality and growth patterns.  
   ![Monthly Sales Trend](images/PythonAnalyses (pandas)/monthly_sales_trend_bars.png)

2. **Top 5 Customers (USD vs. ILS)**  
   Compare spending in USD and converted ILS.  
   ![Top 5 Customers](images/PythonAnalyses (pandas)/top5_customers_spend_usd_ils.png)

3. **Seasonality by Genre**  
   Examine seasonality across top genres.  

   ![Seasonality by Genre](images/PythonAnalyses (pandas)/seasonality_by_genre.png)

> Each analysis was implemented twice — using direct SQL (via SQLAlchemy) and using Pandas.  
> The visualizations shown above are from the Pandas version; SQL outputs are also included.

[Full Project Report (PDF)](docs/Answer_File_chinook.pdf)

## Project Structure

- **`sql/`** – DDL and analysis queries.  
  - `dwh2/` – schema & tables (dimensions/facts)  
  - `analysis/` – analytical SQL queries
- **`python/`** – ETL & analysis scripts.  
  - `etl/` – extraction/transform/load scripts  
  - `analysis/` – analysis & plotting (SQL + Pandas)
- **`data/`** – processed outputs only (raw files are excluded by `.gitignore`).  
- **`images/`** – charts and diagrams (used in this README).  
- **`docs/`** – documentation (e.g., project PDF).  
- **`requirements.txt`** – Python dependencies.  
- **`.env.example`** – sample environment variables (no secrets).

## How to Run

### 1) Create & activate a virtual environment (optional)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Configure environment variables
Create a file named `.env` in the project root (use `.env.example` as a reference).  

Add your database connection string:
```
DB_URL=postgresql://<user>:<password>@localhost:5432/chinook
```

### 4) Create schema & tables
Run the SQL scripts under `sql/dwh2/` (order: create_schema.sql, dimensions, then facts).

### 5) Run ETL
Use the scripts in `python/etl/` to extract, transform, and load data into `dwh2`.  
The optional script (`python/etl/currency_api_loader.py`) fetches daily USD→ILS rates:

- Date range inferred from invoices (e.g., stg.invoice / dwh2.fact_invoice)  
- Output table: `stg.usd_ils_rates`  
- Supports a **dry-run** mode for safe validation

### 6) Run analyses
- SQL queries: `sql/analysis/`  
- Python analyses: `python/analysis/`  
- Plots are saved under `images/` and `data/outputs/`.

Author: Mor Mahlev
