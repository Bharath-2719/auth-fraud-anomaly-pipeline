import glob
import kagglehub
import pandas as pd

# Download the dataset directly from Kaggle
path = kagglehub.dataset_download(
    "samayashar/fraud-detection-transactions-dataset"
)
csv_files = glob.glob(f"{path}/*.csv")

# Load the first CSV file from the returned list into Pandas
df = pd.read_csv(csv_files[0])

print(f"Loaded {len(df):,} rows and {len(df.columns)} columns.")
print("Columns:", list(df.columns))
df.head(5)
