import pandas as pd

def find_header_row(file_path):
    for i in range(10):
        try:
            df = pd.read_excel(file_path, header=i, nrows=5)
            cols = [str(c).upper() for c in df.columns]
            if any("CLIENTE" in c for c in cols) or any("COMMITTENTE" in c for c in cols):
                return i, df.columns.tolist()
        except:
            continue
    return None, None

m54_file = 'M54_REGISTRO OFFERTE_REV03 DEL 20_03_2024.xlsx'
m77_file = 'M77_REGISTRO ORDINI_Rev00 DEL 13_09_2024.xlsx'

h_m54, c_m54 = find_header_row(m54_file)
h_m77, c_m77 = find_header_row(m77_file)

print(f"M54 Header: {h_m54}, Columns: {c_m54}")
print(f"M77 Header: {h_m77}, Columns: {c_m77}")
