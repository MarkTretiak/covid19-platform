# COVID-19 Data Integration, Analysis, and Visualization Platform

A data platform combining Snowflake (structured COVID-19 data), MongoDB (annotations/comments), a FastAPI backend, and a Dash dashboard with forecasting and clustering.

## Architecture
Snowflake(COVID-19 Marketplace dataset + enriched data) --> FastAPI backend (query layer + in-memory cache) --> FastAPI backend (query layer + in-memory cache)

## Technologies

- **Snowflake** — structured data storage, SQL analytics, MATCH_RECOGNIZE pattern detection
- **Python** — FastAPI (API), Dash/Plotly (dashboard), Prophet (forecasting), scikit-learn (clustering)
- **MongoDB Atlas** — annotations and supplementary semi-structured data
- **ydata-profiling** — automated EDA

## Prerequisites

- Python 3.11+
- A Snowflake account (trial works) with the free "COVID-19 Epidemiological Data" Marketplace dataset added
- A MongoDB Atlas account (free M0 tier works)

## Setup

1. **Clone the repo and create a virtual environment:**
```bash
   git clone https://github.com/MarkTretiak/covid19-platform.git
   cd covid19-platform
   python3 -m venv venv
```
   Activate it:
   - For Windows(PowerShell): `venv\Scripts\Activate.ps1`
   - For Mac or Linux: `source venv/bin/activate`

2. **Install dependencies:**
```bash
   pip install -r requirements.txt
```

3. **Configure environment variables.** Copy `.env.example` to `.env` and fill in your real credentials:
```bash
   cp .env.example .env      # Windows: copy .env.example .env
```
   Required values: Snowflake user/password/account identifier, and your MongoDB Atlas connection string.

---

## Task 1 — Snowflake Setup & Resource Monitor

Run in: **Snowflake**

1. Create a Snowflake trial account (AWS, Stockholm region used here).
2. Add the dataset: **Data Products --> Marketplace** --> search "COVID-19 Epidemiological Data" --> **Get**. This mounts it as a read-only database, `COVID19_EPIDEMIOLOGICAL_DATA`.
3. Create your own working database (the Marketplace one is read-only):
   ```sql
   CREATE DATABASE IF NOT EXISTS COVID_PROJECT;
   ```
4. Run `sql/resource_monitor.sql` to create and attach the credit-usage monitor to your active warehouse.

Verify it worked:
```sql
SHOW WAREHOUSES;
```
Check that your active warehouse (`COMPUTE_WH`) has a `resource_monitor` value, not blank.

---

## Task 2 — Data Exploration & Enhancement

Run in **Snowflake**, then **terminal**

1. Explore the raw dataset - run `sql/exploration.sql` in Snowsight.
2. Run the enrichment pipeline (pivots the dataset, joins population data, writes `COVID_ENRICHED`, and generates the EDA report):
   ```bash
   python python/etl/enrich_dataset.py
   ```
3. View the automated EDA report - don't double-click the file, serve it locally instead:
   ```bash
   python -m http.server 8080
   ```
   Then open http://localhost:8080/docs/eda_report.html

Verify it worked in Snowflake, `SELECT COUNT(*) FROM COVID_PROJECT.PUBLIC.COVID_ENRICHED;` should return a non-zero row count, and `docs/eda_report.html` should exist locally.

---

## Task 3 — NoSQL Data Modeling (MongoDB)

Run in **terminal**

1. Create a free MongoDB Atlas cluster (M0 tier) and put its connection string in `.env` as `MONGO_URI`.
2. Seed a sample document:
   ```bash
   python mongo/seed.py
   ```

Verify it worked in Atlas's Data Explorer, check the `covid_platform.annotations` collection has at least one document. Schema design is documented in `mongo/schema.md`.

---

## Task 4 — API Development

Run in **terminal** (keep this running — the dashboard depends on it)

```bash
uvicorn python.api.main:app --port 8000
```

Verify it worked: open http://localhost:8000/docs and try each endpoint (`/metrics`, `/forecast`, `/annotations` GET and POST).

---

## Task 5 — Interactive Visualization

Run in a **second terminal**, with the API (Task 4) still running

```bash
python python/dashboard/app.py
```

Verify it worked: open http://localhost:8050 - pick a country from the dropdown and confirm all three charts load. Try the annotation box at the bottom (bonus feature) and confirm "Saved!" appears and the comment shows in the list below it.

---

## Task 6 — Analytical Features (Forecasting & Clustering)

Run in **terminal**

Forecasting is served live through the dashboard/API (Task 4/5) - no separate step needed. To run it standalone:
```bash
python python/analytics/forecasting.py
```

Clustering (bonus):
```bash
python python/analytics/clustering.py
```

Verify it worked: clustering prints a country/cluster table to the terminal and saves `docs/clusters.csv` and `docs/cluster_scatter.png`.

---

## Task 7 — Performance Optimization

Run in: **Snowflake**

Run `sql/performance.sql`. This adds a clustering key to `COVID_ENRICHED`, creates a view (`mv_country_daily` - a regular view, not materialized, since materialized views require Snowflake Enterprise edition), and shows warehouse/query timing info.

Verify it worked: `SHOW WAREHOUSES;` at the end of the script should run without error and show your active warehouse.

---

## Task 8 — API Caching

No separate run step - caching is built into the `/metrics` and `/forecast` endpoints from Task 4 (`python/api/cache.py`). To see it in action, call the same `/metrics` request twice in a row via http://localhost:8000/docs — the second call returns from the in-memory cache instead of re-querying Snowflake.

---

## Task 9 — Pattern Recognition (MATCH_RECOGNIZE)

Run in: **Snowflake**

Run `sql/match_recognize.sql`. Contains two queries: one on cumulative case totals, one on accelerating new-case bursts (the more meaningful of the two - see the report for interpretation).

---

## Task 10 — Source Code & Repository



---

## Project structure
covid19-platform/
├── sql/ --> Snowflake worksheets (resource monitor, exploration, performance, MATCH_RECOGNIZE)
├── mongo/ --> MongoDB schema design + seed script
├── python/
│ ├── etl/ --> Snowflake connection helper + enrichment pipeline
│ ├── api/ --> FastAPI backend + caching
│ ├── dashboard/ --> Dash frontend
│ └── analytics/ --> Forecasting + clustering
└── docs/ --> Generated EDA report, cluster output, final written report

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/metrics` | GET | Query enriched COVID metrics for a country/date range |
| `/forecast` | GET | 30-day case forecast for a country (Prophet) |
| `/annotations` | GET | Fetch saved annotations for a country |
| `/annotations` | POST | Save a new annotation to MongoDB |

## Author

Mark Tretiak