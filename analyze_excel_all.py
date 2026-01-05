import pandas as pd
import sys

def analyze():
    filename = 'M77_REGISTRO ORDINI_Rev00 DEL 13_09_2024.xlsx'
    try:
        xl = pd.ExcelFile(filename)
        print(f"File: {filename}")
        print("-" * 50)
        for sheet in xl.sheet_names:
            try:
                df = xl.parse(sheet, nrows=5)
                cols = df.columns.tolist()
                print(f"Sheet: {sheet}")
                print(f"Columns: {cols}")
                print(f"Rows: {len(df)}")
                print("-" * 20)
            except Exception as e:
                print(f"Error parsing sheet {sheet}: {e}")
    except Exception as e:
        print(f"Error opening file: {e}")

if __name__ == "__main__":
    analyze()
