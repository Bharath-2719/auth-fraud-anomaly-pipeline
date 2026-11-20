# auth-fraud-anomaly-pipeline
# High-Volume Authentication & Fraud Anomaly Detection Pipeline

An end-to-end Data Engineering and Anomaly Detection pipeline built using **Python, SQL (SQLite), and Scikit-Learn**. Designed to simulate large-scale digital identity and transaction authentication logs, detect impossible-travel patterns via SQL window functions, and flag behavioral anomalies using unsupervised machine learning.

## System Architecture
`Raw CSV Logs` ➔ `Pandas ETL & Schema Standardization` ➔ `Indexed Relational DB (SQLite)` ➔ `SQL Window Function Rules (LAG, DENSE_RANK)` ➔ `Isolation Forest ML Scoring` ➔ `Exported Fraud Alerts & Visuals`

## Repository Structure
* **`01_data_ingestion.py`** — Fetches the raw authentication/transaction dataset via `kagglehub` and validates the schema.
* **`02_etl_and_sql_indexing.py`** — Standardizes column names, loads records into a relational SQLite database, and builds composite indexes (`idx_user_time`, `idx_auth_device`) to optimize query latency.
* **`03_sql_anomaly_queries.sql`** — Production SQL queries using window functions (`LAG()`, `DENSE_RANK()`) and CTEs to detect impossible travel, velocity bursts, and high-risk user accounts.
* **`04_isolation_forest_and_visuals.py`** — Trains an unsupervised **Isolation Forest** model on scaled behavioral features, exports flagged anomalies (`uidai_style_fraud_alerts.csv`), and generates visual analytics.

## Key Technical Highlights
* **Optimized Relational Storage:** Indexed 50,000+ authentication events across user IDs, timestamps, and device types for fast analytical querying.
* **Rule-Based SQL Fraud Detection:**
  * **Impossible Travel Detection:** Uses `LAG()` to flag consecutive logins across distant locations combined with repeated failed attempts.
  * **High-Risk Account Prioritization:** Uses `DENSE_RANK()` to rank users by cumulative risk score and 7-day failure spikes.
  * **Authentication & Temporal Profiling:** Evaluates fraud rates across authentication methods (Biometric, OTP, PIN, Password) and Weekday vs. Weekend traffic.
* **Unsupervised ML Anomaly Engine:** Applies **Isolation Forest** (`contamination=0.05`) on standardized behavioral metrics (`transaction_distance`, `failed_transaction_count_7d`, `risk_score`, `transaction_amount`) to flag hidden anomalies without relying on pre-labeled fraud tags.

## Tech Stack
* **Languages:** Python 3, SQL
* **Libraries:** Pandas, NumPy, SQLite3, Scikit-Learn, Matplotlib, Seaborn, KaggleHub

## Visual Outputs
![Fraud Analysis Charts](fraud_analysis_charts.png)

## How to Run
1. Run `01_data_ingestion.py` and `02_etl_and_sql_indexing.py` to build the indexed SQL database.
2. Execute `03_sql_anomaly_queries.sql` against the database to extract rule-based fraud summaries.
3. Run `04_isolation_forest_and_visuals.py` to generate ML anomaly predictions and visual charts.
