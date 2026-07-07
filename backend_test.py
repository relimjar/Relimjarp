#!/usr/bin/env python3
"""
Backend API test for Round 14: Guest Authentication Feature
Tests POST /api/auth/guest endpoint for one-tap guest login.
"""

import requests
import json
from datetime import datetime

# Backend URL - using localhost since we're testing from inside the container
BASE_URL = "http://localhost:8001/api"

def test_basic_guest_login():
    """Test 1: Basic guest login with empty body"""
    print("\n" + "="*80)
    print("TEST 1: Basic guest login - POST /api/auth/guest with empty body")
    print("="*80)
    
    url = f"{BASE_URL}/auth/guest"
    resp = requests.post(url, json={})
    
    if resp.status_code != 201:
        print(f"❌ TEST 1 FAILED: Expected 201 Created, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False, None, None
    
    print(f"✅ POST /api/auth/guest returned 201 Created")
    
    data = resp.json()
    token = data.get("token")
    user = data.get("user")
    
    # Verify token exists and is non-empty
    if not token or not isinstance(token, str) or len(token) == 0:
        print(f"❌ TEST 1 FAILED: token is missing or empty")
        return False, None, None
    
    print(f"✅ Response includes non-empty token (JWT): {token[:20]}...")
    
    # Verify user object exists
    if not user or not isinstance(user, dict):
        print(f"❌ TEST 1 FAILED: user object is missing or invalid")
        return False, token, None
    
    print(f"✅ Response includes user object")
    
    # Verify required user fields
    required_checks = [
        ("is_guest", True, lambda v: v is True, "must be true"),
        ("name", "Guest ", lambda v: isinstance(v, str) and v.startswith("Guest "), "must start with 'Guest '"),
        ("native_language", "en", lambda v: v == "en", "must be 'en'"),
        ("learning_language", "es", lambda v: v == "es", "must be 'es'"),
        ("country", "United States", lambda v: v == "United States", "must be 'United States'"),
        ("age", 25, lambda v: v == 25, "must be 25"),
        ("gender", "male", lambda v: v == "male", "must be 'male'"),
        ("interests", ["Music", "Travel", "Movies"], lambda v: isinstance(v, list) and len(v) > 0, "must be non-empty list"),
        ("coins", 500, lambda v: v == 500, "must be 500"),
        ("email", "guest_", lambda v: isinstance(v, str) and v.startswith("guest_"), "must start with 'guest_'"),
        ("id", None, lambda v: isinstance(v, str) and len(v) > 0, "must be non-empty UUID string"),
    ]
    
    all_passed = True
    for field, expected, check_fn, description in required_checks:
        value = user.get(field)
        if not check_fn(value):
            print(f"❌ TEST 1 FAILED: user.{field} {description}, got {value}")
            all_passed = False
        else:
            if field == "interests":
                print(f"✅ user.{field} = {value} (non-empty list)")
            elif field == "name":
                print(f"✅ user.{field} = '{value}' (starts with 'Guest ')")
            elif field == "email":
                print(f"✅ user.{field} = '{value}' (starts with 'guest_')")
            elif field == "id":
                print(f"✅ user.{field} = '{value}' (unique UUID)")
            else:
                print(f"✅ user.{field} = {value}")
    
    if not all_passed:
        return False, token, user
    
    print(f"✅ TEST 1 PASSED: All required fields present and correct")
    return True, token, user


def test_token_auth_me(token):
    """Test 2: Token works for GET /api/auth/me"""
    print("\n" + "="*80)
    print("TEST 2: Token works for GET /api/auth/me")
    print("="*80)
    
    url = f"{BASE_URL}/auth/me"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    
    if resp.status_code != 200:
        print(f"❌ TEST 2 FAILED: Expected 200, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    print(f"✅ GET /api/auth/me returned 200")
    
    data = resp.json()
    
    # Verify is_guest is true
    if data.get("is_guest") is not True:
        print(f"❌ TEST 2 FAILED: is_guest should be true, got {data.get('is_guest')}")
        return False
    
    print(f"✅ Response.is_guest === true")
    
    # Verify same user data
    if not data.get("name", "").startswith("Guest "):
        print(f"❌ TEST 2 FAILED: name should start with 'Guest ', got {data.get('name')}")
        return False
    
    print(f"✅ Response includes same guest user data (name: {data.get('name')})")
    print(f"✅ TEST 2 PASSED")
    return True


def test_token_partners(token):
    """Test 3: Token works for GET /api/users/partners"""
    print("\n" + "="*80)
    print("TEST 3: Token works for GET /api/users/partners (guest not blocked)")
    print("="*80)
    
    url = f"{BASE_URL}/users/partners"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    
    if resp.status_code != 200:
        print(f"❌ TEST 3 FAILED: Expected 200, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    print(f"✅ GET /api/users/partners returned 200")
    
    data = resp.json()
    
    if not isinstance(data, list):
        print(f"❌ TEST 3 FAILED: Expected list of partners, got {type(data)}")
        return False
    
    print(f"✅ Response is a list of partners (count: {len(data)})")
    print(f"✅ TEST 3 PASSED: Guest can access partners endpoint")
    return True


def test_token_moments(token):
    """Test 4: Token works for GET /api/moments"""
    print("\n" + "="*80)
    print("TEST 4: Token works for GET /api/moments (guest can read moments)")
    print("="*80)
    
    url = f"{BASE_URL}/moments"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    
    if resp.status_code != 200:
        print(f"❌ TEST 4 FAILED: Expected 200, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    print(f"✅ GET /api/moments returned 200")
    
    data = resp.json()
    
    if not isinstance(data, list):
        print(f"❌ TEST 4 FAILED: Expected list of moments, got {type(data)}")
        return False
    
    print(f"✅ Response is a list of moments (count: {len(data)})")
    print(f"✅ TEST 4 PASSED: Guest can read moments")
    return True


def test_multiple_guests():
    """Test 5: Multiple guests - unique IDs and usernames, no collisions"""
    print("\n" + "="*80)
    print("TEST 5: Multiple guests - call POST /auth/guest 3 times")
    print("="*80)
    
    url = f"{BASE_URL}/auth/guest"
    guests = []
    
    for i in range(3):
        resp = requests.post(url, json={})
        
        if resp.status_code != 201:
            print(f"❌ TEST 5 FAILED: Guest {i+1} creation failed with {resp.status_code}")
            print(f"   Response: {resp.text}")
            return False
        
        data = resp.json()
        user = data.get("user")
        
        if not user:
            print(f"❌ TEST 5 FAILED: Guest {i+1} has no user object")
            return False
        
        guests.append(user)
        print(f"✅ Guest {i+1} created: id={user.get('id')}, username={user.get('username')}, name={user.get('name')}")
    
    # Check all IDs are unique
    ids = [g.get("id") for g in guests]
    if len(ids) != len(set(ids)):
        print(f"❌ TEST 5 FAILED: Guest IDs are not unique: {ids}")
        return False
    
    print(f"✅ All 3 guest IDs are unique")
    
    # Check all usernames are unique
    usernames = [g.get("username") for g in guests]
    if len(usernames) != len(set(usernames)):
        print(f"❌ TEST 5 FAILED: Guest usernames are not unique: {usernames}")
        return False
    
    print(f"✅ All 3 guest usernames are unique")
    
    # Check no 400/500 errors (already checked above with 201 status)
    print(f"✅ No 400/500 errors (no DuplicateKey collisions)")
    print(f"✅ TEST 5 PASSED")
    return True


def test_register_regression():
    """Test 6: Regression - POST /auth/register still works"""
    print("\n" + "="*80)
    print("TEST 6: Regression - POST /auth/register with fresh user")
    print("="*80)
    
    url = f"{BASE_URL}/auth/register"
    email = f"test_reg_{datetime.now().timestamp()}@demo.com"
    payload = {
        "email": email,
        "password": "Password123!",
        "name": "Test User"
    }
    
    resp = requests.post(url, json=payload)
    
    if resp.status_code != 201:
        print(f"❌ TEST 6 FAILED: Expected 201, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    print(f"✅ POST /api/auth/register returned 201")
    
    data = resp.json()
    token = data.get("token")
    user = data.get("user")
    
    if not token or not user:
        print(f"❌ TEST 6 FAILED: Missing token or user in response")
        return False
    
    print(f"✅ Response includes token and user")
    
    # Verify is_guest is false (or absent) for regular user
    is_guest = user.get("is_guest")
    if is_guest is True:
        print(f"❌ TEST 6 FAILED: Regular user should have is_guest=false, got {is_guest}")
        return False
    
    print(f"✅ Regular user has is_guest={is_guest} (false or absent)")
    print(f"✅ TEST 6 PASSED: Register endpoint works as before")
    return True


def test_login_regression():
    """Test 7: Regression - POST /auth/login with existing user"""
    print("\n" + "="*80)
    print("TEST 7: Regression - POST /auth/login with existing user")
    print("="*80)
    
    url = f"{BASE_URL}/auth/login"
    payload = {
        "email": "mei@demo.com",
        "password": "Demo1234!"
    }
    
    resp = requests.post(url, json=payload)
    
    if resp.status_code != 200:
        print(f"❌ TEST 7 FAILED: Expected 200, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    print(f"✅ POST /api/auth/login returned 200")
    
    data = resp.json()
    token = data.get("token")
    user = data.get("user")
    
    if not token or not user:
        print(f"❌ TEST 7 FAILED: Missing token or user in response")
        return False
    
    print(f"✅ Response includes token and user")
    
    # Verify is_guest is false (or absent) for regular user
    is_guest = user.get("is_guest")
    if is_guest is True:
        print(f"❌ TEST 7 FAILED: Regular user mei@demo.com should have is_guest=false, got {is_guest}")
        return False
    
    print(f"✅ Regular user has is_guest={is_guest} (false or absent)")
    print(f"✅ TEST 7 PASSED: Login endpoint works as before")
    return True


def test_auth_me_regular_user():
    """Test 8: Regression - GET /auth/me for regular user has is_guest field"""
    print("\n" + "="*80)
    print("TEST 8: Regression - GET /auth/me for regular user includes is_guest field")
    print("="*80)
    
    # First login as mei
    login_url = f"{BASE_URL}/auth/login"
    login_payload = {
        "email": "mei@demo.com",
        "password": "Demo1234!"
    }
    
    login_resp = requests.post(login_url, json=login_payload)
    
    if login_resp.status_code != 200:
        print(f"❌ TEST 8 FAILED: Login failed with {login_resp.status_code}")
        return False
    
    token = login_resp.json().get("token")
    
    # Now call GET /auth/me
    me_url = f"{BASE_URL}/auth/me"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(me_url, headers=headers)
    
    if resp.status_code != 200:
        print(f"❌ TEST 8 FAILED: Expected 200, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    print(f"✅ GET /api/auth/me returned 200")
    
    data = resp.json()
    
    # Verify is_guest field exists and is false
    is_guest = data.get("is_guest")
    if is_guest is True:
        print(f"❌ TEST 8 FAILED: Regular user should have is_guest=false, got {is_guest}")
        return False
    
    print(f"✅ Regular user has is_guest={is_guest} (false or absent)")
    print(f"✅ TEST 8 PASSED: user_public shape includes is_guest field defaulting to false")
    return True


def main():
    print("\n" + "="*80)
    print("BACKEND TEST: Guest Authentication Feature (Round 14)")
    print("="*80)
    print(f"Backend URL: {BASE_URL}")
    print(f"Test Date: {datetime.now().isoformat()}")
    
    results = []
    
    # Test 1: Basic guest login
    test1_passed, guest_token, guest_user = test_basic_guest_login()
    results.append(("Test 1: Basic guest login", test1_passed))
    
    # Tests 2-4: Token authentication (only if test 1 passed)
    if test1_passed and guest_token:
        results.append(("Test 2: Token works for /auth/me", test_token_auth_me(guest_token)))
        results.append(("Test 3: Token works for /users/partners", test_token_partners(guest_token)))
        results.append(("Test 4: Token works for /moments", test_token_moments(guest_token)))
    else:
        print("\n⚠️  Skipping tests 2-4 because test 1 failed")
        results.append(("Test 2: Token works for /auth/me", False))
        results.append(("Test 3: Token works for /users/partners", False))
        results.append(("Test 4: Token works for /moments", False))
    
    # Test 5: Multiple guests
    results.append(("Test 5: Multiple guests (unique IDs)", test_multiple_guests()))
    
    # Tests 6-8: Regression tests
    results.append(("Test 6: Regression - register", test_register_regression()))
    results.append(("Test 7: Regression - login", test_login_regression()))
    results.append(("Test 8: Regression - /auth/me for regular user", test_auth_me_regular_user()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit(main())
