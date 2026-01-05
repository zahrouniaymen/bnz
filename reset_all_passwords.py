"""
Réinitialiser tous les mots de passe à "123"
"""
import sqlite3
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Connexion à la base de données
conn = sqlite3.connect('backend/sql_app.db')
cursor = conn.cursor()

print("=" * 80)
print("RÉINITIALISATION DE TOUS LES MOTS DE PASSE À '123'")
print("=" * 80)
print()

# Hash du mot de passe "123"
hashed_password = pwd_context.hash("123")

# Récupérer tous les utilisateurs
cursor.execute("SELECT id, username, full_name FROM users")
users = cursor.fetchall()

print(f"Mise à jour de {len(users)} utilisateurs...\n")

# Mettre à jour tous les mots de passe
for user_id, username, full_name in users:
    cursor.execute("""
        UPDATE users 
        SET password_hash = ?
        WHERE id = ?
    """, (hashed_password, user_id))
    
    print(f"✓ {username} ({full_name or 'Sans nom'}) - mot de passe: 123")

conn.commit()
conn.close()

print("\n" + "=" * 80)
print("✅ TOUS LES MOTS DE PASSE ONT ÉTÉ CHANGÉS À '123'")
print("=" * 80)
print("\nVous pouvez maintenant vous connecter avec:")
print("  - admin / 123")
print("  - mirko / 123")
print("  - chiara / 123")
print("  - amira / 123")
print("  - faten / 123")
print("  - (et tous les autres utilisateurs) / 123")
print()
