import pandas as pd
import os

file_path = "M77_REGISTRO ORDINI_Rev00 DEL 13_09_2024.xlsx"
try:
    df = pd.read_excel(file_path, sheet_name="ORDINE", nrows=10, header=None)
    print("First 10 rows of ORDINE:")
    print(df.to_string())
except Exception as e:
    print(f"Error: {e}")
