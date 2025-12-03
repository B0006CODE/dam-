import pandas as pd
import json

# Read the Excel file
df = pd.read_excel('水库信息.xlsx')

# Clean column names
df.columns = df.columns.str.strip()

print("Columns:", df.columns.tolist())
print("\nData shape:", df.shape)
print("\nFirst 5 rows:")
print(df.head())

print("\n\nColumn details:")
for col in df.columns:
    print(f"\n{col}:")
    print(f"  Type: {df[col].dtype}")
    print(f"  Unique values: {df[col].nunique()}")
    print(f"  Sample values: {df[col].dropna().unique()[:5].tolist()}")

# Check province distribution
if '水库地点' in df.columns:
    print("\n\nProvince distribution:")
    print(df['水库地点'].value_counts().head(20))
