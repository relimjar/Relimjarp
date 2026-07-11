"""
Vocab sub-app backend.

Everything a user needs for the 100%-designed Vocab redesign lives here:
- Static-ish content library (topics, words, lessons) seeded on startup.
- Per-user progress (word mastery, lesson completion, streak, XP, level).
- Bookmarks (tutors + words).
- Bookings (private tutor lessons).
- Challenges with computed per-user progress.

Everything is 100% idempotent so restarts are safe.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from auth_utils import get_current_user
from db import db

router = APIRouter(prefix="/vocab", tags=["vocab"])

# --------------------------------------------------------------------------- #
# Collections
# --------------------------------------------------------------------------- #
vocab_topics_col = db["vocab_topics"]
vocab_words_col = db["vocab_words"]
vocab_lessons_col = db["vocab_lessons"]
vocab_progress_col = db["vocab_progress"]          # per (user, word)
vocab_lesson_prog_col = db["vocab_lesson_prog"]    # per (user, lesson)
vocab_bookmarks_col = db["vocab_bookmarks"]        # per (user, target_type, target_id)
vocab_bookings_col = db["vocab_bookings"]          # per (user, tutor, slot)
vocab_challenges_col = db["vocab_challenges"]

CurrentUser = Annotated[dict, Depends(get_current_user)]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _today_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


# --------------------------------------------------------------------------- #
# Seed content
# --------------------------------------------------------------------------- #
TOPICS_SEED: list[dict[str, Any]] = [
    {"id": "medicine", "name": "Medicine", "subtitle": "For healthcare providers", "icon": "medical-outline", "color": "lime"},
    {"id": "virology", "name": "Virology", "subtitle": "Viruses & immunology", "icon": "nutrition-outline", "color": "mint"},
    {"id": "pharmacy", "name": "Pharmacy", "subtitle": "Medicines & prescriptions", "icon": "medkit-outline", "color": "purple"},
    {"id": "genetics", "name": "Genetics", "subtitle": "DNA & heredity", "icon": "git-branch-outline", "color": "mint"},
    {"id": "anatomy", "name": "Anatomy", "subtitle": "Body systems", "icon": "body-outline", "color": "purple"},
    {"id": "education", "name": "Education", "subtitle": "For education professionals", "icon": "school-outline", "color": "lime"},
    {"id": "business", "name": "Business", "subtitle": "For career development", "icon": "briefcase-outline", "color": "lime"},
    {"id": "science", "name": "Science", "subtitle": "For university students", "icon": "flask-outline", "color": "lime"},
    {"id": "tech", "name": "Tech", "subtitle": "For software engineers", "icon": "code-slash-outline", "color": "purple"},
    {"id": "travel", "name": "Travel", "subtitle": "For nomads & tourists", "icon": "airplane-outline", "color": "mint"},
]

# Word bank keyed by topic id.  Each word carries a definition + a translation
# (kept generic English → simple gloss so the UI works out of the box).
WORDS_SEED: dict[str, list[dict[str, str]]] = {
    "medicine": [
        {"term": "Diagnosis", "translation": "identifying an illness", "example": "The doctor confirmed the diagnosis after several tests."},
        {"term": "Prognosis", "translation": "likely course of an illness", "example": "The prognosis is good with early treatment."},
        {"term": "Symptom", "translation": "physical or mental feature of illness", "example": "Fever is a common symptom of infection."},
        {"term": "Chronic", "translation": "long-lasting", "example": "She suffers from chronic back pain."},
        {"term": "Acute", "translation": "sudden and severe", "example": "He had an acute allergic reaction."},
        {"term": "Prescribe", "translation": "order medicine or treatment", "example": "The doctor prescribed antibiotics."},
        {"term": "Referral", "translation": "sending a patient to a specialist", "example": "I need a referral to see a cardiologist."},
        {"term": "Consent", "translation": "permission for treatment", "example": "The patient signed the consent form."},
    ],
    "virology": [
        {"term": "Pathogen", "translation": "disease-causing agent", "example": "Viruses are a common type of pathogen."},
        {"term": "Antibody", "translation": "immune protein", "example": "Antibodies help fight infection."},
        {"term": "Vaccine", "translation": "trains immunity", "example": "The vaccine reduces severe disease."},
        {"term": "Contagious", "translation": "easily spread", "example": "Measles is highly contagious."},
        {"term": "Quarantine", "translation": "isolation to prevent spread", "example": "He was placed in quarantine for 10 days."},
        {"term": "Outbreak", "translation": "sudden appearance of a disease", "example": "There is a flu outbreak at the school."},
    ],
    "pharmacy": [
        {"term": "Dosage", "translation": "amount of medicine", "example": "The dosage is one tablet twice a day."},
        {"term": "Side effect", "translation": "unwanted effect", "example": "Drowsiness is a common side effect."},
        {"term": "Refill", "translation": "renew a prescription", "example": "I need a refill for my medication."},
        {"term": "Over the counter", "translation": "no prescription needed", "example": "Ibuprofen is over the counter."},
        {"term": "Generic", "translation": "non-brand version", "example": "The generic works the same as the brand."},
    ],
    "genetics": [
        {"term": "Gene", "translation": "unit of heredity", "example": "This gene affects eye color."},
        {"term": "DNA", "translation": "genetic material", "example": "DNA carries genetic information."},
        {"term": "Mutation", "translation": "change in DNA", "example": "A mutation can cause disease."},
        {"term": "Heredity", "translation": "passing traits from parents", "example": "Heredity shapes many traits."},
    ],
    "anatomy": [
        {"term": "Cardiac", "translation": "relating to the heart", "example": "Cardiac arrest is a medical emergency."},
        {"term": "Pulmonary", "translation": "relating to the lungs", "example": "Pulmonary function was normal."},
        {"term": "Vascular", "translation": "relating to blood vessels", "example": "Vascular disease can be prevented."},
        {"term": "Neural", "translation": "relating to the nerves", "example": "Neural pathways carry signals."},
    ],
    "education": [
        {"term": "Curriculum", "translation": "planned learning content", "example": "The curriculum covers grammar and reading."},
        {"term": "Assessment", "translation": "evaluation of learning", "example": "Weekly assessments track progress."},
        {"term": "Feedback", "translation": "response to work", "example": "Constructive feedback improves writing."},
        {"term": "Pedagogy", "translation": "teaching methods", "example": "Modern pedagogy emphasises active learning."},
    ],
    "business": [
        {"term": "Revenue", "translation": "income from sales", "example": "Revenue grew 20% last quarter."},
        {"term": "Stakeholder", "translation": "interested party", "example": "We updated all stakeholders on the launch."},
        {"term": "Deadline", "translation": "final date", "example": "The deadline is next Friday."},
        {"term": "Negotiate", "translation": "reach an agreement", "example": "They negotiated a better price."},
    ],
    "science": [
        {"term": "Hypothesis", "translation": "testable prediction", "example": "The hypothesis was confirmed."},
        {"term": "Experiment", "translation": "test to check a hypothesis", "example": "The experiment produced clear results."},
        {"term": "Data", "translation": "collected information", "example": "We analysed the data carefully."},
    ],
    "tech": [
        {"term": "Bug", "translation": "programming error", "example": "I fixed a bug in the login flow."},
        {"term": "Deploy", "translation": "release software", "example": "We deploy every Thursday."},
        {"term": "Feature", "translation": "product capability", "example": "The new feature ships this week."},
    ],
    "travel": [
        {"term": "Itinerary", "translation": "travel plan", "example": "Here is our itinerary for the trip."},
        {"term": "Boarding pass", "translation": "pass to enter a plane", "example": "Please show your boarding pass."},
        {"term": "Layover", "translation": "stop between flights", "example": "We have a two-hour layover in Rome."},
    ],
}

LESSONS_SEED: list[dict[str, Any]] = [
    {
        "id": "hc-job-interview",
        "title": "Prepare for a healthcare job interview",
        "description": "The lesson contains some common healthcare interview questions and tips on how to answer them.",
        "topic_id": "medicine",
        "level": "Advanced",
        "minutes": 35,
        "xp_reward": 40,
    },
    {
        "id": "hc-cv",
        "title": "Writing a healthcare CV",
        "description": "Learn how to write a good CV to apply for a role in healthcare. Practise common vocabulary and write your own CV.",
        "topic_id": "medicine",
        "level": "Intermediate",
        "minutes": 25,
        "xp_reward": 30,
    },
    {
        "id": "pharmacy-basics",
        "title": "Talking to patients in a pharmacy",
        "description": "Common phrases and vocabulary used when helping customers at the pharmacy counter.",
        "topic_id": "pharmacy",
        "level": "Beginner",
        "minutes": 20,
        "xp_reward": 20,
    },
    {
        "id": "virology-terms",
        "title": "Essential virology vocabulary",
        "description": "Master core virology terms with real-world examples used in hospitals and labs.",
        "topic_id": "virology",
        "level": "Advanced",
        "minutes": 30,
        "xp_reward": 35,
    },
    {
        "id": "business-emails",
        "title": "Writing professional emails",
        "description": "Craft clear, polite emails for meetings, follow-ups, and negotiations.",
        "topic_id": "business",
        "level": "Intermediate",
        "minutes": 22,
        "xp_reward": 25,
    },
    {
        "id": "travel-airport",
        "title": "Airport English essentials",
        "description": "Check-in, security, boarding — the phrases you need to travel with confidence.",
        "topic_id": "travel",
        "level": "Beginner",
        "minutes": 18,
        "xp_reward": 20,
    },
]

CHALLENGES_SEED: list[dict[str, Any]] = [
    {"id": "learn-20-words", "title": "Learn 20 new words", "days_left": 3, "goal_type": "words_learned", "target": 20, "icon": "reader-outline"},
    {"id": "complete-3-lessons", "title": "Complete 3 lessons", "days_left": 5, "goal_type": "lessons_completed", "target": 3, "icon": "trophy-outline"},
    {"id": "3-day-streak", "title": "Reach a 3-day streak", "days_left": 7, "goal_type": "streak", "target": 3, "icon": "flame-outline"},
]


def _lesson_steps(lesson: dict[str, Any], words: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Assemble a linear step list for the lesson player from topic words."""
    # Take up to 6 words for the lesson body; final step is a quiz.
    lesson_words = words[:6] if words else []
    steps: list[dict[str, Any]] = []
    for w in lesson_words:
        steps.append({
            "kind": "vocab",
            "term": w["term"],
            "translation": w["translation"],
            "example": w.get("example", ""),
            "word_id": w["id"],
        })
    if lesson_words:
        target = lesson_words[0]
        options = [w["term"] for w in lesson_words[:4]]
        # Ensure the correct answer is present + unique
        if target["term"] not in options:
            options[0] = target["term"]
        steps.append({
            "kind": "quiz",
            "prompt": f"Which word means: “{target['translation']}”?",
            "options": options,
            "answer": target["term"],
            "word_id": target["id"],
        })
    steps.append({"kind": "done", "message": f"You earned {lesson['xp_reward']} XP!"})
    return steps


