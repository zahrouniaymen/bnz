import sqlite3

conn = sqlite3.connect('backend/sql_app.db')
cursor = conn.cursor()

cursor.execute('SELECT username, role, email FROM users')
users = cursor.fetchall()

print("=== UTILISATEURS DANS LA BASE ===\n")
for username, role, email in users:
    print(f"Username: {username}")
    print(f"Role: {role}")
    print(f"Email: {email}")
    print("---")

conn.close()

print("\nESSAYEZ DE VOUS CONNECTER AVEC L'UN DE CES UTILISATEURS")
print("Le mot de passe par defaut est generalement: 'password' ou 'admin'")
