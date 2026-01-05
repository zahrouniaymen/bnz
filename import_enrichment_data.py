import pandas as pd
import sqlite3
import os
from datetime import datetime
import sys

# Add backend to path to use models if needed, but direct SQL is safer for migrations
DB_PATH = r"C:\Users\HP STORE\Desktop\M54\backend\sql_app.db"
EXCEL_PATH = r"C:\Users\HP STORE\Desktop\M54\M77_REGISTRO ORDINI_Rev00 DEL 13_09_2024.xlsx"

def migration():
    print(f"Starting migration from {EXCEL_PATH}...")
    
    if not os.path.exists(EXCEL_PATH):
        print(f"Error: Excel file not found at {EXCEL_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Update Clients with Sector, Domains, and Voto
    print("Enriching Clients...")
    try:
        df_info = pd.read_excel(EXCEL_PATH, sheet_name='INFO')
        # Clean columns
        df_info.columns = [c.strip() for c in df_info.columns]
        
        for index, row in df_info.iterrows():
            cliente = str(row['CLIENTE']).strip()
            settore = str(row['SETTORE']).strip() if pd.notna(row['SETTORE']) else None
            domini = str(row['DOMINI']).strip() if pd.notna(row['DOMINI']) else None
            
            if cliente and cliente != '.':
                # Update existing client by name (case insensitive-ish)
                cursor.execute("""
                    UPDATE clients 
                    SET sector = ?, email_domain = ?
                    WHERE UPPER(name) = UPPER(?) AND (sector IS NULL OR email_domain IS NULL)
                """, (settore, domini, cliente))
    except Exception as e:
        print(f"Error updating clients: {e}")

    # 2. Import Holidays
    print("Importing Holidays...")
    try:
        xl = pd.ExcelFile(EXCEL_PATH)
        if 'FESTIVITA' in xl.sheet_names:
            df_fest = pd.read_excel(EXCEL_PATH, sheet_name='FESTIVITA')
            # The column name is a timestamp in the preview, let's just get all values
            dates = []
            # Check the first column
            col0 = df_fest.columns[0]
            if isinstance(col0, (datetime, pd.Timestamp)):
                dates.append(col0)
            
            for val in df_fest.iloc[:, 0]:
                if isinstance(val, (datetime, pd.Timestamp)):
                    dates.append(val)
            
            for d in dates:
                # Format to ISO for SQLite
                d_str = d.strftime('%Y-%m-%d 00:00:00')
                cursor.execute("INSERT OR IGNORE INTO holidays (date, description, is_recurring) VALUES (?, ?, ?)", 
                             (d_str, 'Festivita M77', 1))
    except Exception as e:
        print(f"Error importing holidays: {e}")

    conn.commit()
    conn.close()
    print("Migration completed successfully.")

if __name__ == "__main__":
    migration()
