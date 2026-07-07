#!/usr/bin/env python3
"""
Backend API test for Round 13: Birthday → Derived Age Feature
Tests PUT /api/users/me with birthday field that derives age automatically.
"""

import requests
import json
from datetime import datetime

# Backend URL - using localhost since we're testing from inside the container
BASE_URL = "http://localhost:8001/api"

def register_user(email, password="Password123!", name="DOB Tester"):
    """Register a fresh user and return token + user data."""
    url = f"{BASE_URL}/auth/register"
    payload = {
        "email": email,
        "password": password,
        "name": name
    }
    resp = requests.post(url, json=payload)
    if resp.status_code != 201:
        print(f"❌ Registration failed for {email}: {resp.status_code} {resp.text}")
        return None, None
    data = resp.json()
    return data.get("token"), data.get("user")

def update_profile(token, updates):
    """PUT /api/users/me with given updates."""
    url = f"{BASE_URL}/users/me"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.put(url, json=updates, headers=headers)
    return resp

def get_me(token):
    """GET /api/auth/me to verify current user state."""
    url = f"{BASE_URL}/auth/me"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    return resp

def test_scenario_1_happy_path():
    """Test 1: Happy path — birthday derives age"""
    print("\n" + "="*80)
    print("TEST 1: Happy path — birthday derives age")
    print("="*80)
    
    # Register fresh user
    email = f"dob_test_happy_{datetime.now().timestamp()}@demo.com"
    token, user = register_user(email)
    if not token:
        print("❌ TEST 1 FAILED: Could not register user")
        return False
    print(f"✅ Registered user: {email}")
    
    # Update with birthday and other fields
    updates = {
        "native_language": "en",
        "learning_language": "es",
        "country": "United States",
        "birthday": "2000-05-15",
        "gender": "male",
        "interests": ["Coffee"]
    }
    resp = update_profile(token, updates)
    
    if resp.status_code != 200:
        print(f"❌ TEST 1 FAILED: PUT /api/users/me returned {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    data = resp.json()
    print(f"✅ PUT /api/users/me returned 200")
    
    # Verify age is derived correctly (should be 26 since today is 2026-07-07 and birthday is 2000-05-15)
    age = data.get("age")
    birthday = data.get("birthday")
    gender = data.get("gender")
    country = data.get("country")
    
    print(f"   Response age: {age}")
    print(f"   Response birthday: {birthday}")
    print(f"   Response gender: {gender}")
    print(f"   Response country: {country}")
    
    # Age should be 26 (2026 - 2000 = 26, and we're past May 15)
    if not isinstance(age, int):
        print(f"❌ TEST 1 FAILED: age is not an integer, got {type(age)}")
        return False
    
    if age < 25 or age > 26:
        print(f"❌ TEST 1 FAILED: age should be 25 or 26, got {age}")
        return False
    
    if birthday != "2000-05-15":
        print(f"❌ TEST 1 FAILED: birthday should be '2000-05-15', got {birthday}")
        return False
    
    if gender != "male":
        print(f"❌ TEST 1 FAILED: gender should be 'male', got {gender}")
        return False
    
    if country != "United States":
        print(f"❌ TEST 1 FAILED: country should be 'United States', got {country}")
        return False
    
    print(f"✅ TEST 1 PASSED: age={age}, birthday={birthday}, gender={gender}, country={country}")
    return True

def test_scenario_2_invalid_format():
    """Test 2: Invalid birthday format"""
    print("\n" + "="*80)
    print("TEST 2: Invalid birthday format")
    print("="*80)
    
    test_cases = [
        ("2000/05/15", "slash format"),
        ("15-05-2000", "DD-MM-YYYY format"),
        ("invalid", "invalid string")
    ]
    
    all_passed = True
    for invalid_birthday, description in test_cases:
        email = f"dob_test_invalid_{datetime.now().timestamp()}@demo.com"
        token, user = register_user(email)
        if not token:
            print(f"❌ TEST 2 ({description}) FAILED: Could not register user")
            all_passed = False
            continue
        
        updates = {"birthday": invalid_birthday}
        resp = update_profile(token, updates)
        
        if resp.status_code != 400:
            print(f"❌ TEST 2 ({description}) FAILED: Expected 400, got {resp.status_code}")
            print(f"   Response: {resp.text}")
            all_passed = False
            continue
        
        data = resp.json()
        detail = data.get("detail", "")
        
        if "Invalid birthday format" not in detail or "YYYY-MM-DD" not in detail:
            print(f"❌ TEST 2 ({description}) FAILED: Expected 'Invalid birthday format. Expected YYYY-MM-DD.', got '{detail}'")
            all_passed = False
            continue
        
        print(f"✅ TEST 2 ({description}) PASSED: Got 400 with correct error message")
    
    return all_passed

def test_scenario_3_too_young():
    """Test 3: Out-of-range age (too young)"""
    print("\n" + "="*80)
    print("TEST 3: Out-of-range age (too young)")
    print("="*80)
    
    email = f"dob_test_young_{datetime.now().timestamp()}@demo.com"
    token, user = register_user(email)
    if not token:
        print("❌ TEST 3 FAILED: Could not register user")
        return False
    
    # Birthday that makes user 6 years old
    updates = {"birthday": "2020-01-01"}
    resp = update_profile(token, updates)
    
    if resp.status_code != 400:
        print(f"❌ TEST 3 FAILED: Expected 400, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    data = resp.json()
    detail = data.get("detail", "")
    
    if "Age must be between 13 and 120" not in detail:
        print(f"❌ TEST 3 FAILED: Expected 'Age must be between 13 and 120.', got '{detail}'")
        return False
    
    print(f"✅ TEST 3 PASSED: Got 400 with correct error message")
    return True

def test_scenario_4_future_date():
    """Test 4: Out-of-range age (future date)"""
    print("\n" + "="*80)
    print("TEST 4: Out-of-range age (future date)")
    print("="*80)
    
    email = f"dob_test_future_{datetime.now().timestamp()}@demo.com"
    token, user = register_user(email)
    if not token:
        print("❌ TEST 4 FAILED: Could not register user")
        return False
    
    # Future birthday
    updates = {"birthday": "2030-01-01"}
    resp = update_profile(token, updates)
    
    if resp.status_code != 400:
        print(f"❌ TEST 4 FAILED: Expected 400, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    data = resp.json()
    detail = data.get("detail", "")
    
    if "Age must be between 13 and 120" not in detail:
        print(f"❌ TEST 4 FAILED: Expected 'Age must be between 13 and 120.', got '{detail}'")
        return False
    
    print(f"✅ TEST 4 PASSED: Got 400 with correct error message")
    return True

def test_scenario_5_age_lock():
    """Test 5: Age lock (birthday cannot change once set)"""
    print("\n" + "="*80)
    print("TEST 5: Age lock (birthday cannot change once set)")
    print("="*80)
    
    email = f"dob_test_lock_{datetime.now().timestamp()}@demo.com"
    token, user = register_user(email)
    if not token:
        print("❌ TEST 5 FAILED: Could not register user")
        return False
    
    # First PUT with birthday
    updates1 = {"birthday": "2000-05-15"}
    resp1 = update_profile(token, updates1)
    
    if resp1.status_code != 200:
        print(f"❌ TEST 5 FAILED: First PUT returned {resp1.status_code}")
        print(f"   Response: {resp1.text}")
        return False
    
    data1 = resp1.json()
    birthday1 = data1.get("birthday")
    age1 = data1.get("age")
    
    print(f"✅ First PUT successful: birthday={birthday1}, age={age1}")
    
    if birthday1 != "2000-05-15":
        print(f"❌ TEST 5 FAILED: First birthday should be '2000-05-15', got {birthday1}")
        return False
    
    if age1 != 26:
        print(f"❌ TEST 5 FAILED: First age should be 26, got {age1}")
        return False
    
    # Second PUT trying to change birthday (should be silently ignored)
    updates2 = {"birthday": "1990-01-01"}
    resp2 = update_profile(token, updates2)
    
    if resp2.status_code != 200:
        print(f"❌ TEST 5 FAILED: Second PUT returned {resp2.status_code}")
        print(f"   Response: {resp2.text}")
        return False
    
    print(f"✅ Second PUT returned 200 (silently ignored)")
    
    # Verify via GET /api/auth/me that birthday and age are unchanged
    resp_me = get_me(token)
    if resp_me.status_code != 200:
        print(f"❌ TEST 5 FAILED: GET /api/auth/me returned {resp_me.status_code}")
        return False
    
    data_me = resp_me.json()
    birthday_final = data_me.get("birthday")
    age_final = data_me.get("age")
    
    print(f"   GET /api/auth/me: birthday={birthday_final}, age={age_final}")
    
    if birthday_final != "2000-05-15":
        print(f"❌ TEST 5 FAILED: Birthday should still be '2000-05-15', got {birthday_final}")
        return False
    
    if age_final != 26:
        print(f"❌ TEST 5 FAILED: Age should still be 26, got {age_final}")
        return False
    
    print(f"✅ TEST 5 PASSED: Birthday and age locked correctly")
    return True

def test_scenario_6_backward_compat():
    """Test 6: Backward compat — text-only update"""
    print("\n" + "="*80)
    print("TEST 6: Backward compat — text-only update")
    print("="*80)
    
    email = f"dob_test_compat_{datetime.now().timestamp()}@demo.com"
    token, user = register_user(email)
    if not token:
        print("❌ TEST 6 FAILED: Could not register user")
        return False
    
    # Update with just bio (no birthday)
    updates = {"bio": "hello there"}
    resp = update_profile(token, updates)
    
    if resp.status_code != 200:
        print(f"❌ TEST 6 FAILED: PUT returned {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    data = resp.json()
    bio = data.get("bio")
    
    if bio != "hello there":
        print(f"❌ TEST 6 FAILED: bio should be 'hello there', got {bio}")
        return False
    
    print(f"✅ TEST 6 PASSED: Text-only update works, bio={bio}")
    return True

def test_scenario_7_direct_age():
    """Test 7: Existing behavior — direct age still works when birthday NOT set"""
    print("\n" + "="*80)
    print("TEST 7: Existing behavior — direct age still works when birthday NOT set")
    print("="*80)
    
    email = f"dob_test_direct_{datetime.now().timestamp()}@demo.com"
    token, user = register_user(email)
    if not token:
        print("❌ TEST 7 FAILED: Could not register user")
        return False
    
    # Update with direct age (no birthday)
    updates = {"age": 30, "gender": "female"}
    resp = update_profile(token, updates)
    
    if resp.status_code != 200:
        print(f"❌ TEST 7 FAILED: PUT returned {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    data = resp.json()
    age = data.get("age")
    
    if age != 30:
        print(f"❌ TEST 7 FAILED: age should be 30, got {age}")
        return False
    
    print(f"✅ TEST 7 PASSED: Direct age update works, age={age}")
    return True

def main():
    print("\n" + "="*80)
    print("BACKEND TEST: Birthday → Derived Age Feature (Round 13)")
    print("="*80)
    print(f"Backend URL: {BASE_URL}")
    print(f"Test Date: {datetime.now().isoformat()}")
    
    results = []
    
    # Run all test scenarios
    results.append(("Test 1: Happy path", test_scenario_1_happy_path()))
    results.append(("Test 2: Invalid format", test_scenario_2_invalid_format()))
    results.append(("Test 3: Too young", test_scenario_3_too_young()))
    results.append(("Test 4: Future date", test_scenario_4_future_date()))
    results.append(("Test 5: Age lock", test_scenario_5_age_lock()))
    results.append(("Test 6: Backward compat", test_scenario_6_backward_compat()))
    results.append(("Test 7: Direct age", test_scenario_7_direct_age()))
    
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
