# 🏢 Olist E-Commerce Business Intelligence Platform

An end-to-end **AI-powered Business Intelligence solution** built on the Brazilian Olist E-Commerce dataset. The platform features a PostgreSQL Star Schema data warehouse, automated Python ETL pipeline, MCP/AI integration, and three interactive Apache Superset dashboards.

---

## 📊 Key Business Metrics

| Metric | Value |
|--------|-------|
| 💰 Total Revenue | **$20.3M** |
| 📦 Total Orders | **98,700+** |
| 👥 Total Customers | **98,700+** |
| ⭐ Average Review Score | **4.03 / 5** |
| 💵 Average Order Value | **$137.75** |
| 🚚 Average Freight Cost | **$19.99** |

---

## 🖼️ Dashboards

### Dashboard 1 — Executive Sales Overview
![Executive Sales Overview](screenshots/dashboard%201.png)

Key charts: Revenue by Month · Top 10 Sellers by Revenue · Top 10 Product Categories · Orders by Review Score · Orders by Payment Type

---

### Dashboard 2 — Operational Deep-Dive
![Operational Deep-Dive](screenshots/dashboard%202.png)

Key charts: Orders by Payment Type · Orders by Review Score · Top Sellers by Revenue · Top Categories by Revenue · Average Order Value by Review Score · Average Freight Cost by Installments

---

### Dashboard 3 — Trend & Revenue Monitor
![Trend & Revenue Monitor](screenshots/dashboard%20NO%20.3.png)

Key charts: Revenue by Month (trend line) · Revenue by Payment Type · Top 10 Product Categories · Top 10 Sellers · Average Order Value by Review Score

---

## 🏗️ Architecture

```
CSV Datasets (Olist)
        ↓
  Python ETL (etl_load.py)
        ↓
PostgreSQL Star Schema (Supabase)
        ↓
Apache Superset Dashboards
        ↑
   Gemini CLI + MCP
(AI-assisted development & natural language querying)
```

---

## 🗄️ Star Schema Design

**Fact Table:**
- `fact_order_items` — transactional measures (revenue, freight, quantity)

**Dimension Tables:**
- `dim_customers` — customer demographics and location
- `dim_sellers` — seller information
- `dim_products` — product categories and attributes
- `dim_orders_context` — order timing and status context

---

## 📁 Project Structure

```
├── etl_load.py                  # Main ETL script
├── golden_queries.sql           # SQL evaluation test suite
├── schema_database.png          # Star Schema diagram
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── .gemini/settings.json        # Gemini CLI MCP configuration
├── screenshots/                 # Dashboard screenshots
│   ├── dashboard 1.png
│   ├── dashboard 2.png
│   └── dashboard NO.3.png
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Database Connection

Create a `.env` file based on `.env.example`:

```env
POSTGRES_HOST=your_host
POSTGRES_PORT=5432
POSTGRES_DATABASE=your_database
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
```

### 3. Run ETL Pipeline

```bash
python etl_load.py
```

The ETL process:
- Loads 9 CSV datasets (100,000+ records)
- Cleans missing values and removes duplicates
- Creates surrogate keys
- Loads dimension tables before the fact table
- Supports **idempotent loading** (safe to run multiple times)

---

## 🤖 AI Integration (MCP)

This project demonstrates **AI-assisted BI development** using:
- **Gemini CLI** — for natural language querying over the data warehouse
- **PostgreSQL MCP Server** — connecting AI to the live database
- **Apache Superset MCP Server** — AI-assisted dashboard generation
- **Golden Queries** — SQL evaluation suite for validating AI-generated queries

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Data Warehouse | PostgreSQL (Supabase) |
| Schema | Star Schema |
| ETL | Python (pandas, psycopg2) |
| Dashboards | Apache Superset |
| AI Integration | Gemini CLI + MCP |
| Data Source | Olist Brazilian E-Commerce Dataset |

---

## 📈 Future Improvements

- Real-time incremental ETL loading
- Predictive analytics using machine learning
- Automated dashboard generation via AI agents
- Natural language querying through public MCP endpoint
- Time-series forecasting for revenue trends

---

## 👤 Author

**Eman Hrustemović**
- 🔗 [GitHub](https://github.com/EmanHrustemovic)
- 🔗 [LinkedIn](https://linkedin.com/in/eman-hrustemovic)
- 📄 [ML Capstone Paper](https://emanhrustemovic.github.io/ml-capstone-paper)
