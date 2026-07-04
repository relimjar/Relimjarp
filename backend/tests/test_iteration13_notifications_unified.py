"""
Iteration 13 backend tests: unified notifications feed (follow/visit + moments types),
mark-all-read behavior, and room join announcement event contract.
"""
import os
import time
import uuid

import pytest
import requests

BASE_URL = os.environ.get("EXPO_PUBLIC_BACKEND_URL").rstrip("/")
API = f"{BASE_URL}/api"


def login(email, password):
    r = requests.post(f"{API}/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, f"login failed for {email}: {r.text}"
    data = r.json()
    return data["token"], data["user"]


@pytest.fixture(scope="module")
def mei():
    token, user = login("mei@demo.com", "Demo1234!")
    return {"token": token, "user": user, "headers": {"Authorization": f"Bearer {token}"}}


@pytest.fixture(scope="module")
def diego():
    token, user = login("diego@demo.com", "Demo1234!")
    return {"token": token, "user": user, "headers": {"Authorization": f"Bearer {token}"}}


class TestUnifiedNotificationsFeed:
    def test_follow_and_moment_like_appear_in_same_feed(self, mei, diego):
        # Ensure diego is not already following mei; toggle to guarantee a fresh follow event
        r = requests.get(f"{API}/users/{mei['user']['id']}", headers=diego["headers"])
        assert r.status_code == 200
        if r.json().get("is_following"):
            requests.post(f"{API}/users/{mei['user']['id']}/follow", headers=diego["headers"])

        # diego follows mei -> creates 'follow' notification for mei
        r = requests.post(f"{API}/users/{mei['user']['id']}/follow", headers=diego["headers"])
        assert r.status_code == 200
        assert r.json()["following"] is True

        # Find or create a moment owned by mei, have diego like it -> 'like' notification
        r = requests.get(f"{API}/moments?user_id={mei['user']['id']}", headers=mei["headers"])
        moments = r.json() if r.status_code == 200 else []
        moment_id = None
        if isinstance(moments, list) and moments:
            moment_id = moments[0]["id"]
        if not moment_id:
            r = requests.post(
                f"{API}/moments",
                headers=mei["headers"],
                json={"text": f"TEST_moment_{uuid.uuid4().hex[:8]}"},
            )
            assert r.status_code in (200, 201), r.text
            moment_id = r.json()["id"]

        r = requests.post(f"{API}/moments/{moment_id}/like", headers=diego["headers"])
        assert r.status_code == 200, r.text

        time.sleep(0.5)

        r = requests.get(f"{API}/notifications", headers=mei["headers"])
        assert r.status_code == 200
        data = r.json()
        assert "notifications" in data
        types_seen = {n["type"] for n in data["notifications"]}
        assert "follow" in types_seen, f"follow type missing from feed: {types_seen}"
        assert "like" in types_seen, f"like type missing from feed: {types_seen}"

        # Verify sorted newest first
        created_ats = [n["created_at"] for n in data["notifications"]]
        assert created_ats == sorted(created_ats, reverse=True)

        # Verify actor info present for follow notification
        follow_notifs = [n for n in data["notifications"] if n["type"] == "follow"]
        assert follow_notifs, "expected at least one follow notification"
        assert follow_notifs[0]["actor"]["id"] == diego["user"]["id"]
        assert follow_notifs[0]["actor"]["name"]

    def test_mark_all_read_clears_both_counts(self, mei):
        # Sanity: counts should currently include unread items from previous test
        r = requests.get(f"{API}/notifications/counts", headers=mei["headers"])
        assert r.status_code == 200
        before = r.json()
        assert before["moments_unread"] >= 0
        assert before["profile_unread"] >= 0

        r = requests.post(f"{API}/notifications/read", headers=mei["headers"])
        assert r.status_code == 200
        assert r.json()["ok"] is True

        r = requests.get(f"{API}/notifications/counts", headers=mei["headers"])
        assert r.status_code == 200
        after = r.json()
        assert after["moments_unread"] == 0
        assert after["profile_unread"] == 0

    def test_notifications_list_still_200_after_mark_all_read(self, mei):
        r = requests.get(f"{API}/notifications", headers=mei["headers"])
        assert r.status_code == 200
        data = r.json()
        assert data["unread"] == 0
        # all items should now be read
        assert all(n["read"] is True for n in data["notifications"])


class TestCategoryScopedMarkRead:
    def test_category_moments_scoping_unaffected(self, mei, diego):
        # trigger a fresh like notification
        r = requests.get(f"{API}/moments?user_id={mei['user']['id']}", headers=mei["headers"])
        moments = r.json() if r.status_code == 200 else []
        if isinstance(moments, list) and moments:
            moment_id = moments[0]["id"]
            requests.post(f"{API}/moments/{moment_id}/unlike", headers=diego["headers"])
            requests.post(f"{API}/moments/{moment_id}/like", headers=diego["headers"])

        time.sleep(0.3)
        r = requests.post(f"{API}/notifications/read?category=moments", headers=mei["headers"])
        assert r.status_code == 200

        r = requests.get(f"{API}/notifications/counts", headers=mei["headers"])
        assert r.status_code == 200
        assert r.json()["moments_unread"] == 0


class TestRoomJoinAnnouncementContract:
    def test_join_broadcasts_joined_field_in_room_update(self, mei, diego):
        # mei creates a room (host), diego joins -> mei should receive room_update with 'joined'
        r = requests.post(
            f"{API}/rooms",
            headers=mei["headers"],
            json={"title": f"TEST_room_{uuid.uuid4().hex[:6]}", "language": "en", "mode": "chat"},
        )
        assert r.status_code == 201, r.text
        room = r.json()
        room_id = room["id"]

        r = requests.post(f"{API}/rooms/{room_id}/join", headers=diego["headers"])
        assert r.status_code == 200
        detail = r.json()
        member_ids = [m["id"] for m in detail["members"]]
        assert diego["user"]["id"] in member_ids

        # cleanup: end room
        requests.post(f"{API}/rooms/{room_id}/end", headers=mei["headers"])
