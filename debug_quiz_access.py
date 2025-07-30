#!/usr/bin/env python3
"""
Debug script to test quiz access
"""

from app import create_app
from backend.models.models import db, User, Quiz, Question, Score
from datetime import datetime

def debug_quiz_access():
    app = create_app()
    with app.app_context():
        print("🔍 Debugging Quiz Access...")
        
        # Check if quiz exists
        quiz = Quiz.query.get(11)
        if not quiz:
            print("❌ Quiz ID 11 does not exist!")
            return
        
        print(f"✅ Quiz ID 11 exists: {quiz.title}")
        print(f"   - Anytime quiz: {quiz.is_anytime_quiz}")
        print(f"   - Active: {quiz.is_active}")
        print(f"   - Questions: {len(quiz.questions)}")
        
        # Check questions
        questions = Question.query.filter_by(quiz_id=11).all()
        print(f"   - Questions found: {len(questions)}")
        for i, q in enumerate(questions[:3]):  # Show first 3
            print(f"     {i+1}. {q.question_statement[:50]}...")
        
        # Check if admin user exists
        admin = User.query.filter_by(user_name="admin@gmail.com").first()
        if not admin:
            print("❌ Admin user not found!")
            return
        
        print(f"✅ Admin user found: {admin.full_name}")
        
        # Check if admin has attempted this quiz
        existing_score = Score.query.filter_by(
            quiz_id=11,
            user_id=admin.user_id
        ).first()
        
        if existing_score:
            print(f"❌ Admin has already attempted quiz 11")
            print(f"   - Score: {existing_score.correct_answers}/{existing_score.total_questions}")
            print(f"   - Percentage: {existing_score.total_score}%")
        else:
            print("✅ Admin has not attempted quiz 11")
        
        # Test quiz availability
        is_available, message = quiz.is_available_for_attempt(admin.user_id)
        print(f"   - Available: {is_available}")
        print(f"   - Message: {message}")
        
        # Check quiz status
        print(f"   - Status: {quiz.get_status()}")
        print(f"   - Expired: {quiz.is_expired()}")
        print(f"   - Time remaining: {quiz.get_time_remaining()} minutes")

if __name__ == "__main__":
    debug_quiz_access() 