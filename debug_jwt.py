#!/usr/bin/env python3
"""
Debug script to test JWT token authentication
"""

import requests
import json
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:5001/api"

def test_health():
    """Test if the API is running"""
    try:
        response = requests.get(f"{BASE_URL.replace('/api', '')}/health")
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print("✅ API is running")
            return True
        else:
            print("❌ API is not responding properly")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

def test_login():
    """Test login and get JWT token"""
    try:
        login_data = {
            "user_name": "admin@gmail.com",
            "password": "admin123"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Login response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print("✅ Login successful")
            print(f"Token: {token[:50]}..." if token else "No token received")
            return token
        else:
            print(f"❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_protected_endpoint(token, endpoint):
    """Test a protected endpoint with JWT token"""
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        print(f"{endpoint}: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ {endpoint} successful")
            return True
        else:
            print(f"❌ {endpoint} failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ {endpoint} error: {e}")
        return False

def main():
    print("🔍 JWT Debug Script")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health():
        print("Cannot proceed - API is not running")
        return
    
    print()
    
    # Test 2: Login
    token = test_login()
    if not token:
        print("Cannot proceed - Login failed")
        return
    
    print()
    
    # Test 3: Test protected endpoints
    endpoints = [
        "/user/dashboard",
        "/user/scores", 
        "/user/score-summary",
        "/admin/dashboard/stats"
    ]
    
    print("Testing protected endpoints:")
    for endpoint in endpoints:
        test_protected_endpoint(token, endpoint)
        print()

if __name__ == "__main__":
    main() 