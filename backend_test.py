#!/usr/bin/env python3
"""
Backend test for Daily Phrase + Check-in Rewards feature
Tests GET /api/phrases/daily and POST /api/users/me/check-in
"""
import requests
import json
import time

BASE_URL = "https://edf855b1-a946-4795-a4f1-66392dbb697e.preview.emergentagent.com/api"

# Test credentials
USER_MEI = {"email": "mei@demo.com", "password": "Demo1234!"}

def login(email, password):
    """Login and return auth token"""
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    if resp.status_code != 200:
        print(f"❌ Login failed for {email}: {resp.status_code} {resp.text}")
        return None
    data = resp.json()
    return data.get("token")

def register_new_user():
    """Register a brand new user for check-in testing"""
    timestamp = int(time.time())
    email = f"testuser_{timestamp}@lingua.app"
    password = "Test1234!"
    name = f"Test User {timestamp}"
    
    resp = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email,
        "password": password,
        "name": name
    })
    
    if resp.status_code != 201:
        print(f"❌ Registration failed: {resp.status_code} {resp.text}")
        return None, None
    
    data = resp.json()
    return data.get("token"), email

def get_headers(token):
    """Get auth headers"""
    return {"Authorization": f"Bearer {token}"}

def print_step(step_num, description):
    """Print test step header"""
    print(f"\n{'='*80}")
    print(f"STEP {step_num}: {description}")
    print('='*80)

