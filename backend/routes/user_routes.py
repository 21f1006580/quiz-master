# routes/user_routes.py 

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.models import db, User, Subject, Chapter, Quiz, Question, Score
from datetime import datetime, timedelta
from sqlalchemy import func
import traceback
from utils.decorators import user_required
from backend.api.notification_tasks import export_user_quiz_csv
from backend.cache import cache_decorator, CacheKeys, CacheExpiry, invalidate_user_cache

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

        print("Fetching user dashboard data for:", user.user_name)

        # Get active subjects with chapter and quiz counts
        subjects = Subject.query.filter_by(is_active=True).all()
        subject_list = []
        print("Found subjects:", len(subjects))
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
        print("Subjects processed:", len(subject_list))

        return jsonify({'subjects': subject_list}), 200
        
    except Exception as e:
        print("Error while fetching dashboard data:", str(e))
        print(f"ERROR traceback: {traceback.format_exc()}")
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


@user_bp.route('/question/<int:question_id>/check', methods=['POST'])
@jwt_required()
def check_answer_instantly(question_id):
    """Check if the selected answer is correct and provide instant feedback"""
    try:
        print(f"Question ID: {question_id}")
        
        data = request.get_json()
        selected_option = data.get('selected_option')  # 0-based index
        
        print(f"Selected option (0-based): {selected_option}")
        
        user_name = get_jwt_identity()
        user = User.query.filter_by(user_name=user_name).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get the question
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'error': 'Question not found'}), 404
            
        print(f"Question: {question.question_statement}")
        print(f"Correct option: {question.correct_option}")
        
        # Convert selected option from 0-based to 1-based for comparison
        selected_option_1based = selected_option + 1 if selected_option is not None else None
        
        # Check if answer is correct
        is_correct = selected_option_1based == question.correct_option
        
        print(f"Selected (1-based): {selected_option_1based}")
        print(f"Is correct: {is_correct}")
        
        # Prepare response
        response_data = {
            'is_correct': is_correct,
            'correct_option': question.correct_option,
            'selected_option': selected_option_1based,
            'question_id': question_id
        }
        
        # Add explanation if available (you can extend your Question model to include explanations)
        if hasattr(question, 'explanation') and question.explanation:
            response_data['explanation'] = question.explanation
        
        print(f"Response: {response_data}")
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"EXCEPTION in check_answer_instantly: {str(e)}")
        import traceback
        traceback.print_exc()
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
                    'is_anytime_quiz': quiz.is_anytime_quiz,
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