async def seed_vocab_content() -> None:
    """Idempotent seed of topics, words, lessons, challenges."""
    # Topics
    for t in TOPICS_SEED:
        await vocab_topics_col.update_one(
            {"_id": t["id"]},
            {"$set": {**t, "_id": t["id"]}},
            upsert=True,
        )
    # Words
    for topic_id, words in WORDS_SEED.items():
        for i, w in enumerate(words):
            wid = f"{topic_id}-{i}"
            await vocab_words_col.update_one(
                {"_id": wid},
                {"$set": {**w, "_id": wid, "id": wid, "topic_id": topic_id}},
                upsert=True,
            )
    # Lessons
    for l in LESSONS_SEED:
        await vocab_lessons_col.update_one(
            {"_id": l["id"]},
            {"$set": {**l, "_id": l["id"]}},
            upsert=True,
        )
    # Challenges
    for c in CHALLENGES_SEED:
        await vocab_challenges_col.update_one(
            {"_id": c["id"]},
            {"$set": {**c, "_id": c["id"]}},
            upsert=True,
        )


# --------------------------------------------------------------------------- #
# Stats helpers
# --------------------------------------------------------------------------- #
def _level_for_xp(xp: int) -> dict[str, Any]:
    # Curve: 100 XP per level.
    level = 1 + xp // 100
    xp_in_level = xp % 100
    xp_to_next = 100 - xp_in_level
    return {"level": level, "xp": xp, "xp_in_level": xp_in_level, "xp_to_next": xp_to_next, "progress": xp_in_level / 100.0}


