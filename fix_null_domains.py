import sqlite3
import os

db_path = 'backend/sql_app.db'
if not os.path.exists(db_path):
    # Try alternate path if called from different CWD
    db_path = 'sql_app.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("UPDATE clients SET email_domain = '' WHERE email_domain IS NULL")
conn.commit()
print(f"Updated {cursor.rowcount} records.")
conn.close()
