"""
"Lessons" — a gamified, bite-sized language learning sub-app (skill path,
XP, streaks, hearts, gems, leaderboard). No auth of its own — maps to the
logged-in main-app user. Original content lives in lessons_content.py.
"""

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from auth_utils import CurrentUser
from db import lessons_profiles_col
from routes.lessons_content import (
    COURSES,
    build_exercises,
    get_path,
    list_courses,
)

router = APIRouter(prefix="/lessons", tags=["lessons"])

MAX_HEARTS = 5
DAILY_GOAL_DEFAULT = 30  # xp


def _today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _week_key() -> str:
    d = datetime.now(timezone.utc).date()
    return f"{d.isocalendar().year}-W{d.isocalendar().week}"


def profile_public(d: dict) -> dict:
    return {
        "id": d["_id"],
        "xp": d.get("xp", 0),
        "weekly_xp": d.get("weekly_xp", 0),
        "streak": d.get("streak", 0),
        "hearts": d.get("hearts", MAX_HEARTS),
        "gems": d.get("gems", 0),
        "daily_goal": d.get("daily_goal", DAILY_GOAL_DEFAULT),
        "xp_today": d.get("xp_today", 0),
        "active_course": d.get("active_course", "es"),
        "completed": d.get("completed", []),
        "name": d.get("name"),
        "avatar_url": d.get("avatar_url"),
    }


