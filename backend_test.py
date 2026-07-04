#!/usr/bin/env python3
"""
Backend API Testing Script for LinguaConnect - Voice Room + Moments Integration
Tests the new features: gift catalog, room creation with moments sharing, 
room ending, private rooms, gift sending, and chat mute functionality.
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend/.env
BASE_URL = "https://368bd428-054d-4ed0-be5c-b4aaf6dfeef5.preview.emergentagent.com"
API_URL = f"{BASE_URL}/api"

# Test credentials from /app/memory/test_credentials.md
USER_A_EMAIL = "mei@demo.com"
USER_A_PASSWORD = "Demo1234!"
USER_B_EMAIL = "diego@demo.com"
USER_B_PASSWORD = "Demo1234!"

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

# Global state for test data
test_state = {
    "user_a_token": None,
    "user_a_id": None,
    "user_a_coins_initial": 0,
    "user_b_token": None,
    "user_b_id": None,
    "room_id": None,
    "moment_id": None,
    "moments_count_before": 0,
}

def print_test(test_name):
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}TEST: {test_name}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")

def print_success(message):
    print(f"{GREEN}✓ {message}{RESET}")

def print_error(message):
    print(f"{RED}✗ {message}{RESET}")

def print_info(message):
    print(f"{YELLOW}ℹ {message}{RESET}")

def login_user(email, password, user_label):
    """Login and return token, user_id, and full user data"""
    print_info(f"Logging in {user_label}: {email}")
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            user_id = data.get("user", {}).get("id")
            coins = data.get("user", {}).get("coins", 0)
            print_success(f"{user_label} logged in successfully (ID: {user_id}, Coins: {coins})")
            return token, user_id, data.get("user")
        else:
            print_error(f"{user_label} login failed: {response.status_code} - {response.text[:200]}")
            return None, None, None
    except Exception as e:
        print_error(f"{user_label} login exception: {str(e)}")
        return None, None, None

def test_1_gift_catalog():
    """Test 1: GET /api/rooms/gift-catalog - should return coins and 4 gifts"""
    print_test("1. GET /api/rooms/gift-catalog (authenticated)")
    
    headers = {"Authorization": f"Bearer {test_state['user_a_token']}"}
    
    try:
        response = requests.get(f"{API_URL}/rooms/gift-catalog", headers=headers, timeout=10)
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.text[:500]}")
        
        if response.status_code != 200:
            print_error(f"Expected 200, got {response.status_code}")
            return False
        
        data = response.json()
        
        # Verify structure
        if "coins" not in data:
            print_error("Missing 'coins' field in response")
            return False
        
        if "gifts" not in data:
            print_error("Missing 'gifts' field in response")
            return False
        
        gifts = data["gifts"]
        if len(gifts) != 4:
            print_error(f"Expected 4 gifts, got {len(gifts)}")
            return False
        
        # Verify all 4 gifts are present
        expected_gifts = {"rose", "heart", "star", "crown"}
        actual_gifts = {g["id"] for g in gifts}
        
        if expected_gifts != actual_gifts:
            print_error(f"Expected gifts {expected_gifts}, got {actual_gifts}")
            return False
        
        print_success(f"Gift catalog returned correctly: {data['coins']} coins, 4 gifts")
        gift_list = ', '.join([f"{g['name']} ({g['emoji']}) - {g['price']} coins" for g in gifts])
        print_success(f"Gifts: {gift_list}")
        
        # Store initial coins for later tests
        test_state["user_a_coins_initial"] = data["coins"]
        
        return True
        
    except Exception as e:
        print_error(f"Gift catalog test failed: {str(e)}")
        return False

def test_2_create_room_with_moments():
    """Test 2: POST /api/rooms with share_to_moments=true"""
    print_test("2. POST /api/rooms (create room with share_to_moments=true)")
    
    headers = {"Authorization": f"Bearer {test_state['user_a_token']}"}
    
    payload = {
        "title": "Test Room ABC",
        "language": "en",
        "languages": ["en"],
        "topic": "Small Talk",
        "mode": "chat",
        "is_private": False,
        "background": 1,
        "share_to_moments": True
    }
    
    print_info(f"Creating room: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(f"{API_URL}/rooms", json=payload, headers=headers, timeout=10)
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.text[:800]}")
        
        if response.status_code != 201:
            print_error(f"Expected 201, got {response.status_code}")
            return False
        
        data = response.json()
        
        # Verify required fields
        checks = [
            ("topic", "Small Talk"),
            ("mode", "chat"),
            ("is_private", False),
            ("background", 1),
            ("member_count", 1),
        ]
        
        for field, expected in checks:
            actual = data.get(field)
            if actual != expected:
                print_error(f"Field '{field}': expected {expected}, got {actual}")
                return False
            print_success(f"Field '{field}' = {actual} ✓")
        
        # Verify host is present
        if "host" not in data or not data["host"]:
            print_error("Missing 'host' field in response")
            return False
        
        print_success(f"Host: {data['host'].get('name')} (ID: {data['host'].get('id')})")
        
        # Store room_id for later tests
        test_state["room_id"] = data.get("id")
        print_success(f"Room created successfully with ID: {test_state['room_id']}")
        
        return True
        
    except Exception as e:
        print_error(f"Create room test failed: {str(e)}")
        return False

def test_3_list_rooms():
    """Test 3: GET /api/rooms - verify created room appears with all fields"""
    print_test("3. GET /api/rooms (list rooms)")
    
    headers = {"Authorization": f"Bearer {test_state['user_a_token']}"}
    
    try:
        response = requests.get(f"{API_URL}/rooms", headers=headers, timeout=10)
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.text[:1000]}")
        
        if response.status_code != 200:
            print_error(f"Expected 200, got {response.status_code}")
            return False
        
        rooms = response.json()
        
        if not isinstance(rooms, list):
            print_error(f"Expected list, got {type(rooms)}")
            return False
        
        print_success(f"Found {len(rooms)} room(s)")
        
        # Find our created room
        our_room = None
        for room in rooms:
            if room.get("id") == test_state["room_id"]:
                our_room = room
                break
        
        if not our_room:
            print_error(f"Created room {test_state['room_id']} not found in list")
            return False
        
        # Verify required fields
        required_fields = ["topic", "mode", "is_private", "background", "members_preview", "member_count"]
        
        for field in required_fields:
            if field not in our_room:
                print_error(f"Missing field '{field}' in room")
                return False
            print_success(f"Field '{field}' present: {our_room[field]}")
        
        # Verify members_preview is an array
        if not isinstance(our_room["members_preview"], list):
            print_error(f"members_preview should be array, got {type(our_room['members_preview'])}")
            return False
        
        print_success(f"Room appears in list with all required fields")
        
        return True
        
    except Exception as e:
        print_error(f"List rooms test failed: {str(e)}")
        return False

def test_4_verify_moment_created():
    """Test 4: GET /api/moments - verify moment with room field (is_live=true)"""
    print_test("4. GET /api/moments (verify moment created with room)")
    
    headers = {"Authorization": f"Bearer {test_state['user_a_token']}"}
    
    try:
        response = requests.get(f"{API_URL}/moments", headers=headers, timeout=10)
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.text[:1500]}")
        
        if response.status_code != 200:
            print_error(f"Expected 200, got {response.status_code}")
            return False
        
        moments = response.json()
        
        if not isinstance(moments, list):
            print_error(f"Expected list, got {type(moments)}")
            return False
        
        print_success(f"Found {len(moments)} moment(s)")
        
        # Store count for later comparison
        test_state["moments_count_before"] = len(moments)
        
        # Find moment with our room
        room_moment = None
        for moment in moments:
            room = moment.get("room")
            if room and room.get("id") == test_state["room_id"]:
                room_moment = moment
                break
        
        if not room_moment:
            print_error(f"No moment found with room_id {test_state['room_id']}")
            return False
        
        # Store moment_id for later tests
        test_state["moment_id"] = room_moment.get("id")
        
        # Verify room field structure
        room = room_moment.get("room")
        
        if not room.get("is_live"):
            print_error(f"Room is_live should be true, got {room.get('is_live')}")
            return False
        
        print_success(f"Room is_live = true ✓")
        
        if room.get("title") != "Test Room ABC":
            print_error(f"Room title should be 'Test Room ABC', got {room.get('title')}")
            return False
        
        print_success(f"Room title = 'Test Room ABC' ✓")
        
        if room.get("member_count") != 1:
            print_error(f"Room member_count should be 1, got {room.get('member_count')}")
            return False
        
        print_success(f"Room member_count = 1 ✓")
        
        print_success(f"Moment created successfully with live room (moment_id: {test_state['moment_id']})")
        
        return True
        
    except Exception as e:
        print_error(f"Verify moment test failed: {str(e)}")
        return False

def test_5_end_room():
    """Test 5: POST /api/rooms/{room_id}/end - end room as host"""
    print_test("5. POST /api/rooms/{room_id}/end (end room as host)")
    
    headers = {"Authorization": f"Bearer {test_state['user_a_token']}"}
    
    try:
        response = requests.post(
            f"{API_URL}/rooms/{test_state['room_id']}/end",
            headers=headers,
            timeout=10
        )
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.text[:500]}")
        
        if response.status_code != 200:
            print_error(f"Expected 200, got {response.status_code}")
            return False
        
        data = response.json()
        
        if not data.get("ok"):
            print_error(f"Expected ok=true, got {data}")
            return False
        
        print_success(f"Room ended successfully")
        
        return True
        
    except Exception as e:
        print_error(f"End room test failed: {str(e)}")
        return False

def test_6_verify_moment_room_ended():
    """Test 6: GET /api/moments - verify same moment shows is_live=false"""
    print_test("6. GET /api/moments (verify room ended in moment)")
    
    headers = {"Authorization": f"Bearer {test_state['user_a_token']}"}
    
    try:
        response = requests.get(f"{API_URL}/moments", headers=headers, timeout=10)
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.text[:1500]}")
        
        if response.status_code != 200:
            print_error(f"Expected 200, got {response.status_code}")
            return False
        
        moments = response.json()
        
        # Find our moment
        our_moment = None
        for moment in moments:
            if moment.get("id") == test_state["moment_id"]:
                our_moment = moment
                break
        
        if not our_moment:
            print_error(f"Moment {test_state['moment_id']} not found")
            return False
        
        # Verify room field shows is_live=false
        room = our_moment.get("room")
        
        if not room:
            print_error("Room field is missing or null")
            return False
        
        if room.get("is_live") != False:
            print_error(f"Room is_live should be false, got {room.get('is_live')}")
            return False
        
        print_success(f"Room is_live = false ✓")
        print_success(f"Moment correctly reflects room ended state")
        
        return True
        
    except Exception as e:
        print_error(f"Verify moment room ended test failed: {str(e)}")
        return False

def test_7_private_room_no_moment():
    """Test 7: Create private room with share_to_moments=true - verify NO moment created"""
    print_test("7. Create private room with share_to_moments=true (should NOT create moment)")
    
    headers = {"Authorization": f"Bearer {test_state['user_a_token']}"}
    
    payload = {
        "title": "Private Test Room",
        "language": "en",
        "languages": ["en"],
        "topic": "Private Chat",
        "mode": "chat",
        "is_private": True,
        "background": 2,
        "share_to_moments": True
    }
    
    print_info(f"Creating private room: {json.dumps(payload, indent=2)}")
    
    try:
        # Create private room
        response = requests.post(f"{API_URL}/rooms", json=payload, headers=headers, timeout=10)
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.text[:800]}")
        
        if response.status_code != 201:
            print_error(f"Expected 201, got {response.status_code}")
            return False
        
        data = response.json()
        private_room_id = data.get("id")
        
        print_success(f"Private room created with ID: {private_room_id}")
        
        # Get moments list
        response = requests.get(f"{API_URL}/moments", headers=headers, timeout=10)
        
        if response.status_code != 200:
            print_error(f"Failed to get moments: {response.status_code}")
            return False
        
        moments = response.json()
        moments_count_after = len(moments)
        
        print_info(f"Moments count before: {test_state['moments_count_before']}, after: {moments_count_after}")
        
        # Check if any new moment was created for this private room
        private_room_moment = None
        for moment in moments:
            room = moment.get("room")
            if room and room.get("id") == private_room_id:
                private_room_moment = moment
                break
        
        if private_room_moment:
            print_error(f"Private room should NOT create a moment, but found moment: {private_room_moment.get('id')}")
            return False
        
        print_success(f"No moment created for private room ✓")
        
        # Clean up: end the private room
        requests.post(f"{API_URL}/rooms/{private_room_id}/end", headers=headers, timeout=10)
        
        return True
        
    except Exception as e:
        print_error(f"Private room test failed: {str(e)}")
        return False

def test_8_gift_sending():
    """Test 8: Gift sending - create room as user B, user A joins and sends gift"""
    print_test("8. Gift sending (user A sends gift to user B in B's room)")
    
    headers_b = {"Authorization": f"Bearer {test_state['user_b_token']}"}
    headers_a = {"Authorization": f"Bearer {test_state['user_a_token']}"}
    
    try:
        # User B creates a room
        payload = {
            "title": "Gift Test Room",
            "language": "en",
            "languages": ["en"],
            "topic": "Testing",
            "mode": "chat",
            "is_private": False,
            "background": 0,
            "share_to_moments": False
        }
        
        print_info("User B creating room...")
        response = requests.post(f"{API_URL}/rooms", json=payload, headers=headers_b, timeout=10)
        
        if response.status_code != 201:
            print_error(f"User B room creation failed: {response.status_code}")
            return False
        
        room_data = response.json()
        gift_room_id = room_data.get("id")
        print_success(f"User B created room: {gift_room_id}")
        
        # User A joins the room
        print_info("User A joining room...")
        response = requests.post(f"{API_URL}/rooms/{gift_room_id}/join", headers=headers_a, timeout=10)
        
        if response.status_code != 200:
            print_error(f"User A join failed: {response.status_code} - {response.text[:200]}")
            return False
        
        print_success("User A joined room")
        
        # Get user A's coins before gift
        coins_before = test_state["user_a_coins_initial"]
        print_info(f"User A coins before gift: {coins_before}")
        
        # User A sends a rose (10 coins) to user B
        gift_payload = {
            "to_user_id": test_state["user_b_id"],
            "gift_id": "rose"
        }
        
        print_info(f"User A sending rose to user B...")
        response = requests.post(
            f"{API_URL}/rooms/{gift_room_id}/gift",
            json=gift_payload,
            headers=headers_a,
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.text[:800]}")
        
        if response.status_code != 201:
            print_error(f"Gift sending failed: {response.status_code}")
            return False
        
        gift_response = response.json()
        
        # Verify coins deducted
        coins_after = gift_response.get("coins")
        
        if coins_after != coins_before - 10:
            print_error(f"Coins not deducted correctly. Before: {coins_before}, After: {coins_after}, Expected: {coins_before - 10}")
            return False
        
        print_success(f"Coins deducted correctly: {coins_before} -> {coins_after} (-10) ✓")
        
        # Verify message returned
        message = gift_response.get("message")
        
        if not message:
            print_error("No message returned in gift response")
            return False
        
        if message.get("type") != "gift":
            print_error(f"Message type should be 'gift', got {message.get('type')}")
            return False
        
        print_success(f"Gift message returned with type='gift' ✓")
        
        # Get room details to verify top_gifters
        print_info("Verifying top_gifters...")
        response = requests.get(f"{API_URL}/rooms/{gift_room_id}", headers=headers_a, timeout=10)
        
        if response.status_code != 200:
            print_error(f"Failed to get room details: {response.status_code}")
            return False
        
        room_data = response.json()
        top_gifters = room_data.get("top_gifters", [])
        
        print_info(f"Top gifters: {json.dumps(top_gifters, indent=2)}")
        
        # Find user A in top_gifters
        user_a_gifter = None
        for gifter in top_gifters:
            if gifter.get("id") == test_state["user_a_id"]:
                user_a_gifter = gifter
                break
        
        if not user_a_gifter:
            print_error(f"User A not found in top_gifters")
            return False
        
        if user_a_gifter.get("coins") != 10:
            print_error(f"User A should have 10 coins in top_gifters, got {user_a_gifter.get('coins')}")
            return False
        
        print_success(f"User A appears in top_gifters with 10 coins ✓")
        
        # Clean up: end the room
        requests.post(f"{API_URL}/rooms/{gift_room_id}/end", headers=headers_b, timeout=10)
        
        return True
        
    except Exception as e:
        print_error(f"Gift sending test failed: {str(e)}")
        return False

def test_9_chat_mute():
    """Test 9: Chat mute - host toggles mute, non-host message fails, host message succeeds"""
    print_test("9. Chat mute (host mutes chat, non-host blocked, host allowed)")
    
    headers_a = {"Authorization": f"Bearer {test_state['user_a_token']}"}
    headers_b = {"Authorization": f"Bearer {test_state['user_b_token']}"}
    
    try:
        # User A creates a room
        payload = {
            "title": "Chat Mute Test Room",
            "language": "en",
            "languages": ["en"],
            "topic": "Testing",
            "mode": "chat",
            "is_private": False,
            "background": 0,
            "share_to_moments": False
        }
        
        print_info("User A (host) creating room...")
        response = requests.post(f"{API_URL}/rooms", json=payload, headers=headers_a, timeout=10)
        
        if response.status_code != 201:
            print_error(f"Room creation failed: {response.status_code}")
            return False
        
        room_data = response.json()
        mute_room_id = room_data.get("id")
        print_success(f"Room created: {mute_room_id}")
        
        # User B joins the room
        print_info("User B (non-host) joining room...")
        response = requests.post(f"{API_URL}/rooms/{mute_room_id}/join", headers=headers_b, timeout=10)
        
        if response.status_code != 200:
            print_error(f"User B join failed: {response.status_code}")
            return False
        
        print_success("User B joined room")
        
        # Host (user A) toggles chat mute
        print_info("Host toggling chat mute...")
        response = requests.post(f"{API_URL}/rooms/{mute_room_id}/chat-mute", headers=headers_a, timeout=10)
        
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.text[:500]}")
        
        if response.status_code != 200:
            print_error(f"Chat mute toggle failed: {response.status_code}")
            return False
        
        mute_data = response.json()
        
        if not mute_data.get("chat_muted"):
            print_error(f"chat_muted should be true, got {mute_data.get('chat_muted')}")
            return False
        
        print_success(f"Chat muted successfully (chat_muted=true) ✓")
        
        # Non-host (user B) tries to send message - should fail with 403
        print_info("Non-host (user B) attempting to send message (should fail)...")
        message_payload = {"text": "This should be blocked"}
        
        response = requests.post(
            f"{API_URL}/rooms/{mute_room_id}/messages",
            json=message_payload,
            headers=headers_b,
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.text[:500]}")
        
        if response.status_code != 403:
            print_error(f"Non-host message should fail with 403, got {response.status_code}")
            return False
        
        print_success(f"Non-host message correctly blocked with 403 ✓")
        
        # Host (user A) sends message - should succeed
        print_info("Host (user A) sending message (should succeed)...")
        message_payload = {"text": "Host message should work"}
        
        response = requests.post(
            f"{API_URL}/rooms/{mute_room_id}/messages",
            json=message_payload,
            headers=headers_a,
            timeout=10
        )
        
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.text[:500]}")
        
        if response.status_code != 201:
            print_error(f"Host message should succeed with 201, got {response.status_code}")
            return False
        
        message_data = response.json()
        
        if message_data.get("text") != "Host message should work":
            print_error(f"Message text mismatch")
            return False
        
        print_success(f"Host message sent successfully ✓")
        
        # Clean up: end the room
        requests.post(f"{API_URL}/rooms/{mute_room_id}/end", headers=headers_a, timeout=10)
        
        return True
        
    except Exception as e:
        print_error(f"Chat mute test failed: {str(e)}")
        return False

def main():
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}LinguaConnect Backend Testing Suite{RESET}")
    print(f"{BLUE}Voice Room + Moments Integration Features{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    print(f"{YELLOW}Backend URL: {API_URL}{RESET}\n")
    
    results = {
        "passed": 0,
        "failed": 0,
        "total": 0
    }
    
    # Setup: Login both users
    print_test("SETUP: Login test users")
    
    token_a, user_a_id, user_a = login_user(USER_A_EMAIL, USER_A_PASSWORD, "User A (mei)")
    if not token_a:
        print_error("CRITICAL: User A login failed. Cannot proceed.")
        sys.exit(1)
    
    test_state["user_a_token"] = token_a
    test_state["user_a_id"] = user_a_id
    test_state["user_a_coins_initial"] = user_a.get("coins", 0)
    
    token_b, user_b_id, user_b = login_user(USER_B_EMAIL, USER_B_PASSWORD, "User B (diego)")
    if not token_b:
        print_error("CRITICAL: User B login failed. Cannot proceed.")
        sys.exit(1)
    
    test_state["user_b_token"] = token_b
    test_state["user_b_id"] = user_b_id
    
    print_success("Setup complete - both users logged in")
    
    # Run all tests
    tests = [
        ("1. Gift Catalog", test_1_gift_catalog),
        ("2. Create Room with Moments", test_2_create_room_with_moments),
        ("3. List Rooms", test_3_list_rooms),
        ("4. Verify Moment Created", test_4_verify_moment_created),
        ("5. End Room", test_5_end_room),
        ("6. Verify Moment Room Ended", test_6_verify_moment_room_ended),
        ("7. Private Room No Moment", test_7_private_room_no_moment),
        ("8. Gift Sending", test_8_gift_sending),
        ("9. Chat Mute", test_9_chat_mute),
    ]
    
    for test_name, test_func in tests:
        results["total"] += 1
        try:
            if test_func():
                results["passed"] += 1
            else:
                results["failed"] += 1
        except Exception as e:
            print_error(f"Test {test_name} raised exception: {str(e)}")
            results["failed"] += 1
    
    print_summary(results)
    
    # Exit with appropriate code
    if results["failed"] == 0:
        sys.exit(0)
    else:
        sys.exit(1)

def print_summary(results):
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}TEST SUMMARY{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    print(f"Total Tests: {results['total']}")
    print(f"{GREEN}Passed: {results['passed']}{RESET}")
    print(f"{RED}Failed: {results['failed']}{RESET}")
    
    if results["failed"] == 0:
        print(f"\n{GREEN}✓ ALL TESTS PASSED{RESET}")
        print(f"{GREEN}✓ Voice Room + Moments integration working correctly{RESET}")
    else:
        print(f"\n{RED}✗ SOME TESTS FAILED - See details above{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

if __name__ == "__main__":
    main()
