import pandas as pd
import os

file_path = "M77_REGISTRO ORDINI_Rev00 DEL 13_09_2024.xlsx"
if not os.path.exists(file_path):
    print(f"File {file_path} not found.")
    exit(1)

try:
    xl = pd.ExcelFile(file_path)
    print("Sheet names:")
    for sheet in xl.sheet_names:
        print(f"- {sheet}")
except Exception as e:
    print(f"Error: {e}")
