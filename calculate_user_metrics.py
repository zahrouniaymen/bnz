"""
Calculate and populate user performance metrics from existing offer data
"""
import sqlite3
from datetime import datetime
from collections import defaultdict

conn = sqlite3.connect('backend/sql_app.db')
cursor = conn.cursor()

print("=" * 80)
print("CALCULATING USER PERFORMANCE METRICS")
print("=" * 80)
print()

# Get all users
cursor.execute("SELECT id, username, full_name FROM users WHERE active = 1")
users = cursor.fetchall()

# Get all offers from 2024-2025
cursor.execute("""
    SELECT 
        o.id, o.managed_by_id, o.status, o.created_at, o.updated_at,
        o.offer_sent_date, o.order_date, o.year_stats
    FROM offers o
    WHERE o.year_stats IN (2024, 2025)
""")
offers = cursor.fetchall()

print(f"Processing {len(offers)} offers for {len(users)} users...")
print()

# Calculate metrics by user and period
user_metrics = defaultdict(lambda: defaultdict(lambda: {
    'offers_handled': 0,
    'accepted': 0,
    'declined': 0,
    'total_processing_time': 0,
    'count_with_time': 0
}))

for offer in offers:
    offer_id, managed_by_id, status, created_at, updated_at, sent_date, order_date, year = offer
    
    if not managed_by_id or not created_at:
        continue
    
    # Parse date and get period
    try:
        created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        period = created.strftime('%Y-%m')
    except:
        continue
    
    # Update metrics
    metrics = user_metrics[managed_by_id][period]
    metrics['offers_handled'] += 1
    
    if status == 'ACCETTATA':
        metrics['accepted'] += 1
    elif status == 'DECLINATA':
        metrics['declined'] += 1
    
    # Calculate processing time if possible
    if updated_at and created_at:
        try:
            created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            updated_dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            hours = (updated_dt - created_dt).total_seconds() / 3600
            if hours > 0 and hours < 720:  # Max 30 days
                metrics['total_processing_time'] += hours
                metrics['count_with_time'] += 1
        except:
            pass

# Insert into database
inserted = 0
for user_id, periods in user_metrics.items():
    for period, metrics in periods.items():
        # Calculate averages
        avg_time = metrics['total_processing_time'] / metrics['count_with_time'] if metrics['count_with_time'] > 0 else 0
        success_rate = (metrics['accepted'] / metrics['offers_handled'] * 100) if metrics['offers_handled'] > 0 else 0
        
        # Get current workload (active offers)
        cursor.execute("""
            SELECT COUNT(*) FROM offers 
            WHERE managed_by_id = ? 
            AND status IN ('IN_LAVORO', 'PENDING_REGISTRATION', 'CHECKS_IN_PROGRESS')
        """, (user_id,))
        workload = cursor.fetchone()[0]
        
        # Insert or update
        cursor.execute("""
            INSERT OR REPLACE INTO user_performance_metrics 
            (user_id, period, offers_handled, avg_processing_time_hours, success_rate, 
             current_workload, accepted_count, declined_count, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (
            user_id, period, metrics['offers_handled'], avg_time, success_rate,
            workload, metrics['accepted'], metrics['declined']
        ))
        inserted += 1

conn.commit()

print(f"[OK] Inserted/Updated {inserted} performance metrics records")

# Verify
cursor.execute("SELECT COUNT(*) FROM user_performance_metrics")
total = cursor.fetchone()[0]
print(f"[OK] Total metrics in database: {total}")

# Show sample
cursor.execute("""
    SELECT u.username, upm.period, upm.offers_handled, upm.success_rate
    FROM user_performance_metrics upm
    JOIN users u ON u.id = upm.user_id
    ORDER BY upm.period DESC
    LIMIT 5
""")
print("\nSample metrics:")
for row in cursor.fetchall():
    print(f"  {row[0]} ({row[1]}): {row[2]} offers, {row[3]:.1f}% success")

conn.close()

print("\n" + "=" * 80)
print("[SUCCESS] User performance metrics calculated!")
print("=" * 80)