async def _compute_stats(user_id: str) -> dict[str, Any]:
    # Words learned = progress rows with status='known'
    words_learned = await vocab_progress_col.count_documents({"user_id": user_id, "status": "known"})
    words_practicing = await vocab_progress_col.count_documents({"user_id": user_id, "status": "learning"})
    lessons_completed = await vocab_lesson_prog_col.count_documents({"user_id": user_id, "status": "completed"})
    xp_docs = await vocab_lesson_prog_col.find({"user_id": user_id, "status": "completed"}).to_list(500)
    xp = sum(d.get("xp_awarded", 0) for d in xp_docs) + words_learned * 2  # +2 XP per learned word
    lvl = _level_for_xp(xp)

    # Streak — count consecutive days ending today with any progress activity
    streak = 0
    today = datetime.now(timezone.utc).date()
    for i in range(0, 60):
        d = today - timedelta(days=i)
        key = d.strftime("%Y-%m-%d")
        has_activity = await vocab_progress_col.count_documents({"user_id": user_id, "date_key": key}, limit=1) > 0
        if not has_activity:
            has_activity = await vocab_lesson_prog_col.count_documents({"user_id": user_id, "completed_at_day": key}, limit=1) > 0
        if has_activity:
            streak += 1
        else:
            if i == 0:
                # No activity today — streak is 0 unless we allow grace; keep at 0.
                break
            break
    return {
        "words_learned": words_learned,
        "words_practicing": words_practicing,
        "lessons_completed": lessons_completed,
        "streak": streak,
        **lvl,
    }


