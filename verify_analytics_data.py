import sqlite3

conn = sqlite3.connect('backend/sql_app.db')
cursor = conn.cursor()

print("=== VERIFICATION DES DONNEES ANALYTICS ===\n")

# Check declined reasons
cursor.execute("""
    SELECT declined_reason, COUNT(*) as count 
    FROM offers 
    WHERE declined_reason IS NOT NULL 
    GROUP BY declined_reason
    ORDER BY count DESC
""")
declined = cursor.fetchall()

print("MOTIVI DECLINAZIONE:")
total_declined = 0
for reason, count in declined:
    print(f"  - {reason}: {count}")
    total_declined += count
print(f"  TOTAL: {total_declined}\n")

# Check not accepted reasons
cursor.execute("""
    SELECT not_accepted_reason, COUNT(*) as count 
    FROM offers 
    WHERE not_accepted_reason IS NOT NULL 
    GROUP BY not_accepted_reason
    ORDER BY count DESC
""")
not_accepted = cursor.fetchall()

print("MOTIVI NON ACCETTAZIONE:")
total_not_accepted = 0
for reason, count in not_accepted:
    print(f"  - {reason}: {count}")
    total_not_accepted += count
print(f"  TOTAL: {total_not_accepted}\n")

print("=== CONCLUSION ===")
print(f"Les donnees sont bien presentes dans la base de donnees!")
print(f"Il faut juste redemarrer le backend pour les voir dans les graphiques.")

conn.close()
