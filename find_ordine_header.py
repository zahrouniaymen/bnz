import pandas as pd
import os

file_path = "M77_REGISTRO ORDINI_Rev00 DEL 13_09_2024.xlsx"
try:
    df = pd.read_excel(file_path, sheet_name="ORDINE", nrows=5, header=None)
    for i, row in df.iterrows():
        print(f"Row {i}: {' | '.join(map(str, row.values))}")
except Exception as e:
    print(f"Error: {e}")
