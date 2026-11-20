from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# 1. Extract features from SQL
ml_query = """
SELECT 
    transaction_id, user_id, authentication_method, device_type, location,
    transaction_amount, failed_transaction_count_7d, 
    card_age, transaction_distance, risk_score, fraud_label
FROM auth_transactions
"""
ml_df = pd.read_sql_query(ml_query, conn)

features = [
    "transaction_amount",
    "failed_transaction_count_7d",
    "card_age",
    "transaction_distance",
    "risk_score",
]
X = ml_df[features].fillna(0)

# 2. Scale features & fit Isolation Forest
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

iso_forest = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
ml_df["anomaly_flag"] = iso_forest.fit_predict(X_scaled)
ml_df["predicted_anomaly"] = ml_df["anomaly_flag"].apply(
    lambda x: 1 if x == -1 else 0
)

# 3. Filter top anomalies & save to CSV
flagged_alerts = ml_df[ml_df["predicted_anomaly"] == 1]
flagged_alerts.to_csv("uidai_style_fraud_alerts.csv", index=False)

print(f"Total Records Processed: {len(ml_df):,}")
print(f"Total High-Risk Anomalies Flagged by ML: {len(flagged_alerts):,}")
print("Saved flagged alerts to 'uidai_style_fraud_alerts.csv'")
display(flagged_alerts.head(5))






import matplotlib.pyplot as plt
import seaborn as sns

# --- QUERY 3: High-Risk User Ranking (Using DENSE_RANK) ---
high_risk_users_query = """
WITH user_risk_summary AS (
    SELECT 
        user_id,
        COUNT(*) AS total_attempts,
        SUM(failed_transaction_count_7d) AS total_7d_failures,
        ROUND(AVG(risk_score), 3) AS avg_risk_score,
        SUM(CASE WHEN fraud_label = 1 THEN 1 ELSE 0 END) AS confirmed_frauds
    FROM auth_transactions
    GROUP BY user_id
)
SELECT 
    DENSE_RANK() OVER (ORDER BY avg_risk_score DESC, total_7d_failures DESC) AS risk_rank,
    user_id,
    total_attempts,
    total_7d_failures,
    avg_risk_score,
    confirmed_frauds
FROM user_risk_summary
LIMIT 10;
"""
print("--- QUERY 3: TOP 10 HIGH-RISK USERS (SQL DENSE_RANK) ---")
display(pd.read_sql_query(high_risk_users_query, conn))

# --- QUERY 4: Weekend vs. Weekday Risk Analysis ---
weekend_risk_query = """
SELECT 
    CASE WHEN is_weekend = 1 THEN 'Weekend' ELSE 'Weekday' END AS day_type,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN fraud_label = 1 THEN 1 ELSE 0 END) AS fraud_count,
    ROUND(100.0 * SUM(CASE WHEN fraud_label = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS fraud_rate_pct,
    ROUND(AVG(risk_score), 3) AS avg_risk_score
FROM auth_transactions
GROUP BY is_weekend;
"""
print("\n--- QUERY 4: WEEKEND VS. WEEKDAY FRAUD ANALYSIS ---")
weekend_df = pd.read_sql_query(weekend_risk_query, conn)
display(weekend_df)

# --- QUERY 5: High-Amount & Velocity Anomaly Filter ---
velocity_query = """
SELECT 
    authentication_method,
    COUNT(*) AS suspicious_burst_events,
    ROUND(AVG(transaction_amount), 2) AS avg_amount,
    ROUND(MAX(transaction_distance), 2) AS max_distance_km
FROM auth_transactions
WHERE failed_transaction_count_7d >= 3 
  AND transaction_amount > (SELECT AVG(transaction_amount) * 1.5 FROM auth_transactions)
GROUP BY authentication_method
ORDER BY suspicious_burst_events DESC;
"""
print(
    "\n--- QUERY 5: HIGH-VALUE + MULTIPLE FAILURE BURSTS BY AUTH METHOD ---"
)
display(pd.read_sql_query(velocity_query, conn))

# --- VISUALIZATION CHARTS FOR GITHUB README ---
sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(1, 2, figsize=(15, 5))

# Chart 1: Fraud Rate by Authentication Method
auth_chart_df = pd.read_sql_query(
    """
    SELECT authentication_method, 
           ROUND(100.0 * SUM(CASE WHEN fraud_label = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS fraud_rate_pct
    FROM auth_transactions
    GROUP BY authentication_method
    ORDER BY fraud_rate_pct DESC
""",
    conn,
)

sns.barplot(
    data=auth_chart_df,
    x="authentication_method",
    y="fraud_rate_pct",
    hue="authentication_method",
    palette="viridis",
    legend=False,
    ax=axes[0],
)
axes[0].set_title(
    "Fraud Rate (%) by Authentication Method", fontsize=13, fontweight="bold"
)
axes[0].set_xlabel("Authentication Method")
axes[0].set_ylabel("Fraud Rate (%)")

# Chart 2: Isolation Forest Anomaly Clusters (Distance vs Risk Score)
sample_df = ml_df.sample(min(2000, len(ml_df)), random_state=42)
sns.scatterplot(
    data=sample_df,
    x="transaction_distance",
    y="risk_score",
    hue="predicted_anomaly",
    palette={0: "#3498db", 1: "#e74c3c"},
    alpha=0.65,
    ax=axes[1],
)
axes[1].set_title(
    "Isolation Forest Anomaly Detection (Distance vs. Risk Score)",
    fontsize=13,
    fontweight="bold",
)
axes[1].set_xlabel("Transaction Distance (km)")
axes[1].set_ylabel("Risk Score")
axes[1].legend(
    title="ML Prediction", labels=["Normal (0)", "Flagged Anomaly (1)"]
)

plt.tight_layout()
plt.savefig("fraud_analysis_charts.png", dpi=300)
plt.show()
print("Charts saved as 'fraud_analysis_charts.png' for your GitHub README!")
