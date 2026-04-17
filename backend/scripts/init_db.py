import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.db.session import engine, Base
from app.db.models import *  # Import all models to ensure they are registered
from app.db.seed import seed_data
from app.db.session import SessionLocal

def init_db():
    print("Connecting to database and creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")
    
    db = SessionLocal()
    try:
        print("Seeding initial data...")
        seed_data(db)
        print("Seeding complete.")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
