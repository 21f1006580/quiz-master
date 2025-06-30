from flask import Flask
from models.models import db
import os

def create_app():
    """Create Flask application instance"""
    app = Flask(__name__)
    
    # Database configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "quiz_master.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'sudar-secret-key'  
    
    # Initializing database with app
    db.init_app(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)