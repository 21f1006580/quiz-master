from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import datetime, timedelta
from backend.models.models import db
from backend.routes.auth_routes import auth_bp
from backend.routes.user_routes import user_bp
from backend.routes.admin_routes import admin_bp
from backend.cache import init_cache
from celery_app import make_celery
import os

# Import Celery
from celery_app import make_celery
import os

# Global celery variable
celery = None

def create_app():
    """Create Flask application instance"""
    global celery
    
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quizmaster.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-key'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    
    # Redis configuration for Celery and caching
    app.config['broker_url'] = 'redis://localhost:6379/0'
    app.config['result_backend'] = 'redis://localhost:6379/0'
    app.config['REDIS_HOST'] = 'localhost'
    app.config['REDIS_PORT'] = 6379
    app.config['REDIS_CACHE_DB'] = 1
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app)
    
    # Initialize cache
    init_cache(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    
    # Create Celery instance
    celery = make_celery(app)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    # Add Celery routes for monitoring
    @app.route('/api/admin/celery/status')
    def celery_status():
        """Check Celery worker status"""
        try:
            # Check if workers are active
            inspect = celery.control.inspect()
            stats = inspect.stats()
            active_tasks = inspect.active()
            
            return jsonify({
                'celery_running': bool(stats),
                'workers': stats or {},
                'active_tasks': active_tasks or {},
                'broker_url': app.config['broker_url']
            })
        except Exception as e:
            return jsonify({
                'celery_running': False,
                'error': str(e)
            })
    
    @app.route('/api/admin/celery/tasks')
    def list_celery_tasks():
        """List available Celery tasks"""
        return jsonify({
            'available_tasks': list(celery.tasks.keys()),
            'scheduled_tasks': list(celery.conf.beat_schedule.keys())
        })
    
    # Add manual task triggers for admins
    @app.route('/api/admin/quiz/expire-check', methods=['POST'])
    def manual_expire_check():
        """Manually trigger quiz expiry check"""
        from backend.api.quiz_tasks import check_and_expire_quizzes
        
        # Run task asynchronously
        task = check_and_expire_quizzes.delay()
        
        return jsonify({
            'message': 'Quiz expiry check started',
            'task_id': task.id,
            'status': 'PENDING'
        })
    
    @app.route('/api/admin/quiz/expire/<int:quiz_id>', methods=['POST'])
    def manual_expire_quiz(quiz_id):
        """Manually expire a specific quiz"""
        from backend.api.quiz_tasks import expire_single_quiz
        
        task = expire_single_quiz.delay(quiz_id)
        
        return jsonify({
            'message': f'Quiz {quiz_id} expiry started',
            'task_id': task.id,
            'status': 'PENDING'
        })
    
    @app.route('/api/admin/task/<task_id>/status')
    def task_status(task_id):
        """Check status of a Celery task"""
        from celery.result import AsyncResult
        
        task = AsyncResult(task_id, app=celery)
        
        if task.state == 'PENDING':
            response = {
                'state': task.state,
                'status': 'Task is waiting to be processed'
            }
        elif task.state == 'SUCCESS':
            response = {
                'state': task.state,
                'result': task.result
            }
        else:
            response = {
                'state': task.state,
                'status': str(task.info)
            }
        
        return jsonify(response)
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)