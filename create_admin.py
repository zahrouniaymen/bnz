# -*- coding: utf-8 -*-
from backend.database import SessionLocal
from backend import models
from passlib.context import CryptContext

# Use the same hashing as auth.py
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

db = SessionLocal()

# Delete ALL existing users to start fresh
print("[INFO] Suppression de tous les utilisateurs...")
db.query(models.User).delete()
db.commit()
print("[OK] Tous les utilisateurs supprimes")

# Create new admin with password "123"
admin = models.User(
    username="admin",
    email="admin@m54.com",
    password_hash=pwd_context.hash("123"),
    role="admin",
    full_name="Administrator",
    department="Direction",
    active=True
)
db.add(admin)
db.commit()
print("[OK] Nouvel utilisateur admin cree!")
print("   Username: admin")
print("   Password: 123")

db.close()
