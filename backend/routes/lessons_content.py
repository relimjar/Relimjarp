"""
Original course content + exercise generator for the "Lessons" sub-app.
All vocabulary and sentences here are written from scratch for this project.
No third-party copyrighted content is used.
"""

import random

# Each word: (target, english, emoji)
COURSES: dict = {
    "es": {
        "name": "Spanish",
        "flag": "es",
        "color": "#FF8A3D",
        "units": [
            {
                "title": "First words",
                "color": "#58CC57",
                "skills": [
                    {"id": "greet", "title": "Greetings", "icon": "hand-left",
                     "words": [("hola", "hello", "👋"), ("adiós", "goodbye", "👋"),
                               ("gracias", "thank you", "🙏"), ("por favor", "please", "✨"),
                               ("sí", "yes", "✅"), ("no", "no", "❌")]},
                    {"id": "food", "title": "Food", "icon": "restaurant",
                     "words": [("agua", "water", "💧"), ("pan", "bread", "🍞"),
                               ("leche", "milk", "🥛"), ("café", "coffee", "☕"),
                               ("manzana", "apple", "🍎"), ("huevo", "egg", "🥚")]},
                    {"id": "animals", "title": "Animals", "icon": "paw",
                     "words": [("gato", "cat", "🐱"), ("perro", "dog", "🐶"),
                               ("pájaro", "bird", "🐦"), ("pez", "fish", "🐟"),
                               ("caballo", "horse", "🐴"), ("vaca", "cow", "🐮")]},
                ],
            },
            {
                "title": "Getting around",
                "color": "#1CB0F6",
                "skills": [
                    {"id": "family", "title": "Family", "icon": "people",
                     "words": [("madre", "mother", "👩"), ("padre", "father", "👨"),
                               ("hijo", "son", "👦"), ("hija", "daughter", "👧"),
                               ("hermano", "brother", "🧑"), ("amigo", "friend", "🤝")]},
                    {"id": "colors", "title": "Colors", "icon": "color-palette",
                     "words": [("rojo", "red", "🔴"), ("azul", "blue", "🔵"),
                               ("verde", "green", "🟢"), ("amarillo", "yellow", "🟡"),
                               ("negro", "black", "⚫"), ("blanco", "white", "⚪")]},
                    {"id": "numbers", "title": "Numbers", "icon": "calculator",
                     "words": [("uno", "one", "1️⃣"), ("dos", "two", "2️⃣"),
                               ("tres", "three", "3️⃣"), ("cuatro", "four", "4️⃣"),
                               ("cinco", "five", "5️⃣"), ("seis", "six", "6️⃣")]},
                ],
            },
            {
                "title": "Everyday life",
                "color": "#CE82FF",
                "skills": [
                    {"id": "home", "title": "Home", "icon": "home",
                     "words": [("casa", "house", "🏠"), ("puerta", "door", "🚪"),
                               ("mesa", "table", "🪑"), ("cama", "bed", "🛏️"),
                               ("libro", "book", "📖"), ("ventana", "window", "🪟")]},
                    {"id": "time", "title": "Time", "icon": "time",
                     "words": [("día", "day", "☀️"), ("noche", "night", "🌙"),
                               ("hoy", "today", "📅"), ("mañana", "tomorrow", "⏭️"),
                               ("hora", "hour", "⏰"), ("semana", "week", "🗓️")]},
                ],
            },
        ],
    },
    "fr": {
        "name": "French",
        "flag": "fr",
        "color": "#8A5EF7",
        "units": [
            {
                "title": "First words",
                "color": "#58CC57",
                "skills": [
                    {"id": "greet", "title": "Greetings", "icon": "hand-left",
                     "words": [("bonjour", "hello", "👋"), ("au revoir", "goodbye", "👋"),
                               ("merci", "thank you", "🙏"), ("oui", "yes", "✅"),
                               ("non", "no", "❌"), ("s'il te plaît", "please", "✨")]},
                    {"id": "food", "title": "Food", "icon": "restaurant",
                     "words": [("eau", "water", "💧"), ("pain", "bread", "🍞"),
                               ("lait", "milk", "🥛"), ("café", "coffee", "☕"),
                               ("pomme", "apple", "🍎"), ("fromage", "cheese", "🧀")]},
                    {"id": "animals", "title": "Animals", "icon": "paw",
                     "words": [("chat", "cat", "🐱"), ("chien", "dog", "🐶"),
                               ("oiseau", "bird", "🐦"), ("poisson", "fish", "🐟"),
                               ("cheval", "horse", "🐴"), ("vache", "cow", "🐮")]},
                ],
            },
            {
                "title": "Getting around",
                "color": "#1CB0F6",
                "skills": [
                    {"id": "family", "title": "Family", "icon": "people",
                     "words": [("mère", "mother", "👩"), ("père", "father", "👨"),
                               ("fils", "son", "👦"), ("fille", "daughter", "👧"),
                               ("frère", "brother", "🧑"), ("ami", "friend", "🤝")]},
                    {"id": "colors", "title": "Colors", "icon": "color-palette",
                     "words": [("rouge", "red", "🔴"), ("bleu", "blue", "🔵"),
                               ("vert", "green", "🟢"), ("jaune", "yellow", "🟡"),
                               ("noir", "black", "⚫"), ("blanc", "white", "⚪")]},
                ],
            },
        ],
    },
}