def main():
    print("🧪 DAILY PHRASE + CHECK-IN REWARDS FEATURE TEST")
    print("="*80)
    
    # ========================================================================
    # PART 1: GET /api/phrases/daily TESTS
    # ========================================================================
    print("\n" + "="*80)
    print("PART 1: GET /api/phrases/daily TESTS")
    print("="*80)
    
    # Login mei for phrase tests
    print("\n📝 Logging in mei@demo.com...")
    token_mei = login(USER_MEI["email"], USER_MEI["password"])
    
    if not token_mei:
        print("❌ Failed to login mei@demo.com. Aborting test.")
        return
    
    print(f"✅ mei@demo.com logged in")
    headers_mei = get_headers(token_mei)
    
    # TEST 1: Without auth → 401/403
    print_step(1, "GET /api/phrases/daily WITHOUT auth → expect 401/403")
    resp = requests.get(f"{BASE_URL}/phrases/daily")
    print(f"Status: {resp.status_code}")
    
    if resp.status_code not in [401, 403]:
        print(f"❌ FAILED: Expected 401 or 403, got {resp.status_code}")
        return
    
    print(f"✅ PASSED: Correctly rejected without auth ({resp.status_code})")
    
    # TEST 2: With auth, ?lang=ja → 200 with roman (non-null)
    print_step(2, "GET /api/phrases/daily?lang=ja WITH auth → expect 200 with roman non-null")
    resp = requests.get(f"{BASE_URL}/phrases/daily?lang=ja", headers=headers_mei)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"❌ FAILED: Expected 200, got {resp.status_code}")
        print(f"Response: {resp.text}")
        return
    
    data = resp.json()
    print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    # Verify required fields
    required_fields = ["lang", "lang_name", "text", "roman", "meaning", "category", "date"]
    for field in required_fields:
        if field not in data:
            print(f"❌ FAILED: Missing required field '{field}'")
            return
    
    if data["lang"] != "ja":
        print(f"❌ FAILED: Expected lang='ja', got '{data['lang']}'")
        return
    
    if data["lang_name"] != "Japanese":
        print(f"❌ FAILED: Expected lang_name='Japanese', got '{data['lang_name']}'")
        return
    
    if data["roman"] is None:
        print(f"❌ FAILED: Expected roman to be non-null for Japanese, got None")
        return
    
    print(f"✅ PASSED: Japanese phrase with all required fields")
    print(f"   lang: {data['lang']}")
    print(f"   lang_name: {data['lang_name']}")
    print(f"   text: {data['text']}")
    print(f"   roman: {data['roman']}")
    print(f"   meaning: {data['meaning']}")
    print(f"   category: {data['category']}")
    print(f"   date: {data['date']}")
    
    # TEST 3: ?lang=en → roman is null
    print_step(3, "GET /api/phrases/daily?lang=en → expect roman is null")
    resp = requests.get(f"{BASE_URL}/phrases/daily?lang=en", headers=headers_mei)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"❌ FAILED: Expected 200, got {resp.status_code}")
        return
    
    data = resp.json()
    print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    if data["lang"] != "en":
        print(f"❌ FAILED: Expected lang='en', got '{data['lang']}'")
        return
    
    if data["roman"] is not None:
        print(f"❌ FAILED: Expected roman to be null for English, got '{data['roman']}'")
        return
    
    print(f"✅ PASSED: English phrase with roman=null")
    print(f"   text: {data['text']}")
    print(f"   meaning: {data['meaning']}")
    
    # TEST 4: ?lang=zz (invalid) → falls back to user's learning language or "en"
    print_step(4, "GET /api/phrases/daily?lang=zz (invalid) → expect fallback, still 200")
    resp = requests.get(f"{BASE_URL}/phrases/daily?lang=zz", headers=headers_mei)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"❌ FAILED: Expected 200 (fallback), got {resp.status_code}")
        return
    
    data = resp.json()
    print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    # Should fallback to a valid language (user's learning language or 'en')
    valid_langs = ["en", "es", "fr", "de", "it", "pt", "zh", "ja", "ko", "ru", "ar", "hi", "tr", "nl", "pl", "sv", "vi", "th", "id", "el"]
    if data["lang"] not in valid_langs:
        print(f"❌ FAILED: Expected fallback to valid language, got '{data['lang']}'")
        return
    
    print(f"✅ PASSED: Invalid lang code falls back to '{data['lang']}' (still 200)")
    
    # TEST 5: No lang param → uses user's learning language
    print_step(5, "GET /api/phrases/daily (no lang param) → expect 200, uses user's learning language")
    resp = requests.get(f"{BASE_URL}/phrases/daily", headers=headers_mei)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"❌ FAILED: Expected 200, got {resp.status_code}")
        return
    
    data = resp.json()
    print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    if data["lang"] not in valid_langs:
        print(f"❌ FAILED: Expected valid language, got '{data['lang']}'")
        return
    
    print(f"✅ PASSED: No lang param returns phrase in '{data['lang']}'")
    
    # ========================================================================
    # PART 2: POST /api/users/me/check-in TESTS
    # ========================================================================
    print("\n" + "="*80)
    print("PART 2: POST /api/users/me/check-in TESTS")
    print("="*80)
    
    # TEST 6: Without auth → 401/403
    print_step(6, "POST /api/users/me/check-in WITHOUT auth → expect 401/403")
    resp = requests.post(f"{BASE_URL}/users/me/check-in")
    print(f"Status: {resp.status_code}")
    
    if resp.status_code not in [401, 403]:
        print(f"❌ FAILED: Expected 401 or 403, got {resp.status_code}")
        return
    
    print(f"✅ PASSED: Correctly rejected without auth ({resp.status_code})")
    
    # TEST 7: Register a brand new user for check-in testing
    print_step(7, "Register a brand new user for check-in testing")
    new_token, new_email = register_new_user()
    
    if not new_token:
        print("❌ FAILED: Could not register new user")
        return
    
    print(f"✅ PASSED: New user registered: {new_email}")
    headers_new = get_headers(new_token)
    
    # TEST 8: First check-in → already_checked_in=false, coins_awarded>=15
    print_step(8, "First check-in → expect already_checked_in=false, coins_awarded>=15")
    resp = requests.post(f"{BASE_URL}/users/me/check-in", headers=headers_new)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"❌ FAILED: Expected 200, got {resp.status_code}")
        print(f"Response: {resp.text}")
        return
    
    data = resp.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    # Verify required fields
    required_fields = ["already_checked_in", "coins_awarded", "streak_count", "coins"]
    for field in required_fields:
        if field not in data:
            print(f"❌ FAILED: Missing required field '{field}'")
            return
    
    if data["already_checked_in"] != False:
        print(f"❌ FAILED: Expected already_checked_in=false, got {data['already_checked_in']}")
        return
    
    if data["coins_awarded"] < 15:
        print(f"❌ FAILED: Expected coins_awarded>=15, got {data['coins_awarded']}")
        return
    
    if data["streak_count"] < 1:
        print(f"❌ FAILED: Expected streak_count>=1, got {data['streak_count']}")
        return
    
    if not isinstance(data["coins"], int):
        print(f"❌ FAILED: Expected coins to be int, got {type(data['coins'])}")
        return
    
    first_coins = data["coins"]
    coins_awarded = data["coins_awarded"]
    
    print(f"✅ PASSED: First check-in successful")
    print(f"   already_checked_in: {data['already_checked_in']}")
    print(f"   coins_awarded: {data['coins_awarded']}")
    print(f"   streak_count: {data['streak_count']}")
    print(f"   coins: {data['coins']}")
    
    # TEST 9: Second check-in same day → already_checked_in=true, coins_awarded=0
    print_step(9, "Second check-in same day → expect already_checked_in=true, coins_awarded=0")
    resp = requests.post(f"{BASE_URL}/users/me/check-in", headers=headers_new)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"❌ FAILED: Expected 200, got {resp.status_code}")
        return
    
    data = resp.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if data["already_checked_in"] != True:
        print(f"❌ FAILED: Expected already_checked_in=true, got {data['already_checked_in']}")
        return
    
    if data["coins_awarded"] != 0:
        print(f"❌ FAILED: Expected coins_awarded=0, got {data['coins_awarded']}")
        return
    
    if data["coins"] != first_coins:
        print(f"❌ FAILED: Expected coins to remain {first_coins}, got {data['coins']}")
        return
    
    print(f"✅ PASSED: Second check-in idempotent (already_checked_in=true, coins unchanged)")
    print(f"   already_checked_in: {data['already_checked_in']}")
    print(f"   coins_awarded: {data['coins_awarded']}")
    print(f"   coins: {data['coins']}")
    
    # ========================================================================
    # PART 3: SMOKE TESTS (existing endpoints)
    # ========================================================================
    print("\n" + "="*80)
    print("PART 3: SMOKE TESTS (existing endpoints)")
    print("="*80)
    
    # TEST 10: POST /api/auth/login with mei@demo.com
    print_step(10, "POST /api/auth/login with mei@demo.com/Demo1234!")
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "mei@demo.com",
        "password": "Demo1234!"
    })
    print(f"Status: {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"❌ FAILED: Login failed with {resp.status_code}")
        print(f"Response: {resp.text}")
        return
    
    data = resp.json()
    if "token" not in data:
        print(f"❌ FAILED: Missing 'token' in response")
        return
    
    print(f"✅ PASSED: Login successful, token received")
    
    # TEST 11: GET /api/users/partners with token
    print_step(11, "GET /api/users/partners with token")
    resp = requests.get(f"{BASE_URL}/users/partners", headers=headers_mei)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"❌ FAILED: Partners endpoint failed with {resp.status_code}")
        print(f"Response: {resp.text}")
        return
    
    data = resp.json()
    if not isinstance(data, list):
        print(f"❌ FAILED: Expected list response, got {type(data)}")
        return
    
    print(f"✅ PASSED: Partners endpoint working, returned {len(data)} partners")
    
    # FINAL SUMMARY
    print("\n" + "="*80)
    print("🎉 ALL TESTS PASSED (11/11)")
    print("="*80)
    print("\n📋 PART 1: GET /api/phrases/daily (5/5)")
    print("✅ Test 1: Without auth → 401/403")
    print("✅ Test 2: ?lang=ja → 200 with roman non-null")
    print("✅ Test 3: ?lang=en → roman is null")
    print("✅ Test 4: ?lang=zz (invalid) → fallback, still 200")
    print("✅ Test 5: No lang param → uses user's learning language")
    print("\n📋 PART 2: POST /api/users/me/check-in (4/4)")
    print("✅ Test 6: Without auth → 401/403")
    print("✅ Test 7: Register new user")
    print("✅ Test 8: First check-in → already_checked_in=false, coins_awarded>=15")
    print("✅ Test 9: Second check-in → already_checked_in=true, coins_awarded=0")
    print("\n📋 PART 3: SMOKE TESTS (2/2)")
    print("✅ Test 10: POST /api/auth/login → success")
    print("✅ Test 11: GET /api/users/partners → success")
    print("="*80)

if __name__ == "__main__":
    main()
