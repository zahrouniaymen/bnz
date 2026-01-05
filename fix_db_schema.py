import sqlite3
import os

DB_PATH = 'backend/sql_app.db'

def fix_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Add voto to clients
    try:
        cursor.execute('ALTER TABLE clients ADD COLUMN voto INTEGER')
        print("Added 'voto' to clients table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("'voto' already exists in clients.")
        else:
            print(f"Error adding 'voto': {e}")

    # Add is_new_item to offers
    try:
        cursor.execute('ALTER TABLE offers ADD COLUMN is_new_item BOOLEAN DEFAULT 1')
        print("Added 'is_new_item' to offers table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("'is_new_item' already exists in offers.")
        else:
            print(f"Error adding 'is_new_item': {e}")
            
    conn.commit()
    conn.close()
    print("Database schema fix attempt completed.")

if __name__ == "__main__":
    fix_schema()
