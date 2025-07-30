#!/usr/bin/env python3
"""
Integration tests for Quiz Master application
"""

import sys
import os
import subprocess
import time
import requests

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from backend.models.models import db, User, Subject, Chapter, Quiz, Question

def test_flask_app():
    """Test Flask app creation"""
    print("🧪 Testing Flask app creation...")
    try:
        app = create_app()
        print("✅ Flask app created successfully")
        return True
    except Exception as e:
        print(f"❌ Flask app creation failed: {e}")
        return False

def test_database():
    """Test database connection"""
    print("🧪 Testing database connection...")
    try:
        app = create_app()
        with app.app_context():
            users = User.query.count()
            subjects = Subject.query.count()
            chapters = Chapter.query.count()
            quizzes = Quiz.query.count()
            questions = Question.query.count()
            
            print("✅ Database connected successfully")
            print(f"   - Users: {users}")
            print(f"   - Subjects: {subjects}")
            print(f"   - Chapters: {chapters}")
            print(f"   - Quizzes: {quizzes}")
            print(f"   - Questions: {questions}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_celery_tasks():
    """Test Celery tasks import"""
    print("🧪 Testing Celery tasks...")
    try:
        from backend.api.quiz_tasks import check_and_expire_quizzes
        from backend.api.notification_tasks import send_daily_reminders
        print("✅ Celery tasks imported successfully")
        return True
    except Exception as e:
        print(f"❌ Celery tasks import failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("🧪 Testing API endpoints...")
    try:
        base_url = "http://localhost:5001/api"
        
        # Test health endpoint
        response = requests.get("http://localhost:5001/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
            
        # Test login endpoint
        login_data = {
            "user_name": "admin@gmail.com",
            "password": "admin123"
        }
        response = requests.post(f"{base_url}/auth/login", json=login_data, timeout=5)
        if response.status_code == 200:
            print("✅ Login endpoint working")
        else:
            print(f"❌ Login endpoint failed: {response.status_code}")
            return False
            
        return True
    except requests.exceptions.ConnectionError:
        print("❌ API test failed: Server not running")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_frontend_build():
    """Test frontend build"""
    print("🧪 Testing frontend build...")
    try:
        result = subprocess.run(['npm', 'run', 'build'], 
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✅ Frontend build successful")
            return True
        else:
            print(f"❌ Frontend build failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Frontend build test failed: {e}")
        return False

def test_startup_script():
    """Test startup script syntax"""
    print("🧪 Testing startup script...")
    try:
        # Test bash script syntax
        result = subprocess.run(['bash', '-n', 'start.sh'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Startup script syntax is valid")
            return True
        else:
            print(f"❌ Startup script syntax error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Startup script test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 Starting Quiz Master Integration Tests...")
    print("=" * 50)
    
    tests = [
        test_flask_app,
        test_database,
        test_celery_tasks,
        test_api_endpoints,
        test_frontend_build,
        test_startup_script
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Application is ready.")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 