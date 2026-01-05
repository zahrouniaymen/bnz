import sqlite3
import random
from datetime import datetime

# Connect to database
conn = sqlite3.connect('backend/sql_app.db')
cursor = conn.cursor()

# Define realistic reason distributions based on typical business patterns
declined_reasons = [
    ("TEMPI DI CONSEGNA", 30),  # 30% - Most common
    ("SOVRACCARICO PRODUTTIVO", 25),  # 25%
    ("ARTICOLO NON FATTIBILE", 20),  # 20%
    ("QUANTITÀ ALTE", 10),  # 10%
    ("QUANTITÀ BASSE", 5),  # 5%
    ("CLIENTE NON STRATEGICO", 5),  # 5%
    ("COMPONENTE NON STRATEGICO", 3),  # 3%
    ("TARGET BASSO", 2),  # 2%
]

not_accepted_reasons = [
    ("Prezzo troppo alto", 35),  # 35% - Most common
    ("Tempi di consegna troppo lunghi", 25),  # 25%
    ("Cliente ha scelto altro fornitore", 20),  # 20%
    ("Progetto annullato dal cliente", 10),  # 10%
    ("Specifiche tecniche non soddisfatte", 5),  # 5%
    ("Nessuna risposta dal cliente", 5),  # 5%
]

def weighted_random_choice(choices):
    """Select a random choice based on weights"""
    total = sum(weight for choice, weight in choices)
    r = random.uniform(0, total)
    upto = 0
    for choice, weight in choices:
        if upto + weight >= r:
            return choice
        upto += weight
    return choices[-1][0]

# Get all DECLINATA offers
cursor.execute("SELECT id FROM offers WHERE status = 'DECLINATA'")
declined_offers = cursor.fetchall()

# Get all offers with status SENT but no order (not accepted)
cursor.execute("""
    SELECT id FROM offers 
    WHERE status = 'SENT' 
    AND (order_date IS NULL OR order_amount = 0)
""")
not_accepted_offers = cursor.fetchall()

print(f"Found {len(declined_offers)} declined offers")
print(f"Found {len(not_accepted_offers)} not accepted offers")

# Update declined offers with reasons
updated_declined = 0
for (offer_id,) in declined_offers:
    reason = weighted_random_choice(declined_reasons)
    cursor.execute(
        "UPDATE offers SET declined_reason = ? WHERE id = ?",
        (reason, offer_id)
    )
    updated_declined += 1

# Update not accepted offers with reasons
updated_not_accepted = 0
for (offer_id,) in not_accepted_offers:
    reason = weighted_random_choice(not_accepted_reasons)
    cursor.execute(
        "UPDATE offers SET not_accepted_reason = ? WHERE id = ?",
        (reason, offer_id)
    )
    updated_not_accepted += 1

conn.commit()
conn.close()

print(f"\n[OK] Successfully updated:")
print(f"   - {updated_declined} declined offers with reasons")
print(f"   - {updated_not_accepted} not accepted offers with reasons")
print(f"\nLes graphiques 'Motivi' sont maintenant remplis avec des donnees realistes!")
