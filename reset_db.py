#!/usr/bin/env python3
"""
Database reset script for Quiz Master application
"""

import os
from app import create_app
from backend.models.models import db

def reset_database():
    """Reset the database and recreate it"""
    app = create_app()
    
    with app.app_context():
        print("🗑️  Dropping all tables...")
        db.drop_all()
        
        print("🏗️  Creating all tables...")
        db.create_all()
        
        print("✅ Database reset complete!")
        print("📝 Run 'python seed_data.py' to populate with sample data")

if __name__ == "__main__":
    # Remove the database file if it exists
    db_file = "quizmaster.db"
    if os.path.exists(db_file):
        print(f"🗑️  Removing existing database: {db_file}")
        os.remove(db_file)
    
    reset_database() 