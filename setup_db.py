# setup_db.py
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.base import Base
from app.db.session import engine

def init_database():
    try:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        print(f"📁 Database file created at: {Path('inventory.db').absolute()}")
    except Exception as e:
        print(f"❌ Error creating database: {e}")

if __name__ == "__main__":
    init_database()