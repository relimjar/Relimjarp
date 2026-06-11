# PRD — LinguaConnect (HelloTalk Clone)

## Original Problem Statement
"Can you clone hellotalk app" — A language exchange application similar to HelloTalk featuring user profiles, native/target language matching, and messaging capabilities.

## User Choices (confirmed Feb 2026)
- Full HelloTalk feature scope ("All")
- JWT-based email/password authentication
- AI-powered translation & grammar correction via **GPT-5.2** (Emergent Universal Key)
- **WebSocket** real-time chat
- HelloTalk-like design (light, friendly sky blue) — design system in `/app/design_guidelines.json`

## Tech Stack
- Frontend: Expo (React Native) + Expo Router, Figtree/Nunito fonts, light sky-blue theme
- Backend: FastAPI + Motor (MongoDB), JWT (PyJWT + passlib bcrypt), WebSocket at `/api/ws`
- AI: emergentintegrations LlmChat → openai/gpt-5.2 (EMERGENT_LLM_KEY in backend/.env)

## Architecture
### Backend (`/app/backend/`)
- `server.py` — app, CORS, WS endpoint `/api/ws?token=JWT`, router registration
- `db.py` — Mongo client + collections + indexes
- `auth_utils.py` — bcrypt hashing, JWT create/decode, `get_current_user` dependency
- `models.py` — Pydantic request models + user serializers (uuid string `_id`)
- `ws_manager.py` — ConnectionManager (user_id → websockets, `send_to_user`)
- `routes/` — auth.py, users.py, chats.py, moments.py, ai.py
- `seed.py` — idempotent: 9 demo users + 6 moments (password Demo1234!)
- `tests/` — test_api.py (8 tests), test_websocket.py (2 tests, added by testing agent)

### Key API Endpoints (all `/api` prefixed)
- POST /auth/register, /auth/login; GET /auth/me
- PUT /users/me; GET /users/partners?language=&search=; GET /users/{id}
- POST /chats {partner_id}; GET /chats; GET /chats/{id}; GET/POST /chats/{id}/messages; POST /chats/{id}/read
- GET/POST /moments; GET /moments/{id}; POST /moments/{id}/like; POST /moments/{id}/comments
- POST /ai/translate {text, target_language}; POST /ai/correct {text, language}
- WS /api/ws?token= → pushes `{type:"new_message", conversation_id, message, sender}`

### Frontend (`/app/frontend/`)
- `app/index.tsx` — welcome/gate (redirects: onboarding if languages unset, else tabs)
- `app/auth.tsx` — login/register toggle
- `app/onboarding.tsx` — 3 steps: native lang, learning lang, proficiency
- `app/(tabs)/` — connect (partner discovery + filters + search), chats (inbox + WS refresh + unread badges), moments (feed + composer FAB + likes), profile (view/edit + logout)
- `app/chat/[id].tsx` — real-time chat, per-bubble AI translate, AI grammar check on drafts (correction card with "Use this")
- `app/user/[id].tsx` — partner profile; `app/moment/[id].tsx` — moment detail + comments
- `src/` — theme.ts, constants/languages.ts (20 langs), utils/api.ts, utils/time.ts, context/AuthContext.tsx, hooks/use-chat-socket.ts, components/Avatar.tsx + LanguagePair.tsx

## DB Schema (uuid string _id everywhere)
- users: email(unique), password_hash, name, bio, country, avatar_url, native_language, learning_language, proficiency, created_at
- conversations: participant_ids[2], last_message{}, unread{userId:count}, updated_at
- messages: conversation_id, sender_id, text, created_at
- moments: user_id, text, likes[userIds], comment_count, created_at
- comments: moment_id, user_id, text, created_at

## What's Implemented (Feb 2026 — MVP COMPLETE)
✅ JWT auth (register/login/me) · onboarding · partner discovery with language matching/filters/search · real-time WebSocket 1-on-1 chat with unread counts · AI translate (per message bubble) · AI grammar correction (draft check) · Moments feed (post/like/comment) · profile view/edit · logout · seed data
✅ Tested: 10/10 backend pytest + full frontend E2E by testing agent (iteration_1.json) — all pass

## Backlog (P1/P2 — not yet built)
- P1: Voice messages / audio recording in chat
- P1: Image upload in chat & moments (needs object storage playbook)
- P1: Avatar upload for registered users (currently initials fallback; seeded users use pravatar URLs)
- P2: Typing indicators & online presence (WS infra ready)
- P2: Message corrections inline (HelloTalk-style strike-through correction of partner messages)
- P2: Followers/following on Moments, hashtags
- P2: Push notifications (ONLY if user requests)
- P2: Streaks / learning stats gamification

## Notes for Future Agents
- Emergent LLM key in backend/.env; one transient "budget exceeded" error observed then self-resolved
- Metro runs in CI mode — restart expo via supervisorctl after installing frontend deps
- Test credentials: /app/memory/test_credentials.md (demo@demo.com / Demo1234!)
- shadow uses RN 0.81 `boxShadow` string (cross-platform); tab buttons have testIDs `tab-connect` etc.
