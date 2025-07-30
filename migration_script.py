# migration_script.py - Run this to fix your existing database
# Place this in your project root and run: python migration_script.py

import sqlite3
import os
from datetime import datetime

def migrate_database():
    # Path to your database file
    db_path = 'quizmaster.db'
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found! Creating new database...")
        # If no database exists, Flask will create it with the correct schema
        return
    
    print("Found existing database. Starting migration...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check what tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = [row[0] for row in cursor.fetchall()]
        print(f"Existing tables: {existing_tables}")
        
        # Check if quiz table exists and what it looks like
        if 'quiz' in existing_tables:
            cursor.execute("PRAGMA table_info(quiz)")
            columns = [col[1] for col in cursor.fetchall()]
            print(f"Quiz table columns: {columns}")
            
            # Add missing columns to quiz table
            new_columns = [
                ('end_date_time', 'DATETIME'),
                ('allow_multiple_attempts', 'BOOLEAN DEFAULT 0'),
                ('show_results_immediately', 'BOOLEAN DEFAULT 1'),
                ('auto_start', 'BOOLEAN DEFAULT 1'),
                ('auto_end', 'BOOLEAN DEFAULT 1')
            ]
            
            for col_name, col_def in new_columns:
                if col_name not in columns:
                    try:
                        cursor.execute(f"ALTER TABLE quiz ADD COLUMN {col_name} {col_def}")
                        print(f"Added column {col_name} to quiz table")
                    except Exception as e:
                        print(f"Could not add column {col_name}: {e}")
            
            # Update existing records with default values
            cursor.execute("""
                UPDATE quiz SET 
                    allow_multiple_attempts = 0,
                    show_results_immediately = 1,
                    auto_start = 1,
                    auto_end = 1
                WHERE allow_multiple_attempts IS NULL
            """)
            
            # Handle time_duration conversion from HH:MM to minutes
            cursor.execute("SELECT quiz_id, time_duration FROM quiz")
            quizzes = cursor.fetchall()
            
            for quiz_id, time_duration in quizzes:
                if time_duration and ':' in str(time_duration):
                    try:
                        hours, minutes = map(int, str(time_duration).split(':'))
                        total_minutes = hours * 60 + minutes
                        cursor.execute("UPDATE quiz SET time_duration = ? WHERE quiz_id = ?", 
                                     (total_minutes, quiz_id))
                        print(f"Converted quiz {quiz_id} duration: {time_duration} → {total_minutes} minutes")
                    except Exception as e:
                        print(f"Could not convert duration for quiz {quiz_id}: {e}")
        
        # Check if we need to rename quiz table to quizzes
        if 'quiz' in existing_tables and 'quizzes' not in existing_tables:
            cursor.execute("ALTER TABLE quiz RENAME TO quizzes")
            print("Renamed 'quiz' table to 'quizzes'")
        
        # Check if we need to rename chapter table to chapters  
        if 'chapter' in existing_tables and 'chapters' not in existing_tables:
            cursor.execute("ALTER TABLE chapter RENAME TO chapters")
            print("Renamed 'chapter' table to 'chapters'")
            
        # Check if we need to rename subject table to subjects
        if 'subject' in existing_tables and 'subjects' not in existing_tables:
            cursor.execute("ALTER TABLE subject RENAME TO subjects")
            print("Renamed 'subject' table to 'subjects'")
            
        # Check if we need to rename question table to questions
        if 'question' in existing_tables and 'questions' not in existing_tables:
            cursor.execute("ALTER TABLE question RENAME TO questions")
            print("Renamed 'question' table to 'questions'")
            
        # Check if we need to rename user table to users
        if 'user' in existing_tables and 'users' not in existing_tables:
            cursor.execute("ALTER TABLE user RENAME TO users")
            print("Renamed 'user' table to 'users'")
            
        # Check if we need to rename score table to scores
        if 'score' in existing_tables and 'scores' not in existing_tables:
            cursor.execute("ALTER TABLE score RENAME TO scores")
            print("Renamed 'score' table to 'scores'")
        
        conn.commit()
        print("✅ Database migration completed successfully!")
        
        # Show final table structure
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        final_tables = [row[0] for row in cursor.fetchall()]
        print(f"Final tables: {final_tables}")
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        conn.rollback()
        
        # If migration fails, let's at least check the current state
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Current tables after error: {tables}")
        
    finally:
        conn.close()

def backup_database():
    """Create a backup of the database before migration"""
    db_path = 'quizmaster.db'
    if os.path.exists(db_path):
        backup_path = f'quizmaster_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        return backup_path
    return None

if __name__ == "__main__":
    print("Starting database migration...")
    
    # Create backup first
    backup_file = backup_database()
    if backup_file:
        print(f"Backup created: {backup_file}")
    
    # Run migration
    migrate_database()
    
    print("\nMigration complete! You can now restart your Flask application.")