@user_bp.route('/quiz/<int:quiz_id>/status', methods=['GET'])
@jwt_required()
def check_quiz_status(quiz_id):
    """Check current quiz status (useful for live updates)"""
    try:
        user_name = get_jwt_identity()
        user = User.query.filter_by(user_name=user_name).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        # Check if quiz should be auto-locked
        was_locked = quiz.auto_lock_if_expired()
        if was_locked:
            db.session.commit()
        
        is_available, message = quiz.is_available_for_attempt(user.user_id)
        
        return jsonify({
            'quiz_id': quiz.quiz_id,
            'title': quiz.title,
            'status': quiz.get_status(),
            'is_available': is_available,
            'availability_message': message,
            'time_remaining': quiz.get_time_remaining(),
            'expires_at': quiz.get_effective_end_time().isoformat() if quiz.get_effective_end_time() else None,
            'was_auto_locked': was_locked,
            'current_time': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/quiz/<int:quiz_id>/take', methods=['GET'])
@jwt_required()
def start_quiz(quiz_id):
    """Start a quiz with auto-expiry checking"""
    try:
        print(f"=== QUIZ ACCESS CHECK (with auto-expiry) ===")
        print(f"Quiz ID: {quiz_id}")
        print(f"Timestamp: {datetime.now()}")
        
        user_name = get_jwt_identity()
        user = User.query.filter_by(user_name=user_name).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        print(f"Quiz: {quiz.title}")
        print(f"Quiz status before check: {quiz.get_status()}")
        print(f"Quiz active: {quiz.is_active}")
        print(f"Quiz expired: {quiz.is_expired()}")
        
        # AUTO-EXPIRY CHECK: This will automatically lock quiz if expired
        is_available, message = quiz.is_available_for_attempt(user.user_id)
        
        if not is_available:
            print(f"Quiz not available: {message}")
            return jsonify({
                'error': message,
                'quiz_status': quiz.get_status(),
                'time_remaining': quiz.get_time_remaining()
            }), 403
        
        print(f"✅ Quiz available for attempt")
        
        # Get questions
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        if not questions:
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
            'subject_name': quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else None,
            'time_remaining_until_expiry': quiz.get_time_remaining(),
            'quiz_expires_at': quiz.get_effective_end_time().isoformat() if quiz.get_effective_end_time() else None,
            'show_results_immediately': quiz.show_results_immediately,
            'auto_expire_enabled': quiz.auto_expire,
            'is_anytime_quiz': quiz.is_anytime_quiz
        }
    
        print(f"Time until expiry: {quiz.get_time_remaining()} minutes")
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"EXCEPTION in start_quiz: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
@jwt_required()
def submit_quiz(quiz_id):
    """Submit quiz with expiry validation"""
    try:
        print(f"Quiz ID: {quiz_id}")
        print(f"Submission time: {datetime.now()}")
        
        data = request.get_json()
        user_answers = data.get('answers', {})
        time_taken = data.get('time_taken', 0)

        user_name = get_jwt_identity()
        user = User.query.filter_by(user_name=user_name).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        # CRITICAL: Check if quiz expired during attempt
        is_available, message = quiz.is_available_for_attempt(user.user_id)
        
        # Allow submission if quiz just expired (grace period for ongoing attempts)
        if not is_available and quiz.is_expired():
            # Check if user already has an ongoing attempt (more lenient check)
            existing_attempt = Score.query.filter_by(
                quiz_id=quiz_id,
                user_id=user.user_id
            ).first()
            
            if existing_attempt and not quiz.allow_multiple_attempts:
                print(f"❌ Quiz expired and user {user.user_id} already submitted quiz {quiz_id}")
                return jsonify({'error': 'Quiz has expired and you have already submitted'}), 403
            
            # Allow submission with warning if quiz just expired
            print("⚠️  Quiz expired during attempt - allowing submission with warning")
            submission_warning = "Quiz expired during your attempt, but submission was accepted"
        else:
            submission_warning = None
        
        # Check for existing attempts (if multiple attempts not allowed)
        if not quiz.allow_multiple_attempts:
            existing_score = Score.query.filter_by(
                user_id=user.user_id, 
                quiz_id=quiz_id
            ).first()
            
            if existing_score:
                print(f"❌ User {user.user_id} already attempted quiz {quiz_id}")
                return jsonify({'error': 'You have already attempted this quiz'}), 403

        # Process submission (existing logic)
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        if not questions:
            return jsonify({'error': 'No questions found for this quiz'}), 404

        total_questions = len(questions)
        correct_answers = 0
        detailed_results = []

        for question in questions:
            question_id = str(question.question_id)
            user_answer_index = user_answers.get(question_id)
            
            is_correct = False
            user_option = None
            
            if user_answer_index is not None:
                user_option = user_answer_index + 1
                is_correct = (user_option == question.correct_option)
                if is_correct:
                    correct_answers += 1
            
            detailed_results.append({
                'question_id': question.question_id,
                'question_text': question.question_statement,
                'correct_option': question.correct_option,
                'user_answer': user_option,
                'is_correct': is_correct,
                'options': [question.option1, question.option2, 
                           question.option3 if question.option3 else None,
                           question.option4 if question.option4 else None]
            })

        percentage_score = round((correct_answers / total_questions) * 100, 2) if total_questions > 0 else 0
        
        # Save score
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

        print(f"✅ Quiz submitted successfully: {correct_answers}/{total_questions} = {percentage_score}%")
        if submission_warning:
            print(f"⚠️  {submission_warning}")

        response_data = {
            'message': 'Quiz submitted successfully',
            'score': {
                'total_questions': total_questions,
                'correct_answers': correct_answers,
                'percentage_score': percentage_score,
                'time_taken': time_taken,
                'detailed_results': detailed_results
            }
        }
        
        if submission_warning:
            response_data['warning'] = submission_warning
        
        return jsonify(response_data), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"EXCEPTION in submit_quiz: {str(e)}")
        import traceback
        traceback.print_exc()
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
        print(f"Fetching scores for user: {user.user_name} (ID: {user.user_id})")

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

        print(f"Found {len(scores)} scores for user {user.user_name}")

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

        print("Scores fetched successfully")

        return jsonify({'scores': result}), 200
        
    except Exception as e:
        print(f"Error while getting scores {e}")
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
    
