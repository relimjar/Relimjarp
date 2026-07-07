#!/usr/bin/env python3
"""
Backend API test for Round 15: Share-to-Moments Endpoint Update
Tests POST /api/rooms/{room_id}/share-to-moments with new features:
1. Any authenticated user (not just host) can share
2. Body accepts optional {text} for custom caption
"""

import requests
import json
from datetime import datetime

# Backend URL - using localhost since we're testing from inside the container
BASE_URL = "http://localhost:8001/api"

def login_user(email, password):
    """Helper: Login and return token"""
    url = f"{BASE_URL}/auth/login"
    resp = requests.post(url, json={"email": email, "password": password})
    if resp.status_code != 200:
        raise Exception(f"Login failed for {email}: {resp.status_code} {resp.text}")
    return resp.json()["token"], resp.json()["user"]["id"]


def test_scenario_1_host_shares_with_caption():
    """
    Scenario 1: Host shares with caption
    - Login mei, create a public room
    - POST /api/rooms/{room_id}/share-to-moments with body {"text": "Come join us! 🎙️"}
    - Expect 201, response {"shared": true}
    - GET /api/moments — find moment with text=="Come join us! 🎙️" AND room_id==room_id AND user_id==mei_id
    """
    print("\n" + "="*80)
    print("SCENARIO 1: Host shares with caption")
    print("="*80)
    
    # Login mei
    print("Step 1: Login mei@demo.com")
    mei_token, mei_id = login_user("mei@demo.com", "Demo1234!")
    print(f"✅ Logged in as mei (user_id: {mei_id})")
    
    # Create public room
    print("\nStep 2: Create public room")
    create_url = f"{BASE_URL}/rooms"
    headers = {"Authorization": f"Bearer {mei_token}"}
    room_data = {
        "title": "Round 15 Test",
        "language": "en",
        "topic": "General",
        "mode": "chat",
        "is_private": False
    }
    resp = requests.post(create_url, json=room_data, headers=headers)
    if resp.status_code != 201:
        print(f"❌ FAILED: Room creation failed with {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    room = resp.json()
    room_id = room["id"]
    print(f"✅ Created room: {room_id} (title: {room['title']})")
    
    # Share to moments with caption
    print("\nStep 3: Share to moments with caption")
    share_url = f"{BASE_URL}/rooms/{room_id}/share-to-moments"
    share_body = {"text": "Come join us! 🎙️"}
    resp = requests.post(share_url, json=share_body, headers=headers)
    
    if resp.status_code != 201:
        print(f"❌ FAILED: Expected 201, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    print(f"✅ POST /api/rooms/{room_id}/share-to-moments returned 201")
    
    data = resp.json()
    if data.get("shared") is not True:
        print(f"❌ FAILED: Expected {{shared: true}}, got {data}")
        return False
    
    print(f"✅ Response: {data}")
    
    # Verify moment created
    print("\nStep 4: Verify moment in feed")
    moments_url = f"{BASE_URL}/moments"
    resp = requests.get(moments_url, headers=headers)
    
    if resp.status_code != 200:
        print(f"❌ FAILED: GET /api/moments failed with {resp.status_code}")
        return False
    
    moments = resp.json()
    
    # Find moment with matching text, room.id, and author.id
    found = False
    for moment in moments:
        if (moment.get("text") == "Come join us! 🎙️" and 
            moment.get("room", {}).get("id") == room_id and 
            moment.get("author", {}).get("id") == mei_id):
            found = True
            print(f"✅ Found moment in feed:")
            print(f"   - text: {moment['text']}")
            print(f"   - room.id: {moment['room']['id']}")
            print(f"   - author.id: {moment['author']['id']}")
            break
    
    if not found:
        print(f"❌ FAILED: Moment not found in feed")
        print(f"   Looking for: text='Come join us! 🎙️', room.id={room_id}, author.id={mei_id}")
        return False
    
    print(f"✅ SCENARIO 1 PASSED")
    return True, room_id, mei_token, mei_id


def test_scenario_2_audience_shares_with_caption(room_id, mei_token):
    """
    Scenario 2: Audience (non-host) shares with caption — this was 403 previously
    - Login diego
    - Diego joins the room
    - POST /api/rooms/{room_id}/share-to-moments with body {"text": "This is awesome"}
    - Expect 201 (NOT 403)
    - GET /api/moments — find moment with text=="This is awesome" AND room_id==room_id AND user_id==diego_id
    """
    print("\n" + "="*80)
    print("SCENARIO 2: Audience (non-host) shares with caption")
    print("="*80)
    
    # Login diego
    print("Step 1: Login diego@demo.com")
    diego_token, diego_id = login_user("diego@demo.com", "Demo1234!")
    print(f"✅ Logged in as diego (user_id: {diego_id})")
    
    # Diego joins room
    print(f"\nStep 2: Diego joins room {room_id}")
    join_url = f"{BASE_URL}/rooms/{room_id}/join"
    headers_diego = {"Authorization": f"Bearer {diego_token}"}
    resp = requests.post(join_url, headers=headers_diego)
    
    if resp.status_code != 200:
        print(f"❌ FAILED: Join room failed with {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    print(f"✅ Diego joined room")
    
    # Diego shares to moments with caption
    print("\nStep 3: Diego shares to moments with caption")
    share_url = f"{BASE_URL}/rooms/{room_id}/share-to-moments"
    share_body = {"text": "This is awesome"}
    resp = requests.post(share_url, json=share_body, headers=headers_diego)
    
    if resp.status_code != 201:
        print(f"❌ FAILED: Expected 201, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        if resp.status_code == 403:
            print(f"   ⚠️  CRITICAL: Still getting 403 (non-host blocked) - feature not implemented!")
        return False
    
    print(f"✅ POST /api/rooms/{room_id}/share-to-moments returned 201 (NOT 403)")
    
    data = resp.json()
    if data.get("shared") is not True:
        print(f"❌ FAILED: Expected {{shared: true}}, got {data}")
        return False
    
    print(f"✅ Response: {data}")
    
    # Verify moment created
    print("\nStep 4: Verify moment in feed")
    moments_url = f"{BASE_URL}/moments"
    resp = requests.get(moments_url, headers=headers_diego)
    
    if resp.status_code != 200:
        print(f"❌ FAILED: GET /api/moments failed with {resp.status_code}")
        return False
    
    moments = resp.json()
    
    # Find moment with matching text, room.id, and author.id
    found = False
    for moment in moments:
        if (moment.get("text") == "This is awesome" and 
            moment.get("room", {}).get("id") == room_id and 
            moment.get("author", {}).get("id") == diego_id):
            found = True
            print(f"✅ Found moment in feed:")
            print(f"   - text: {moment['text']}")
            print(f"   - room.id: {moment['room']['id']}")
            print(f"   - author.id: {moment['author']['id']}")
            break
    
    if not found:
        print(f"❌ FAILED: Moment not found in feed")
        print(f"   Looking for: text='This is awesome', room.id={room_id}, author.id={diego_id}")
        return False
    
    print(f"✅ SCENARIO 2 PASSED")
    return True


def test_scenario_3_share_without_caption(room_id, mei_token, mei_id):
    """
    Scenario 3: Share without caption (empty body or {})
    - Login mei
    - POST /api/rooms/{room_id}/share-to-moments with empty body
    - Expect 201
    - GET /api/moments — the newly-created moment's text auto-generated (starts with 🎙️ and contains room title)
    """
    print("\n" + "="*80)
    print("SCENARIO 3: Share without caption (empty body)")
    print("="*80)
    
    print(f"Step 1: Share room {room_id} with empty body")
    share_url = f"{BASE_URL}/rooms/{room_id}/share-to-moments"
    headers = {"Authorization": f"Bearer {mei_token}"}
    
    # Get moments count before
    moments_url = f"{BASE_URL}/moments"
    resp = requests.get(moments_url, headers=headers)
    moments_before = resp.json()
    count_before = len(moments_before)
    
    # Share with empty body
    resp = requests.post(share_url, json={}, headers=headers)
    
    if resp.status_code != 201:
        print(f"❌ FAILED: Expected 201, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    print(f"✅ POST /api/rooms/{room_id}/share-to-moments returned 201")
    
    data = resp.json()
    if data.get("shared") is not True:
        print(f"❌ FAILED: Expected {{shared: true}}, got {data}")
        return False
    
    print(f"✅ Response: {data}")
    
    # Verify moment created with auto-generated text
    print("\nStep 2: Verify moment with auto-generated text")
    resp = requests.get(moments_url, headers=headers)
    moments_after = resp.json()
    count_after = len(moments_after)
    
    if count_after <= count_before:
        print(f"❌ FAILED: No new moment created (before: {count_before}, after: {count_after})")
        return False
    
    # Find the newest moment for this room by mei
    newest_moment = None
    for moment in moments_after:
        room = moment.get("room")
        author = moment.get("author")
        if (room and room.get("id") == room_id and 
            author and author.get("id") == mei_id):
            if newest_moment is None or moment.get("created_at", "") > newest_moment.get("created_at", ""):
                newest_moment = moment
    
    if not newest_moment:
        print(f"❌ FAILED: No moment found for room.id={room_id}, author.id={mei_id}")
        return False
    
    text = newest_moment.get("text", "")
    
    # Check auto-generated text starts with 🎙️ and contains room title
    if not text.startswith("🎙️"):
        print(f"❌ FAILED: Auto-generated text should start with 🎙️, got: {text}")
        return False
    
    if "Round 15 Test" not in text:
        print(f"❌ FAILED: Auto-generated text should contain room title 'Round 15 Test', got: {text}")
        return False
    
    print(f"✅ Found moment with auto-generated text:")
    print(f"   - text: {text}")
    print(f"   - Starts with 🎙️: ✅")
    print(f"   - Contains room title: ✅")
    
    print(f"✅ SCENARIO 3 PASSED")
    return True


def test_scenario_4_private_room_refuses():
    """
    Scenario 4: Private room refuses
    - Login mei, create private room
    - POST /api/rooms/{priv_id}/share-to-moments with body {"text":"try"}
    - Expect 400 with detail "Private rooms can't be shared"
    """
    print("\n" + "="*80)
    print("SCENARIO 4: Private room refuses")
    print("="*80)
    
    # Login mei
    print("Step 1: Login mei@demo.com")
    mei_token, mei_id = login_user("mei@demo.com", "Demo1234!")
    print(f"✅ Logged in as mei")
    
    # Create private room
    print("\nStep 2: Create private room")
    create_url = f"{BASE_URL}/rooms"
    headers = {"Authorization": f"Bearer {mei_token}"}
    room_data = {
        "title": "Secret",
        "language": "en",
        "topic": "General",
        "mode": "chat",
        "is_private": True
    }
    resp = requests.post(create_url, json=room_data, headers=headers)
    
    if resp.status_code != 201:
        print(f"❌ FAILED: Private room creation failed with {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    room = resp.json()
    priv_id = room["id"]
    print(f"✅ Created private room: {priv_id}")
    
    # Try to share private room
    print("\nStep 3: Try to share private room")
    share_url = f"{BASE_URL}/rooms/{priv_id}/share-to-moments"
    share_body = {"text": "try"}
    resp = requests.post(share_url, json=share_body, headers=headers)
    
    if resp.status_code != 400:
        print(f"❌ FAILED: Expected 400, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    print(f"✅ POST /api/rooms/{priv_id}/share-to-moments returned 400")
    
    data = resp.json()
    detail = data.get("detail", "")
    
    if detail != "Private rooms can't be shared":
        print(f"❌ FAILED: Expected detail 'Private rooms can't be shared', got: {detail}")
        return False
    
    print(f"✅ Response detail: {detail}")
    
    print(f"✅ SCENARIO 4 PASSED")
    return True


def test_scenario_5_unknown_room():
    """
    Scenario 5: Unknown room
    - POST /api/rooms/nonexistent-id-12345/share-to-moments {}
    - Expect 404
    """
    print("\n" + "="*80)
    print("SCENARIO 5: Unknown room")
    print("="*80)
    
    # Login mei
    print("Step 1: Login mei@demo.com")
    mei_token, mei_id = login_user("mei@demo.com", "Demo1234!")
    print(f"✅ Logged in as mei")
    
    # Try to share unknown room
    print("\nStep 2: Try to share unknown room")
    share_url = f"{BASE_URL}/rooms/nonexistent-id-12345/share-to-moments"
    headers = {"Authorization": f"Bearer {mei_token}"}
    resp = requests.post(share_url, json={}, headers=headers)
    
    if resp.status_code != 404:
        print(f"❌ FAILED: Expected 404, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    print(f"✅ POST /api/rooms/nonexistent-id-12345/share-to-moments returned 404")
    
    print(f"✅ SCENARIO 5 PASSED")
    return True


def test_scenario_6_text_validation():
    """
    Scenario 6: Text validation
    - POST /api/rooms/{room_id}/share-to-moments with body {"text": "a"*600} (over 500 chars)
    - Expect 422 (pydantic validation)
    """
    print("\n" + "="*80)
    print("SCENARIO 6: Text validation (over 500 chars)")
    print("="*80)
    
    # Login mei
    print("Step 1: Login mei@demo.com")
    mei_token, mei_id = login_user("mei@demo.com", "Demo1234!")
    print(f"✅ Logged in as mei")
    
    # Create public room
    print("\nStep 2: Create public room")
    create_url = f"{BASE_URL}/rooms"
    headers = {"Authorization": f"Bearer {mei_token}"}
    room_data = {
        "title": "Validation Test",
        "language": "en",
        "topic": "General",
        "mode": "chat",
        "is_private": False
    }
    resp = requests.post(create_url, json=room_data, headers=headers)
    
    if resp.status_code != 201:
        print(f"❌ FAILED: Room creation failed with {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    room = resp.json()
    room_id = room["id"]
    print(f"✅ Created room: {room_id}")
    
    # Try to share with text over 500 chars
    print("\nStep 3: Try to share with text over 500 chars")
    share_url = f"{BASE_URL}/rooms/{room_id}/share-to-moments"
    long_text = "a" * 600
    share_body = {"text": long_text}
    resp = requests.post(share_url, json=share_body, headers=headers)
    
    if resp.status_code != 422:
        print(f"❌ FAILED: Expected 422, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    print(f"✅ POST /api/rooms/{room_id}/share-to-moments returned 422")
    
    data = resp.json()
    print(f"✅ Validation error: {data}")
    
    print(f"✅ SCENARIO 6 PASSED")
    return True


def main():
    print("\n" + "="*80)
    print("BACKEND TEST: Share-to-Moments Endpoint Update (Round 15)")
    print("="*80)
    print(f"Backend URL: {BASE_URL}")
    print(f"Test Date: {datetime.now().isoformat()}")
    print("\nTesting 2 key changes:")
    print("1. Any authenticated user (not just host) can share to moments")
    print("2. Body accepts optional {text} for custom caption")
    
    results = []
    
    # Scenario 1: Host shares with caption
    result = test_scenario_1_host_shares_with_caption()
    if isinstance(result, tuple):
        test1_passed, room_id, mei_token, mei_id = result
        results.append(("Scenario 1: Host shares with caption", test1_passed))
    else:
        test1_passed = False
        results.append(("Scenario 1: Host shares with caption", False))
        room_id = None
        mei_token = None
        mei_id = None
    
    # Scenario 2: Audience shares with caption (only if scenario 1 passed)
    if test1_passed and room_id and mei_token:
        results.append(("Scenario 2: Audience shares with caption", test_scenario_2_audience_shares_with_caption(room_id, mei_token)))
    else:
        print("\n⚠️  Skipping scenario 2 because scenario 1 failed")
        results.append(("Scenario 2: Audience shares with caption", False))
    
    # Scenario 3: Share without caption (only if scenario 1 passed)
    if test1_passed and room_id and mei_token and mei_id:
        results.append(("Scenario 3: Share without caption", test_scenario_3_share_without_caption(room_id, mei_token, mei_id)))
    else:
        print("\n⚠️  Skipping scenario 3 because scenario 1 failed")
        results.append(("Scenario 3: Share without caption", False))
    
    # Scenario 4: Private room refuses
    results.append(("Scenario 4: Private room refuses", test_scenario_4_private_room_refuses()))
    
    # Scenario 5: Unknown room
    results.append(("Scenario 5: Unknown room", test_scenario_5_unknown_room()))
    
    # Scenario 6: Text validation
    results.append(("Scenario 6: Text validation", test_scenario_6_text_validation()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} scenarios passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} scenario(s) failed")
        return 1

if __name__ == "__main__":
    exit(main())
