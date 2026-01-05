import pandas as pd
import os
from datetime import datetime

print("=" * 80)
print("ANALYSE APPROFONDIE DES FICHIERS EXCEL M54 ET M77")
print("=" * 80)
print()

# Files to analyze
files = {
    "M54": "M54_REGISTRO OFFERTE_REV03 DEL 20_03_2024.xlsx",
    "M77": "M77_REGISTRO ORDINI_Rev00 DEL 13_09_2024.xlsx"
}

analysis_results = {}

for file_key, file_path in files.items():
    if not os.path.exists(file_path):
        print(f"[ERREUR] Fichier non trouve: {file_path}")
        continue
    
    print(f"\n{'='*80}")
    print(f"ANALYSE DU FICHIER: {file_key}")
    print(f"{'='*80}\n")
    
    xl = pd.ExcelFile(file_path)
    analysis_results[file_key] = {}
    
    for sheet_name in xl.sheet_names:
        print(f"\n--- SHEET: {sheet_name} ---")
        
        try:
            # Read first few rows to understand structure
            df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=10)
            
            # Basic info
            print(f"  Colonnes ({len(df.columns)}): {', '.join([str(col)[:30] for col in df.columns[:10]])}")
            if len(df.columns) > 10:
                print(f"  ... et {len(df.columns) - 10} autres colonnes")
            
            # Read full sheet to count rows (excluding 2023 if date column exists)
            df_full = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # Try to identify date columns and filter out 2023
            date_cols = [col for col in df_full.columns if any(keyword in str(col).lower() for keyword in ['data', 'date', 'anno', 'year'])]
            
            total_rows = len(df_full)
            rows_2024_2025 = total_rows
            
            if date_cols:
                for date_col in date_cols:
                    try:
                        df_full[date_col] = pd.to_datetime(df_full[date_col], errors='coerce')
                        if df_full[date_col].notna().any():
                            df_filtered = df_full[df_full[date_col].dt.year.isin([2024, 2025])]
                            rows_2024_2025 = len(df_filtered)
                            break
                    except:
                        pass
            
            print(f"  Lignes totales: {total_rows}")
            if rows_2024_2025 != total_rows:
                print(f"  Lignes 2024-2025: {rows_2024_2025}")
            
            # Sample data
            print(f"  Exemple de donnees (premiere ligne):")
            if len(df) > 0:
                for col in df.columns[:5]:
                    val = df[col].iloc[0] if not pd.isna(df[col].iloc[0]) else "N/A"
                    print(f"    - {col}: {str(val)[:50]}")
            
            # Store analysis
            analysis_results[file_key][sheet_name] = {
                "columns": list(df.columns),
                "total_rows": total_rows,
                "rows_2024_2025": rows_2024_2025,
                "sample": df.head(3).to_dict()
            }
            
        except Exception as e:
            print(f"  [ERREUR] Impossible de lire: {str(e)[:100]}")
            analysis_results[file_key][sheet_name] = {"error": str(e)}

print("\n" + "="*80)
print("ANALYSE TERMINEE")
print("="*80)
print("\nLes resultats detailles sont sauvegardes pour analyse approfondie.")
