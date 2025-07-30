from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from backend.models.models import db, create_admin_user
from backend.routes.auth_routes import auth_bp
from backend.routes.admin_routes import admin_bp
from backend.routes.user_routes import user_bp

# Import Celery
from celery_app import make_celery
import os

# Global celery variable
celery = None

def create_app():
    """Create Flask application instance"""
    global celery
    
    app = Flask(__name__)
    
    # Database configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "quizmaster.db")}'
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'sudar-secret-key-change-in-production'  
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-key-change-in-production'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Tokens don't expire (change for production)

    app.config['broker_url'] = 'redis://localhost:6379/0'
    app.config['result_backend'] = 'redis://localhost:6379/0'
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Initialize CORS
    CORS(app, supports_credentials=True, resources={
        r"/api/*": {
            "origins": ["http://localhost:8080", "http://127.0.0.1:8080"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Initialize database with app
    db.init_app(app)
    
    # Create Celery instance
    celery = make_celery(app)
    
    # Store celery instance in app for easy access
    app.celery = celery
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    
    # Add Celery routes for monitoring
    @app.route('/api/admin/celery/status')
    def celery_status():
        """Check Celery worker status"""
        try:
            # Check if workers are active
            inspect = celery.control.inspect()
            stats = inspect.stats()
            active_tasks = inspect.active()
            
            return {
                'celery_running': bool(stats),
                'workers': stats or {},
                'active_tasks': active_tasks or {},
                'broker_url': app.config['broker_url']
            }
        except Exception as e:
            return {
                'celery_running': False,
                'error': str(e)
            }
    
    @app.route('/api/admin/celery/tasks')
    def list_celery_tasks():
        """List available Celery tasks"""
        return {
            'available_tasks': list(celery.tasks.keys()),
            'scheduled_tasks': list(celery.conf.beat_schedule.keys())
        }
    
    # Add manual task triggers for admins
    @app.route('/api/admin/quiz/expire-check', methods=['POST'])
    def manual_expire_check():
        """Manually trigger quiz expiry check"""
        from backend.api.quiz_tasks import check_and_expire_quizzes
        
        # Run task asynchronously
        task = check_and_expire_quizzes.delay()
        
        return {
            'message': 'Quiz expiry check started',
            'task_id': task.id,
            'status': 'PENDING'
        }
    
    @app.route('/api/admin/quiz/expire/<int:quiz_id>', methods=['POST'])
    def manual_expire_quiz(quiz_id):
        """Manually expire a specific quiz"""
        from backend.api.quiz_tasks import expire_single_quiz
        
        task = expire_single_quiz.delay(quiz_id)
        
        return {
            'message': f'Quiz {quiz_id} expiry started',
            'task_id': task.id,
            'status': 'PENDING'
        }
    
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
        
        return response
    
    with app.app_context():
        db.create_all()
        create_admin_user()
        
    return app

if __name__ == '__main__':
    app = create_app()
    # Now app.celery exists because we created it in create_app()
    celery = app.celery 
    
    app.run(debug=True, host='0.0.0.0', port=5000)