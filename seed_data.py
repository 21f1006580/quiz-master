#!/usr/bin/env python3
"""
Seed data script for Quiz Master application
"""

from app import create_app
from backend.models.models import db, User, Subject, Chapter, Quiz, Question, Score, create_admin_user
from datetime import datetime, timedelta

def seed_data():
    app = create_app()
    with app.app_context():
        # Create admin user first
        create_admin_user()
        
        # Clear existing data (except admin user)
        Question.query.delete()
        Quiz.query.delete()
        Chapter.query.delete()
        Subject.query.delete()
        Score.query.delete()
        
        # Create subjects
        subjects = [
            Subject(name="Mathematics", description="Advanced mathematics including algebra, calculus, and statistics"),
            Subject(name="Physics", description="Classical mechanics, thermodynamics, and modern physics"),
            Subject(name="Computer Science", description="Programming, algorithms, and data structures"),
            Subject(name="English Literature", description="Classic and modern literature analysis")
        ]
        
        for subject in subjects:
            db.session.add(subject)
        db.session.commit()
        
        # Create chapters
        chapters = [
            # Mathematics chapters
            Chapter(name="Algebra", description="Linear equations, polynomials, and matrices", subject_id=1),
            Chapter(name="Calculus", description="Derivatives, integrals, and limits", subject_id=1),
            Chapter(name="Statistics", description="Probability, distributions, and hypothesis testing", subject_id=1),
            
            # Physics chapters
            Chapter(name="Mechanics", description="Newton's laws, energy, and momentum", subject_id=2),
            Chapter(name="Thermodynamics", description="Heat, work, and entropy", subject_id=2),
            Chapter(name="Electromagnetism", description="Electric and magnetic fields", subject_id=2),
            
            # Computer Science chapters
            Chapter(name="Programming Fundamentals", description="Variables, loops, and functions", subject_id=3),
            Chapter(name="Data Structures", description="Arrays, linked lists, and trees", subject_id=3),
            Chapter(name="Algorithms", description="Sorting, searching, and optimization", subject_id=3),
            
            # English Literature chapters
            Chapter(name="Shakespeare", description="Hamlet, Macbeth, and sonnets", subject_id=4),
            Chapter(name="Modern Literature", description="20th century novels and poetry", subject_id=4),
            Chapter(name="Poetry Analysis", description="Metaphor, symbolism, and form", subject_id=4)
        ]
        
        for chapter in chapters:
            db.session.add(chapter)
        db.session.commit()
        
        # Create quizzes
        now = datetime.utcnow()
        quizzes = [
            # Mathematics quizzes
            Quiz(title="Algebra Basics", chapter_id=1, date_of_quiz=now + timedelta(days=1), time_duration=30, remarks="Basic algebraic concepts"),
            Quiz(title="Calculus Fundamentals", chapter_id=2, date_of_quiz=now + timedelta(days=2), time_duration=45, remarks="Introduction to calculus"),
            Quiz(title="Statistics Quiz", chapter_id=3, date_of_quiz=now + timedelta(days=3), time_duration=40, remarks="Probability and statistics"),
            
            # Physics quizzes
            Quiz(title="Mechanics Test", chapter_id=4, date_of_quiz=now + timedelta(days=1), time_duration=35, remarks="Newton's laws and energy"),
            Quiz(title="Thermodynamics Quiz", chapter_id=5, date_of_quiz=now + timedelta(days=2), time_duration=30, remarks="Heat and energy transfer"),
            Quiz(title="Electromagnetism", chapter_id=6, date_of_quiz=now + timedelta(days=3), time_duration=50, remarks="Electric and magnetic fields"),
            
            # Computer Science quizzes
            Quiz(title="Programming Basics", chapter_id=7, date_of_quiz=now + timedelta(days=1), time_duration=25, remarks="Variables and control structures"),
            Quiz(title="Data Structures", chapter_id=8, date_of_quiz=now + timedelta(days=2), time_duration=40, remarks="Arrays and linked lists"),
            Quiz(title="Algorithm Analysis", chapter_id=9, date_of_quiz=now + timedelta(days=3), time_duration=45, remarks="Complexity and optimization"),
            
            # English Literature quizzes
            Quiz(title="Shakespeare's Works", chapter_id=10, date_of_quiz=now + timedelta(days=1), time_duration=30, remarks="Famous plays and sonnets"),
            Quiz(title="Modern Literature", chapter_id=11, date_of_quiz=now + timedelta(days=2), time_duration=35, remarks="20th century literature"),
            Quiz(title="Poetry Analysis", chapter_id=12, date_of_quiz=now + timedelta(days=3), time_duration=30, remarks="Poetic devices and themes")
        ]
        
        for quiz in quizzes:
            db.session.add(quiz)
        db.session.commit()
        
        # Create questions for each quiz
        questions_data = [
            # Algebra Basics questions
            (1, "What is the solution to 2x + 5 = 13?", ["x = 4", "x = 8", "x = 6", "x = 3"], 1),
            (1, "Simplify: 3(x + 2) - 2x", ["x + 6", "x + 2", "3x + 6", "x + 4"], 1),
            (1, "What is the slope of the line y = 2x + 3?", ["2", "3", "1", "0"], 1),
            (1, "Solve: x² - 4 = 0", ["x = ±2", "x = 2", "x = -2", "x = 0"], 1),
            (1, "What is the y-intercept of y = -3x + 7?", ["7", "-3", "3", "-7"], 1),
            
            # Calculus Fundamentals questions
            (2, "What is the derivative of x²?", ["2x", "x", "2x²", "x²"], 1),
            (2, "What is the integral of 2x?", ["x² + C", "2x² + C", "x + C", "2x + C"], 1),
            (2, "What is the limit of x² as x approaches 2?", ["4", "2", "0", "∞"], 1),
            (2, "What is the derivative of sin(x)?", ["cos(x)", "sin(x)", "-cos(x)", "-sin(x)"], 1),
            (2, "What is the integral of cos(x)?", ["sin(x) + C", "cos(x) + C", "-sin(x) + C", "-cos(x) + C"], 1),
            
            # Statistics Quiz questions
            (3, "What is the mean of [1, 2, 3, 4, 5]?", ["3", "2.5", "4", "2"], 1),
            (3, "What is the median of [1, 3, 5, 7, 9]?", ["5", "3", "7", "4"], 1),
            (3, "What is the mode of [1, 2, 2, 3, 4]?", ["2", "1", "3", "4"], 1),
            (3, "What is the standard deviation of [1, 1, 1, 1, 1]?", ["0", "1", "0.5", "2"], 1),
            (3, "What is the probability of rolling a 6 on a fair die?", ["1/6", "1/3", "1/2", "1/4"], 1),
            
            # Mechanics Test questions
            (4, "What is Newton's First Law about?", ["Inertia", "Force", "Action-Reaction", "Gravity"], 1),
            (4, "What is the formula for kinetic energy?", ["½mv²", "mgh", "mv", "ma"], 1),
            (4, "What is the SI unit of force?", ["Newton", "Joule", "Watt", "Pascal"], 1),
            (4, "What is the acceleration due to gravity on Earth?", ["9.8 m/s²", "10 m/s²", "9.5 m/s²", "9.9 m/s²"], 1),
            (4, "What is the formula for momentum?", ["mv", "ma", "mgh", "½mv²"], 1),
            
            # Programming Basics questions
            (7, "What is a variable?", ["A container for data", "A function", "A loop", "A condition"], 1),
            (7, "What is the purpose of a loop?", ["Repeat code", "Store data", "Define functions", "Handle errors"], 1),
            (7, "What is a function?", ["Reusable code block", "Data type", "Variable", "Operator"], 1),
            (7, "What is an array?", ["Collection of elements", "Single value", "Function", "Loop"], 1),
            (7, "What is debugging?", ["Finding and fixing errors", "Writing code", "Running programs", "Documenting code"], 1),
            
            # Shakespeare's Works questions
            (10, "Who wrote 'Hamlet'?", ["William Shakespeare", "Charles Dickens", "Jane Austen", "Mark Twain"], 1),
            (10, "What is the famous quote from Hamlet?", ["'To be or not to be'", "'Romeo, Romeo'", "'Macbeth'", "'Othello'"], 1),
            (10, "What is a sonnet?", ["14-line poem", "10-line poem", "20-line poem", "Free verse"], 1),
            (10, "What is the setting of 'Macbeth'?", ["Scotland", "England", "France", "Italy"], 1),
            (10, "What is the main theme of 'Romeo and Juliet'?", ["Love and fate", "War and peace", "Power and corruption", "Revenge"], 1)
        ]
        
        for quiz_id, statement, options, correct in questions_data:
            question = Question(
                quiz_id=quiz_id,
                question_statement=statement,
                option1=options[0],
                option2=options[1],
                option3=options[2],
                option4=options[3],
                correct_option=correct
            )
            db.session.add(question)
        
        db.session.commit()
        print("✅ Sample data seeded successfully!")
        print(f"📚 Created {len(subjects)} subjects")
        print(f"📖 Created {len(chapters)} chapters")
        print(f"📝 Created {len(quizzes)} quizzes")
        print(f"❓ Created {len(questions_data)} questions")

if __name__ == "__main__":
    seed_data() 