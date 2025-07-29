from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from backend.models.models import User

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        try:
            # Get JWT claims
            claims = get_jwt()
            
            # Check if user is admin
            if not claims.get('is_admin', False):
                return jsonify({'error': 'Admin access required'}), 403
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authentication failed', 'details': str(e)}), 401
    
    return decorated_function

def user_required(f):
    """Decorator to require authenticated user (admin or regular user)"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        try:
            current_user = get_jwt_identity()
            user = User.query.filter_by(user_name=current_user).first()
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authentication failed', 'details': str(e)}), 401
    
    return decorated_function

def get_current_user():
    """Helper function to get current user object"""
    try:
        current_user = get_jwt_identity()
        return User.query.filter_by(user_name=current_user).first()
    except:
        return None