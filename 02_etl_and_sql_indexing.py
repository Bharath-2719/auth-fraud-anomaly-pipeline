import sqlite3
import time

# Clean column names
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

# Standardize target column name if needed
if "fraud_label" not in df.columns and "is_fraud" in df.columns:
  df.rename(columns={"is_fraud": "fraud_label"}, inplace=True)

print("Available SQL columns:", list(df.columns))

# Load into in-memory SQLite database
conn = sqlite3.connect(":memory:")
df.to_sql("auth_transactions", conn, if_exists="replace", index=False)

# Create Composite Indexes
cursor = conn.cursor()
start_idx = time.time()
cursor.execute(
    "CREATE INDEX idx_user_time ON auth_transactions(user_id, timestamp);"
)
cursor.execute(
    "CREATE INDEX idx_auth_device ON auth_transactions(authentication_method,"
    " device_type);"
)
conn.commit()

print(f"Loaded into SQL & indexed in {time.time() - start_idx:.3f} seconds.")
