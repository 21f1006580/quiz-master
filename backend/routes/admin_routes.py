# routes/admin_routes.py - Admin Dashboard API Routes


from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from functools import wraps
from backend.models.models import db, User, Subject, Chapter, Quiz, Question

from utils.decorators import admin_required
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_name = get_jwt_identity()
        user = User.query.filter_by(user_name=current_user_name).first()
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

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
    """Create a new quiz"""
    data = request.get_json()
    
    required_fields = ['title', 'chapter_id', 'date_of_quiz', 'time_duration']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Verify chapter exists
    chapter = Chapter.query.get(data['chapter_id'])
    if not chapter:
        return jsonify({'error': 'Chapter not found'}), 404
    
    try:
        # Parse date string to datetime
        quiz_date = datetime.fromisoformat(data['date_of_quiz'].replace('Z', '+00:00'))
        
        quiz = Quiz(
            title=data['title'],
            chapter_id=data['chapter_id'],
            date_of_quiz=quiz_date,
            time_duration=data['time_duration'],
            remarks=data.get('remarks', ''),
            is_active=True      
        )
        
        db.session.add(quiz)
        db.session.commit()
        return jsonify({'message': 'Quiz created successfully', 'quiz': quiz.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/quizzes/<int:quiz_id>', methods=['PUT'])
@admin_required
def update_quiz(quiz_id):
    """Update a quiz"""
    quiz = Quiz.query.get_or_404(quiz_id)
    data = request.get_json()
    
    try:
        if data.get('title'):
            quiz.title = data['title']
        if data.get('date_of_quiz'):
            quiz.date_of_quiz = datetime.fromisoformat(data['date_of_quiz'].replace('Z', '+00:00'))
        if data.get('time_duration'):
            quiz.time_duration = data['time_duration']
        if 'remarks' in data:
            quiz.remarks = data['remarks']
        
        db.session.commit()
        return jsonify({'message': 'Quiz updated successfully', 'quiz': quiz.to_dict()})
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

@admin_bp.route('/questions', methods=['POST'])
@admin_required
def create_question():
    """Create a new question"""
    data = request.get_json()
    
    required_fields = ['quiz_id', 'question_statement', 'option1', 'option2', 'correct_option']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Verify quiz exists
    quiz = Quiz.query.get(data['quiz_id'])
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404
    
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
        return jsonify({'message': 'Question created successfully', 'question': question.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

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
            question.correct_option = data['correct_option']
        
        db.session.commit()
        return jsonify({'message': 'Question updated successfully', 'question': question.to_dict()})
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

# ============= USERS MANAGEMENT =============

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """Get all users with their details"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    
    query = User.query.filter(User.role != 'admin')
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
    total_users = User.query.filter(User.role != 'admin').count()
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