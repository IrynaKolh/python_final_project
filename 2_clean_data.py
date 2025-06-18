import pandas as pd
import os
import re

input_folder = "started_csv"
output_folder = "cleaned_csv"
os.makedirs(output_folder, exist_ok=True)

# Get all CSV-files from dir started_csv
csv_files = [
    f
    for f in os.listdir(input_folder)
    if f.endswith(".csv") and not f.endswith("_cleaned.csv")
]
for file in csv_files:
    try:
        print(f"Handling file: {file}")
        file_path = os.path.join(input_folder, file)
        df = pd.read_csv(file_path)
        # last metric ("Doubles", "AVG", etc.)
        metric_col = df.columns[-1]

        # === Validation ===
        valid_year = df["Year"].notna() & (df["Year"].astype(str).str.lower() != "year")
        valid_league = df["League"].isin(["AL", "NL"])        
        df[metric_col] = pd.to_numeric(df[metric_col], errors="coerce")
        valid_metric = df[metric_col].notna()
        is_valid = valid_year & valid_league & valid_metric
        removed_rows = df[~is_valid]
        cleaned_rows = df[is_valid].copy()

        # Cleaning
        cleaned_rows["Year"] = cleaned_rows["Year"].astype(int)
        cleaned_rows["League"] = cleaned_rows["League"].astype(str).str.strip()
        cleaned_rows["Player"] = cleaned_rows["Player"].astype(str).str.strip()
        cleaned_rows["Team"] = cleaned_rows["Team"].astype(str).str.strip()
        cleaned_rows[metric_col] = cleaned_rows[metric_col].astype(float)

        # Saving cleaned data to dir cleaned_csv/
        cleaned_filename = file.replace(".csv", "_cleaned.csv")
        output_path = os.path.join(output_folder, cleaned_filename)
        cleaned_rows.to_csv(output_path, index=False)
        print(f"Saved: {output_path}")
    except Exception as e:
        print(f"Error in {file}: {e}")
