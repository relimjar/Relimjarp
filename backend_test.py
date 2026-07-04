#!/usr/bin/env python3
"""
Backend API Testing Script for LinguaConnect
Tests auth flow, DB connectivity, and core endpoints after .env fix
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend/.env
BASE_URL = "https://368bd428-054d-4ed0-be5c-b4aaf6dfeef5.preview.emergentagent.com"
API_URL = f"{BASE_URL}/api"

# Test credentials
ADMIN_EMAIL = "admin@lingua.app"
ADMIN_PASSWORD = "Admin1234!"

# Generate unique test user email with timestamp
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
TEST_USER_EMAIL = f"testuser_{timestamp}@lingua.app"
TEST_USER_PASSWORD = "TestPass123!"
TEST_USER_NAME = "Sarah Chen"

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(test_name):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}TEST: {test_name}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

def print_success(message):
    print(f"{GREEN}✓ {message}{RESET}")

def print_error(message):
    print(f"{RED}✗ {message}{RESET}")

def print_info(message):
    print(f"{YELLOW}ℹ {message}{RESET}")

def test_health_check():
    """Test 1: GET /api/ - Backend health check"""
    print_test("Backend Health Check - GET /api/")
    
    try:
        response = requests.get(f"{API_URL}/", timeout=10)
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("message") == "LinguaConnect API":
                print_success("Backend is reachable and healthy")
                return True
            else:
                print_error(f"Unexpected response: {data}")
                return False
        else:
            print_error(f"Expected 200, got {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check failed: {str(e)}")
        return False

def test_register_user():
    """Test 2: POST /api/auth/register - Register new test user"""
    print_test(f"User Registration - POST /api/auth/register")
    
    payload = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
        "name": TEST_USER_NAME,
        "native_languages": ["English"],
        "learning_languages": ["Spanish", "French"],
        "gender": "female"
    }
    
    print_info(f"Registering user: {TEST_USER_EMAIL}")
    print_info(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{API_URL}/auth/register",
            json=payload,
            timeout=10
        )
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.text[:500]}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            if "token" in data and "user" in data:
                print_success(f"User registered successfully: {data['user'].get('email')}")
                print_success(f"Token received: {data['token'][:20]}...")
                return True, data
            else:
                print_error(f"Missing token or user in response: {data}")
                return False, None
        else:
            print_error(f"Registration failed with status {response.status_code}")
            return False, None
    except Exception as e:
        print_error(f"Registration request failed: {str(e)}")
        return False, None

def test_login_user(email, password, user_type="test user"):
    """Test 3: POST /api/auth/login - Login with credentials"""
    print_test(f"User Login ({user_type}) - POST /api/auth/login")
    
    payload = {
        "email": email,
        "password": password
    }
    
    print_info(f"Logging in: {email}")
    
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json=payload,
            timeout=10
        )
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            if "token" in data and "user" in data:
                print_success(f"Login successful for {email}")
                print_success(f"Token received: {data['token'][:20]}...")
                print_success(f"User ID: {data['user'].get('id')}")
                return True, data
            else:
                print_error(f"Missing token or user in response: {data}")
                return False, None
        else:
            print_error(f"Login failed with status {response.status_code}")
            return False, None
    except Exception as e:
        print_error(f"Login request failed: {str(e)}")
        return False, None

def test_get_profile(token):
    """Test 4: GET /api/auth/me - Get user profile with token"""
    print_test("Get User Profile - GET /api/auth/me")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print_info(f"Using token: {token[:20]}...")
    
    try:
        response = requests.get(
            f"{API_URL}/auth/me",
            headers=headers,
            timeout=10
        )
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            if "email" in data and "id" in data:
                print_success(f"Profile retrieved: {data.get('email')}")
                print_success(f"User ID: {data.get('id')}")
                print_success(f"Name: {data.get('name')}")
                return True, data
            else:
                print_error(f"Missing expected fields in profile: {data}")
                return False, None
        else:
            print_error(f"Get profile failed with status {response.status_code}")
            return False, None
    except Exception as e:
        print_error(f"Get profile request failed: {str(e)}")
        return False, None

def test_get_partners(token):
    """Test 5: GET /api/users/partners - Check DB connectivity"""
    print_test("Get Partners List - GET /api/users/partners")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(
            f"{API_URL}/users/partners",
            headers=headers,
            timeout=10
        )
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Partners endpoint accessible (returned {len(data)} partners)")
            return True
        else:
            print_error(f"Get partners failed with status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get partners request failed: {str(e)}")
        return False

def test_get_rooms(token):
    """Test 6: GET /api/rooms - Check DB connectivity"""
    print_test("Get Rooms List - GET /api/rooms")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(
            f"{API_URL}/rooms",
            headers=headers,
            timeout=10
        )
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Rooms endpoint accessible (returned {len(data)} rooms)")
            return True
        else:
            print_error(f"Get rooms failed with status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get rooms request failed: {str(e)}")
        return False

def main():
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}LinguaConnect Backend Testing Suite{RESET}")
    print(f"{BLUE}Testing .env fix and auth flow{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"{YELLOW}Backend URL: {API_URL}{RESET}\n")
    
    results = {
        "passed": 0,
        "failed": 0,
        "total": 0
    }
    
    # Test 1: Health Check
    results["total"] += 1
    if test_health_check():
        results["passed"] += 1
    else:
        results["failed"] += 1
        print_error("CRITICAL: Backend health check failed. Stopping tests.")
        print_summary(results)
        sys.exit(1)
    
    # Test 2: Register new user
    results["total"] += 1
    register_success, register_data = test_register_user()
    if register_success:
        results["passed"] += 1
        test_user_token = register_data["token"]
    else:
        results["failed"] += 1
        print_error("CRITICAL: User registration failed. Stopping auth flow tests.")
        print_summary(results)
        sys.exit(1)
    
    # Test 3: Login with new user
    results["total"] += 1
    login_success, login_data = test_login_user(TEST_USER_EMAIL, TEST_USER_PASSWORD, "new test user")
    if login_success:
        results["passed"] += 1
        test_user_token = login_data["token"]  # Use login token
    else:
        results["failed"] += 1
        print_error("CRITICAL: User login failed. This is the 'can't enter app' issue.")
    
    # Test 4: Get profile with token
    results["total"] += 1
    if test_get_profile(test_user_token)[0]:
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 5: Login with admin account
    results["total"] += 1
    admin_login_success, admin_data = test_login_user(ADMIN_EMAIL, ADMIN_PASSWORD, "admin")
    if admin_login_success:
        results["passed"] += 1
        admin_token = admin_data["token"]
    else:
        results["failed"] += 1
        admin_token = test_user_token  # Fallback to test user token
    
    # Test 6: Get partners (DB connectivity check)
    results["total"] += 1
    if test_get_partners(admin_token):
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 7: Get rooms (DB connectivity check)
    results["total"] += 1
    if test_get_rooms(admin_token):
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    print_summary(results)
    
    # Exit with appropriate code
    if results["failed"] == 0:
        sys.exit(0)
    else:
        sys.exit(1)

def print_summary(results):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}TEST SUMMARY{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"Total Tests: {results['total']}")
    print(f"{GREEN}Passed: {results['passed']}{RESET}")
    print(f"{RED}Failed: {results['failed']}{RESET}")
    
    if results["failed"] == 0:
        print(f"\n{GREEN}✓ ALL TESTS PASSED - Backend is fully operational{RESET}")
        print(f"{GREEN}✓ Auth flow working - 'Can't enter app' issue is RESOLVED{RESET}")
    else:
        print(f"\n{RED}✗ SOME TESTS FAILED - See details above{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

if __name__ == "__main__":
    main()