@user_bp.route('/quiz/<int:quiz_id>/results', methods=['GET'])
@jwt_required()
def get_quiz_results(quiz_id):
    """Get detailed results for a completed quiz attempt"""
    try:
        print(f"=== QUIZ RESULTS ENDPOINT HIT ===")
        print(f"Quiz ID: {quiz_id}")
        
        user_name = get_jwt_identity()
        user = User.query.filter_by(user_name=user_name).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get user's most recent score for this quiz
        score = Score.query.filter_by(
            quiz_id=quiz_id, 
            user_id=user.user_id
        ).order_by(Score.attempt_datetime.desc()).first()

        if not score:
            return jsonify({'error': 'No quiz attempt found'}), 404

        # Get quiz details
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404

        # Get all questions for this quiz with correct answers
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        
        question_results = []
        for question in questions:
            # Get all options
            options = [question.option1, question.option2]
            if question.option3:
                options.append(question.option3)
            if question.option4:
                options.append(question.option4)
            
            question_results.append({
                'question_id': question.question_id,
                'question_statement': question.question_statement,
                'options': options,
                'correct_option': question.correct_option,
                'correct_answer_text': options[question.correct_option - 1] if question.correct_option <= len(options) else None
            })

        # Get chapter and subject info
        chapter = quiz.chapter
        subject = chapter.subject if chapter else None

        result_data = {
            'quiz_info': {
                'quiz_id': quiz.quiz_id,
                'title': quiz.title,
                'chapter_name': chapter.name if chapter else 'Unknown',
                'subject_name': subject.name if subject else 'Unknown',
                'date_of_quiz': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
                'time_duration': quiz.time_duration,
                'remarks': quiz.remarks
            },
            'score_info': {
                'total_questions': score.total_questions,
                'correct_answers': score.correct_answers,
                'total_score': score.total_score,
                'time_taken': score.time_taken,
                'attempted_on': score.attempt_datetime.isoformat()
            },
            'questions': question_results
        }

        print(f"SUCCESS: Returning results for quiz {quiz_id}")
        return jsonify(result_data), 200
        
    except Exception as e:
        print(f"EXCEPTION in get_quiz_results: {str(e)}")
        import traceback
        traceback.print_exc()
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

@user_bp.route('/debug-schema', methods=['GET'])
def debug_schema():
    # Clear metadata and reflect the table
    db.metadata.clear()
    db.metadata.reflect(db.engine)
    
    # Get table info
    table = db.metadata.tables.get('quizzes')
    if table is not None:
        columns = [col.name for col in table.columns]
        print(f"SQLAlchemy sees columns: {columns}")
        return jsonify({'sqlalchemy_sees_columns': columns})
    else:
        print("Table not found")
        return jsonify({'error': 'Table not found in metadata'})

@user_bp.route('/export/csv', methods=['POST'])
@user_required
def trigger_user_csv_export():
    """Trigger CSV export for user"""
    try:
        current_user_name = get_jwt_identity()
        user = User.query.filter_by(user_name=current_user_name).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Start async task
        task = export_user_quiz_csv.delay(user.user_id)
        
        return jsonify({
            'success': True,
            'message': 'CSV export started. You will receive an email when complete.',
            'task_id': task.id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/stats', methods=['GET'])
@user_required
@cache_decorator(CacheKeys.USER_DASHBOARD, CacheExpiry.MEDIUM)
def get_user_stats():
    """Get user dashboard statistics"""
    try:
        current_user_name = get_jwt_identity()
        user = User.query.filter_by(user_name=current_user_name).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's scores
        scores = Score.query.filter_by(user_id=user.user_id).all()
        
        if scores:
            total_quizzes = len(scores)
            avg_score = sum(s.total_score for s in scores) / total_quizzes
            best_score = max(s.total_score for s in scores)
            total_time = sum(s.time_taken or 0 for s in scores)
            
            # Recent activity (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_scores = [s for s in scores if s.attempt_datetime >= week_ago]
            recent_quizzes = len(recent_scores)
            
            # Subject-wise performance
            subject_stats = {}
            for score in scores:
                quiz = score.quiz
                chapter = quiz.chapter
                subject_name = chapter.subject.name
                
                if subject_name not in subject_stats:
                    subject_stats[subject_name] = {
                        'quizzes_taken': 0,
                        'total_score': 0,
                        'best_score': 0
                    }
                
                subject_stats[subject_name]['quizzes_taken'] += 1
                subject_stats[subject_name]['total_score'] += score.total_score
                subject_stats[subject_name]['best_score'] = max(
                    subject_stats[subject_name]['best_score'],
                    score.total_score
                )
            
            # Calculate averages
            for subject in subject_stats.values():
                subject['avg_score'] = round(subject['total_score'] / subject['quizzes_taken'], 2)
                subject['total_score'] = round(subject['total_score'], 2)
        else:
            total_quizzes = 0
            avg_score = 0
            best_score = 0
            total_time = 0
            recent_quizzes = 0
            subject_stats = {}
        
        stats = {
            'total_quizzes': total_quizzes,
            'avg_score': round(avg_score, 2),
            'best_score': best_score,
            'total_time_minutes': round(total_time / 60, 2),
            'recent_quizzes': recent_quizzes,
            'subject_stats': subject_stats
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500