async def _ensure(user: dict) -> dict:
    uid = user["_id"]
    p = await lessons_profiles_col.find_one({"external_user_id": uid})
    if p:
        return await _rollover(p)
    doc = {
        "_id": str(uuid.uuid4()),
        "external_user_id": uid,
        "name": user.get("name") or "Learner",
        "avatar_url": user.get("avatar_url"),
        "xp": 0,
        "weekly_xp": 0,
        "week_key": _week_key(),
        "xp_today": 0,
        "streak": 0,
        "hearts": MAX_HEARTS,
        "gems": 20,
        "daily_goal": DAILY_GOAL_DEFAULT,
        "active_course": "es",
        "completed": [],
        "last_active": None,
        "hearts_updated": _today(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await lessons_profiles_col.insert_one(doc)
    return doc


async def _rollover(p: dict) -> dict:
    """Reset day/week counters + regenerate a heart per day of absence."""
    updates: dict = {}
    today = _today()
    if p.get("week_key") != _week_key():
        updates["week_key"] = _week_key()
        updates["weekly_xp"] = 0
    if p.get("hearts_updated") != today:
        # +1 heart for each day since last update, capped
        try:
            last = datetime.fromisoformat(p.get("hearts_updated") or today).date()
            gap = (datetime.now(timezone.utc).date() - last).days
        except Exception:
            gap = 1
        new_hearts = min(MAX_HEARTS, p.get("hearts", MAX_HEARTS) + max(1, gap))
        updates["hearts"] = new_hearts
        updates["hearts_updated"] = today
        updates["xp_today"] = 0
    if updates:
        await lessons_profiles_col.update_one({"_id": p["_id"]}, {"$set": updates})
        p.update(updates)
    return p


# --------------------------------------------------------------------------- #
@router.get("/me")
async def get_me(current_user: CurrentUser):
    p = await _ensure(current_user)
    return profile_public(p)


@router.get("/courses")
async def courses(current_user: CurrentUser):
    return list_courses()


class CourseSelect(BaseModel):
    lang: str


@router.post("/course")
async def set_course(body: CourseSelect, current_user: CurrentUser):
    if body.lang not in COURSES:
        raise HTTPException(status_code=404, detail="Course not found")
    p = await _ensure(current_user)
    await lessons_profiles_col.update_one(
        {"_id": p["_id"]}, {"$set": {"active_course": body.lang}}
    )
    return {"active_course": body.lang}


@router.get("/path")
async def path(current_user: CurrentUser, lang: str | None = None):
    p = await _ensure(current_user)
    lang = lang or p.get("active_course", "es")
    if lang not in COURSES:
        raise HTTPException(status_code=404, detail="Course not found")
    units = get_path(lang)
    completed = set(p.get("completed", []))
    # Determine unlocked: a lesson is unlocked if it's the first, or the
    # previous lesson (in flat order) is completed.
    flat = [s for u in units for s in u["skills"]]
    unlocked_ids = set()
    prev_done = True
    for s in flat:
        if prev_done or s["lesson_id"] in completed:
            unlocked_ids.add(s["lesson_id"])
        prev_done = s["lesson_id"] in completed
    for u in units:
        for s in u["skills"]:
            s["completed"] = s["lesson_id"] in completed
            s["unlocked"] = s["lesson_id"] in unlocked_ids or s["completed"]
    return {"lang": lang, "name": COURSES[lang]["name"], "units": units}


@router.get("/lesson/{lesson_id}")
async def lesson(lesson_id: str, current_user: CurrentUser):
    lang = lesson_id.split("-")[0]
    if lang not in COURSES:
        raise HTTPException(status_code=404, detail="Lesson not found")
    exercises = build_exercises(lang, lesson_id)
    if not exercises:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return {"lesson_id": lesson_id, "exercises": exercises}


class CompleteBody(BaseModel):
    lesson_id: str
    correct: int
    total: int
    hearts_left: int | None = None


@router.post("/complete")
async def complete(body: CompleteBody, current_user: CurrentUser):
    p = await _ensure(current_user)
    base_xp = 10
    accuracy = (body.correct / body.total) if body.total else 0
    bonus = 5 if accuracy >= 0.99 else 0
    first_time = body.lesson_id not in set(p.get("completed", []))
    earned = base_xp + bonus + (5 if first_time else 0)

    today = _today()
    updates: dict = {
        "$inc": {"xp": earned, "weekly_xp": earned, "xp_today": earned},
        "$set": {"last_active": today},
    }
    if first_time:
        updates.setdefault("$addToSet", {})["completed"] = body.lesson_id
        updates["$inc"]["gems"] = 2
    if body.hearts_left is not None:
        updates["$set"]["hearts"] = max(0, min(MAX_HEARTS, body.hearts_left))

    # Streak: increment if last streak day wasn't today.
    last = p.get("last_active")
    if last != today:
        yesterday = (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()
        new_streak = p.get("streak", 0) + 1 if last == yesterday or last is None else 1
        updates["$set"]["streak"] = new_streak

    await lessons_profiles_col.update_one({"_id": p["_id"]}, updates)
    p = await lessons_profiles_col.find_one({"_id": p["_id"]})
    return {"earned_xp": earned, "profile": profile_public(p)}


class HeartRefill(BaseModel):
    pass


@router.post("/hearts/refill")
async def refill_hearts(current_user: CurrentUser):
    p = await _ensure(current_user)
    cost = 15
    if p.get("hearts", 0) >= MAX_HEARTS:
        return {"hearts": p["hearts"], "gems": p.get("gems", 0)}
    if p.get("gems", 0) < cost:
        raise HTTPException(status_code=400, detail="Not enough gems")
    await lessons_profiles_col.update_one(
        {"_id": p["_id"]},
        {"$set": {"hearts": MAX_HEARTS}, "$inc": {"gems": -cost}},
    )
    p = await lessons_profiles_col.find_one({"_id": p["_id"]})
    return {"hearts": p["hearts"], "gems": p.get("gems", 0)}


@router.get("/leaderboard")
async def leaderboard(current_user: CurrentUser):
    await _ensure(current_user)
    cursor = lessons_profiles_col.find({"week_key": _week_key()}).sort("weekly_xp", -1)
    rows = await cursor.to_list(30)
    if len(rows) < 3:
        # include everyone if the week just rolled over
        rows = await lessons_profiles_col.find({}).sort("weekly_xp", -1).to_list(30)
    me = current_user["_id"]
    return [
        {
            "rank": i + 1,
            "name": r.get("name"),
            "avatar_url": r.get("avatar_url"),
            "weekly_xp": r.get("weekly_xp", 0),
            "is_me": r.get("external_user_id") == me,
        }
        for i, r in enumerate(rows)
    ]


@router.get("/quests")
async def quests(current_user: CurrentUser):
    p = await _ensure(current_user)
    xp_today = p.get("xp_today", 0)
    goal = p.get("daily_goal", DAILY_GOAL_DEFAULT)
    return {
        "daily": [
            {"id": "earn_xp", "title": f"Earn {goal} XP", "icon": "flash",
             "progress": min(xp_today, goal), "target": goal},
            {"id": "lessons_2", "title": "Complete 2 lessons", "icon": "checkmark-done",
             "progress": min(2, len([1 for _ in range(min(2, xp_today // 10))])), "target": 2},
            {"id": "perfect", "title": "Get a perfect lesson", "icon": "star",
             "progress": 0, "target": 1},
        ],
        "streak": p.get("streak", 0),
    }
