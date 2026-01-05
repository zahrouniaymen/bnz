# -*- coding: utf-8 -*-
"""Test login authentication"""
from backend.database import SessionLocal
from backend import models, auth

db = SessionLocal()

# Test authentication
username = "admin"
password = "123"

print(f"[TEST] Tentative de connexion avec: {username} / {password}")

user = db.query(models.User).filter(models.User.username == username).first()
if not user:
    print("[ERROR] Utilisateur non trouve!")
else:
    print(f"[OK] Utilisateur trouve: {user.username}")
    print(f"     Email: {user.email}")
    print(f"     Role: {user.role}")
    print(f"     Active: {user.active}")
    
    # Test password verification
    is_valid = auth.verify_password(password, user.password_hash)
    print(f"[TEST] Verification mot de passe: {is_valid}")
    
    if is_valid:
        print("[OK] Authentification reussie!")
    else:
        print("[ERROR] Mot de passe incorrect!")
        
        # Try to create a new hash and compare
        new_hash = auth.get_password_hash(password)
        print(f"[INFO] Nouveau hash genere pour test")
        is_valid_new = auth.verify_password(password, new_hash)
        print(f"[TEST] Verification avec nouveau hash: {is_valid_new}")

db.close()
