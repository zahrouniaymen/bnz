import pandas as pd
import os

file_path = "M77_REGISTRO ORDINI_Rev00 DEL 13_09_2024.xlsx"
if not os.path.exists(file_path):
    print(f"File {file_path} not found.")
    exit(1)

try:
    # Read only the first row to get column names
    df = pd.read_excel(file_path, sheet_name="ORDINE", nrows=0)
    print("Columns in REGISTRO:")
    for col in df.columns:
        print(f"- {col}")
except Exception as e:
    print(f"Error reading Excel: {e}")
