import pandas as pd
import os

file_path = "M77_REGISTRO ORDINI_Rev00 DEL 13_09_2024.xlsx"
try:
    # Read first 20 rows to find header
    df = pd.read_excel(file_path, sheet_name="ORDINE", nrows=20, header=None)
    for i, row in df.iterrows():
        # Print row index and content to find labels
        row_str = " | ".join([str(val).replace("\n", " ") for val in row.values])
        print(f"Row {i}: {row_str}")
except Exception as e:
    print(f"Error: {e}")
