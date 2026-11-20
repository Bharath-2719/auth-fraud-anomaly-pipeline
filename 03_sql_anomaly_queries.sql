# Query 1: Impossible Travel & Rapid Consecutive Attempts (Using SQL LAG)
impossible_travel_query = """
WITH user_history AS (
    SELECT 
        transaction_id,
        user_id,
        timestamp,
        location,
        authentication_method,
        transaction_distance,
        failed_transaction_count_7d,
        LAG(location) OVER (PARTITION BY user_id ORDER BY timestamp) AS prev_location,
        LAG(timestamp) OVER (PARTITION BY user_id ORDER BY timestamp) AS prev_timestamp
    FROM auth_transactions
)
SELECT 
    transaction_id,
    user_id,
    prev_location,
    location AS current_location,
    ROUND(transaction_distance, 2) AS distance_km,
    authentication_method,
    failed_transaction_count_7d
FROM user_history
WHERE prev_location IS NOT NULL 
  AND prev_location != location
  AND transaction_distance > 500
  AND failed_transaction_count_7d >= 3
ORDER BY transaction_distance DESC
LIMIT 10;
"""

print("--- TOP FLAGGED IMPOSSIBLE TRAVEL & FAILURE ANOMALIES (SQL) ---")
sql_anomalies = pd.read_sql_query(impossible_travel_query, conn)
display(sql_anomalies)

# Query 2: Risk Breakdown by Authentication Method & Device Type
auth_summary_query = """
SELECT 
    authentication_method,
    device_type,
    COUNT(*) AS total_events,
    SUM(CASE WHEN fraud_label = 1 THEN 1 ELSE 0 END) AS confirmed_frauds,
    ROUND(AVG(risk_score), 3) AS avg_risk_score,
    ROUND(100.0 * SUM(CASE WHEN fraud_label = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS fraud_rate_pct
FROM auth_transactions
GROUP BY authentication_method, device_type
ORDER BY fraud_rate_pct DESC;
"""

print("\n--- AUTHENTICATION & DEVICE RISK SUMMARY (SQL) ---")
display(pd.read_sql_query(auth_summary_query, conn))
