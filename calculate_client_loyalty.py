"""
Calculate and update client loyalty scores from existing offer data
"""
import sqlite3

conn = sqlite3.connect('backend/sql_app.db')
cursor = conn.cursor()

print("=" * 80)
print("CALCULATING CLIENT LOYALTY SCORES")
print("=" * 80)
print()

# Get all clients
cursor.execute("SELECT id, name FROM clients")
clients = cursor.fetchall()

print(f"Processing {len(clients)} clients...")
print()

updated = 0
for client_id, client_name in clients:
    # Count new items vs reorders for 2024-2025
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN is_new_item = 1 THEN 1 ELSE 0 END) as new_items,
            SUM(CASE WHEN is_new_item = 0 THEN 1 ELSE 0 END) as reorders,
            COUNT(*) as total
        FROM offers
        WHERE client_id = ? AND year_stats IN (2024, 2025)
    """, (client_id,))
    
    result = cursor.fetchone()
    new_items = result[0] or 0
    reorders = result[1] or 0
    total = result[2] or 0
    
    if total == 0:
        continue
    
    # Calculate loyalty score (0-100)
    # Higher score = more reorders (loyal customer)
    loyalty_score = (reorders / total * 100) if total > 0 else 0
    
    # Bonus for high volume clients
    if total > 20:
        loyalty_score = min(100, loyalty_score * 1.1)
    
    # Update client
    cursor.execute("""
        UPDATE clients 
        SET new_items_count = ?, reorder_count = ?, loyalty_score = ?
        WHERE id = ?
    """, (new_items, reorders, loyalty_score, client_id))
    
    updated += 1
    
    if updated <= 5:  # Show first 5
        print(f"  {client_name}: {new_items} new, {reorders} reorders, loyalty: {loyalty_score:.1f}%")

conn.commit()

print(f"\n[OK] Updated {updated} clients with loyalty scores")

# Show top loyal clients
print("\nTop 10 Most Loyal Clients:")
cursor.execute("""
    SELECT name, loyalty_score, reorder_count, new_items_count
    FROM clients
    WHERE loyalty_score > 0
    ORDER BY loyalty_score DESC
    LIMIT 10
""")
for i, row in enumerate(cursor.fetchall(), 1):
    print(f"  {i}. {row[0]}: {row[1]:.1f}% ({row[2]} reorders, {row[3]} new)")

conn.close()

print("\n" + "=" * 80)
print("[SUCCESS] Client loyalty scores calculated!")
print("=" * 80)
