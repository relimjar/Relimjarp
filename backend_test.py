#!/usr/bin/env python3
"""
Round 17 Backend Testing - Poll Feature on Moments
Tests for:
A) Create moment with 3-option poll
B) Vote for option 0 (Coffee)
C) Revote for option 2 (Water) - one vote per user
D) Diego also votes for option 2
E) Vote on non-existent moment
F) Vote on moment without poll
G) Vote with out-of-range option
H) Create moment with only 1 poll option (invalid)
I) Create moment with poll but no text no image (poll counts as content)
J) Backward compat - no poll field
K) GET /api/moments returns poll in list
"""

import requests
import sys
from datetime import datetime

# Backend URL from frontend/.env
BASE_URL = "https://23e89f0c-4dcc-40fe-82d2-2e242a0a0207.preview.emergentagent.com/api"

# Test credentials
MEI_EMAIL = "mei@demo.com"
MEI_PASSWORD = "Demo1234!"
DIEGO_EMAIL = "diego@demo.com"
DIEGO_PASSWORD = "Demo1234!"

def login(email, password):
    """Login and return token + user data"""
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    if resp.status_code != 200:
        print(f"❌ Login failed for {email}: {resp.status_code} {resp.text}")
        return None, None
    data = resp.json()
    return data.get("token"), data.get("user")

