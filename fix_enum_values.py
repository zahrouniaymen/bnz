import sqlite3

conn = sqlite3.connect('backend/sql_app.db')
cursor = conn.cursor()

print("=== CORRECTION DES VALEURS ENUM ===\n")

# Fix declined_reason values to match enum
corrections = {
    "TEMPI DI CONSEGNA": "TEMPI_CONSEGNA",
    "ARTICOLO NON FATTIBILE": "ARTICOLO_NON_FATTIBILE",
    "SOVRACCARICO PRODUTTIVO": "SOVRACCARICO_PRODUTTIVO",
    "QUANTITÀ ALTE": "QUANTITA_ALTE",
    "QUANTITÀ BASSE": "QUANTITA_BASSE",
    "CLIENTE NON STRATEGICO": "CLIENTE_NON_STRATEGICO",
    "COMPONENTE NON STRATEGICO": "COMPONENTE_NON_STRATEGICO",
    "TARGET BASSO": "TARGET_BASSO"
}

for old_value, new_value in corrections.items():
    cursor.execute(
        "UPDATE offers SET declined_reason = ? WHERE declined_reason = ?",
        (new_value, old_value)
    )
    if cursor.rowcount > 0:
        print(f"[OK] {cursor.rowcount} offres: '{old_value}' -> '{new_value}'")

conn.commit()

# Verify
cursor.execute("SELECT declined_reason, COUNT(*) FROM offers WHERE declined_reason IS NOT NULL GROUP BY declined_reason")
print("\n=== VERIFICATION ===")
for reason, count in cursor.fetchall():
    print(f"  {reason}: {count}")

conn.close()

print("\n[OK] CORRECTION TERMINEE!")
print("Redemarrez le backend maintenant (Ctrl+C puis start_app.bat)")