# --------------------------------------------------------------------------- #
# Request models
# --------------------------------------------------------------------------- #
class WordProgressIn(BaseModel):
    word_id: str
    status: Literal["new", "learning", "known"]


class LessonCompleteIn(BaseModel):
    step_count: Optional[int] = None
    correct_count: Optional[int] = None


class BookmarkToggleIn(BaseModel):
    target_type: Literal["tutor", "word", "lesson"]
    target_id: str


class BookingIn(BaseModel):
    tutor_id: str
    slot_iso: str = Field(..., description="ISO-8601 datetime for the booked slot")
    duration_min: int = 60
    note: Optional[str] = None


# --------------------------------------------------------------------------- #
# Routes — content
# --------------------------------------------------------------------------- #
@router.get("/topics")
async def list_topics(current: CurrentUser) -> list[dict[str, Any]]:
    docs = await vocab_topics_col.find({}).to_list(200)
    # Attach word count + user's known count per topic.
    out = []
    for t in docs:
        wcount = await vocab_words_col.count_documents({"topic_id": t["_id"]})
        known = await vocab_progress_col.count_documents({"user_id": current["_id"], "topic_id": t["_id"], "status": "known"})
        out.append({
            "id": t["_id"],
            "name": t["name"],
            "subtitle": t["subtitle"],
            "icon": t["icon"],
            "color": t.get("color", "mint"),
            "word_count": wcount,
            "words_learned": known,
        })
    return out