def test_a_create_moment_with_poll():
    """A) Create moment with 3-option poll"""
    print("\n" + "="*80)
    print("TEST A: Create moment with 3-option poll")
    print("="*80)
    
    token, mei_user = login(MEI_EMAIL, MEI_PASSWORD)
    if not token:
        return None
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create moment with poll
    moment_data = {
        "text": "Favorite drink?",
        "poll": {
            "options": [
                {"text": "Coffee"},
                {"text": "Tea"},
                {"text": "Water"}
            ]
        }
    }
    
    resp = requests.post(f"{BASE_URL}/moments", json=moment_data, headers=headers)
    print(f"\n1. POST /api/moments with poll → {resp.status_code}")
    
    if resp.status_code != 201:
        print(f"   ❌ Expected 201, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return None
    
    moment = resp.json()
    moment_id = moment.get("id")
    print(f"   ✅ Moment created with ID: {moment_id}")
    
    # 2. Verify response.poll structure
    print(f"\n2. Verify response.poll:")
    
    poll = moment.get("poll")
    if not poll:
        print(f"   ❌ poll field is missing")
        return None
    
    # Check options length
    options = poll.get("options")
    if not options or len(options) != 3:
        print(f"   ❌ Expected 3 options, got {len(options) if options else 0}")
        return None
    print(f"   ✅ options.length = 3")
    
    # Check each option
    expected_texts = ["Coffee", "Tea", "Water"]
    for i, (opt, expected_text) in enumerate(zip(options, expected_texts)):
        text = opt.get("text")
        votes = opt.get("votes")
        
        if text != expected_text:
            print(f"   ❌ options[{i}].text: expected '{expected_text}', got '{text}'")
            return None
        
        if votes != 0:
            print(f"   ❌ options[{i}].votes: expected 0, got {votes}")
            return None
        
        print(f"   ✅ options[{i}]: text='{text}', votes=0")
    
    # Check total_votes
    total_votes = poll.get("total_votes")
    if total_votes != 0:
        print(f"   ❌ total_votes: expected 0, got {total_votes}")
        return None
    print(f"   ✅ total_votes = 0")
    
    # Check my_vote
    my_vote = poll.get("my_vote")
    if my_vote is not None:
        print(f"   ❌ my_vote: expected null, got {my_vote}")
        return None
    print(f"   ✅ my_vote = null")
    
    print(f"\n✅ TEST A PASSED")
    return moment_id

def test_b_vote_for_option_0(moment_id):
    """B) Vote for option 0 (Coffee)"""
    print("\n" + "="*80)
    print("TEST B: Vote for option 0 (Coffee)")
    print("="*80)
    
    token, mei_user = login(MEI_EMAIL, MEI_PASSWORD)
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Vote for option 0
    vote_data = {"option_index": 0}
    resp = requests.post(f"{BASE_URL}/moments/{moment_id}/vote", json=vote_data, headers=headers)
    print(f"\n1. POST /api/moments/{moment_id}/vote (option_index=0) → {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"   ❌ Expected 200, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    moment = resp.json()
    
    # 2. Verify response.poll
    print(f"\n2. Verify response.poll after voting:")
    
    poll = moment.get("poll")
    if not poll:
        print(f"   ❌ poll field is missing")
        return False
    
    options = poll.get("options")
    
    # Check option 0 votes
    if options[0].get("votes") != 1:
        print(f"   ❌ options[0].votes: expected 1, got {options[0].get('votes')}")
        return False
    print(f"   ✅ options[0].votes = 1")
    
    # Check option 1 votes
    if options[1].get("votes") != 0:
        print(f"   ❌ options[1].votes: expected 0, got {options[1].get('votes')}")
        return False
    print(f"   ✅ options[1].votes = 0")
    
    # Check option 2 votes
    if options[2].get("votes") != 0:
        print(f"   ❌ options[2].votes: expected 0, got {options[2].get('votes')}")
        return False
    print(f"   ✅ options[2].votes = 0")
    
    # Check my_vote
    my_vote = poll.get("my_vote")
    if my_vote != 0:
        print(f"   ❌ my_vote: expected 0, got {my_vote}")
        return False
    print(f"   ✅ my_vote = 0")
    
    # Check total_votes
    total_votes = poll.get("total_votes")
    if total_votes != 1:
        print(f"   ❌ total_votes: expected 1, got {total_votes}")
        return False
    print(f"   ✅ total_votes = 1")
    
    print(f"\n✅ TEST B PASSED")
    return True

def test_c_revote_for_option_2(moment_id):
    """C) Revote for option 2 (Water) - one vote per user"""
    print("\n" + "="*80)
    print("TEST C: Revote for option 2 (Water) - one vote per user")
    print("="*80)
    
    token, mei_user = login(MEI_EMAIL, MEI_PASSWORD)
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Revote for option 2
    vote_data = {"option_index": 2}
    resp = requests.post(f"{BASE_URL}/moments/{moment_id}/vote", json=vote_data, headers=headers)
    print(f"\n1. POST /api/moments/{moment_id}/vote (option_index=2) → {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"   ❌ Expected 200, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    moment = resp.json()
    
    # 2. Verify response.poll
    print(f"\n2. Verify response.poll after revoting:")
    
    poll = moment.get("poll")
    if not poll:
        print(f"   ❌ poll field is missing")
        return False
    
    options = poll.get("options")
    
    # Check option 0 votes (should be 0 now, vote moved)
    if options[0].get("votes") != 0:
        print(f"   ❌ options[0].votes: expected 0, got {options[0].get('votes')}")
        return False
    print(f"   ✅ options[0].votes = 0 (vote moved from Coffee)")
    
    # Check option 1 votes
    if options[1].get("votes") != 0:
        print(f"   ❌ options[1].votes: expected 0, got {options[1].get('votes')}")
        return False
    print(f"   ✅ options[1].votes = 0")
    
    # Check option 2 votes (should be 1 now)
    if options[2].get("votes") != 1:
        print(f"   ❌ options[2].votes: expected 1, got {options[2].get('votes')}")
        return False
    print(f"   ✅ options[2].votes = 1 (vote moved to Water)")
    
    # Check my_vote
    my_vote = poll.get("my_vote")
    if my_vote != 2:
        print(f"   ❌ my_vote: expected 2, got {my_vote}")
        return False
    print(f"   ✅ my_vote = 2")
    
    # Check total_votes (should still be 1, not 2)
    total_votes = poll.get("total_votes")
    if total_votes != 1:
        print(f"   ❌ total_votes: expected 1 (still 1, not 2), got {total_votes}")
        return False
    print(f"   ✅ total_votes = 1 (still 1, not 2 - vote moved, not added)")
    
    print(f"\n✅ TEST C PASSED")
    return True

def test_d_diego_votes_option_2(moment_id):
    """D) Diego also votes for option 2"""
    print("\n" + "="*80)
    print("TEST D: Diego also votes for option 2")
    print("="*80)
    
    diego_token, diego_user = login(DIEGO_EMAIL, DIEGO_PASSWORD)
    if not diego_token:
        return False
    
    diego_headers = {"Authorization": f"Bearer {diego_token}"}
    
    # 1. Diego votes for option 2
    vote_data = {"option_index": 2}
    resp = requests.post(f"{BASE_URL}/moments/{moment_id}/vote", json=vote_data, headers=diego_headers)
    print(f"\n1. POST /api/moments/{moment_id}/vote as Diego (option_index=2) → {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"   ❌ Expected 200, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    moment = resp.json()
    
    # 2. Verify response.poll from Diego's POV
    print(f"\n2. Verify response.poll from Diego's POV:")
    
    poll = moment.get("poll")
    if not poll:
        print(f"   ❌ poll field is missing")
        return False
    
    options = poll.get("options")
    
    # Check option 2 votes (should be 2 now: mei + diego)
    if options[2].get("votes") != 2:
        print(f"   ❌ options[2].votes: expected 2, got {options[2].get('votes')}")
        return False
    print(f"   ✅ options[2].votes = 2 (mei + diego)")
    
    # Check total_votes
    total_votes = poll.get("total_votes")
    if total_votes != 2:
        print(f"   ❌ total_votes: expected 2, got {total_votes}")
        return False
    print(f"   ✅ total_votes = 2")
    
    # Check my_vote from Diego's POV
    my_vote = poll.get("my_vote")
    if my_vote != 2:
        print(f"   ❌ my_vote (Diego's): expected 2, got {my_vote}")
        return False
    print(f"   ✅ my_vote = 2 (from Diego's view)")
    
    # 3. GET moment as Mei and verify
    mei_token, mei_user = login(MEI_EMAIL, MEI_PASSWORD)
    mei_headers = {"Authorization": f"Bearer {mei_token}"}
    
    resp = requests.get(f"{BASE_URL}/moments/{moment_id}", headers=mei_headers)
    print(f"\n3. GET /api/moments/{moment_id} as Mei → {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"   ❌ Expected 200, got {resp.status_code}")
        return False
    
    moment = resp.json()
    poll = moment.get("poll")
    
    # Check my_vote from Mei's POV
    my_vote = poll.get("my_vote")
    if my_vote != 2:
        print(f"   ❌ my_vote (Mei's): expected 2, got {my_vote}")
        return False
    print(f"   ✅ my_vote = 2 (from Mei's view)")
    
    # Check total_votes
    total_votes = poll.get("total_votes")
    if total_votes != 2:
        print(f"   ❌ total_votes: expected 2, got {total_votes}")
        return False
    print(f"   ✅ total_votes = 2 (both mei + diego on option 2)")
    
    print(f"\n✅ TEST D PASSED")
    return True

def test_e_vote_nonexistent_moment():
    """E) Vote on non-existent moment"""
    print("\n" + "="*80)
    print("TEST E: Vote on non-existent moment")
    print("="*80)
    
    token, mei_user = login(MEI_EMAIL, MEI_PASSWORD)
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Vote on non-existent moment
    fake_id = "nonexistent-id-xxx"
    vote_data = {"option_index": 0}
    resp = requests.post(f"{BASE_URL}/moments/{fake_id}/vote", json=vote_data, headers=headers)
    print(f"\n1. POST /api/moments/{fake_id}/vote → {resp.status_code}")
    
    if resp.status_code != 404:
        print(f"   ❌ Expected 404, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    print(f"   ✅ Non-existent moment correctly returns 404")
    
    print(f"\n✅ TEST E PASSED")
    return True

def test_f_vote_moment_without_poll():
    """F) Vote on moment without poll"""
    print("\n" + "="*80)
    print("TEST F: Vote on moment without poll")
    print("="*80)
    
    token, mei_user = login(MEI_EMAIL, MEI_PASSWORD)
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create moment without poll
    moment_data = {"text": "just text"}
    resp = requests.post(f"{BASE_URL}/moments", json=moment_data, headers=headers)
    print(f"\n1. POST /api/moments (no poll) → {resp.status_code}")
    
    if resp.status_code != 201:
        print(f"   ❌ Expected 201, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    moment = resp.json()
    moment_id = moment.get("id")
    print(f"   ✅ Moment created without poll, ID: {moment_id}")
    
    # 2. Try to vote on it
    vote_data = {"option_index": 0}
    resp = requests.post(f"{BASE_URL}/moments/{moment_id}/vote", json=vote_data, headers=headers)
    print(f"\n2. POST /api/moments/{moment_id}/vote → {resp.status_code}")
    
    if resp.status_code != 400:
        print(f"   ❌ Expected 400, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    # Check error message
    error_data = resp.json()
    detail = error_data.get("detail", "")
    if "no poll" not in detail.lower():
        print(f"   ❌ Expected error message about 'no poll', got: {detail}")
        return False
    
    print(f"   ✅ Voting on moment without poll returns 400 with detail: '{detail}'")
    
    print(f"\n✅ TEST F PASSED")
    return True

def test_g_vote_out_of_range():
    """G) Vote with out-of-range option"""
    print("\n" + "="*80)
    print("TEST G: Vote with out-of-range option")
    print("="*80)
    
    token, mei_user = login(MEI_EMAIL, MEI_PASSWORD)
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create moment with poll
    moment_data = {
        "text": "Test poll",
        "poll": {
            "options": [
                {"text": "A"},
                {"text": "B"}
            ]
        }
    }
    
    resp = requests.post(f"{BASE_URL}/moments", json=moment_data, headers=headers)
    print(f"\n1. POST /api/moments with 2-option poll → {resp.status_code}")
    
    if resp.status_code != 201:
        print(f"   ❌ Expected 201, got {resp.status_code}")
        return False
    
    moment = resp.json()
    moment_id = moment.get("id")
    print(f"   ✅ Moment created with 2 options")
    
    # 2. Try to vote with option_index=99
    vote_data = {"option_index": 99}
    resp = requests.post(f"{BASE_URL}/moments/{moment_id}/vote", json=vote_data, headers=headers)
    print(f"\n2. POST /api/moments/{moment_id}/vote (option_index=99) → {resp.status_code}")
    
    if resp.status_code != 422:
        print(f"   ❌ Expected 422 (Pydantic validation), got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    print(f"   ✅ Out-of-range option correctly returns 422 (Pydantic ge/le validation)")
    
    print(f"\n✅ TEST G PASSED")
    return True

def test_h_poll_with_only_1_option():
    """H) Create moment with only 1 poll option (invalid)"""
    print("\n" + "="*80)
    print("TEST H: Create moment with only 1 poll option (invalid)")
    print("="*80)
    
    token, mei_user = login(MEI_EMAIL, MEI_PASSWORD)
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Try to create moment with only 1 poll option
    moment_data = {
        "text": "bad poll",
        "poll": {
            "options": [
                {"text": "only one"}
            ]
        }
    }
    
    resp = requests.post(f"{BASE_URL}/moments", json=moment_data, headers=headers)
    print(f"\n1. POST /api/moments with 1 poll option → {resp.status_code}")
    
    if resp.status_code != 422:
        print(f"   ❌ Expected 422 (Pydantic min_length validation), got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    print(f"   ✅ 1-option poll correctly rejected with 422 (Pydantic min_length=2)")
    
    print(f"\n✅ TEST H PASSED")
    return True

def test_i_poll_without_text_or_image():
    """I) Create moment with poll but no text no image (poll counts as content)"""
    print("\n" + "="*80)
    print("TEST I: Create moment with poll but no text no image (poll counts as content)")
    print("="*80)
    
    token, mei_user = login(MEI_EMAIL, MEI_PASSWORD)
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create moment with poll only (no text, no image)
    moment_data = {
        "poll": {
            "options": [
                {"text": "A"},
                {"text": "B"}
            ]
        }
    }
    
    resp = requests.post(f"{BASE_URL}/moments", json=moment_data, headers=headers)
    print(f"\n1. POST /api/moments with poll only (no text, no image) → {resp.status_code}")
    
    if resp.status_code != 201:
        print(f"   ❌ Expected 201 (poll counts as content), got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    moment = resp.json()
    poll = moment.get("poll")
    
    if not poll:
        print(f"   ❌ poll field is missing")
        return False
    
    print(f"   ✅ Moment with poll only created successfully (poll counts as content)")
    
    print(f"\n✅ TEST I PASSED")
    return True

def test_j_backward_compat_no_poll():
    """J) Backward compat - no poll field"""
    print("\n" + "="*80)
    print("TEST J: Backward compat - no poll field")
    print("="*80)
    
    token, mei_user = login(MEI_EMAIL, MEI_PASSWORD)
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create moment without poll
    moment_data = {"text": "hi"}
    resp = requests.post(f"{BASE_URL}/moments", json=moment_data, headers=headers)
    print(f"\n1. POST /api/moments (no poll field) → {resp.status_code}")
    
    if resp.status_code != 201:
        print(f"   ❌ Expected 201, got {resp.status_code}")
        print(f"   Response: {resp.text}")
        return False
    
    moment = resp.json()
    poll = moment.get("poll")
    
    if poll is not None:
        print(f"   ❌ Expected poll=null, got {repr(poll)}")
        return False
    
    print(f"   ✅ Moment without poll returns poll=null (backward compatible)")
    
    print(f"\n✅ TEST J PASSED")
    return True

def test_k_get_moments_returns_poll():
    """K) GET /api/moments returns poll in list"""
    print("\n" + "="*80)
    print("TEST K: GET /api/moments returns poll in list")
    print("="*80)
    
    token, mei_user = login(MEI_EMAIL, MEI_PASSWORD)
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create moment with poll
    moment_data = {
        "text": "List test poll",
        "poll": {
            "options": [
                {"text": "Option A"},
                {"text": "Option B"}
            ]
        }
    }
    
    resp = requests.post(f"{BASE_URL}/moments", json=moment_data, headers=headers)
    print(f"\n1. POST /api/moments with poll → {resp.status_code}")
    
    if resp.status_code != 201:
        print(f"   ❌ Expected 201, got {resp.status_code}")
        return False
    
    moment = resp.json()
    moment_id = moment.get("id")
    print(f"   ✅ Moment created with poll, ID: {moment_id}")
    
    # 2. GET /api/moments and verify poll is in list
    resp = requests.get(f"{BASE_URL}/moments", headers=headers)
    print(f"\n2. GET /api/moments → {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"   ❌ Expected 200, got {resp.status_code}")
        return False
    
    moments = resp.json()
    
    # Find the most recent moment (should be first in list)
    if not moments:
        print(f"   ❌ No moments found")
        return False
    
    first_moment = moments[0]
    
    # Verify it has poll field
    poll = first_moment.get("poll")
    if not poll:
        print(f"   ❌ First moment in list doesn't have poll field")
        print(f"   First moment text: {first_moment.get('text')}")
        return False
    
    # Verify poll structure
    options = poll.get("options")
    if not options or len(options) < 2:
        print(f"   ❌ Poll options missing or invalid")
        return False
    
    print(f"   ✅ GET /api/moments returns poll field correctly")
    print(f"   ✅ First moment has poll with {len(options)} options")
    print(f"   ✅ Poll structure: question={poll.get('question')}, total_votes={poll.get('total_votes')}, my_vote={poll.get('my_vote')}")
    
    print(f"\n✅ TEST K PASSED")
    return True

def main():
    print("\n" + "="*80)
    print("ROUND 17 BACKEND TESTING - POLL FEATURE ON MOMENTS")
    print("="*80)
    print(f"Backend URL: {BASE_URL}")
    print(f"Test users: {MEI_EMAIL}, {DIEGO_EMAIL}")
    
    results = {}
    
    # Test A: Create moment with 3-option poll
    moment_id = test_a_create_moment_with_poll()
    results["A"] = bool(moment_id)
    
    if moment_id:
        # Test B: Vote for option 0
        results["B"] = test_b_vote_for_option_0(moment_id)
        
        # Test C: Revote for option 2
        results["C"] = test_c_revote_for_option_2(moment_id)
        
        # Test D: Diego votes for option 2
        results["D"] = test_d_diego_votes_option_2(moment_id)
    else:
        results["B"] = False
        results["C"] = False
        results["D"] = False
    
    # Test E: Vote on non-existent moment
    results["E"] = test_e_vote_nonexistent_moment()
    
    # Test F: Vote on moment without poll
    results["F"] = test_f_vote_moment_without_poll()
    
    # Test G: Vote with out-of-range option
    results["G"] = test_g_vote_out_of_range()
    
    # Test H: Create moment with only 1 poll option
    results["H"] = test_h_poll_with_only_1_option()
    
    # Test I: Create moment with poll but no text no image
    results["I"] = test_i_poll_without_text_or_image()
    
    # Test J: Backward compat - no poll field
    results["J"] = test_j_backward_compat_no_poll()
    
    # Test K: GET /api/moments returns poll in list
    results["K"] = test_k_get_moments_returns_poll()
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"Test {test}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
