import sqlite3
import pandas as pd
import os

input_folder = "cleaned_csv"
db_name = "baseball.db"

# Get all CSV files from the cleaned_csv directory
csv_files = [f for f in os.listdir(input_folder) if f.endswith("_cleaned.csv")]


with sqlite3.connect(db_name) as conn:
    cursor = conn.cursor()
    for file in csv_files:
        try:
            file_path = os.path.join(input_folder, file)
            df = pd.read_csv(file_path)
            # Table name "_cleaned.csv"
            table_name = os.path.splitext(file)[0].replace("_cleaned", "").lower().replace(" ", "_")
            # Metric column is the last column in the DataFrame
            metric_col = df.columns[-1]
            metric_sql = metric_col.lower().replace(" ", "_")
            print(f"Import to table: {table_name}")
            # Drop the table if it exists
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            # Create the table 
            cursor.execute(f"""
                CREATE TABLE {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Year INTEGER,
                    League TEXT,
                    Player TEXT,
                    Team TEXT,
                    {metric_sql} REAL
                )
            """)
            # Insert data into the table
            for _, row in df.iterrows():
                cursor.execute(f"""
                    INSERT INTO {table_name} (Year, League, Player, Team, {metric_sql})
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    int(row["Year"]),
                    row["League"],
                    row["Player"],
                    row["Team"],
                    float(row[metric_col])
                ))
            print(f"Uploaded: {file} → {table_name}")
        except Exception as e:
            print(f"Error during loading {file}: {e}")