@router.get("/topics/{topic_id}")
async def get_topic(topic_id: str, current: CurrentUser) -> dict[str, Any]:
    t = await vocab_topics_col.find_one({"_id": topic_id})
    if not t:
        raise HTTPException(404, "Topic not found")
    wcount = await vocab_words_col.count_documents({"topic_id": topic_id})
    known = await vocab_progress_col.count_documents({"user_id": current["_id"], "topic_id": topic_id, "status": "known"})
    return {
        "id": t["_id"],
        "name": t["name"],
        "subtitle": t["subtitle"],
        "icon": t["icon"],
        "color": t.get("color", "mint"),
        "word_count": wcount,
        "words_learned": known,
    }


@router.get("/topics/{topic_id}/words")
async def list_words(topic_id: str, current: CurrentUser) -> list[dict[str, Any]]:
    docs = await vocab_words_col.find({"topic_id": topic_id}).to_list(500)
    # Attach per-user status
    prog = {p["word_id"]: p for p in await vocab_progress_col.find({"user_id": current["_id"], "topic_id": topic_id}).to_list(2000)}
    return [{
        "id": d["_id"],
        "term": d["term"],
        "translation": d["translation"],
        "example": d.get("example", ""),
        "topic_id": d["topic_id"],
        "status": (prog.get(d["_id"]) or {}).get("status", "new"),
    } for d in docs]


@router.get("/lessons")
async def list_lessons(topic_id: Optional[str] = None, level: Optional[str] = None, current: CurrentUser = None) -> list[dict[str, Any]]:
    q: dict[str, Any] = {}
    if topic_id:
        q["topic_id"] = topic_id
    if level:
        q["level"] = level
    docs = await vocab_lessons_col.find(q).sort([("minutes", 1)]).to_list(200)
    completed = {p["lesson_id"] for p in await vocab_lesson_prog_col.find({"user_id": current["_id"], "status": "completed"}).to_list(500)}
    return [{
        "id": d["_id"],
        "title": d["title"],
        "description": d["description"],
        "topic_id": d["topic_id"],
        "level": d["level"],
        "minutes": d["minutes"],
        "xp_reward": d.get("xp_reward", 20),
        "completed": d["_id"] in completed,
    } for d in docs]


@router.get("/lessons/{lesson_id}")
async def get_lesson(lesson_id: str, current: CurrentUser) -> dict[str, Any]:
    l = await vocab_lessons_col.find_one({"_id": lesson_id})
    if not l:
        raise HTTPException(404, "Lesson not found")
    words = await vocab_words_col.find({"topic_id": l["topic_id"]}).to_list(20)
    steps = _lesson_steps(l, words)
    prog = await vocab_lesson_prog_col.find_one({"user_id": current["_id"], "lesson_id": lesson_id})
    return {
        "id": l["_id"],
        "title": l["title"],
        "description": l["description"],
        "topic_id": l["topic_id"],
        "level": l["level"],
        "minutes": l["minutes"],
        "xp_reward": l.get("xp_reward", 20),
        "steps": steps,
        "progress": {
            "status": (prog or {}).get("status", "new"),
            "current_step": (prog or {}).get("current_step", 0),
            "xp_awarded": (prog or {}).get("xp_awarded", 0),
        },
    }


# --------------------------------------------------------------------------- #
# Routes — progress
# --------------------------------------------------------------------------- #
@router.post("/progress/word")
async def set_word_progress(body: WordProgressIn, current: CurrentUser) -> dict[str, Any]:
    word = await vocab_words_col.find_one({"_id": body.word_id})
    if not word:
        raise HTTPException(404, "Word not found")
    await vocab_progress_col.update_one(
        {"user_id": current["_id"], "word_id": body.word_id},
        {"$set": {
            "user_id": current["_id"],
            "word_id": body.word_id,
            "topic_id": word["topic_id"],
            "status": body.status,
            "updated_at": _now(),
            "date_key": _today_key(),
        }},
        upsert=True,
    )
    return {"ok": True, "stats": await _compute_stats(current["_id"])}


