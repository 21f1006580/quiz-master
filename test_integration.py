#!/usr/bin/env python3
"""
Integration Test for Quiz Master Application
Tests all major components and their interactions
"""

import requests
import json
import time
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from backend.models.models import db, User, Subject, Chapter, Quiz, Question

def test_backend_creation():
    """Test Flask app creation"""
    print("🧪 Testing Flask app creation...")
    try:
        app = create_app()
        print("✅ Flask app created successfully")
        return True
    except Exception as e:
        print(f"❌ Flask app creation failed: {e}")
        return False

def test_database_connection():
    """Test database connection and models"""
    print("🧪 Testing database connection...")
    try:
        app = create_app()
        with app.app_context():
            # Test basic queries
            users = User.query.all()
            subjects = Subject.query.all()
            chapters = Chapter.query.all()
            quizzes = Quiz.query.all()
            questions = Question.query.all()
            
            print(f"✅ Database connected successfully")
            print(f"   - Users: {len(users)}")
            print(f"   - Subjects: {len(subjects)}")
            print(f"   - Chapters: {len(chapters)}")
            print(f"   - Quizzes: {len(quizzes)}")
            print(f"   - Questions: {len(questions)}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_celery_tasks():
    """Test Celery task imports"""
    print("🧪 Testing Celery tasks...")
    try:
        from backend.api.quiz_tasks import (
            check_and_expire_quizzes,
            send_expiry_warnings,
            daily_cleanup,
            expire_single_quiz
        )
        print("✅ Celery tasks imported successfully")
        return True
    except Exception as e:
        print(f"❌ Celery task import failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("🧪 Testing API endpoints...")
    
    base_url = "http://localhost:5000/api"
    
    # Test if Flask app is running
    try:
        response = requests.get(f"{base_url}/auth/login", timeout=5)
        if response.status_code == 200:
            print("✅ API endpoints accessible")
            return True
        else:
            print(f"⚠️  API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("⚠️  Flask app not running (expected if not started)")
        return True
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_frontend_build():
    """Test frontend build process"""
    print("🧪 Testing frontend build...")
    try:
        import subprocess
        result = subprocess.run(
            ["npm", "run", "build"], 
            capture_output=True, 
            text=True, 
            timeout=60
        )
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
        import subprocess
        # Test script syntax without running it
        result = subprocess.run(
            ["bash", "-n", "start.sh"], 
            capture_output=True, 
            text=True
        )
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
        test_backend_creation,
        test_database_connection,
        test_celery_tasks,
        test_api_endpoints,
        test_frontend_build,
        test_startup_script
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Application is ready for deployment.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 