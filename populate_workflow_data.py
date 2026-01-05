
import sqlite3
import random
from datetime import datetime, timedelta
import os

# Database path
DB_PATH = 'backend/sql_app.db'

def populate_workflow():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Fetching existing offers...")
    cursor.execute("""
        SELECT id, mail_date, offer_sent_date, status, managed_by_id, year_stats 
        FROM offers 
        WHERE year_stats IN (2024, 2025)
    """)
    offers = cursor.fetchall()

    print(f"Found {len(offers)} offers. Generating workflow steps...")

    # Departments for workflow
    phases = [
        ('Commerciale', 1),
        ('Tecnico', 2),
        ('Commerciale', 3)
    ]

    count = 0
    for offer_id, mail_date, sent_date, status, user_id, year in offers:
        # Skip if already has steps
        cursor.execute("SELECT COUNT(*) FROM workflow_steps WHERE offer_id = ?", (offer_id,))
        if cursor.fetchone()[0] > 0:
            continue

        # Determine start date
        if mail_date:
            try:
                start_dt = datetime.fromisoformat(mail_date)
            except:
                start_dt = datetime(year, 1, 1) + timedelta(days=random.randint(0, 364))
        else:
            start_dt = datetime(year, 1, 1) + timedelta(days=random.randint(0, 364))

        current_dt = start_dt
        
        for i, (dept, order_idx) in enumerate(phases):
            # Generate duration
            # Phase 1: Commerciale (Ingresso) - 1-4 hours
            # Phase 2: Tecnico (Fattibilita) - 4-48 hours
            # Phase 3: Commerciale (Chiusura) - 1-8 hours
            
            if dept == 'Commerciale' and order_idx == 1:
                duration_h = random.uniform(0.5, 4)
            elif dept == 'Tecnico':
                duration_h = random.uniform(2, 72)
            else:
                duration_h = random.uniform(1, 12)
            
            # If it's the last phase and we have a sent_date, try to align
            if i == len(phases) - 1 and sent_date:
                try:
                    sent_dt = datetime.fromisoformat(sent_date)
                    if sent_dt > current_dt:
                        duration_h = (sent_dt - current_dt).total_seconds() / 3600
                except:
                    pass

            completed_dt = current_dt + timedelta(hours=duration_h)
            
            # Bottleneck if Tecnico takes > 48h
            is_bottleneck = 1 if (dept == 'Tecnico' and duration_h > 48) else 0
            
            cursor.execute("""
                INSERT INTO workflow_steps (
                    offer_id, department, assigned_to_id, status, order_index,
                    started_at, completed_at, actual_duration_minutes, bottleneck_flag,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """, (
                offer_id, dept, user_id or 1, 'completed', order_idx,
                current_dt.isoformat(), completed_dt.isoformat(), 
                int(duration_h * 60), is_bottleneck
            ))
            
            current_dt = completed_dt + timedelta(minutes=random.randint(5, 60)) # Some buffer between phases
        
        count += 1
        if count % 100 == 0:
            print(f"Processed {count} offers...")

    conn.commit()
    conn.close()
    print(f"Successfully populated workflow steps for {count} offers.")

if __name__ == "__main__":
    populate_workflow()
