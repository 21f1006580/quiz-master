from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from backend.models.models import db, create_admin_user
from backend.routes.auth_routes import auth_bp
from backend.routes.admin_routes import admin_bp
from backend.routes.user_routes import user_bp

from celery import Celery
from celery import current_app as current_celery_app
from backend.api.celery import make_celery

import os

def create_app():
    """Create Flask application instance"""
    app = Flask(__name__)
    
    # Database configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "quizmaster.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'sudar-secret-key-change-in-production'  
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-key-change-in-production'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Tokens don't expire (change for production)

    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Initialize database with app
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    
    with app.app_context():
        db.create_all()
        create_admin_user()
    
    celery = make_celery(app)
    app.celery = celery
        
    return app
 
if __name__ == '__main__':
    app = create_app()
    CORS(app, supports_credentials=True)
    celery = app.celery 
    app.run(debug=True)