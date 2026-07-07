#!/usr/bin/env python3
"""
Backend test for Round 12: Chat message reactions + room-share messages
Tests two new features:
  A) POST /api/chats/{cid}/messages/{mid}/react - toggle emoji reactions
  B) POST /api/chats/{cid}/messages accepts room_id (room-share card message)
"""

import requests
import sys

# Backend URL - using localhost since we're testing from inside the container
BASE_URL = "http://localhost:8001/api"

# Test credentials from /app/memory/test_credentials.md
MEI_EMAIL = "mei@demo.com"
MEI_PASSWORD = "Demo1234!"
DIEGO_EMAIL = "diego@demo.com"
DIEGO_PASSWORD = "Demo1234!"


def login(email: str, password: str) -> tuple[str, str]:
    """Login and return (token, user_id)"""
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password},
        timeout=10,
    )
    if resp.status_code != 200:
        print(f"❌ Login failed for {email}: {resp.status_code} {resp.text}")
        sys.exit(1)
    data = resp.json()
    return data["token"], data["user"]["id"]


def test_feature_a_reactions():
    """
    Test A: POST /api/chats/{cid}/messages/{mid}/react - toggle emoji reaction
    
    Steps:
    1. Login mei. Ensure conversation exists with diego.
    2. Mei sends text message, grab msg_id.
    3. Mei reacts with ❤️ → verify reactions == [{emoji:"❤️", count:1, user_ids:[mei_id]}]
    4. Mei reacts with ❤️ again → reactions cleared (empty array)
    5. Mei reacts with 😂 → replaces. reactions == [{emoji:"😂", count:1, user_ids:[mei_id]}]
    6. Diego also reacts 😂 on same msg → reactions == [{emoji:"😂", count:2, user_ids has both}]
    7. Diego reacts with 🔥 → now reactions has 2 entries
    8. GET /api/chats/{cid}/messages - message shows same aggregated reactions
    9. Unauth (no token) call → 401
    10. Unknown message id → 404 "Message not found"
    """
    print("\n" + "="*80)
    print("TEST A: POST /api/chats/{cid}/messages/{mid}/react - emoji reactions")
    print("="*80)
    
    # Step 1: Login mei and diego
    print("\n[Step 1] Login mei and diego...")
    mei_token, mei_id = login(MEI_EMAIL, MEI_PASSWORD)
    diego_token, diego_id = login(DIEGO_EMAIL, DIEGO_PASSWORD)
    print(f"✅ Mei logged in: {mei_id}")
    print(f"✅ Diego logged in: {diego_id}")
    
    # Ensure conversation exists (idempotent)
    print(f"\n[Step 1b] Ensure conversation exists between mei and diego...")
    resp = requests.post(
        f"{BASE_URL}/chats",
        json={"partner_id": diego_id},
        headers={"Authorization": f"Bearer {mei_token}"},
        timeout=10,
    )
    if resp.status_code not in [200, 201]:
        print(f"❌ Failed to create/get conversation: {resp.status_code} {resp.text}")
        return False
    conv_id = resp.json()["id"]
    print(f"✅ Conversation ID: {conv_id}")
    
    # Step 2: Mei sends text message
    print(f"\n[Step 2] Mei sends text message...")
    resp = requests.post(
        f"{BASE_URL}/chats/{conv_id}/messages",
        json={"text": "Hi"},
        headers={"Authorization": f"Bearer {mei_token}"},
        timeout=10,
    )
    if resp.status_code != 201:
        print(f"❌ Failed to send message: {resp.status_code} {resp.text}")
        return False
    msg = resp.json()
    msg_id = msg["id"]
    print(f"✅ Message sent: {msg_id}")
    print(f"   Initial reactions: {msg.get('reactions', [])}")
    
    # Step 3: Mei reacts with ❤️
    print(f"\n[Step 3] Mei reacts with ❤️...")
    resp = requests.post(
        f"{BASE_URL}/chats/{conv_id}/messages/{msg_id}/react",
        json={"emoji": "❤️"},
        headers={"Authorization": f"Bearer {mei_token}"},
        timeout=10,
    )
    if resp.status_code != 200:
        print(f"❌ Failed to react: {resp.status_code} {resp.text}")
        return False
    msg = resp.json()
    reactions = msg.get("reactions", [])
    print(f"✅ Reaction added. Reactions: {reactions}")
    
    # Verify: reactions == [{emoji:"❤️", count:1, user_ids:[mei_id]}]
    if len(reactions) != 1:
        print(f"❌ Expected 1 reaction, got {len(reactions)}")
        return False
    if reactions[0]["emoji"] != "❤️":
        print(f"❌ Expected emoji ❤️, got {reactions[0]['emoji']}")
        return False
    if reactions[0]["count"] != 1:
        print(f"❌ Expected count 1, got {reactions[0]['count']}")
        return False
    if mei_id not in reactions[0]["user_ids"]:
        print(f"❌ Expected mei_id in user_ids, got {reactions[0]['user_ids']}")
        return False
    print(f"✅ VERIFY: reactions == [{{emoji:'❤️', count:1, user_ids:[{mei_id}]}}]")
    
    # Step 4: Mei reacts with ❤️ again → reactions cleared
    print(f"\n[Step 4] Mei reacts with ❤️ again (toggle off)...")
    resp = requests.post(
        f"{BASE_URL}/chats/{conv_id}/messages/{msg_id}/react",
        json={"emoji": "❤️"},
        headers={"Authorization": f"Bearer {mei_token}"},
        timeout=10,
    )
    if resp.status_code != 200:
        print(f"❌ Failed to react: {resp.status_code} {resp.text}")
        return False
    msg = resp.json()
    reactions = msg.get("reactions", [])
    print(f"✅ Reaction toggled off. Reactions: {reactions}")
    
    if len(reactions) != 0:
        print(f"❌ Expected empty reactions, got {reactions}")
        return False
    print(f"✅ VERIFY: reactions cleared (empty array)")
    
    # Step 5: Mei reacts with 😂 → replaces
    print(f"\n[Step 5] Mei reacts with 😂...")
    resp = requests.post(
        f"{BASE_URL}/chats/{conv_id}/messages/{msg_id}/react",
        json={"emoji": "😂"},
        headers={"Authorization": f"Bearer {mei_token}"},
        timeout=10,
    )
    if resp.status_code != 200:
        print(f"❌ Failed to react: {resp.status_code} {resp.text}")
        return False
    msg = resp.json()
    reactions = msg.get("reactions", [])
    print(f"✅ Reaction replaced. Reactions: {reactions}")
    
    if len(reactions) != 1:
        print(f"❌ Expected 1 reaction, got {len(reactions)}")
        return False
    if reactions[0]["emoji"] != "😂":
        print(f"❌ Expected emoji 😂, got {reactions[0]['emoji']}")
        return False
    if reactions[0]["count"] != 1:
        print(f"❌ Expected count 1, got {reactions[0]['count']}")
        return False
    print(f"✅ VERIFY: reactions == [{{emoji:'😂', count:1, user_ids:[{mei_id}]}}]")
    
    # Step 6: Diego also reacts 😂 on same msg
    print(f"\n[Step 6] Diego also reacts 😂 on same message...")
    resp = requests.post(
        f"{BASE_URL}/chats/{conv_id}/messages/{msg_id}/react",
        json={"emoji": "😂"},
        headers={"Authorization": f"Bearer {diego_token}"},
        timeout=10,
    )
    if resp.status_code != 200:
        print(f"❌ Failed to react: {resp.status_code} {resp.text}")
        return False
    msg = resp.json()
    reactions = msg.get("reactions", [])
    print(f"✅ Diego reacted. Reactions: {reactions}")
    
    if len(reactions) != 1:
        print(f"❌ Expected 1 reaction group, got {len(reactions)}")
        return False
    if reactions[0]["emoji"] != "😂":
        print(f"❌ Expected emoji 😂, got {reactions[0]['emoji']}")
        return False
    if reactions[0]["count"] != 2:
        print(f"❌ Expected count 2, got {reactions[0]['count']}")
        return False
    if mei_id not in reactions[0]["user_ids"] or diego_id not in reactions[0]["user_ids"]:
        print(f"❌ Expected both mei and diego in user_ids, got {reactions[0]['user_ids']}")
        return False
    print(f"✅ VERIFY: reactions == [{{emoji:'😂', count:2, user_ids:[{mei_id}, {diego_id}]}}]")
    
    # Step 7: Diego reacts with 🔥 → now reactions has 2 entries
    print(f"\n[Step 7] Diego reacts with 🔥 (replaces his 😂)...")
    resp = requests.post(
        f"{BASE_URL}/chats/{conv_id}/messages/{msg_id}/react",
        json={"emoji": "🔥"},
        headers={"Authorization": f"Bearer {diego_token}"},
        timeout=10,
    )
    if resp.status_code != 200:
        print(f"❌ Failed to react: {resp.status_code} {resp.text}")
        return False
    msg = resp.json()
    reactions = msg.get("reactions", [])
    print(f"✅ Diego changed reaction. Reactions: {reactions}")
    
    if len(reactions) != 2:
        print(f"❌ Expected 2 reaction groups, got {len(reactions)}")
        return False
    
    # Find 😂 and 🔥 reactions
    laugh_reaction = next((r for r in reactions if r["emoji"] == "😂"), None)
    fire_reaction = next((r for r in reactions if r["emoji"] == "🔥"), None)
    
    if not laugh_reaction:
        print(f"❌ Expected 😂 reaction, not found in {reactions}")
        return False
    if laugh_reaction["count"] != 1 or mei_id not in laugh_reaction["user_ids"]:
        print(f"❌ Expected 😂 with count:1 and mei_id, got {laugh_reaction}")
        return False
    
    if not fire_reaction:
        print(f"❌ Expected 🔥 reaction, not found in {reactions}")
        return False
    if fire_reaction["count"] != 1 or diego_id not in fire_reaction["user_ids"]:
        print(f"❌ Expected 🔥 with count:1 and diego_id, got {fire_reaction}")
        return False
    
    print(f"✅ VERIFY: reactions has 2 entries - 😂 (mei) and 🔥 (diego)")
    
    # Step 8: GET /api/chats/{cid}/messages - verify same reactions
    print(f"\n[Step 8] GET /api/chats/{conv_id}/messages - verify reactions persist...")
    resp = requests.get(
        f"{BASE_URL}/chats/{conv_id}/messages",
        headers={"Authorization": f"Bearer {mei_token}"},
        timeout=10,
    )
    if resp.status_code != 200:
        print(f"❌ Failed to get messages: {resp.status_code} {resp.text}")
        return False
    messages = resp.json()
    target_msg = next((m for m in messages if m["id"] == msg_id), None)
    if not target_msg:
        print(f"❌ Message {msg_id} not found in messages list")
        return False
    
    reactions = target_msg.get("reactions", [])
    print(f"✅ Message found in list. Reactions: {reactions}")
    
    if len(reactions) != 2:
        print(f"❌ Expected 2 reaction groups, got {len(reactions)}")
        return False
    print(f"✅ VERIFY: GET messages shows same aggregated reactions")
    
    # Step 9: Unauth (no token) call → 401
    print(f"\n[Step 9] Test unauthorized call (no token) → 401...")
    resp = requests.post(
        f"{BASE_URL}/chats/{conv_id}/messages/{msg_id}/react",
        json={"emoji": "👍"},
        timeout=10,
    )
    if resp.status_code != 401:
        print(f"❌ Expected 401, got {resp.status_code}")
        return False
    print(f"✅ VERIFY: Unauthorized call returns 401")
    
    # Step 10: Unknown message id → 404
    print(f"\n[Step 10] Test unknown message id → 404...")
    fake_msg_id = "00000000-0000-0000-0000-000000000000"
    resp = requests.post(
        f"{BASE_URL}/chats/{conv_id}/messages/{fake_msg_id}/react",
        json={"emoji": "👍"},
        headers={"Authorization": f"Bearer {mei_token}"},
        timeout=10,
    )
    if resp.status_code != 404:
        print(f"❌ Expected 404, got {resp.status_code}")
        return False
    if "not found" not in resp.text.lower():
        print(f"❌ Expected 'not found' in error message, got: {resp.text}")
        return False
    print(f"✅ VERIFY: Unknown message id returns 404 'Message not found'")
    
    print(f"\n{'='*80}")
    print(f"✅ TEST A PASSED: All 10 steps verified successfully")
    print(f"{'='*80}")
    return True


