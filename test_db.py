#!/usr/bin/env python3
"""Simple database test script"""

from app import create_app
from backend.models.models import User, Subject, Chapter, Quiz, Question

def test_database():
    app = create_app()
    
    with app.app_context():
        # Check admin user
        admin = User.query.filter_by(is_admin=True).first()
        print(f"✅ Admin user found: {admin.user_name if admin else 'No admin found'}")
        
        # Check sample data
        subjects = Subject.query.count()
        chapters = Chapter.query.count()
        quizzes = Quiz.query.count()
        questions = Question.query.count()
        
        print(f"✅ Database contains:")
        print(f"   - {subjects} subjects")
        print(f"   - {chapters} chapters")
        print(f"   - {quizzes} quizzes")
        print(f"   - {questions} questions")
        
        # Check regular users
        users = User.query.filter_by(is_admin=False).count()
        print(f"   - {users} regular users")

if __name__ == "__main__":
    test_database() 