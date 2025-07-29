from flask import Blueprint, request, jsonify, render_template,redirect
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from backend.models.models import db, User
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint('auth', __name__,url_prefix='api/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user"""

    if request.method == 'GET':
        return render_template('register.html')
        
    try:
        # Handle both JSON (API) and form data (HTML form)
        if request.is_json:
            # API request with JSON data
            data = request.get_json()
        else:
            # HTML form request with form data
            data = {
                'user_name': request.form.get('user_name'),
                'password': request.form.get('password'),
                'full_name': request.form.get('full_name'),
                'qualification': request.form.get('qualification'),
                'date_of_birth': request.form.get('date_of_birth')
            }
        
        # Validate required fields
        required_fields = ['user_name', 'password', 'full_name']
        for field in required_fields:
            if not data.get(field):
                if request.is_json:
                    return jsonify({'error': f'{field} is required'}), 400
                else:
                    return f"{field} is required", 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(user_name=data['user_name']).first()
        if existing_user:
            if request.is_json:
                return jsonify({'error': 'User already exists'}), 409
            else:
                return "User already exists", 409
        
        # Create new user
        user = User(
            user_name=data['user_name'],
            full_name=data['full_name'],
            qualification=data.get('qualification'),
            is_admin=False  # Regular users are not admin
        )
        
        # Parse date_of_birth if provided
        if data.get('date_of_birth'):
            try:
                user.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            except ValueError:
                if request.is_json:
                    return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
                else:
                    return "Invalid date format. Use YYYY-MM-DD", 400
        
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        access_token = create_access_token(identity=user.user_name)
        
        # Return appropriate response based on request type
        if request.is_json:
            return jsonify({
                'message': 'User registered successfully',
                'access_token': access_token,   
                'user': user.to_dict()
            }), 201
        else:
            # For HTML form, redirect to login page
            return redirect('/api/auth/login')
        
    except IntegrityError:
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': 'User already exists'}), 409
        else:
            return "User already exists", 409
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': 'Registration failed', 'details': str(e)}), 500
        else:
            return f"Registration failed: {str(e)}", 500

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login user and return JWT token"""

    if request.method == 'GET':
        return render_template('login.html')
    
    try:
        # Handle both JSON (API) and form data (HTML form)
        if request.is_json:
            # API request with JSON data
            data = request.get_json()
        else:
            # HTML form request with form data
            data = {
                'user_name': request.form.get('user_name'),
                'password': request.form.get('password')
            }
        print("Form data received:", data)
        
        # Validate required fields
        if not data.get('user_name') or not data.get('password'):
            if request.is_json:
                return jsonify({'error': 'Username and password are required'}), 400
            else:
                return "Username and password are required", 400
        
        # Find user
        user = User.query.filter_by(user_name=data['user_name']).first()
        
        if not user or not user.check_password(data['password']):
            if request.is_json:
                return jsonify({'error': 'Invalid credentials'}), 401
            else:
                return "Invalid credentials", 401
        
        # Create JWT token with user info
        additional_claims = {
            'user_id': user.user_id,
            'is_admin': user.is_admin,
            'full_name': user.full_name
        }
        
        access_token = create_access_token(
            identity=user.user_name,
            additional_claims=additional_claims
        )
        
        # Return appropriate response based on request type
        if request.is_json:
            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,  
                'user': user.to_dict()
            }), 200
        else:
            # For HTML form, you might want to redirect to a dashboard
            # or set the token in a cookie/session for web app usage
            return f"Login successful! Welcome {user.full_name}"
        
    except Exception as e:
        print(f"Exception duing Login: {e}")
        if request.is_json:

            return jsonify({'error': 'Login failed', 'details': str(e)}), 500
        else:
            return f"Login failed: {str(e)}", 500

@auth_bp.route('/admin-login', methods=['POST'])
def admin_login():
    """Admin login endpoint"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('user_name') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Find user and check if admin
        user = User.query.filter_by(user_name=data['user_name'], is_admin=True).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid admin credentials'}), 401
        
        # Create JWT token with admin info
        additional_claims = {
            'user_id': user.user_id,
            'is_admin': user.is_admin,
            'full_name': user.full_name
        }
        
        access_token = create_access_token(
            identity=user.user_name,
            additional_claims=additional_claims
        )
        
        return jsonify({
            'message': 'Admin login successful',
            'access_token': access_token,  
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Admin login failed', 'details': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(user_name=current_user).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get profile', 'details': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('old_password') or not data.get('new_password'):
            return jsonify({'error': 'Old password and new password are required'}), 400
        
        user = User.query.filter_by(user_name=current_user).first()
        
        if not user or not user.check_password(data['old_password']):
            return jsonify({'error': 'Invalid old password'}), 401
        
        user.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to change password', 'details': str(e)}), 500
