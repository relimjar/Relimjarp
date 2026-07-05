"""Daily phrase feature: a curated phrase bank per language, rotated by
day-of-year so every user sees the same "phrase of the day" per language.
No LLM call needed — instant, deterministic and offline-friendly.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Query

from auth_utils import CurrentUser

router = APIRouter(prefix="/phrases", tags=["phrases"])

LANG_NAMES = {
    "en": "English", "es": "Spanish", "fr": "French", "de": "German",
    "it": "Italian", "pt": "Portuguese", "zh": "Chinese", "ja": "Japanese",
    "ko": "Korean", "ru": "Russian", "ar": "Arabic", "hi": "Hindi",
    "tr": "Turkish", "nl": "Dutch", "pl": "Polish", "sv": "Swedish",
    "vi": "Vietnamese", "th": "Thai", "id": "Indonesian", "el": "Greek",
}

# Each entry: (phrase, romanization-or-None, English meaning, category)
PHRASE_BANK: dict[str, list[tuple[str, str | None, str, str]]] = {
    "en": [
        ("Break the ice", None, "Start a conversation in a friendly way", "Idiom"),
        ("It's a piece of cake", None, "Something very easy to do", "Idiom"),
        ("Long time no see!", None, "Greeting after not meeting for a while", "Greeting"),
        ("What do you do for fun?", None, "Asking about someone's hobbies", "Small Talk"),
        ("Could you say that again, please?", None, "Politely ask someone to repeat", "Useful"),
        ("I'm all ears", None, "I'm listening carefully", "Idiom"),
        ("Better late than never", None, "Doing it late is better than not at all", "Proverb"),
        ("Practice makes perfect", None, "Skill comes from repetition", "Proverb"),
    ],
    "es": [
        ("Mucho gusto", "MOO-choh GOOS-toh", "Nice to meet you", "Greeting"),
        ("¿Qué tal?", "keh TAHL", "How's it going?", "Greeting"),
        ("No pasa nada", "noh PAH-sah NAH-dah", "No worries / it's fine", "Useful"),
        ("Estoy aprendiendo español", "es-TOY ah-pren-DYEN-doh es-pah-NYOL", "I'm learning Spanish", "Useful"),
        ("Más vale tarde que nunca", "mahs BAH-leh TAR-deh keh NOON-kah", "Better late than never", "Proverb"),
        ("¡Qué chévere!", "keh CHEH-veh-reh", "How cool!", "Slang"),
        ("Poco a poco", "POH-koh ah POH-koh", "Little by little", "Useful"),
        ("¿Puedes hablar más despacio?", "PWEH-dehs ah-BLAR mahs des-PAH-syoh", "Can you speak more slowly?", "Useful"),
    ],
    "fr": [
        ("Enchanté(e)", "on-shon-TAY", "Nice to meet you", "Greeting"),
        ("Ça roule ?", "sah ROOL", "How's it going? (casual)", "Slang"),
        ("Petit à petit", "puh-TEE ah puh-TEE", "Little by little", "Useful"),
        ("J'apprends le français", "zhah-PRON luh fron-SEH", "I'm learning French", "Useful"),
        ("C'est la vie", "seh lah VEE", "That's life", "Idiom"),
        ("Avoir le coup de foudre", "ah-VWAR luh koo duh FOODR", "Love at first sight", "Idiom"),
        ("Pouvez-vous répéter ?", "poo-VAY voo ray-pay-TAY", "Could you repeat that?", "Useful"),
        ("Qui vivra verra", "kee vee-VRAH veh-RAH", "Time will tell", "Proverb"),
    ],
    "de": [
        ("Freut mich!", "froyt mikh", "Nice to meet you", "Greeting"),
        ("Wie läuft's?", "vee loyfts", "How's it going?", "Greeting"),
        ("Ich lerne Deutsch", "ikh LEHR-neh doytch", "I'm learning German", "Useful"),
        ("Übung macht den Meister", "UY-boong makht dehn MYS-ter", "Practice makes perfect", "Proverb"),
        ("Das ist mir Wurst", "dahs ist meer voorst", "I don't care (lit. it's sausage to me)", "Idiom"),
        ("Kannst du das wiederholen?", "kahnst doo dahs vee-der-HOH-len", "Can you repeat that?", "Useful"),
        ("Alles klar!", "AH-les klar", "All good / understood", "Useful"),
        ("Aller Anfang ist schwer", "AH-ler AHN-fang ist shvehr", "Every beginning is hard", "Proverb"),
    ],
    "it": [
        ("Piacere!", "pyah-CHEH-reh", "Nice to meet you", "Greeting"),
        ("Come va?", "KOH-meh vah", "How's it going?", "Greeting"),
        ("Sto imparando l'italiano", "stoh eem-pah-RAHN-doh lee-tah-LYAH-noh", "I'm learning Italian", "Useful"),
        ("In bocca al lupo!", "een BOHK-kah ahl LOO-poh", "Good luck! (lit. into the wolf's mouth)", "Idiom"),
        ("Piano piano", "PYAH-noh PYAH-noh", "Slowly, step by step", "Useful"),
        ("Puoi ripetere, per favore?", "pwoy ree-PEH-teh-reh pehr fah-VOH-reh", "Can you repeat, please?", "Useful"),
        ("Chi dorme non piglia pesci", "kee DOR-meh non PEE-lyah PEH-shee", "The early bird catches the worm", "Proverb"),
        ("Che figata!", "keh fee-GAH-tah", "How cool!", "Slang"),
    ],
    "pt": [
        ("Muito prazer", "MOO-ee-too prah-ZEHR", "Nice to meet you", "Greeting"),
        ("Tudo bem?", "TOO-doo beng", "All good?", "Greeting"),
        ("Estou aprendendo português", "es-TOH ah-pren-DEN-doo por-too-GEHS", "I'm learning Portuguese", "Useful"),
        ("Pouco a pouco", "POH-koo ah POH-koo", "Little by little", "Useful"),
        ("Deixa a vida me levar", "DAY-shah ah VEE-dah mee leh-VAR", "Let life take me (go with the flow)", "Idiom"),
        ("Pode repetir, por favor?", "POH-jee heh-peh-CHEER por fah-VOR", "Can you repeat, please?", "Useful"),
        ("Que legal!", "kee leh-GOW", "How cool!", "Slang"),
        ("Água mole em pedra dura...", "AH-gwah MOH-lee eng PEH-drah DOO-rah", "Persistence pays off", "Proverb"),
    ],
    "zh": [
        ("很高兴认识你", "hěn gāoxìng rènshi nǐ", "Nice to meet you", "Greeting"),
        ("最近怎么样？", "zuìjìn zěnmeyàng", "How have you been lately?", "Greeting"),
        ("我在学中文", "wǒ zài xué zhōngwén", "I'm learning Chinese", "Useful"),
        ("加油！", "jiāyóu", "Keep going! / You can do it!", "Useful"),
        ("慢慢来", "màn màn lái", "Take it slowly", "Useful"),
        ("请再说一遍", "qǐng zài shuō yí biàn", "Please say it again", "Useful"),
        ("熟能生巧", "shú néng shēng qiǎo", "Practice makes perfect", "Proverb"),
        ("太棒了！", "tài bàng le", "Awesome!", "Slang"),
    ],
    "ja": [
        ("はじめまして", "hajimemashite", "Nice to meet you", "Greeting"),
        ("元気ですか？", "genki desu ka", "How are you?", "Greeting"),
        ("日本語を勉強しています", "nihongo o benkyou shiteimasu", "I'm studying Japanese", "Useful"),
        ("頑張って！", "ganbatte", "Do your best! / Good luck!", "Useful"),
        ("もう一度お願いします", "mou ichido onegaishimasu", "One more time, please", "Useful"),
        ("継続は力なり", "keizoku wa chikara nari", "Persistence is power", "Proverb"),
        ("すごい！", "sugoi", "Amazing!", "Slang"),
        ("よろしくお願いします", "yoroshiku onegaishimasu", "Please treat me well (versatile greeting)", "Greeting"),
    ],
    "ko": [
        ("만나서 반가워요", "mannaseo bangawoyo", "Nice to meet you", "Greeting"),
        ("잘 지냈어요?", "jal jinaesseoyo", "Have you been well?", "Greeting"),
        ("한국어를 배우고 있어요", "hangugeo-reul baeugo isseoyo", "I'm learning Korean", "Useful"),
        ("화이팅!", "hwaiting", "Fighting! / You can do it!", "Slang"),
        ("천천히 말해 주세요", "cheoncheonhi malhae juseyo", "Please speak slowly", "Useful"),
        ("시작이 반이다", "sijaki banida", "Starting is half the battle", "Proverb"),
        ("대박!", "daebak", "Awesome! / No way!", "Slang"),
        ("다시 한 번 말해 주세요", "dasi han beon malhae juseyo", "Please say that once more", "Useful"),
    ],
    "ru": [
        ("Очень приятно", "OH-chen pree-YAT-nah", "Nice to meet you", "Greeting"),
        ("Как дела?", "kak dee-LAH", "How are you?", "Greeting"),
        ("Я учу русский", "ya oo-CHOO ROO-skee", "I'm learning Russian", "Useful"),
        ("Повторите, пожалуйста", "pahf-tah-REE-tye pah-ZHAH-loo-stah", "Repeat, please", "Useful"),
        ("Терпение и труд всё перетрут", "tyer-PYEH-nye ee troot vsyo pye-rye-TROOT", "Patience and work conquer all", "Proverb"),
        ("Классно!", "KLAHS-nah", "Cool!", "Slang"),
        ("Не за что", "NYE-za-shta", "You're welcome / no problem", "Useful"),
        ("Мир тесен", "meer TYEH-syen", "It's a small world", "Idiom"),
    ],
    "ar": [
        ("تشرفنا", "tasharrafna", "Nice to meet you", "Greeting"),
        ("كيف الحال؟", "kayf al-haal", "How are you?", "Greeting"),
        ("أتعلم العربية", "ata'allam al-'arabiyya", "I'm learning Arabic", "Useful"),
        ("من فضلك أعد", "min fadlik a'id", "Please repeat", "Useful"),
        ("شوية شوية", "shwaya shwaya", "Little by little", "Useful"),
        ("الصبر مفتاح الفرج", "as-sabr miftah al-faraj", "Patience is the key to relief", "Proverb"),
        ("ممتاز!", "mumtaz", "Excellent!", "Useful"),
        ("يلا بينا", "yalla bina", "Let's go!", "Slang"),
    ],
    "hi": [
        ("आपसे मिलकर खुशी हुई", "aapse milkar khushi hui", "Nice to meet you", "Greeting"),
        ("क्या हाल है?", "kya haal hai", "How are you?", "Greeting"),
        ("मैं हिंदी सीख रहा हूँ", "main hindi seekh raha hoon", "I'm learning Hindi", "Useful"),
        ("कृपया दोहराइए", "kripya dohraiye", "Please repeat", "Useful"),
        ("धीरे-धीरे", "dheere-dheere", "Slowly, gradually", "Useful"),
        ("जहाँ चाह वहाँ राह", "jahan chaah wahan raah", "Where there's a will, there's a way", "Proverb"),
        ("बहुत बढ़िया!", "bahut badhiya", "Very good!", "Slang"),
        ("कोई बात नहीं", "koi baat nahin", "No problem", "Useful"),
    ],
    "tr": [
        ("Memnun oldum", "mem-NOON ol-DOOM", "Nice to meet you", "Greeting"),
        ("Nasılsın?", "NAH-suhl-suhn", "How are you?", "Greeting"),
        ("Türkçe öğreniyorum", "TEWRK-cheh ur-reh-NEE-yoh-room", "I'm learning Turkish", "Useful"),
        ("Tekrar eder misiniz?", "tek-RAR eh-DEHR mee-see-neez", "Could you repeat?", "Useful"),
        ("Yavaş yavaş", "yah-VASH yah-VASH", "Slowly, step by step", "Useful"),
        ("Damlaya damlaya göl olur", "dahm-lah-YAH dahm-lah-YAH gurl oh-LOOR", "Drop by drop, a lake forms", "Proverb"),
        ("Harika!", "hah-REE-kah", "Wonderful!", "Slang"),
        ("Kolay gelsin", "koh-LIGH gel-SEEN", "May it come easy (said to someone working)", "Useful"),
    ],
    "nl": [
        ("Aangenaam", "AHN-guh-nahm", "Nice to meet you", "Greeting"),
        ("Hoe gaat het?", "hoo GAHT het", "How's it going?", "Greeting"),
        ("Ik leer Nederlands", "ik layr NAY-der-lahnts", "I'm learning Dutch", "Useful"),
        ("Kun je dat herhalen?", "kun yuh daht her-HAH-len", "Can you repeat that?", "Useful"),
        ("Beetje bij beetje", "BAY-tyuh by BAY-tyuh", "Little by little", "Useful"),
        ("Oefening baart kunst", "OO-fuh-ning bahrt kunst", "Practice makes perfect", "Proverb"),
        ("Gezellig!", "khuh-ZEL-likh", "Cozy / fun atmosphere (untranslatable!)", "Slang"),
        ("Geen probleem", "khayn proh-BLAYM", "No problem", "Useful"),
    ],
    "pl": [
        ("Miło mi", "MEE-woh mee", "Nice to meet you", "Greeting"),
        ("Jak leci?", "yahk LEH-chee", "How's it going?", "Greeting"),
        ("Uczę się polskiego", "OO-cheh sheh pol-SKYEH-goh", "I'm learning Polish", "Useful"),
        ("Możesz powtórzyć?", "MOH-zhesh pof-TOO-zhich", "Can you repeat?", "Useful"),
        ("Krok po kroku", "krok poh KROH-koo", "Step by step", "Useful"),
        ("Nie od razu Kraków zbudowano", "nyeh od RAH-zoo KRAH-koof zboo-doh-VAH-noh", "Krakow wasn't built in a day", "Proverb"),
        ("Super!", "SOO-per", "Great!", "Slang"),
        ("Nie ma sprawy", "nyeh mah SPRAH-vih", "No problem", "Useful"),
    ],
    "sv": [
        ("Trevligt att träffas", "TREV-likt at TREF-fas", "Nice to meet you", "Greeting"),
        ("Läget?", "LEH-get", "What's up?", "Slang"),
        ("Jag lär mig svenska", "yah lair may SVEN-ska", "I'm learning Swedish", "Useful"),
        ("Kan du upprepa det?", "kan doo OOP-reh-pa deh", "Can you repeat that?", "Useful"),
        ("Lite i taget", "LEE-teh ee TAH-get", "A little at a time", "Useful"),
        ("Övning ger färdighet", "URV-ning yehr FAIR-dig-het", "Practice makes perfect", "Proverb"),
        ("Vad kul!", "vah KOOL", "How fun!", "Slang"),
        ("Ingen fara", "ING-en FAH-ra", "No worries", "Useful"),
    ],
    "vi": [
        ("Rất vui được gặp bạn", "zut vooy duhk gap ban", "Nice to meet you", "Greeting"),
        ("Bạn khỏe không?", "ban kweh khong", "How are you?", "Greeting"),
        ("Tôi đang học tiếng Việt", "toy dang hok tyeng vyet", "I'm learning Vietnamese", "Useful"),
        ("Bạn nói lại được không?", "ban noy lie duhk khong", "Can you say that again?", "Useful"),
        ("Từ từ", "tuh tuh", "Slowly, take it easy", "Useful"),
        ("Có công mài sắt, có ngày nên kim", "koh kong my sat koh ngay nen kim", "Perseverance leads to success", "Proverb"),
        ("Tuyệt vời!", "twyet vuhy", "Wonderful!", "Slang"),
        ("Không sao", "khong sao", "No problem", "Useful"),
    ],
    "th": [
        ("ยินดีที่ได้รู้จัก", "yin-dee tee dai roo-jak", "Nice to meet you", "Greeting"),
        ("สบายดีไหม", "sa-bai-dee mai", "How are you?", "Greeting"),
        ("ฉันกำลังเรียนภาษาไทย", "chan gam-lang rian pa-sa thai", "I'm learning Thai", "Useful"),
        ("พูดอีกครั้งได้ไหม", "poot eek krang dai mai", "Can you say it again?", "Useful"),
        ("ช้า ๆ ได้พร้าเล่มงาม", "cha cha dai pra lem ngam", "Slow and steady wins", "Proverb"),
        ("ไม่เป็นไร", "mai pen rai", "It's okay / no worries", "Useful"),
        ("เจ๋งมาก!", "jeng mak", "So cool!", "Slang"),
        ("สู้ ๆ", "soo soo", "Keep fighting! / You can do it!", "Slang"),
    ],
    "id": [
        ("Senang bertemu denganmu", "seh-NANG ber-TEH-moo deng-AN-moo", "Nice to meet you", "Greeting"),
        ("Apa kabar?", "AH-pah KAH-bar", "How are you?", "Greeting"),
        ("Saya sedang belajar bahasa Indonesia", "SAH-yah seh-DANG beh-LAH-jar", "I'm learning Indonesian", "Useful"),
        ("Bisa diulang?", "BEE-sah dee-OO-lang", "Can you repeat?", "Useful"),
        ("Pelan-pelan", "peh-LAHN peh-LAHN", "Slowly, step by step", "Useful"),
        ("Sedikit demi sedikit, lama-lama menjadi bukit", "seh-DEE-kit DEH-mee seh-DEE-kit", "Little by little becomes a hill", "Proverb"),
        ("Keren banget!", "KEH-ren BANG-et", "So cool!", "Slang"),
        ("Tidak apa-apa", "TEE-dak AH-pah AH-pah", "No problem", "Useful"),
    ],
    "el": [
        ("Χάρηκα", "HA-ree-ka", "Nice to meet you", "Greeting"),
        ("Τι κάνεις;", "tee KA-nees", "How are you?", "Greeting"),
        ("Μαθαίνω ελληνικά", "ma-THEH-no eh-lee-nee-KA", "I'm learning Greek", "Useful"),
        ("Μπορείς να το επαναλάβεις;", "bo-REES na to eh-pa-na-LA-vees", "Can you repeat that?", "Useful"),
        ("Σιγά σιγά", "see-GHA see-GHA", "Slowly, little by little", "Useful"),
        ("Η αρχή είναι το ήμισυ του παντός", "ee ar-HEE EE-neh to EE-mee-see too pan-DOS", "The beginning is half of everything", "Proverb"),
        ("Τέλεια!", "TEH-lee-a", "Perfect!", "Slang"),
        ("Κανένα πρόβλημα", "ka-NEH-na PRO-vlee-ma", "No problem", "Useful"),
    ],
}


@router.get("/daily")
async def daily_phrase(
    current_user: CurrentUser,
    lang: str = Query(default=""),
):
    """Phrase of the day for a language (defaults to the user's first
    learning language, then English)."""
    code = (lang or "").lower().strip()
    if code not in PHRASE_BANK:
        learning = current_user.get("learning_languages") or []
        fallback = learning[0] if learning else current_user.get("learning_language")
        code = fallback if fallback in PHRASE_BANK else "en"
    bank = PHRASE_BANK[code]
    now = datetime.now(timezone.utc)
    idx = now.timetuple().tm_yday % len(bank)
    text, roman, meaning, category = bank[idx]
    return {
        "lang": code,
        "lang_name": LANG_NAMES.get(code, code.upper()),
        "text": text,
        "roman": roman,
        "meaning": meaning,
        "category": category,
        "date": now.date().isoformat(),
    }
