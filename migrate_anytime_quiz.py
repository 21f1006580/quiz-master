#!/usr/bin/env python3
"""
Migration script to add is_anytime_quiz column to quizzes table
"""

import sqlite3
import os

def migrate_anytime_quiz():
    """Add is_anytime_quiz column to quizzes table"""
    
    db_path = 'instance/quizmaster.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found. Please run the application first to create the database.")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(quizzes)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_anytime_quiz' in columns:
            print("✅ is_anytime_quiz column already exists")
            return True
        
        # Add the new column
        print("🔄 Adding is_anytime_quiz column to quizzes table...")
        cursor.execute("ALTER TABLE quizzes ADD COLUMN is_anytime_quiz BOOLEAN DEFAULT 0")
        
        # Commit changes
        conn.commit()
        print("✅ Successfully added is_anytime_quiz column")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(quizzes)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_anytime_quiz' in columns:
            print("✅ Column verification successful")
            return True
        else:
            print("❌ Column was not added successfully")
            return False
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🚀 Anytime Quiz Migration")
    print("=" * 30)
    
    success = migrate_anytime_quiz()
    
    if success:
        print("🎉 Migration completed successfully!")
        print("You can now create anytime quizzes in the admin panel.")
    else:
        print("❌ Migration failed. Please check the error messages above.") 