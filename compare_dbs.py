from sqlalchemy import create_engine, text
import os

def check_db(path):
    if not os.path.exists(path):
        return f"{path}: NOT FOUND"
    try:
        engine = create_engine(f"sqlite:///{path}")
        with engine.connect() as conn:
            offers = conn.execute(text("SELECT COUNT(*) FROM offers")).scalar()
            clients = conn.execute(text("SELECT COUNT(*) FROM clients")).scalar()
            return f"{path}: {offers} offers, {clients} clients"
    except Exception as e:
        return f"{path}: Error - {e}"

print("Checking databases...")
print(check_db("sql_app.db"))
print(check_db("backend/sql_app.db"))
