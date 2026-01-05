import sqlite3
from passlib.context import CryptContext

# Initialize password hasher (same as backend)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Connect to database
conn = sqlite3.connect('backend/sql_app.db')
cursor = conn.cursor()

print("=== NETTOYAGE DES UTILISATEURS ===\n")

# Delete all users
cursor.execute("DELETE FROM users")
print("[OK] Tous les anciens utilisateurs supprimes")

# Create new admin user with password "123"
hashed_password = pwd_context.hash("123")
cursor.execute("""
    INSERT INTO users (username, email, password_hash, role, full_name, active, created_at)
    VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
""", ("admin", "admin@benozzi.com", hashed_password, "admin", "Administrator", 1))

print("[OK] Nouvel utilisateur admin cree")
print("     Username: admin")
print("     Password: 123")
print("     Role: admin")

conn.commit()
conn.close()

print("\n=== TERMINE ===")
print("\nVous pouvez maintenant vous connecter avec:")
print("  Username: admin")
print("  Password: 123")
