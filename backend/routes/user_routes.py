# routes/user_routes.py

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.models import db, User, Subject, Chapter, Quiz, Question, Score
from datetime import datetime,timedelta

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

@user_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def user_dashboard():
    user_name = get_jwt_identity()
    user = User.query.filter_by(user_name=user_name).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    subjects = Subject.query.filter_by(is_active=True).all()
    subject_list = []
    for subj in subjects:
        subject_list.append({
            'id': subj.subject_id,
            'name': subj.name,
            'description': subj.description
        })

    return jsonify({'subjects': subject_list})


@user_bp.route('/quizzes/<int:subject_id>', methods=['GET'])
@jwt_required()
def get_quizzes(subject_id):
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    quiz_list = []

    for chap in chapters:
        for quiz in chap.quizzes:
            quiz_list.append({
                'quiz_id': quiz.quiz_id,
                'chapter_name': chap.name,
                'date': quiz.date_of_quiz,
                'duration': quiz.time_duration,
                'remarks': quiz.remarks
            })

    return jsonify({'quizzes': quiz_list})


@user_bp.route('/quiz/<int:quiz_id>', methods=['GET'])
@jwt_required()
def get_quiz_details(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz.quiz_id).all()

    question_data = [{
        'id': q.question_id,
        'statement': q.question_statement,
        'options': [q.option1, q.option2, q.option3, q.option4]
    } for q in questions]

    return jsonify({
        'quiz_id': quiz.quiz_id,
        'duration': quiz.time_duration,
        'questions': question_data
    })


@user_bp.route('/quiz/submit', methods=['POST'])
@jwt_required()
def submit_quiz():
    data = request.get_json()
    quiz_id = data.get('quiz_id')
    user_answers = data.get('answers')  # format: {question_id: selected_option}

    user_name = get_jwt_identity()
    user = User.query.filter_by(user_name=user_name).first()

    if not user or not quiz_id or not user_answers:
        return jsonify({'error': 'Missing data'}), 400
    
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404
    
    now = datetime.utcnow()
    quiz_start = quiz.date_of_quiz
    quiz_end = quiz_start + timedelta(minutes=quiz.time_duration)

    if now < quiz_start:
        return jsonify({'error': 'Quiz has not started yet'}), 403
    if now > quiz_end:
        return jsonify({'error': 'Quiz has ended'}), 403

    # If within valid time window, process score
    total_score = 0
    for qid, ans in user_answers.items():
        question = Question.query.get(qid)
        if question and question.correct_option == ans:
            total_score += 1

    # Get total questions for this quiz
    total_questions = Question.query.filter_by(quiz_id=quiz_id).count()
    
    score_entry = Score(
        quiz_id=quiz_id,
        user_id=user.user_id,
        total_questions=total_questions,
        correct_answers=total_score,
        total_score=(total_score / total_questions * 100) if total_questions > 0 else 0,
        time_taken=0  # We'll add timer functionality later
    )
    db.session.add(score_entry)
    db.session.commit()

    return jsonify({'message': 'Quiz submitted', 'score': total_score})


@user_bp.route('/scores', methods=['GET'])
@jwt_required()
def get_user_scores():
    user_name = get_jwt_identity()
    user = User.query.filter_by(user_name=user_name).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    scores = Score.query.filter_by(user_id=user.user_id).all()
    result = []
    for s in scores:
        result.append({
            'quiz_id': s.quiz_id,
            'total_scored': s.correct_answers,
            'attempted_on': s.attempt_datetime.strftime('%Y-%m-%d %H:%M')
        })

    return jsonify({'scores': result})


@user_bp.route('/quiz-summary/<int:quiz_id>', methods=['GET'])
@jwt_required()
def get_quiz_summary(quiz_id):
    user_name = get_jwt_identity()
    user = User.query.filter_by(user_name=user_name).first()

    score = Score.query.filter_by(quiz_id=quiz_id, user_id=user.user_id)\
        .order_by(Score.attempt_datetime.desc()).first()

    if not score:
        return jsonify({'error': 'No attempt found for this quiz'}), 404

    quiz = Quiz.query.get(quiz_id)
    chapter = quiz.chapter.name
    subject = quiz.chapter.subject.name

    return jsonify({
        'quiz_id': quiz.id,
        'subject': subject,
        'chapter': chapter,
        'date': quiz.date_of_quiz,
        'duration': quiz.time_duration,
        'remarks': quiz.remarks,
        'score': score.correct_answers,
        'attempted_on': score.attempt_datetime.strftime('%Y-%m-%d %H:%M:%S')
    })

@user_bp.route('/score-summary', methods=['GET'])
@jwt_required()
def get_score_summary():
    user_name = get_jwt_identity()
    user = User.query.filter_by(user_name=user_name).first()

    scores = Score.query.filter_by(user_id=user.user_id).all()
    total_score = sum([s.correct_answers for s in scores])
    quiz_count = len(scores)
    avg_score = round(total_score / quiz_count, 2) if quiz_count > 0 else 0

    return jsonify({
        'total_quizzes_attempted': quiz_count,
        'total_score': total_score,
        'average_score': avg_score
    })
