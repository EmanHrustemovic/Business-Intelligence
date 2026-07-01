# Olist Business Intelligence Platform


This project implements a Star Schema data warehouse using PostgreSQL (Supabase) and a Python-based ETL process for the **Olist Brazilian E-Commerce Dataset**. The project also includes interactive business intelligence dashboards developed in Apache Superset.

---

# Project Structure

```
etl_load.py                     Main ETL script
requirements.txt                Python dependencies
README.md                       Project documentation
.gitignore
.env.example
.gemini/settings.json           Gemini CLI MCP configuration

olist_customers_dataset.csv
olist_geolocation_dataset.csv
olist_order_items_dataset.csv
olist_order_payments_dataset.csv
olist_order_reviews_dataset.csv
olist_orders_dataset.csv
olist_products_dataset.csv
olist_sellers_dataset.csv
product_category_name_translation.csv

schema_database.png   Star Schema 
golden_queries.sql            Evaluation SQL test suite
```

---

# Star Schema Design

The data warehouse follows a Star Schema optimized for analytical reporting.

### Dimension Tables

* dim_customers
* dim_sellers
* dim_products
* dim_orders_context

### Fact Table

* fact_order_items

The ETL process integrates multiple Olist datasets into a single analytical Star Schema. Payment information, review scores and translated product categories are merged into the fact table during loading to simplify analytical queries.
The schema follows a classic star schema where fact_order_items stores transactional measures while the dimension tables provide descriptive business context.

---

# Prerequisites

* Python 3.10+
* PostgreSQL (Supabase)
* Apache Superset
* Virtual Environment (recommended)

---

# Setup Instructions

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Database Connection

Create a `.env` file or configure the PostgreSQL connection inside Gemini CLI.

Example:

```text
POSTGRES_HOST=your_host
POSTGRES_PORT=5432
POSTGRES_DATABASE=your_database
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
```

---

## Run ETL

```bash
python etl_load.py
```

The ETL process:

* Loads CSV files
* Cleans missing values
* Removes duplicates
* Creates surrogate keys
* Loads dimension tables
* Loads the fact table

The script can be executed multiple times safely thanks to idempotent loading.

---

# Dashboards

The project contains three Apache Superset dashboards.

### Dashboard 1

Executive Sales Overview

Contains:

* Revenue by Month
* Orders by Month
* Revenue by Product Category
* Revenue by Seller
* Revenue by State
* Average Review Score

---

### Dashboard 2

Operational Deep-Dive

Contains:

* Orders by Payment Type
* Orders by Review Score
* Top Sellers by Revenue
* Top Categories by Revenue
* Average Order Value by Review Score
* Average Freight Cost by Installments

---

### Dashboard 3

Trend & Revenue Monitor

Contains:

* Total Revenue KPI
* Total Orders KPI
* Average Review Score KPI
* Revenue by Month
* Revenue by Payment Type
* Top Categories
* Top Sellers
* Average Order Value by Review Score

---

# Built with Gemini CLI

This project was developed using **Gemini CLI** together with:

* PostgreSQL MCP Server
* Apache Superset MCP Server
* Supabase PostgreSQL

---

# Example Development Prompts

The project was developed using prompts similar to the following:

## 1. Data Warehouse Design

* Design a Star Schema for the Olist dataset.
* Create PostgreSQL dimension and fact tables.
* Generate SQL DDL scripts.

## 2. ETL Development

* Generate a Python ETL script using pandas and psycopg2.
* Handle NULL values.
* Perform data cleaning.
* Remove duplicate records.
* Translate Portuguese product categories
* Load dimensions before the fact table.
* Implement idempotent loading.


## 3. Dashboard Development

* Connect Apache Superset to PostgreSQL.
* Design Executive Dashboard.
* Design Operational Dashboard.
* Design Trend Dashboard.
* Generate SQL queries for all charts.
* Create KPIs and business metrics. 

## 4. SQL Analytics

* Generate SQL queries for KPI calculation.
* Create reusable datasets for Superset.
* Optimize analytical SQL queries.

---

# Key Features

* Star Schema Data Warehouse
* Automated ETL Pipeline
* PostgreSQL (Supabase)
* Apache Superset Dashboards
* Idempotent Data Loading
* Data Cleaning
* Business KPI Reporting
* SQL-based Analytics
* Business Metrics & KPI Tracking
* AI-assisted BI Development using Gemini CLI
* AI Agent Evaluation using Golden Queries


# PostgreSQL MCP Configuration

Gemini CLI communicates with the PostgreSQL database using environment variables stored in the local .env file.

POSTGRES_HOST=...
POSTGRES_PORT=5432
POSTGRES_DATABASE=...
POSTGRES_USER=...
POSTGRES_PASSWORD=...


# Future Improvements

Possible future improvements include:

- AI-powered natural language querying through the MCP Agent
- Automated dashboard generation
- Incremental ETL loading
- Predictive analytics using machine learning
- Real-time business monitoring