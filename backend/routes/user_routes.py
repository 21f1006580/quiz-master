# routes/user_routes.py 

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.models import db, User, Subject, Chapter, Quiz, Question, Score
from datetime import datetime, timedelta
from sqlalchemy import func

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

@user_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def user_dashboard():
    """Get user dashboard data with subjects"""
    try:
        user_name = get_jwt_identity()
        user = User.query.filter_by(user_name=user_name).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get active subjects with chapter and quiz counts
        subjects = Subject.query.filter_by(is_active=True).all()
        subject_list = []
        
        for subj in subjects:
            # Count chapters and available quizzes for this subject
            chapter_count = Chapter.query.filter_by(subject_id=subj.subject_id).count()
            
            # Count quizzes that are currently available (date <= now)
            available_quizzes = db.session.query(Quiz).join(Chapter).filter(
                Chapter.subject_id == subj.subject_id,
                Quiz.is_active == True,
                Quiz.date_of_quiz <= datetime.utcnow()
            ).count()
            
            subject_list.append({
                'id': subj.subject_id,
                'name': subj.name,
                'description': subj.description,
                'chapter_count': chapter_count,
                'available_quizzes': available_quizzes
            })

        return jsonify({'subjects': subject_list}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile and stats"""
    try:
        user_name = get_jwt_identity()
        user = User.query.filter_by(user_name=user_name).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Calculate user stats
        scores = Score.query.filter_by(user_id=user.user_id).all()
        total_attempts = len(scores)
        
        if total_attempts > 0:
            total_score = sum([s.total_score for s in scores])
            average_score = round(total_score / total_attempts, 2)
            best_score = max([s.total_score for s in scores])
            recent_attempts = len([s for s in scores if s.attempt_datetime >= datetime.utcnow() - timedelta(days=7)])
        else:
            average_score = 0
            best_score = 0
            recent_attempts = 0

        return jsonify({
            'user': user.to_dict(),
            'stats': {
                'quizzes_attempted': total_attempts,
                'average_score': average_score,
                'recent_attempts': recent_attempts,
                'best_score': best_score
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/subjects/<int:subject_id>/quizzes', methods=['GET'])
@jwt_required()
def get_quizzes_by_subject(subject_id):
    """Get all available quizzes for a subject"""
    try:
        print("Inside get all quiz functions")
        user_name = get_jwt_identity()
        user = User.query.filter_by(user_name=user_name).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get subject
        subject = Subject.query.get_or_404(subject_id)
        
        # Get chapters for this subject
        chapters = Chapter.query.filter_by(subject_id=subject_id).all()
        quiz_list = []
        print(subject,chapters)

        for chapter in chapters:
            for quiz in chapter.quizzes:
                # Check if user has already attempted this quiz
                user_score = Score.query.filter_by(
                    user_id=user.user_id, 
                    quiz_id=quiz.quiz_id
                ).first()
                
                # Get question count
                question_count = Question.query.filter_by(quiz_id=quiz.quiz_id).count()
                print(f"Question count {question_count}")
                
                quiz_data = {
                    'quiz_id': quiz.quiz_id,
                    'title': quiz.title,
                    'chapter_name': chapter.name,
                    'chapter_id': chapter.chapter_id,
                    'date_of_quiz': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
                    'time_duration': quiz.time_duration,
                    'remarks': quiz.remarks,
                    'question_count': question_count,
                    'is_active': quiz.is_active,
                    'attempted': user_score is not None,
                    'user_score': user_score.total_score if user_score else None,
                    'attempt_date': user_score.attempt_datetime.isoformat() if user_score else None
                }
                quiz_list.append(quiz_data)

        return jsonify({
            'subject': subject.to_dict(),
            'quizzes': quiz_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# In your user_routes.py - Update the route to match frontend expectation

@user_bp.route('/quiz/<int:quiz_id>/take', methods=['GET'])
@jwt_required()
def start_quiz(quiz_id):
    """Start a quiz attempt - get quiz details and questions"""
    try:
        print(f"=== START QUIZ ENDPOINT HIT ===")
        print(f"Quiz ID: {quiz_id}")
        
        user_name = get_jwt_identity()
        print(f"User: {user_name}")
        
        user = User.query.filter_by(user_name=user_name).first()
        if not user:
            print("ERROR: User not found")
            return jsonify({'error': 'User not found'}), 404

        quiz = Quiz.query.get(quiz_id)  # Use .get() instead of .get_or_404() for better error handling
        if not quiz:
            print(f"ERROR: Quiz {quiz_id} not found")
            return jsonify({'error': 'Quiz not found'}), 404
            
        print(f"Quiz found: {quiz.title}")
        
        # Check if quiz is active
        if not quiz.is_active:
            print(f"ERROR: Quiz {quiz_id} is not active")
            return jsonify({'error': 'This quiz is not available'}), 403
        
        # Check if user has already attempted this quiz
        existing_score = Score.query.filter_by(
            user_id=user.user_id, 
            quiz_id=quiz_id
        ).first()
        
        if existing_score:
            print(f"ERROR: User {user.user_name} already attempted quiz {quiz_id}")
            return jsonify({'error': 'You have already attempted this quiz'}), 403
        
        # Get questions for this quiz
        questions = Question.query.filter_by(quiz_id=quiz.quiz_id).all()
        print(f"Found {len(questions)} questions for quiz {quiz_id}")
        
        if not questions:
            print(f"ERROR: No questions found for quiz {quiz_id}")
            return jsonify({'error': 'No questions available for this quiz'}), 404

        question_data = []
        for q in questions:
            options = [q.option1, q.option2]
            if q.option3:
                options.append(q.option3)
            if q.option4:
                options.append(q.option4)
                
            question_data.append({
                'id': q.question_id,
                'statement': q.question_statement,
                'options': options
            })

        response_data = {
            'quiz_id': quiz.quiz_id,
            'title': quiz.title,
            'duration': quiz.time_duration,
            'total_questions': len(questions),
            'questions': question_data,
            'chapter_name': quiz.chapter.name if quiz.chapter else None,
            'subject_name': quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else None
        }
        
        print(f"SUCCESS: Returning quiz data with {len(question_data)} questions")
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"EXCEPTION in start_quiz: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
@jwt_required()
def submit_quiz(quiz_id):
    """Submit quiz answers and calculate score"""
    try:
        data = request.get_json()
        user_answers = data.get('answers', {})  # format: {question_id: selected_option_index}
        time_taken = data.get('time_taken', 0)  # time in seconds

        user_name = get_jwt_identity()
        user = User.query.filter_by(user_name=user_name).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        quiz = Quiz.query.get_or_404(quiz_id)
        
        # Check if user has already attempted this quiz
        existing_score = Score.query.filter_by(
            user_id=user.user_id, 
            quiz_id=quiz_id
        ).first()
        
        if existing_score:
            return jsonify({'error': 'You have already attempted this quiz'}), 403

        # Get all questions for this quiz
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        if not questions:
            return jsonify({'error': 'No questions found for this quiz'}), 404

        # Calculate score
        total_questions = len(questions)
        correct_answers = 0
        detailed_results = []

        for question in questions:
            question_id = str(question.question_id)
            user_answer_index = user_answers.get(question_id)
            
            # Check if answer is correct
            is_correct = False
            if user_answer_index is not None:
                # Convert 0-based index to 1-based option number
                user_option = user_answer_index + 1
                is_correct = (user_option == question.correct_option)
                if is_correct:
                    correct_answers += 1
            
            detailed_results.append({
                'question_id': question.question_id,
                'question_text': question.question_statement,
                'correct_option': question.correct_option,
                'user_answer': user_answer_index + 1 if user_answer_index is not None else None,
                'is_correct': is_correct
            })

        # Calculate percentage score
        percentage_score = round((correct_answers / total_questions) * 100, 2) if total_questions > 0 else 0
        
        # Save score to database
        score_entry = Score(
            quiz_id=quiz_id,
            user_id=user.user_id,
            total_questions=total_questions,
            correct_answers=correct_answers,
            total_score=percentage_score,
            time_taken=time_taken
        )
        
        db.session.add(score_entry)
        db.session.commit()

        return jsonify({
            'message': 'Quiz submitted successfully',
            'score': {
                'total_questions': total_questions,
                'correct_answers': correct_answers,
                'percentage_score': percentage_score,
                'time_taken': time_taken,
                'detailed_results': detailed_results
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/scores', methods=['GET'])
@jwt_required()
def get_user_scores():
    """Get user's quiz attempt history"""
    try:
        user_name = get_jwt_identity()
        user = User.query.filter_by(user_name=user_name).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get scores with quiz details
        scores = db.session.query(Score, Quiz, Chapter, Subject).join(
            Quiz, Score.quiz_id == Quiz.quiz_id
        ).join(
            Chapter, Quiz.chapter_id == Chapter.chapter_id
        ).join(
            Subject, Chapter.subject_id == Subject.subject_id
        ).filter(
            Score.user_id == user.user_id
        ).order_by(Score.attempt_datetime.desc()).all()

        result = []
        for score, quiz, chapter, subject in scores:
            result.append({
                'score_id': score.score_id,
                'quiz_id': score.quiz_id,
                'quiz_title': quiz.title,
                'chapter_name': chapter.name,
                'subject_name': subject.name,
                'total_questions': score.total_questions,
                'correct_answers': score.correct_answers,
                'total_score': score.total_score,
                'time_taken': score.time_taken,
                'attempted_on': score.attempt_datetime.isoformat()
            })

        return jsonify({'scores': result}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/quiz-summary/<int:quiz_id>', methods=['GET'])
@jwt_required()
def get_quiz_summary(quiz_id):
    """Get detailed summary of a quiz attempt"""
    try:
        user_name = get_jwt_identity()
        user = User.query.filter_by(user_name=user_name).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get user's score for this quiz
        score = Score.query.filter_by(
            quiz_id=quiz_id, 
            user_id=user.user_id
        ).order_by(Score.attempt_datetime.desc()).first()

        if not score:
            return jsonify({'error': 'No attempt found for this quiz'}), 404

        quiz = Quiz.query.get_or_404(quiz_id)
        chapter = quiz.chapter
        subject = chapter.subject if chapter else None

        return jsonify({
            'quiz_id': quiz.quiz_id,
            'quiz_title': quiz.title,
            'subject': subject.name if subject else 'Unknown',
            'chapter': chapter.name if chapter else 'Unknown',
            'date': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
            'duration': quiz.time_duration,
            'remarks': quiz.remarks,
            'score': score.correct_answers,
            'total_questions': score.total_questions,
            'percentage_score': score.total_score,
            'time_taken': score.time_taken,
            'attempted_on': score.attempt_datetime.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/score-summary', methods=['GET'])
@jwt_required()
def get_score_summary():
    """Get user's overall score statistics"""
    try:
        user_name = get_jwt_identity()
        user = User.query.filter_by(user_name=user_name).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        scores = Score.query.filter_by(user_id=user.user_id).all()
        
        if not scores:
            return jsonify({
                'total_quizzes_attempted': 0,
                'total_score': 0,
                'average_score': 0,
                'best_score': 0,
                'total_time_spent': 0
            }), 200

        total_score = sum([s.total_score for s in scores])
        quiz_count = len(scores)
        average_score = round(total_score / quiz_count, 2) if quiz_count > 0 else 0
        best_score = max([s.total_score for s in scores]) if scores else 0
        total_time_spent = sum([s.time_taken or 0 for s in scores])

        return jsonify({
            'total_quizzes_attempted': quiz_count,
            'total_score': total_score,
            'average_score': average_score,
            'best_score': best_score,
            'total_time_spent': total_time_spent  # in seconds
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500