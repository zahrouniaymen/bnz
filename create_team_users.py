"""
Créer 4 utilisateurs et répartir les offres entre eux de manière réaliste
"""
import sqlite3
from passlib.context import CryptContext
import random

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

conn = sqlite3.connect('backend/sql_app.db')
cursor = conn.cursor()

print("=" * 80)
print("CRÉATION DES UTILISATEURS ET RÉPARTITION DES OFFRES")
print("=" * 80)
print()

# Créer les 4 utilisateurs
users = [
    {
        'username': 'mirko',
        'email': 'mirko@benozzi.com',
        'full_name': 'Mirko Benozzi',
        'role': 'commerciale',
        'department': 'Commerciale'
    },
    {
        'username': 'chiara',
        'email': 'chiara@benozzi.com',
        'full_name': 'Chiara Rossi',
        'role': 'commerciale',
        'department': 'Commerciale'
    },
    {
        'username': 'amira',
        'email': 'amira@benozzi.com',
        'full_name': 'Amira Benali',
        'role': 'commerciale',
        'department': 'Commerciale'
    },
    {
        'username': 'faten',
        'email': 'faten@benozzi.com',
        'full_name': 'Faten Khalil',
        'role': 'commerciale',
        'department': 'Commerciale'
    }
]

# Hash du mot de passe "123"
hashed_password = pwd_context.hash("123")

print("Création des utilisateurs...")
user_ids = {}

for user in users:
    # Vérifier si l'utilisateur existe déjà
    cursor.execute("SELECT id FROM users WHERE username = ?", (user['username'],))
    existing = cursor.fetchone()
    
    if existing:
        user_ids[user['username']] = existing[0]
        print(f"[SKIP] {user['full_name']} existe déjà (ID: {existing[0]})")
    else:
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, department, full_name, active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 1, datetime('now'))
        """, (user['username'], user['email'], hashed_password, user['role'], user['department'], user['full_name']))
        user_ids[user['username']] = cursor.lastrowid
        print(f"[OK] {user['full_name']} créé (ID: {cursor.lastrowid})")

conn.commit()

# Récupérer toutes les offres 2024-2025
cursor.execute("""
    SELECT id, year_stats FROM offers 
    WHERE year_stats IN (2024, 2025)
    ORDER BY id
""")
offers = cursor.fetchall()

print(f"\n{len(offers)} offres à répartir...")

# Répartition réaliste (avec un peu de variation)
# Mirko: 30%, Chiara: 25%, Amira: 25%, Faten: 20%
weights = {
    'mirko': 0.30,
    'chiara': 0.25,
    'amira': 0.25,
    'faten': 0.20
}

# Créer une liste pondérée d'utilisateurs
user_pool = []
for username, weight in weights.items():
    count = int(len(offers) * weight)
    user_pool.extend([user_ids[username]] * count)

# Compléter avec des utilisateurs aléatoires si nécessaire
while len(user_pool) < len(offers):
    user_pool.append(random.choice(list(user_ids.values())))

# Mélanger pour randomiser
random.shuffle(user_pool)

# Assigner les offres
print("\nRépartition des offres...")
assignments = {username: 0 for username in user_ids.keys()}

for i, (offer_id, year) in enumerate(offers):
    assigned_user_id = user_pool[i]
    
    cursor.execute("""
        UPDATE offers 
        SET managed_by_id = ?
        WHERE id = ?
    """, (assigned_user_id, offer_id))
    
    # Compter les assignments
    for username, uid in user_ids.items():
        if uid == assigned_user_id:
            assignments[username] += 1
            break

conn.commit()

print("\n--- RÉSUMÉ ---")
for username, count in assignments.items():
    percentage = (count / len(offers) * 100) if len(offers) > 0 else 0
    print(f"  {username.capitalize()}: {count} offres ({percentage:.1f}%)")

# Recalculer les métriques de performance pour chaque utilisateur
print("\nRecalcul des métriques de performance...")
cursor.execute("DELETE FROM user_performance_metrics")

from datetime import datetime
from collections import defaultdict

# Calculer les métriques par utilisateur et période
for username, user_id in user_ids.items():
    cursor.execute("""
        SELECT 
            o.id, o.status, o.created_at, o.updated_at,
            strftime('%Y-%m', o.created_at) as period
        FROM offers o
        WHERE o.managed_by_id = ? AND o.year_stats IN (2024, 2025)
    """, (user_id,))
    
    user_offers = cursor.fetchall()
    
    # Grouper par période
    periods = defaultdict(lambda: {'total': 0, 'accepted': 0, 'declined': 0})
    
    for offer in user_offers:
        offer_id, status, created, updated, period = offer
        if period:
            periods[period]['total'] += 1
            if status == 'ACCETTATA':
                periods[period]['accepted'] += 1
            elif status == 'DECLINATA':
                periods[period]['declined'] += 1
    
    # Insérer les métriques
    for period, metrics in periods.items():
        success_rate = (metrics['accepted'] / metrics['total'] * 100) if metrics['total'] > 0 else 0
        
        # Workload actuel
        cursor.execute("""
            SELECT COUNT(*) FROM offers 
            WHERE managed_by_id = ? 
            AND status IN ('IN_LAVORO', 'PENDING_REGISTRATION', 'CHECKS_IN_PROGRESS')
        """, (user_id,))
        workload = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO user_performance_metrics 
            (user_id, period, offers_handled, success_rate, current_workload, 
             accepted_count, declined_count, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (user_id, period, metrics['total'], success_rate, workload, 
              metrics['accepted'], metrics['declined']))

conn.commit()

print(f"[OK] Métriques calculées pour {len(user_ids)} utilisateurs")

# Vérification finale
print("\n--- VÉRIFICATION ---")
cursor.execute("""
    SELECT u.username, COUNT(o.id) as total_offers
    FROM users u
    LEFT JOIN offers o ON o.managed_by_id = u.id AND o.year_stats IN (2024, 2025)
    WHERE u.username IN ('mirko', 'chiara', 'amira', 'faten')
    GROUP BY u.username
    ORDER BY total_offers DESC
""")

for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} offres")

conn.close()

print("\n" + "=" * 80)
print("[SUCCESS] 4 utilisateurs créés et offres réparties!")
print("=" * 80)
print("\nConnexions disponibles:")
print("  - admin / 123 (voit TOUT)")
print("  - mirko / 123 (voit ses offres)")
print("  - chiara / 123 (voit ses offres)")
print("  - amira / 123 (voit ses offres)")
print("  - faten / 123 (voit ses offres)")
