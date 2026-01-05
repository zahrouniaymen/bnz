import sys
import os
from sqlalchemy import create_all
from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine
from backend import models, schemas
from pydantic import ValidationError

def test_serialization():
    db = SessionLocal()
    try:
        clients = db.query(models.Client).all()
        print(f"Total clients in DB: {len(clients)}")
        
        success_count = 0
        fail_count = 0
        
        for client in clients:
            try:
                # Manually trigger Pydantic validation as FastAPI would
                client_data = schemas.Client.model_validate(client)
                success_count += 1
            except ValidationError as e:
                fail_count += 1
                if fail_count <= 5:
                    print(f"Validation Error for client {client.id}: {e}")
            except Exception as e:
                fail_count += 1
                if fail_count <= 5:
                    print(f"General Error for client {client.id}: {e}")
                    
        print(f"Successfully validated: {success_count}")
        print(f"Failed to validate: {fail_count}")
        
    finally:
        db.close()

if __name__ == "__main__":
    # Ensure BASE_DIR is handled if database.py uses it
    test_serialization()
