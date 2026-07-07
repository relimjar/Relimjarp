import random
import re
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, status
from pymongo.errors import DuplicateKeyError

from auth_utils import CurrentUser, create_access_token, hash_password, verify_password
from db import users_col
from models import LoginRequest, RegisterRequest, user_public

router = APIRouter(prefix="/auth", tags=["auth"])


async def touch_streak(doc: dict) -> dict:
    """Consecutive-day streak: +1 if last active yesterday, reset to 1 otherwise."""
    today = datetime.now(timezone.utc).date()
    last = doc.get("last_active_date")
    if last == today.isoformat():
        return doc
    if last == (today - timedelta(days=1)).isoformat():
        streak = (doc.get("streak_count") or 0) + 1
    else:
        streak = 1
    updates = {"streak_count": streak, "last_active_date": today.isoformat()}
    await users_col.update_one({"_id": doc["_id"]}, {"$set": updates})
    doc.update(updates)
    return doc


async def generate_username(name: str | None) -> str:
    """Unique auto-assigned username: lowercase name + random digits."""
    base = re.sub(r"[^a-z0-9]", "", (name or "user").lower())[:12] or "user"
    for _ in range(20):
        candidate = f"{base}{random.randint(100, 9999)}"
        if not await users_col.find_one({"username": candidate}):
            return candidate
    return f"user{uuid.uuid4().hex[:8]}"


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest):
    user_id = str(uuid.uuid4())
    doc = {
        "_id": user_id,
        "email": body.email.lower(),
        "password_hash": hash_password(body.password),
        "name": body.name.strip(),
        "username": await generate_username(body.name),
        "username_changed_at": None,
        "bio": None,
        "country": None,
        "avatar_url": None,
        "native_language": None,
        "learning_language": None,
        "proficiency": None,
        "streak_count": 1,
        "coins": 1000,
        "last_active_date": datetime.now(timezone.utc).date().isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        await users_col.insert_one(doc)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Email already registered")
    return {"token": create_access_token(user_id), "user": user_public(doc)}


@router.post("/guest", status_code=status.HTTP_201_CREATED)
async def guest():
    """One-tap guest account — lets a visitor explore the app without signing
    up. Creates a real user record so all features (chat, moments, rooms)
    keep working, just pre-filled with sensible defaults so onboarding can be
    skipped. Guests can convert to a full account later from Settings."""
    user_id = str(uuid.uuid4())
    guest_number = random.randint(1000, 9999)
    guest_name = f"Guest {guest_number}"
    now = datetime.now(timezone.utc)
    doc = {
        "_id": user_id,
        "email": f"guest_{user_id[:8]}@guest.linguaconnect.local",
        "password_hash": hash_password(uuid.uuid4().hex),  # unreachable password
        "name": guest_name,
        "username": await generate_username(guest_name),
        "username_changed_at": None,
        "bio": None,
        "country": "United States",
        "avatar_url": None,
        "native_language": "en",
        "learning_language": "es",
        "learning_languages": ["es"],
        "proficiency": "Beginner",
        "age": 25,
        "gender": "male",
        "interests": ["Music", "Travel", "Movies"],
        "is_guest": True,
        "streak_count": 1,
        "coins": 500,
        "last_active_date": now.date().isoformat(),
        "created_at": now.isoformat(),
    }
    await users_col.insert_one(doc)
    return {"token": create_access_token(user_id), "user": user_public(doc)}


@router.post("/login")
async def login(body: LoginRequest):
    doc = await users_col.find_one({"email": body.email.lower()})
    if not doc or not verify_password(body.password, doc["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if doc.get("banned"):
        raise HTTPException(status_code=403, detail="Your account has been banned.")
    doc = await touch_streak(doc)
    return {"token": create_access_token(doc["_id"]), "user": user_public(doc)}


@router.get("/me")
async def me(current_user: CurrentUser):
    current_user = await touch_streak(current_user)
    return user_public(current_user)
