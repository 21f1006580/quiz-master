# routes/admin_routes.py - Admin Dashboard API Routes

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
from backend.models.models import db, User, Subject, Chapter, Quiz, Question, Score
from backend.cache import cache_decorator, CacheKeys, CacheExpiry, invalidate_admin_cache
from datetime import datetime, timedelta
from sqlalchemy import or_
from backend.api.notification_tasks import export_admin_user_csv
from utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# ============= SEARCH FUNCTIONALITY =============

@admin_bp.route('/search', methods=['GET'])
@admin_required
def search_admin():
    """Search users, subjects, and quizzes"""
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'all')  # all, users, subjects, quizzes
    
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    results = {}
    
    if search_type in ['all', 'users']:
        users = User.query.filter(
            or_(
                User.user_name.ilike(f'%{query}%'),
                User.full_name.ilike(f'%{query}%')
            )
        ).limit(10).all()
        results['users'] = [{
            'user_id': user.user_id,
            'user_name': user.user_name,
            'full_name': user.full_name,
            'is_admin': user.is_admin
        } for user in users]
    
    if search_type in ['all', 'subjects']:
        subjects = Subject.query.filter(
            Subject.name.ilike(f'%{query}%')
        ).limit(10).all()
        results['subjects'] = [{
            'subject_id': subject.subject_id,
            'name': subject.name,
            'description': subject.description
        } for subject in subjects]
    
    if search_type in ['all', 'quizzes']:
        quizzes = Quiz.query.filter(
            Quiz.title.ilike(f'%{query}%')
        ).limit(10).all()
        results['quizzes'] = [{
            'quiz_id': quiz.quiz_id,
            'title': quiz.title,
            'date_of_quiz': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
            'duration': quiz.time_duration,
            'is_active': quiz.is_active
        } for quiz in quizzes]
    
    return jsonify(results)

