from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os

# Use absolute path to ensure consistency regardless of execution directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "sql_app.db")).replace('\\', '/')
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

print(f"DATABASE CONNECTED TO: {DB_PATH}")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