@router.post("/lessons/{lesson_id}/complete")
async def complete_lesson(lesson_id: str, body: LessonCompleteIn, current: CurrentUser) -> dict[str, Any]:
    l = await vocab_lessons_col.find_one({"_id": lesson_id})
    if not l:
        raise HTTPException(404, "Lesson not found")
    existing = await vocab_lesson_prog_col.find_one({"user_id": current["_id"], "lesson_id": lesson_id})
    # Award XP only once (first completion).
    xp = 0 if (existing and existing.get("status") == "completed") else l.get("xp_reward", 20)
    await vocab_lesson_prog_col.update_one(
        {"user_id": current["_id"], "lesson_id": lesson_id},
        {"$set": {
            "user_id": current["_id"],
            "lesson_id": lesson_id,
            "status": "completed",
            "xp_awarded": (existing or {}).get("xp_awarded", 0) + xp,
            "correct_count": body.correct_count,
            "step_count": body.step_count,
            "completed_at": _now(),
            "completed_at_day": _today_key(),
        }},
        upsert=True,
    )
    return {"ok": True, "xp_awarded": xp, "stats": await _compute_stats(current["_id"])}


# --------------------------------------------------------------------------- #
# Routes — me
# --------------------------------------------------------------------------- #
@router.get("/me/stats")
async def me_stats(current: CurrentUser) -> dict[str, Any]:
    return await _compute_stats(current["_id"])


@router.get("/me/continue")
async def me_continue(current: CurrentUser) -> dict[str, Any]:
    """Best 'continue' suggestion: most recently interacted lesson or a starter."""
    prog = await vocab_lesson_prog_col.find({"user_id": current["_id"], "status": {"$ne": "completed"}}).sort([("_id", -1)]).to_list(5)
    lesson: Optional[dict[str, Any]] = None
    if prog:
        lesson = await vocab_lessons_col.find_one({"_id": prog[0]["lesson_id"]})
    if not lesson:
        # First uncompleted lesson otherwise first ever
        completed_ids = [p["lesson_id"] for p in await vocab_lesson_prog_col.find({"user_id": current["_id"], "status": "completed"}).to_list(500)]
        lesson = await vocab_lessons_col.find_one({"_id": {"$nin": completed_ids}}) or await vocab_lessons_col.find_one({})
    if not lesson:
        raise HTTPException(404, "No lessons available")
    topic = await vocab_topics_col.find_one({"_id": lesson["topic_id"]})
    lp = await vocab_lesson_prog_col.find_one({"user_id": current["_id"], "lesson_id": lesson["_id"]}) or {}
    total_steps = 7  # 6 vocab + 1 quiz (matches _lesson_steps output for full topics)
    progress = 0.0
    if lp:
        progress = min(1.0, (lp.get("current_step", 0) or 0) / max(1, total_steps))
    return {
        "id": lesson["_id"],
        "title": lesson["title"],
        "topic_id": lesson["topic_id"],
        "topic_name": (topic or {}).get("name", ""),
        "level": lesson["level"],
        "minutes": lesson["minutes"],
        "progress": progress,
        "tag": "In progress" if lp else "Recommended",
    }


@router.get("/me/bookmarks")
async def list_bookmarks(current: CurrentUser) -> dict[str, list[dict[str, Any]]]:
    docs = await vocab_bookmarks_col.find({"user_id": current["_id"]}).to_list(500)
    return {
        "tutors": [d for d in docs if d["target_type"] == "tutor"],
        "words": [d for d in docs if d["target_type"] == "word"],
        "lessons": [d for d in docs if d["target_type"] == "lesson"],
    }


