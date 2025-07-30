#!/usr/bin/env python3
"""
Database initialization script for Quiz Master application
"""

import os
import sys
from app import create_app
from backend.models.models import db, create_admin_user

def init_database():
    """Initialize database with tables and seed data"""
    app = create_app()
    
    with app.app_context():
        print("🗄️  Initializing database...")
        
        # Create all tables
        print("📋 Creating database tables...")
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Create admin user
        print("👤 Creating admin user...")
        create_admin_user()
        print("✅ Admin user created successfully!")
        
        # Check if we need to seed data
        from backend.models.models import User, Subject, Chapter, Quiz, Question
        
        # Check if subjects exist
        subjects_count = Subject.query.count()
        if subjects_count == 0:
            print("🌱 No sample data found. Running seed script...")
            try:
                # Import and run seed data
                from seed_data import seed_data
                seed_data()
                print("✅ Sample data seeded successfully!")
            except Exception as e:
                print(f"⚠️  Warning: Could not seed sample data: {e}")
                print("You can manually run: python seed_data.py")
        else:
            print(f"✅ Database already contains {subjects_count} subjects")
        
        print("🎉 Database initialization complete!")
        print("📊 Database contains:")
        print(f"   - Users: {User.query.count()}")
        print(f"   - Subjects: {Subject.query.count()}")
        print(f"   - Chapters: {Chapter.query.count()}")
        print(f"   - Quizzes: {Quiz.query.count()}")
        print(f"   - Questions: {Question.query.count()}")

def check_database():
    """Check database status"""
    app = create_app()
    
    with app.app_context():
        try:
            # Test database connection
            db.session.execute(db.text('SELECT 1'))
            print("✅ Database connection successful")
            
            # Check if tables exist
            from backend.models.models import User, Subject
            users_count = User.query.count()
            subjects_count = Subject.query.count()
            
            print(f"📊 Database status:")
            print(f"   - Users: {users_count}")
            print(f"   - Subjects: {subjects_count}")
            
            if users_count == 0:
                print("⚠️  No users found. Run: python init_db.py")
            elif subjects_count == 0:
                print("⚠️  No subjects found. Run: python seed_data.py")
            else:
                print("✅ Database is properly initialized")
                
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False
    
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        check_database()
    else:
        init_database() 