def test_feature_b_room_share():
    """
    Test B: POST /api/chats/{cid}/messages accepts room_id (room-share card message)
    
    Steps:
    1. Login mei. Create voice room.
    2. Send room card message: POST /api/chats/{cid}/messages {room_id}
    3. Verify response: type=="room", room_id==room_id, text starts with "🎙️",
       room field contains: id, title, is_live=true, member_count>=1, language, host
    4. GET /api/chats/{cid}/messages - same message with same room field
    5. Verify last_message on conversation reflects preview text
    6. Sending with unknown room_id → 404 "Voice room not found"
    7. Backward compat: POST {text:"Just text"} still returns type="text"
    8. Empty text without room_id → 400
    """
    print("\n" + "="*80)
    print("TEST B: POST /api/chats/{cid}/messages with room_id (room-share card)")
    print("="*80)
    
    # Step 1: Login mei and create voice room
    print("\n[Step 1] Login mei and create voice room...")
    mei_token, mei_id = login(MEI_EMAIL, MEI_PASSWORD)
    diego_token, diego_id = login(DIEGO_EMAIL, DIEGO_PASSWORD)
    print(f"✅ Mei logged in: {mei_id}")
    
    resp = requests.post(
        f"{BASE_URL}/rooms",
        json={
            "title": "Chat Share Test",
            "language": "en",
            "topic": "Talking",
            "mode": "chat",
        },
        headers={"Authorization": f"Bearer {mei_token}"},
        timeout=10,
    )
    if resp.status_code != 201:
        print(f"❌ Failed to create room: {resp.status_code} {resp.text}")
        return False
    room = resp.json()
    room_id = room["id"]
    print(f"✅ Room created: {room_id} - '{room['title']}'")
    
    # Ensure conversation exists
    print(f"\n[Step 1b] Ensure conversation exists between mei and diego...")
    resp = requests.post(
        f"{BASE_URL}/chats",
        json={"partner_id": diego_id},
        headers={"Authorization": f"Bearer {mei_token}"},
        timeout=10,
    )
    if resp.status_code not in [200, 201]:
        print(f"❌ Failed to create/get conversation: {resp.status_code} {resp.text}")
        return False
    conv_id = resp.json()["id"]
    print(f"✅ Conversation ID: {conv_id}")
    
    # Step 2: Send room card message
    print(f"\n[Step 2] Send room card message with room_id...")
    resp = requests.post(
        f"{BASE_URL}/chats/{conv_id}/messages",
        json={"room_id": room_id},
        headers={"Authorization": f"Bearer {mei_token}"},
        timeout=10,
    )
    if resp.status_code != 201:
        print(f"❌ Failed to send room message: {resp.status_code} {resp.text}")
        return False
    msg = resp.json()
    print(f"✅ Room message sent: {msg['id']}")
    print(f"   Message: {msg}")
    
    # Step 3: Verify response fields
    print(f"\n[Step 3] Verify response fields...")
    
    if msg.get("type") != "room":
        print(f"❌ Expected type='room', got '{msg.get('type')}'")
        return False
    print(f"✅ type == 'room'")
    
    if msg.get("room_id") != room_id:
        print(f"❌ Expected room_id={room_id}, got {msg.get('room_id')}")
        return False
    print(f"✅ room_id == {room_id}")
    
    if not msg.get("text", "").startswith("🎙️"):
        print(f"❌ Expected text to start with '🎙️', got '{msg.get('text')}'")
        return False
    print(f"✅ text starts with '🎙️': '{msg['text']}'")
    
    room_field = msg.get("room")
    if not room_field:
        print(f"❌ Expected 'room' field in response, got None")
        return False
    print(f"✅ 'room' field present: {room_field}")
    
    # Verify room field structure
    required_fields = ["id", "title", "is_live", "member_count", "language", "host"]
    for field in required_fields:
        if field not in room_field:
            print(f"❌ Expected '{field}' in room field, not found")
            return False
    print(f"✅ All required room fields present: {required_fields}")
    
    if room_field["title"] != "Chat Share Test":
        print(f"❌ Expected title='Chat Share Test', got '{room_field['title']}'")
        return False
    print(f"✅ room.title == 'Chat Share Test'")
    
    if room_field["is_live"] != True:
        print(f"❌ Expected is_live=true, got {room_field['is_live']}")
        return False
    print(f"✅ room.is_live == true")
    
    if room_field["member_count"] < 1:
        print(f"❌ Expected member_count >= 1, got {room_field['member_count']}")
        return False
    print(f"✅ room.member_count >= 1: {room_field['member_count']}")
    
    if room_field["language"] != "en":
        print(f"❌ Expected language='en', got '{room_field['language']}'")
        return False
    print(f"✅ room.language == 'en'")
    
    host = room_field.get("host")
    if not host or not host.get("id") or not host.get("name"):
        print(f"❌ Expected host with id and name, got {host}")
        return False
    print(f"✅ room.host present: id={host['id']}, name={host['name']}")
    
    # Step 4: GET /api/chats/{cid}/messages - verify same room field
    print(f"\n[Step 4] GET /api/chats/{conv_id}/messages - verify room field persists...")
    resp = requests.get(
        f"{BASE_URL}/chats/{conv_id}/messages",
        headers={"Authorization": f"Bearer {mei_token}"},
        timeout=10,
    )
    if resp.status_code != 200:
        print(f"❌ Failed to get messages: {resp.status_code} {resp.text}")
        return False
    messages = resp.json()
    target_msg = next((m for m in messages if m["id"] == msg["id"]), None)
    if not target_msg:
        print(f"❌ Room message not found in messages list")
        return False
    
    room_field_from_list = target_msg.get("room")
    if not room_field_from_list:
        print(f"❌ Expected 'room' field in message from list, got None")
        return False
    
    if room_field_from_list["title"] != "Chat Share Test":
        print(f"❌ Expected title='Chat Share Test' in list, got '{room_field_from_list['title']}'")
        return False
    
    print(f"✅ GET messages returns same room field: {room_field_from_list}")
    
    # Step 5: Verify last_message on conversation
    print(f"\n[Step 5] Verify last_message on conversation reflects preview text...")
    resp = requests.get(
        f"{BASE_URL}/chats/{conv_id}",
        headers={"Authorization": f"Bearer {mei_token}"},
        timeout=10,
    )
    if resp.status_code != 200:
        print(f"❌ Failed to get conversation: {resp.status_code} {resp.text}")
        return False
    conv = resp.json()
    last_msg = conv.get("last_message")
    if not last_msg:
        print(f"❌ Expected last_message in conversation, got None")
        return False
    
    if not last_msg.get("text", "").startswith("🎙️"):
        print(f"❌ Expected last_message.text to start with '🎙️', got '{last_msg.get('text')}'")
        return False
    
    if "Chat Share Test" not in last_msg.get("text", ""):
        print(f"❌ Expected 'Chat Share Test' in last_message.text, got '{last_msg.get('text')}'")
        return False
    
    print(f"✅ last_message reflects preview text: '{last_msg['text']}'")
    
    # Step 6: Sending with unknown room_id → 404
    print(f"\n[Step 6] Test unknown room_id → 404 'Voice room not found'...")
    fake_room_id = "00000000-0000-0000-0000-000000000000"
    resp = requests.post(
        f"{BASE_URL}/chats/{conv_id}/messages",
        json={"room_id": fake_room_id},
        headers={"Authorization": f"Bearer {mei_token}"},
        timeout=10,
    )
    if resp.status_code != 404:
        print(f"❌ Expected 404, got {resp.status_code}")
        return False
    if "room not found" not in resp.text.lower():
        print(f"❌ Expected 'room not found' in error, got: {resp.text}")
        return False
    print(f"✅ VERIFY: Unknown room_id returns 404 'Voice room not found'")
    
    # Step 7: Backward compat - text message still works
    print(f"\n[Step 7] Backward compat: POST {{text:'Just text'}} returns type='text'...")
    resp = requests.post(
        f"{BASE_URL}/chats/{conv_id}/messages",
        json={"text": "Just text"},
        headers={"Authorization": f"Bearer {mei_token}"},
        timeout=10,
    )
    if resp.status_code != 201:
        print(f"❌ Failed to send text message: {resp.status_code} {resp.text}")
        return False
    msg = resp.json()
    if msg.get("type") != "text":
        print(f"❌ Expected type='text', got '{msg.get('type')}'")
        return False
    if "room" in msg:
        print(f"❌ Expected no 'room' field for text message, got {msg.get('room')}")
        return False
    print(f"✅ VERIFY: Text message returns type='text' with no room field")
    
    # Step 8: Empty text without room_id → 400
    print(f"\n[Step 8] Test empty text without room_id → 400...")
    resp = requests.post(
        f"{BASE_URL}/chats/{conv_id}/messages",
        json={"text": ""},
        headers={"Authorization": f"Bearer {mei_token}"},
        timeout=10,
    )
    if resp.status_code != 400:
        print(f"❌ Expected 400, got {resp.status_code}")
        return False
    print(f"✅ VERIFY: Empty text without room_id returns 400")
    
    print(f"\n{'='*80}")
    print(f"✅ TEST B PASSED: All 8 steps verified successfully")
    print(f"{'='*80}")
    return True


def main():
    print("\n" + "="*80)
    print("ROUND 12 BACKEND TESTING: Chat Reactions + Room-Share Messages")
    print("="*80)
    print(f"Backend URL: {BASE_URL}")
    print(f"Test users: {MEI_EMAIL}, {DIEGO_EMAIL}")
    
    try:
        # Test Feature A: Message reactions
        test_a_passed = test_feature_a_reactions()
        
        # Test Feature B: Room-share messages
        test_b_passed = test_feature_b_room_share()
        
        # Summary
        print("\n" + "="*80)
        print("FINAL SUMMARY")
        print("="*80)
        print(f"Feature A (Message Reactions): {'✅ PASSED' if test_a_passed else '❌ FAILED'}")
        print(f"Feature B (Room-Share Messages): {'✅ PASSED' if test_b_passed else '❌ FAILED'}")
        
        if test_a_passed and test_b_passed:
            print("\n🎉 ALL TESTS PASSED - Both features working correctly!")
            return 0
        else:
            print("\n❌ SOME TESTS FAILED - See details above")
            return 1
            
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