@router.post("/bookmarks/toggle")
async def toggle_bookmark(body: BookmarkToggleIn, current: CurrentUser) -> dict[str, Any]:
    existing = await vocab_bookmarks_col.find_one({
        "user_id": current["_id"], "target_type": body.target_type, "target_id": body.target_id,
    })
    if existing:
        await vocab_bookmarks_col.delete_one({"_id": existing["_id"]})
        return {"bookmarked": False}
    await vocab_bookmarks_col.insert_one({
        "_id": str(uuid.uuid4()),
        "user_id": current["_id"],
        "target_type": body.target_type,
        "target_id": body.target_id,
        "created_at": _now(),
    })
    return {"bookmarked": True}


@router.get("/bookmarks/status/{target_type}/{target_id}")
async def bookmark_status(target_type: str, target_id: str, current: CurrentUser) -> dict[str, bool]:
    hit = await vocab_bookmarks_col.find_one({
        "user_id": current["_id"], "target_type": target_type, "target_id": target_id,
    })
    return {"bookmarked": bool(hit)}


# --------------------------------------------------------------------------- #
# Routes — bookings
# --------------------------------------------------------------------------- #
@router.post("/bookings")
async def create_booking(body: BookingIn, current: CurrentUser) -> dict[str, Any]:
    booking = {
        "_id": str(uuid.uuid4()),
        "user_id": current["_id"],
        "tutor_id": body.tutor_id,
        "slot_iso": body.slot_iso,
        "duration_min": body.duration_min,
        "note": body.note,
        "status": "confirmed",
        "created_at": _now(),
    }
    await vocab_bookings_col.insert_one(booking)
    # Try to enrich with tutor snapshot for the response
    tutor = await db["pro_profiles"].find_one({"_id": body.tutor_id}) or await db["pro_profiles"].find_one({"user_id": body.tutor_id})
    if tutor:
        booking["tutor_name"] = tutor.get("name") or tutor.get("display_name")
        booking["tutor_avatar_url"] = tutor.get("avatar_url")
    return booking


@router.get("/me/bookings")
async def my_bookings(current: CurrentUser) -> list[dict[str, Any]]:
    docs = await vocab_bookings_col.find({"user_id": current["_id"]}).sort([("slot_iso", 1)]).to_list(200)
    # Enrich
    tutor_ids = list({d["tutor_id"] for d in docs})
    tutors_map: dict[str, dict[str, Any]] = {}
    if tutor_ids:
        async for t in db["pro_profiles"].find({"_id": {"$in": tutor_ids}}):
            tutors_map[t["_id"]] = t
    out = []
    for d in docs:
        t = tutors_map.get(d["tutor_id"], {})
        out.append({
            **d,
            "tutor_name": t.get("name") or t.get("display_name") or "Tutor",
            "tutor_avatar_url": t.get("avatar_url"),
        })
    return out


@router.delete("/bookings/{booking_id}")
async def cancel_booking(booking_id: str, current: CurrentUser) -> dict[str, bool]:
    res = await vocab_bookings_col.delete_one({"_id": booking_id, "user_id": current["_id"]})
    if not res.deleted_count:
        raise HTTPException(404, "Booking not found")
    return {"ok": True}


# --------------------------------------------------------------------------- #
# Routes — challenges
# --------------------------------------------------------------------------- #
@router.get("/challenges")
async def list_challenges(current: CurrentUser) -> list[dict[str, Any]]:
    docs = await vocab_challenges_col.find({}).to_list(200)
    stats = await _compute_stats(current["_id"])
    out = []
    for c in docs:
        goal = c.get("goal_type")
        current_val = 0
        if goal == "words_learned":
            current_val = stats["words_learned"]
        elif goal == "lessons_completed":
            current_val = stats["lessons_completed"]
        elif goal == "streak":
            current_val = stats["streak"]
        target = c.get("target", 1)
        out.append({
            "id": c["_id"],
            "title": c["title"],
            "days_left": c.get("days_left", 3),
            "icon": c.get("icon", "reader-outline"),
            "goal_type": goal,
            "target": target,
            "current": current_val,
            "progress": min(1.0, current_val / max(1, target)),
            "completed": current_val >= target,
        })
    return out
