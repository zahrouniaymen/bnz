"""
Database migration script to add analytics fields to existing models.
This script safely adds new columns without affecting existing data.
"""
import sqlite3
import os

# Database path
db_path = 'backend/sql_app.db'

if not os.path.exists(db_path):
    print(f"[ERROR] Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("DATABASE MIGRATION: Adding Analytics Fields")
print("=" * 80)
print()

# Function to safely add column
def add_column_if_not_exists(table, column, definition):
    try:
        # Check if column exists
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        
        if column in columns:
            print(f"[SKIP] {table}.{column} already exists")
            return False
        
        # Add column
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        print(f"[OK] Added {table}.{column}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to add {table}.{column}: {e}")
        return False

# Client table analytics fields
print("\n--- CLIENT TABLE ---")
add_column_if_not_exists('clients', 'new_items_count', 'INTEGER DEFAULT 0')
add_column_if_not_exists('clients', 'reorder_count', 'INTEGER DEFAULT 0')
add_column_if_not_exists('clients', 'loyalty_score', 'REAL DEFAULT 0.0')

# WorkflowStep table timing fields
print("\n--- WORKFLOW_STEPS TABLE ---")
add_column_if_not_exists('workflow_steps', 'actual_duration_minutes', 'INTEGER')
add_column_if_not_exists('workflow_steps', 'waiting_time_minutes', 'INTEGER')
add_column_if_not_exists('workflow_steps', 'bottleneck_flag', 'BOOLEAN DEFAULT 0')

# Commit changes
conn.commit()

# Verify additions
print("\n--- VERIFICATION ---")
cursor.execute("PRAGMA table_info(clients)")
client_cols = [row[1] for row in cursor.fetchall()]
print(f"Client columns: {', '.join([c for c in client_cols if c in ['new_items_count', 'reorder_count', 'loyalty_score']])}")

cursor.execute("PRAGMA table_info(workflow_steps)")
workflow_cols = [row[1] for row in cursor.fetchall()]
print(f"WorkflowStep columns: {', '.join([c for c in workflow_cols if c in ['actual_duration_minutes', 'waiting_time_minutes', 'bottleneck_flag']])}")

conn.close()

print("\n" + "=" * 80)
print("[SUCCESS] Migration completed successfully!")
print("=" * 80)
print("\nNext step: Update backend/models.py to reflect these new columns")
