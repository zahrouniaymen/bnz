"""
Create user_performance_metrics table in database
"""
import sqlite3

conn = sqlite3.connect('backend/sql_app.db')
cursor = conn.cursor()

print("Creating user_performance_metrics table...")

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    period VARCHAR(7) NOT NULL,
    offers_handled INTEGER DEFAULT 0,
    avg_processing_time_hours REAL DEFAULT 0.0,
    success_rate REAL DEFAULT 0.0,
    current_workload INTEGER DEFAULT 0,
    avg_response_time_hours REAL DEFAULT 0.0,
    total_hours_worked REAL DEFAULT 0.0,
    declined_count INTEGER DEFAULT 0,
    accepted_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, period)
)
""")

conn.commit()
print("[OK] Table created successfully!")

# Verify
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_performance_metrics'")
if cursor.fetchone():
    print("[OK] Table verified in database")
else:
    print("[ERROR] Table not found!")

conn.close()
