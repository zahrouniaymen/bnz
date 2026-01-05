import sqlite3

conn = sqlite3.connect('backend/sql_app.db')
cursor = conn.cursor()

cursor.execute('PRAGMA table_info(users)')
columns = cursor.fetchall()

print("Colonnes de la table users:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

conn.close()
