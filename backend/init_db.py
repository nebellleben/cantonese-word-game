"""
Database initialization script.
Run this script to create the database tables and initialize default data.
"""
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.db.base import init_db

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialization complete!")