def course_summary(lang: str) -> dict:
    c = COURSES[lang]
    return {"lang": lang, "name": c["name"], "flag": c["flag"], "color": c["color"]}


def list_courses() -> list:
    return [course_summary(k) for k in COURSES]


def get_path(lang: str) -> list:
    """Units -> skills (each skill == one lesson node)."""
    c = COURSES[lang]
    units = []
    for ui, unit in enumerate(c["units"]):
        skills = []
        for si, sk in enumerate(unit["skills"]):
            skills.append(
                {
                    "lesson_id": f"{lang}-{ui}-{si}",
                    "title": sk["title"],
                    "icon": sk["icon"],
                    "unit_index": ui,
                    "skill_index": si,
                }
            )
        units.append({"index": ui, "title": unit["title"], "color": unit["color"], "skills": skills})
    return units


def _all_words(lang: str) -> list:
    out = []
    for unit in COURSES[lang]["units"]:
        for sk in unit["skills"]:
            out.extend(sk["words"])
    return out


def _skill(lang: str, ui: int, si: int):
    return COURSES[lang]["units"][ui]["skills"][si]


def build_exercises(lang: str, lesson_id: str, seed: int | None = None) -> list:
    """Generate a varied set of exercises for one lesson from its vocabulary."""
    try:
        _, ui, si = lesson_id.split("-")
        ui, si = int(ui), int(si)
        skill = _skill(lang, ui, si)
    except Exception:
        return []

    rng = random.Random(seed if seed is not None else lesson_id)
    words = list(skill["words"])
    pool = _all_words(lang)
    exercises = []

    # 1) Intro "select the image" for first two words (multiple choice with emoji)
    for target, english, emoji in words[:2]:
        distractors = rng.sample([w for w in pool if w[1] != english], 3)
        options = [{"text": target, "emoji": emoji, "correct": True}] + [
            {"text": d[0], "emoji": d[2], "correct": False} for d in distractors
        ]
        rng.shuffle(options)
        exercises.append(
            {"type": "select", "prompt": f"Which one is “{english}”?", "options": options}
        )

    # 2) Listening — hear the word, choose the written form (frontend uses TTS)
    t, e, em = words[2 % len(words)]
    dist = rng.sample([w for w in pool if w[1] != e], 3)
    opts = [{"text": t, "correct": True}] + [{"text": d[0], "correct": False} for d in dist]
    rng.shuffle(opts)
    exercises.append(
        {"type": "listen", "prompt": "Tap what you hear", "audio": t, "options": opts}
    )

    # 3) Translate to English — word bank
    t, e, em = words[rng.randrange(len(words))]
    bank_wrong = rng.sample([w[1] for w in pool if w[1] != e], 3)
    bank = [e] + bank_wrong
    rng.shuffle(bank)
    exercises.append(
        {
            "type": "translate",
            "prompt": f"Translate “{t}”",
            "answer": [e],
            "bank": bank,
        }
    )

    # 4) Match pairs — target <-> english
    pairs_src = rng.sample(words, min(4, len(words)))
    exercises.append(
        {
            "type": "match",
            "prompt": "Tap the matching pairs",
            "pairs": [{"a": w[0], "b": w[1]} for w in pairs_src],
        }
    )

    # 5) Fill in the blank (choose the target word)
    t, e, em = words[rng.randrange(len(words))]
    fdist = rng.sample([w[0] for w in pool if w[0] != t], 3)
    fopts = [{"text": t, "correct": True}] + [{"text": d, "correct": False} for d in fdist]
    rng.shuffle(fopts)
    exercises.append(
        {
            "type": "fill",
            "prompt": f"Complete: “___” means {e}",
            "options": fopts,
        }
    )

    return exercises
