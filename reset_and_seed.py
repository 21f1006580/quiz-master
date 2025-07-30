#!/usr/bin/env python3
"""
Complete database reset and reseed script
"""

import os
import sqlite3
from app import create_app
from backend.models.models import db, User, Subject, Chapter, Quiz, Question, Score, create_admin_user
from datetime import datetime, timedelta

def reset_and_seed():
    app = create_app()
    with app.app_context():
        print("🗑️  Resetting database...")
        
        # Drop all tables
        db.drop_all()
        print("✅ All tables dropped")
        
        # Create all tables
        db.create_all()
        print("✅ All tables created")
        
        # Create admin user
        create_admin_user()
        print("✅ Admin user created")
        
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
        print("✅ Subjects created")
        
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
        print("✅ Chapters created")
        
        # Create quizzes
        now = datetime.utcnow()
        quizzes = [
            # Mathematics quizzes (Scheduled) - Available immediately for testing
            Quiz(title="Algebra Basics", chapter_id=1, date_of_quiz=now - timedelta(hours=1), time_duration=30, remarks="Basic algebraic concepts", is_anytime_quiz=False),
            Quiz(title="Calculus Fundamentals", chapter_id=2, date_of_quiz=now + timedelta(days=1), time_duration=45, remarks="Introduction to calculus", is_anytime_quiz=False),
            Quiz(title="Statistics Quiz", chapter_id=3, date_of_quiz=now + timedelta(days=2), time_duration=40, remarks="Probability and statistics", is_anytime_quiz=False),
            
            # Mathematics quizzes (Anytime)
            Quiz(title="Algebra Practice", chapter_id=1, date_of_quiz=now, time_duration=20, remarks="Practice algebra anytime", is_anytime_quiz=True),
            Quiz(title="Calculus Practice", chapter_id=2, date_of_quiz=now, time_duration=25, remarks="Practice calculus concepts", is_anytime_quiz=True),
            Quiz(title="Statistics Practice", chapter_id=3, date_of_quiz=now, time_duration=30, remarks="Practice statistics anytime", is_anytime_quiz=True),
            
            # Physics quizzes (Scheduled) - Available immediately for testing
            Quiz(title="Mechanics Test", chapter_id=4, date_of_quiz=now - timedelta(hours=1), time_duration=35, remarks="Newton's laws and energy", is_anytime_quiz=False),
            Quiz(title="Thermodynamics Quiz", chapter_id=5, date_of_quiz=now + timedelta(days=1), time_duration=30, remarks="Heat and energy transfer", is_anytime_quiz=False),
            Quiz(title="Electromagnetism", chapter_id=6, date_of_quiz=now + timedelta(days=2), time_duration=50, remarks="Electric and magnetic fields", is_anytime_quiz=False),
            
            # Physics quizzes (Anytime)
            Quiz(title="Mechanics Practice", chapter_id=4, date_of_quiz=now, time_duration=20, remarks="Practice mechanics anytime", is_anytime_quiz=True),
            Quiz(title="Physics Fundamentals", chapter_id=5, date_of_quiz=now, time_duration=25, remarks="Basic physics concepts", is_anytime_quiz=True),
            
            # Computer Science quizzes (Scheduled)
            Quiz(title="Programming Basics", chapter_id=7, date_of_quiz=now + timedelta(days=1), time_duration=25, remarks="Variables and control structures", is_anytime_quiz=False),
            Quiz(title="Data Structures", chapter_id=8, date_of_quiz=now + timedelta(days=2), time_duration=40, remarks="Arrays and linked lists", is_anytime_quiz=False),
            Quiz(title="Algorithm Analysis", chapter_id=9, date_of_quiz=now + timedelta(days=3), time_duration=45, remarks="Complexity and optimization", is_anytime_quiz=False),
            
            # Computer Science quizzes (Anytime)
            Quiz(title="Programming Practice", chapter_id=7, date_of_quiz=now, time_duration=15, remarks="Practice programming anytime", is_anytime_quiz=True),
            Quiz(title="Coding Fundamentals", chapter_id=8, date_of_quiz=now, time_duration=20, remarks="Basic coding concepts", is_anytime_quiz=True),
            Quiz(title="Algorithm Practice", chapter_id=9, date_of_quiz=now, time_duration=30, remarks="Practice algorithms anytime", is_anytime_quiz=True),
            
            # English Literature quizzes (Scheduled)
            Quiz(title="Shakespeare's Works", chapter_id=10, date_of_quiz=now + timedelta(days=1), time_duration=30, remarks="Famous plays and sonnets", is_anytime_quiz=False),
            Quiz(title="Modern Literature", chapter_id=11, date_of_quiz=now + timedelta(days=2), time_duration=35, remarks="20th century literature", is_anytime_quiz=False),
            Quiz(title="Poetry Analysis", chapter_id=12, date_of_quiz=now + timedelta(days=3), time_duration=30, remarks="Poetic devices and themes", is_anytime_quiz=False),
            
            # English Literature quizzes (Anytime)
            Quiz(title="Literature Practice", chapter_id=10, date_of_quiz=now, time_duration=20, remarks="Practice literature anytime", is_anytime_quiz=True),
            Quiz(title="Poetry Practice", chapter_id=12, date_of_quiz=now, time_duration=15, remarks="Practice poetry analysis", is_anytime_quiz=True)
        ]
        
        for quiz in quizzes:
            db.session.add(quiz)
        db.session.commit()
        print("✅ Quizzes created")
        
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
            (10, "What is the main theme of 'Romeo and Juliet'?", ["Love and fate", "War and peace", "Power and corruption", "Revenge"], 1),
            
            # Anytime Practice Quiz Questions
            
            # Algebra Practice questions
            (4, "What is the solution to x + 3 = 8?", ["x = 5", "x = 11", "x = 3", "x = 8"], 1),
            (4, "Simplify: 2(x + 1) + 3", ["2x + 5", "2x + 3", "2x + 1", "2x + 2"], 1),
            (4, "What is the slope of y = 3x + 2?", ["3", "2", "1", "0"], 1),
            
            # Calculus Practice questions
            (5, "What is the derivative of 3x²?", ["6x", "3x", "6x²", "3x²"], 1),
            (5, "What is the integral of 3x²?", ["x³ + C", "3x³ + C", "x² + C", "3x² + C"], 1),
            (5, "What is the limit of 1/x as x approaches ∞?", ["0", "1", "∞", "-∞"], 1),
            
            # Statistics Practice questions
            (6, "What is the mean of [2, 4, 6, 8, 10]?", ["6", "5", "7", "4"], 1),
            (6, "What is the median of [1, 2, 3, 4, 5, 6]?", ["3.5", "3", "4", "2.5"], 1),
            (6, "What is the mode of [1, 1, 2, 3, 3, 3]?", ["3", "1", "2", "No mode"], 1),
            
            # Mechanics Practice questions
            (10, "What is Newton's Second Law?", ["F = ma", "F = mg", "F = mv", "F = mgh"], 1),
            (10, "What is the unit of energy?", ["Joule", "Newton", "Watt", "Pascal"], 1),
            (10, "What is the formula for potential energy?", ["mgh", "½mv²", "ma", "mv"], 1),
            
            # Physics Fundamentals questions
            (11, "What is the SI unit of mass?", ["Kilogram", "Newton", "Meter", "Second"], 1),
            (11, "What is the SI unit of length?", ["Meter", "Centimeter", "Kilometer", "Inch"], 1),
            (11, "What is the SI unit of time?", ["Second", "Minute", "Hour", "Day"], 1),
            
            # Programming Practice questions
            (15, "What is a loop used for?", ["Repeating code", "Storing data", "Defining functions", "Handling errors"], 1),
            (15, "What is a variable?", ["Container for data", "Function", "Loop", "Condition"], 1),
            (15, "What is debugging?", ["Finding errors", "Writing code", "Running programs", "Documenting"], 1),
            
            # Coding Fundamentals questions
            (16, "What is an array?", ["Collection of elements", "Single value", "Function", "Loop"], 1),
            (16, "What is a function?", ["Reusable code block", "Data type", "Variable", "Operator"], 1),
            (16, "What is a string?", ["Text data", "Number data", "Boolean data", "Array data"], 1),
            
            # Algorithm Practice questions
            (17, "What is time complexity?", ["Algorithm efficiency", "Code length", "Memory usage", "Program speed"], 1),
            (17, "What is Big O notation?", ["Complexity measure", "Code style", "Data structure", "Programming language"], 1),
            (17, "What is a sorting algorithm?", ["Arranging data", "Searching data", "Storing data", "Deleting data"], 1),
            
            # Literature Practice questions
            (21, "What is a metaphor?", ["Comparison without 'like' or 'as'", "Direct comparison", "Sound device", "Rhyme scheme"], 1),
            (21, "What is a simile?", ["Comparison using 'like' or 'as'", "Direct comparison", "Sound device", "Rhyme scheme"], 1),
            (21, "What is alliteration?", ["Repetition of sounds", "Repetition of words", "Rhyme scheme", "Meter pattern"], 1),
            
            # Poetry Practice questions
            (22, "What is a stanza?", ["Group of lines", "Single line", "Rhyme scheme", "Meter pattern"], 1),
            (22, "What is a rhyme scheme?", ["Pattern of rhymes", "Number of lines", "Meter pattern", "Poem length"], 1),
            (22, "What is free verse?", ["No regular meter or rhyme", "Regular meter", "Regular rhyme", "Fixed form"], 1)
        ]
        
        for quiz_id, statement, options, correct_option in questions_data:
            question = Question(
                quiz_id=quiz_id,
                question_statement=statement,
                option1=options[0],
                option2=options[1],
                option3=options[2],
                option4=options[3],
                correct_option=correct_option
            )
            db.session.add(question)
        
        db.session.commit()
        print("✅ Questions created")
        
        print("\n🎉 Database reset and reseeded successfully!")
        print(f"📚 Created {len(subjects)} subjects")
        print(f"📖 Created {len(chapters)} chapters")
        print(f"📝 Created {len(quizzes)} quizzes (including anytime quizzes)")
        print(f"❓ Created {len(questions_data)} questions")
        print("🎯 Anytime quizzes available for immediate testing!")

if __name__ == "__main__":
    reset_and_seed() 