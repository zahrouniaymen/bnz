import requests
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Add backend to path
sys.path.append(os.getcwd())
import backend.models as models
from backend.database import Base

# Setup DB connection (Absolute path as fixed)
SQLALCHEMY_DATABASE_URL = "sqlite:///C:/Users/HP STORE/Desktop/M54/backend/sql_app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def run_test():
    print("1. Creating/Updating Test User...")
    user = db.query(models.User).filter(models.User.username == "test_debug").first()
    if not user:
        user = models.User(
            username="test_debug", 
            email="test_debug@example.com",
            role="admin",
            full_name="Debug User"
        )
        db.add(user)
    
    user.password_hash = pwd_context.hash("debug123")
    user.active = True
    db.commit()
    print("   User 'test_debug' ready.")

    print("\n2. Logging in via API (http://localhost:8003/auth/login)...")
    try:
        response = requests.post(
            "http://localhost:8003/auth/login",
            data={"username": "test_debug", "password": "debug123"}
        )
    except Exception as e:
        print(f"FAILED to connect to server: {e}")
        return

    if response.status_code != 200:
        print(f"FAILED to login: {response.status_code} {response.text}")
        return
    
    token = response.json()["access_token"]
    print("   Login Successful. Got Token.")

    print("\n3. Fetching Analytics Data (2024)...")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get("http://localhost:8003/analytics/monthly-evolution/2024", headers=headers)
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"   SUCCESS! Response Code: 200")
        january = next((m for m in data if m['month'] == 'January' or m['month'] == '01'), None)
        print(f"   Sample Data (Jan): {january}")
        
        non_zero = [m for m in data if m['requests'] > 0]
        print(f"   Months with data: {len(non_zero)} / 12")
        if len(non_zero) > 1:
            print("   VERDICT: SYSTEM IS WORKING PERFECTLY.")
        else:
            print("   VERDICT: DATA IS STILL EMPTY/WRONG.")
            
    else:
        print(f"FAILED to get analytics: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    run_test()