@admin_bp.route('/search/users', methods=['GET'])
@admin_required
def search_users():
    """Search users by name or email"""
    try:
        query = request.args.get('q', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        users = User.query.filter(
            User.is_admin == False,
            (User.user_name.contains(query) | 
             User.full_name.contains(query))
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/search/subjects', methods=['GET'])
@admin_required
def search_subjects():
    """Search subjects by name"""
    try:
        query = request.args.get('q', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        subjects = Subject.query.filter(
            Subject.name.contains(query)
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'subjects': [subject.to_dict() for subject in subjects.items],
            'total': subjects.total,
            'pages': subjects.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/search/quizzes', methods=['GET'])
@admin_required
def search_quizzes():
    """Search quizzes by title"""
    try:
        query = request.args.get('q', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        quizzes = Quiz.query.filter(
            Quiz.title.contains(query)
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'quizzes': [quiz.to_dict() for quiz in quizzes.items],
            'total': quizzes.total,
            'pages': quizzes.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= CSV EXPORT FUNCTIONALITY =============

@admin_bp.route('/export/users-csv', methods=['POST'])
@admin_required
def trigger_user_csv_export():
    """Trigger CSV export of all user performance data"""
    try:
        # Start the async task
        task = export_admin_user_csv.delay()
        
        return jsonify({
            'message': 'CSV export started',
            'task_id': task.id,
            'status': 'PENDING'
        }), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/export/quiz-csv/<int:quiz_id>', methods=['POST'])
@admin_required
def trigger_quiz_csv_export(quiz_id):
    """Trigger CSV export of specific quiz results"""
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        
        # Get all scores for this quiz
        scores = db.session.query(Score, User).join(
            User, Score.user_id == User.user_id
        ).filter(
            Score.quiz_id == quiz_id
        ).all()
        
        # Create CSV data
        import csv
        import io
        
        csv_data = io.StringIO()
        csv_writer = csv.writer(csv_data)
        
        # Write header
        csv_writer.writerow([
            'User ID', 'Username', 'Full Name', 'Score (%)',
            'Correct Answers', 'Total Questions', 'Time Taken (seconds)',
            'Attempt Date'
        ])
        
        # Write data
        for score, user in scores:
            csv_writer.writerow([
                user.user_id,
                user.user_name,
                user.full_name,
                score.total_score,
                score.correct_answers,
                score.total_questions,
                score.time_taken or 0,
                score.attempt_datetime.strftime('%Y-%m-%d %H:%M')
            ])
        
        # Return CSV data
        from flask import Response
        output = csv_data.getvalue()
        
        return Response(
            output,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=quiz_{quiz_id}_results.csv'}
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/export/csv', methods=['POST'])
@admin_required
def trigger_csv_export():
    """Trigger CSV export for admin"""
    try:
        # Start async task
        task = export_admin_user_csv.delay()
        
        return jsonify({
            'success': True,
            'message': 'CSV export started. You will receive an email when complete.',
            'task_id': task.id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= CACHE MANAGEMENT =============

@admin_bp.route('/cache/stats', methods=['GET'])
@admin_required
def get_cache_stats():
    """Get cache statistics"""
    try:
        from backend.cache import get_cache_stats
        stats = get_cache_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/cache/clear', methods=['POST'])
@admin_required
def clear_cache():
    """Clear all cache"""
    try:
        from backend.cache import clear_cache_pattern
        clear_cache_pattern('*')
        return jsonify({'message': 'Cache cleared successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= SUBJECTS CRUD =============


# GET all subjects
@admin_bp.route('/subjects', methods=['GET'])
@admin_required
def get_subjects():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        
        query = Subject.query
        
        if search:
            query = query.filter(Subject.name.contains(search))
        
        subjects = query.filter_by(is_active=True).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'subjects': [subject.to_dict() for subject in subjects.items],
            'total': subjects.total,
            'pages': subjects.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# CREATE new subject
@admin_bp.route('/subjects', methods=['POST'])
@admin_required
def create_subject():
    try:
        data = request.get_json()
        
        # Validation
        if not data or not data.get('name'):
            return jsonify({'error': 'Subject name is required'}), 400
        
        # Check if subject already exists
        existing_subject = Subject.query.filter_by(name=data['name']).first()
        if existing_subject:
            return jsonify({'error': 'Subject with this name already exists'}), 400
        
        # Create new subject
        subject = Subject(
            name=data['name'].strip(),
            description=data.get('description', '').strip()
        )
        
        db.session.add(subject)
        db.session.commit()
        
        return jsonify({
            'message': 'Subject created successfully',
            'subject': subject.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# UPDATE subject
@admin_bp.route('/subjects/<int:subject_id>', methods=['PUT'])
@admin_required
def update_subject(subject_id):
    try:
        subject = Subject.query.get_or_404(subject_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Check if name is being updated and doesn't conflict
        if 'name' in data and data['name'] != subject.name:
            existing_subject = Subject.query.filter_by(name=data['name']).first()
            if existing_subject:
                return jsonify({'error': 'Subject with this name already exists'}), 400
            subject.name = data['name'].strip()
        
        # Update other fields
        if 'description' in data:
            subject.description = data['description'].strip()
        
        subject.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Subject updated successfully',
            'subject': subject.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# DELETE subject (soft delete)
@admin_bp.route('/subjects/<int:subject_id>', methods=['DELETE'])
@admin_required
def delete_subject(subject_id):
    try:
        subject = Subject.query.get_or_404(subject_id)
        
        # Soft delete - just mark as inactive
        subject.is_active = False
        subject.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Subject deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============= CHAPTERS CRUD =============

@admin_bp.route('/subjects/<int:subject_id>/chapters', methods=['GET'])
@admin_required
def get_chapters(subject_id):
    """Get chapters for a specific subject"""
    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    
    return jsonify({
        'subject': subject.to_dict(),
        'chapters': [chapter.to_dict() for chapter in chapters]
    })

# Add this route to your admin_routes.py file in the CHAPTERS CRUD section

@admin_bp.route('/chapters', methods=['GET'])
@admin_required
def get_all_chapters():
    """Get all chapters (with optional subject filter)"""
    subject_id = request.args.get('subject_id')
    
    if subject_id:
        # Filter by subject if provided
        chapters = Chapter.query.filter_by(subject_id=subject_id).all()
        subject = Subject.query.get_or_404(subject_id)
        return jsonify({
            'subject': subject.to_dict(),
            'chapters': [chapter.to_dict() for chapter in chapters]
        })
    else:
        # Get all chapters with their subject information
        chapters = Chapter.query.all()
        chapters_with_subject = []
        
        for chapter in chapters:
            chapter_dict = chapter.to_dict()
            if chapter.subject:
                chapter_dict['subject_name'] = chapter.subject.name
            chapters_with_subject.append(chapter_dict)
        
        return jsonify({
            'chapters': chapters_with_subject
        })

@admin_bp.route('/chapters', methods=['POST'])
@admin_required
def create_chapter():
    """Create a new chapter"""
    data = request.get_json()
    
    if not data.get('name') or not data.get('subject_id'):
        return jsonify({'error': 'Chapter name and subject_id are required'}), 400
    
    # Verify subject exists
    subject = Subject.query.get(data['subject_id'])
    if not subject:
        return jsonify({'error': 'Subject not found'}), 404
    
    chapter = Chapter(
        name=data['name'],
        description=data.get('description', ''),
        subject_id=data['subject_id']
    )
    
    try:
        db.session.add(chapter)
        db.session.commit()
        return jsonify({'message': 'Chapter created successfully', 'chapter': chapter.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/chapters/<int:chapter_id>', methods=['GET'])
@admin_required
def get_single_chapter(chapter_id):
    """Get a specific chapter with its subject information"""
    chapter = Chapter.query.get_or_404(chapter_id)
    chapter_dict = chapter.to_dict()
    
    if chapter.subject:
        chapter_dict['subject_name'] = chapter.subject.name
    
    return jsonify({
        'chapter': chapter_dict
    })

@admin_bp.route('/chapters/<int:chapter_id>', methods=['PUT'])
@admin_required
def update_chapter(chapter_id):
    """Update a chapter"""
    chapter = Chapter.query.get_or_404(chapter_id)
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'error': 'Chapter name is required'}), 400
    
    try:
        chapter.name = data['name']
        chapter.description = data.get('description', chapter.description)
        db.session.commit()
        return jsonify({'message': 'Chapter updated successfully', 'chapter': chapter.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/chapters/<int:chapter_id>', methods=['DELETE'])
@admin_required
def delete_chapter(chapter_id):
    """Delete a chapter and all its quizzes"""
    chapter = Chapter.query.get_or_404(chapter_id)
    
    try:
        db.session.delete(chapter)
        db.session.commit()
        return jsonify({'message': 'Chapter deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============= QUIZZES CRUD =============

@admin_bp.route('/chapters/<int:chapter_id>/quizzes', methods=['GET'])
@admin_required
def get_quizzes(chapter_id):
    """Get quizzes for a specific chapter"""
    chapter = Chapter.query.get_or_404(chapter_id)
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    
    return jsonify({
        'chapter': chapter.to_dict(),
        'quizzes': [quiz.to_dict() for quiz in quizzes]
    })
@admin_bp.route('/quizzes', methods=['POST'])
@admin_required
def create_quiz():
    """Create a new quiz with scheduling"""
    try:
        data = request.get_json()
        
        # Check if this is an anytime quiz
        is_anytime_quiz = data.get('is_anytime_quiz', False)
        
        # Validation for scheduled quizzes
        if not is_anytime_quiz:
            required_fields = ['title', 'chapter_id', 'start_date', 'start_time', 'time_duration']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'{field} is required for scheduled quizzes'}), 400
        else:
            # For anytime quizzes, only title, chapter_id, and time_duration are required
            required_fields = ['title', 'chapter_id', 'time_duration']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'{field} is required'}), 400
        
        # Verify chapter exists
        chapter = Chapter.query.get(data['chapter_id'])
        if not chapter:
            return jsonify({'error': 'Chapter not found'}), 404
        
        # Handle start datetime based on quiz type
        if is_anytime_quiz:
            # For anytime quizzes, set start time to current time
            start_datetime = datetime.now()
        else:
            # Parse start datetime for scheduled quizzes
            start_datetime_str = f"{data['start_date']} {data['start_time']}"
            start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M')
            
            # Validate start time is in future for scheduled quizzes
            if start_datetime <= datetime.now():
                return jsonify({'error': 'Quiz start time must be in the future'}), 400
        
        # Create quiz
        quiz = Quiz(
            title=data['title'],
            chapter_id=data['chapter_id'],
            date_of_quiz=start_datetime,
            time_duration=int(data['time_duration']),
            is_anytime_quiz=is_anytime_quiz,
            remarks=data.get('remarks', ''),
            is_active=data.get('is_active', True)
        )
        
        # Set optional fields if they exist in model
        if hasattr(quiz, 'allow_multiple_attempts'):
            quiz.allow_multiple_attempts = data.get('allow_multiple_attempts', False)
        if hasattr(quiz, 'show_results_immediately'):
            quiz.show_results_immediately = data.get('show_results_immediately', True)
        
        db.session.add(quiz)
        db.session.commit()
        
        return jsonify({
            'message': 'Quiz created successfully',
            'quiz': quiz.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': 'Invalid date/time format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/quizzes/<int:quiz_id>', methods=['PUT'])
@admin_required
def update_quiz(quiz_id):
    """Update quiz"""
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        data = request.get_json()
        
        # Update basic fields
        if data.get('title'):
            quiz.title = data['title']
        if 'remarks' in data:
            quiz.remarks = data['remarks']
        if 'is_active' in data:
            quiz.is_active = data['is_active']
        
        # Update anytime quiz setting
        if 'is_anytime_quiz' in data:
            quiz.is_anytime_quiz = data['is_anytime_quiz']
            # If converting to anytime quiz, set start time to current time
            if data['is_anytime_quiz']:
                quiz.date_of_quiz = datetime.now()
        
        # Update start datetime if provided (only for scheduled quizzes)
        if not quiz.is_anytime_quiz and data.get('start_date') and data.get('start_time'):
            start_datetime_str = f"{data['start_date']} {data['start_time']}"
            start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M')
            quiz.date_of_quiz = start_datetime
        
        # Update duration
        if data.get('time_duration'):
            quiz.time_duration = int(data['time_duration'])
        
        # Update optional fields
        if hasattr(quiz, 'allow_multiple_attempts') and 'allow_multiple_attempts' in data:
            quiz.allow_multiple_attempts = data['allow_multiple_attempts']
        if hasattr(quiz, 'show_results_immediately') and 'show_results_immediately' in data:
            quiz.show_results_immediately = data['show_results_immediately']
        
        quiz.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Quiz updated successfully',
            'quiz': quiz.to_dict()
        })
        
    except ValueError as e:
        return jsonify({'error': 'Invalid date/time format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/quizzes/<int:quiz_id>', methods=['DELETE'])
@admin_required
def delete_quiz(quiz_id):
    """Delete a quiz and all its questions"""
    quiz = Quiz.query.get_or_404(quiz_id)
    
    try:
        db.session.delete(quiz)
        db.session.commit()
        return jsonify({'message': 'Quiz deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============= QUESTIONS CRUD =============

@admin_bp.route('/chapters/<int:chapter_id>/questions', methods=['GET'])
@admin_required
def get_questions_by_chapter(chapter_id):
    """Get all questions for all quizzes in a specific chapter"""
    chapter = Chapter.query.get_or_404(chapter_id)
    
    # Get all quizzes for this chapter
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    
    # Get all questions for all quizzes in this chapter
    quiz_ids = [quiz.quiz_id for quiz in quizzes]
    questions = Question.query.filter(Question.quiz_id.in_(quiz_ids)).all() if quiz_ids else []
    
    # Add quiz and chapter info to each question
    questions_with_context = []
    for question in questions:
        question_dict = question.to_dict()
        # Find the quiz for this question
        quiz = next((q for q in quizzes if q.quiz_id == question.quiz_id), None)
        if quiz:
            question_dict['quiz_title'] = quiz.title
            question_dict['chapter_id'] = chapter_id
            question_dict['chapter_name'] = chapter.name
        questions_with_context.append(question_dict)
    
    return jsonify({
        'chapter': chapter.to_dict(),
        'questions': questions_with_context,
        'quizzes': [quiz.to_dict() for quiz in quizzes]  # Include available quizzes
    })


# Enhanced user routes for quiz availability checking
@admin_bp.route('/quiz/<int:quiz_id>/take', methods=['GET'])
@jwt_required()
def start_quiz(quiz_id):
    """Start a quiz with scheduling validation"""
    try:
        print(f"=== QUIZ ACCESS CHECK ===")
        print(f"Quiz ID: {quiz_id}")
        
        user_name = get_jwt_identity()
        user = User.query.filter_by(user_name=user_name).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        print(f"Quiz: {quiz.title}")
        print(f"Quiz status: {quiz.get_status()}")
        print(f"Is available: {quiz.is_available_now()}")
        
        # Check if quiz is available
        can_attempt, message = quiz.can_user_attempt(user.user_id)
        if not can_attempt:
            return jsonify({'error': message}), 403
        
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
            'time_remaining': quiz.get_time_remaining(),
            'show_results_immediately': quiz.show_results_immediately
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"EXCEPTION in start_quiz: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    
@admin_bp.route('/quizzes/<int:quiz_id>/questions', methods=['GET'])
@admin_required
def get_questions(quiz_id):
    """Get questions for a specific quiz"""
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    return jsonify({
        'quiz': quiz.to_dict(),
        'questions': [question.to_dict() for question in questions]
    })
# Updated Questions API - Remove auto-quiz creation, enforce proper quiz selection

@admin_bp.route('/questions', methods=['POST'])
@admin_required
def create_question():
    """Create a new question - requires explicit quiz_id"""
    data = request.get_json()
    
    # Strict validation - quiz_id is mandatory
    required_fields = ['quiz_id', 'question_statement', 'option1', 'option2', 'correct_option']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Verify quiz exists
    quiz = Quiz.query.get(data['quiz_id'])
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404
    
    # Validate correct_option
    if data['correct_option'] not in [1, 2, 3, 4]:
        return jsonify({'error': 'correct_option must be 1, 2, 3, or 4'}), 400
    
    question = Question(
        quiz_id=data['quiz_id'],
        question_statement=data['question_statement'],
        option1=data['option1'],
        option2=data['option2'],
        option3=data.get('option3', ''),
        option4=data.get('option4', ''),
        correct_option=data['correct_option']
    )
    
    try:
        db.session.add(question)
        db.session.commit()
        
        # Return question with additional context
        question_dict = question.to_dict()
        question_dict['quiz_title'] = quiz.title
        question_dict['chapter_id'] = quiz.chapter_id
        question_dict['chapter_name'] = quiz.chapter.name if quiz.chapter else None
        
        return jsonify({
            'message': 'Question created successfully', 
            'question': question_dict
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/questions/<int:question_id>', methods=['GET'])
@admin_required
def get_question(question_id):
    """Get a specific question with context"""
    question = Question.query.get_or_404(question_id)
    question_dict = question.to_dict()
    
    # Add context information
    if question.quiz:
        question_dict['quiz_title'] = question.quiz.title
        question_dict['chapter_id'] = question.quiz.chapter_id
        if question.quiz.chapter:
            question_dict['chapter_name'] = question.quiz.chapter.name
            question_dict['subject_id'] = question.quiz.chapter.subject_id
            if question.quiz.chapter.subject:
                question_dict['subject_name'] = question.quiz.chapter.subject.name
    
    return jsonify({'question': question_dict})

@admin_bp.route('/questions/<int:question_id>', methods=['PUT'])
@admin_required
def update_question(question_id):
    """Update a question"""
    question = Question.query.get_or_404(question_id)
    data = request.get_json()
    
    try:
        if data.get('question_statement'):
            question.question_statement = data['question_statement']
        if data.get('option1'):
            question.option1 = data['option1']
        if data.get('option2'):
            question.option2 = data['option2']
        if 'option3' in data:
            question.option3 = data['option3']
        if 'option4' in data:
            question.option4 = data['option4']
        if data.get('correct_option'):
            if data['correct_option'] not in [1, 2, 3, 4]:
                return jsonify({'error': 'correct_option must be 1, 2, 3, or 4'}), 400
            question.correct_option = data['correct_option']
        
        db.session.commit()
        
        # Return updated question with context
        question_dict = question.to_dict()
        if question.quiz:
            question_dict['quiz_title'] = question.quiz.title
            question_dict['chapter_id'] = question.quiz.chapter_id
            if question.quiz.chapter:
                question_dict['chapter_name'] = question.quiz.chapter.name
        
        return jsonify({
            'message': 'Question updated successfully', 
            'question': question_dict
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/questions/<int:question_id>', methods=['DELETE'])
@admin_required
def delete_question(question_id):
    """Delete a question"""
    question = Question.query.get_or_404(question_id)
    
    try:
        db.session.delete(question)
        db.session.commit()
        return jsonify({'message': 'Question deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============= HELPER ENDPOINTS =============

@admin_bp.route('/chapters/<int:chapter_id>/available-quizzes', methods=['GET'])
@admin_required
def get_available_quizzes(chapter_id):
    """Get all quizzes available for a chapter"""
    chapter = Chapter.query.get_or_404(chapter_id)
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    
    return jsonify({
        'chapter': chapter.to_dict(),
        'quizzes': [quiz.to_dict() for quiz in quizzes]
    })

@admin_bp.route('/subjects/<int:subject_id>/all-questions', methods=['GET'])
@admin_required
def get_all_questions_by_subject(subject_id):
    """Get all questions for a subject (across all chapters and quizzes)"""
    subject = Subject.query.get_or_404(subject_id)
    
    # Get all chapters for this subject
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    chapter_ids = [chapter.chapter_id for chapter in chapters]
    
    # Get all quizzes for these chapters
    quizzes = Quiz.query.filter(Quiz.chapter_id.in_(chapter_ids)).all() if chapter_ids else []
    quiz_ids = [quiz.quiz_id for quiz in quizzes]
    
    # Get all questions for these quizzes
    questions = Question.query.filter(Question.quiz_id.in_(quiz_ids)).all() if quiz_ids else []
    
    # Add context to questions
    questions_with_context = []
    for question in questions:
        question_dict = question.to_dict()
        quiz = next((q for q in quizzes if q.quiz_id == question.quiz_id), None)
        if quiz:
            chapter = next((c for c in chapters if c.chapter_id == quiz.chapter_id), None)
            if chapter:
                question_dict['quiz_title'] = quiz.title
                question_dict['chapter_id'] = chapter.chapter_id
                question_dict['chapter_name'] = chapter.name
                question_dict['subject_id'] = subject_id
                question_dict['subject_name'] = subject.name
        questions_with_context.append(question_dict)
    
    return jsonify({
        'subject': subject.to_dict(),
        'questions': questions_with_context,
        'total_questions': len(questions_with_context)
    })


@admin_bp.route('/quizzes/status-check', methods=['POST'])
@admin_required
def bulk_quiz_status_update():
    """Automatically update quiz statuses based on current time"""
    try:
        now = datetime.utcnow()
        updated_count = 0
        
        # Auto-activate quizzes that should start
        quizzes_to_activate = Quiz.query.filter(
            Quiz.auto_start == True,
            Quiz.is_active == False,
            Quiz.date_of_quiz <= now
        ).all()
        
        for quiz in quizzes_to_activate:
            quiz.is_active = True
            updated_count += 1
        
        # Auto-deactivate expired quizzes
        quizzes_to_expire = Quiz.query.filter(
            Quiz.auto_end == True,
            Quiz.is_active == True,
            Quiz.end_date_time <= now
        ).all()
        
        for quiz in quizzes_to_expire:
            quiz.is_active = False
            updated_count += 1
        
        if updated_count > 0:
            db.session.commit()
        
        return jsonify({
            'message': f'Updated {updated_count} quiz statuses',
            'updated_count': updated_count
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
# ============= USERS MANAGEMENT =============

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """Get all users with their details"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    print(f"Debug: Getting users - page: {page}, per_page: {per_page}, search: '{search}'")
    
    query = User.query.filter(User.is_admin == 0)
    if search:
        query = query.filter(User.username.contains(search) | User.email.contains(search))
    
    users = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'users': [user.to_dict() for user in users.items],
        'total': users.total,
        'pages': users.pages,
        'current_page': page
    })

@admin_bp.route('/dashboard/stats', methods=['GET'])
@admin_required
def get_dashboard_stats():
    """Get dashboard statistics"""
    total_users = User.query.filter(User.is_admin == False).count()
    total_subjects = Subject.query.count()
    total_chapters = Chapter.query.count()
    total_quizzes = Quiz.query.count()
    total_questions = Question.query.count()
    
    return jsonify({
        'total_users': total_users,
        'total_subjects': total_subjects,
        'total_chapters': total_chapters,
        'total_quizzes': total_quizzes,
        'total_questions': total_questions
    })

@admin_bp.route('/stats', methods=['GET'])
@admin_required
@cache_decorator(CacheKeys.ADMIN_STATS, CacheExpiry.MEDIUM)
def get_admin_stats():
    """Get admin dashboard statistics"""
    try:
        # Total counts
        total_users = User.query.filter_by(is_admin=False).count()
        total_subjects = Subject.query.count()
        total_quizzes = Quiz.query.count()
        total_questions = Question.query.count()
        
        # Recent activity
        recent_quizzes = Quiz.query.filter(
            Quiz.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        # Active quizzes
        active_quizzes = Quiz.query.filter_by(is_active=True).count()
        
        # Top performing users
        top_users = db.session.query(
            User.user_name,
            User.full_name,
            db.func.avg(Score.total_score).label('avg_score'),
            db.func.count(Score.score_id).label('quiz_count')
        ).join(Score, User.user_id == Score.user_id).filter(
            User.is_admin == False
        ).group_by(User.user_id).order_by(
            db.func.avg(Score.total_score).desc()
        ).limit(5).all()
        
        stats = {
            'total_users': total_users,
            'total_subjects': total_subjects,
            'total_quizzes': total_quizzes,
            'total_questions': total_questions,
            'recent_quizzes': recent_quizzes,
            'active_quizzes': active_quizzes,
            'top_users': [{
                'user_name': user.user_name,
                'full_name': user.full_name,
                'avg_score': round(float(user.avg_score), 2),
                'quiz_count': user.quiz_count
            } for user in top_users]
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Admin route to manually trigger expiry check
@admin_bp.route('/quizzes/expire-check', methods=['POST'])
@admin_required
def manual_expire_check():
    """Manually trigger quiz expiry check"""
    try:
        expired_count = 0
        locked_quizzes = []
        
        # Find and expire quizzes
        quizzes = Quiz.query.filter(
            Quiz.is_active == True,
            Quiz.auto_expire == True
        ).all()
        
        for quiz in quizzes:
            if quiz.auto_lock_if_expired():
                expired_count += 1
                locked_quizzes.append({
                    'id': quiz.quiz_id,
                    'title': quiz.title,
                    'expired_at': quiz.get_effective_end_time().isoformat() if quiz.get_effective_end_time() else None
                })
        
        if expired_count > 0:
            db.session.commit()
        
        return jsonify({
            'message': f'Expiry check completed. {expired_count} quizzes locked.',
            'expired_count': expired_count,
            'locked_quizzes': locked_quizzes,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500