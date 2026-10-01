import os
import re
import json
from typing import Dict, Any, Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
GLOSSARY_PATH = os.path.join(DATA_DIR, "crops_glossary.json")

_glossary_cache = None


def _load_glossary() -> Dict[str, Any]:
    global _glossary_cache
    if _glossary_cache is None:
        if os.path.exists(GLOSSARY_PATH):
            with open(GLOSSARY_PATH, "r", encoding="utf-8") as f:
                _glossary_cache = json.load(f)
        else:
            _glossary_cache = {}
    return _glossary_cache


MARATHI_MARKERS = {
    "आहे", "काय", "भाव", "विकू", "थांबू", "नाही", "कसा", "च्या", "मध्ये", "शेतात",
    "शेतकरी", "पाहिजे", "करा", "सांग", "झाले", "मिळेल", "कांदा", "कांद्याचा", "टोमॅटोचे",
    "गहूचे", "बाजार", "बाजारभाव", "कुठे", "जवळ", "कधी", "माझ्याकडे", "आहेत", "शहरात",
    "जिंकले", "कोण", "पडेल", "तुरीचा", "गव्हाचा"
}

HINDI_MARKERS = {
    "है", "क्या", "दाम", "बेचूं", "रुकूं", "नहीं", "कैसा", "के", "में", "खेत",
    "किसान", "चाहिए", "बताओ", "हुआ", "मिलेगा", "प्याज", "टमाटर", "गेहूं", "मंडी",
    "कहाँ", "पास", "कब", "मेरे", "रखूं", "कितना", "होगी", "होगा", "प्रधानमंत्री",
    "सरसों", "मौसम", "बारिश"
}

OFF_TOPIC_KEYWORDS = {
    "france", "paris", "president", "prime minister", "capital", "movie", "cricket",
    "football", "bitcoin", "crypto", "actor", "song", "dance", "poem", "recipe",
    "medicine", "dosage", "tablet", "paracetamol", "symptoms", "प्रधानमंत्री",
    "प्रधान मंत्री", "पॅरिस", "फ्रांस", "मॅच", "जिंकले", "क्रिकेट"
}

ENGLISH_WORDS = {
    "tell", "when", "crosses", "give", "what", "which", "is", "the", "near",
    "best", "should", "i", "sell", "or", "hold", "weather", "forecast", "capital",
    "of", "in", "please", "rate", "price", "today", "show", "help", "mandi"
}

HINGLISH_WORDS = {
    "karo", "jab", "ho", "jaye", "kya", "hai", "batao", "bhai", "chal",
    "raha", "hoga", "mera", "meri", "mere", "pass", "bechu", "ruku", "daam"
}

MARATHISH_WORDS = {
    "madhe", "sanga", "ahe", "viku", "thambu", "kanda", "sheti", "kuthe", "kay"
}


def detect_language(text: str) -> str:
    """
    Detect language of input text:
    'mr' (Marathi), 'hi' (Hindi), 'gu' (Gujarati), 'ta' (Tamil), or 'en' (English).
    """
    t = text.strip()
    if not t:
        return "hi"

    # Check Tamil Unicode block
    if any("\u0b80" <= ch <= "\u0bff" for ch in t):
        return "ta"

    # Check Telugu Unicode block
    if any("\u0c00" <= ch <= "\u0c7f" for ch in t):
        return "te"

    # Check Kannada Unicode block
    if any("\u0c80" <= ch <= "\u0cff" for ch in t):
        return "kn"

    # Check Malayalam Unicode block
    if any("\u0d00" <= ch <= "\u0d7f" for ch in t):
        return "ml"

    # Check Gujarati Unicode block
    if any("\u0a80" <= ch <= "\u0aff" for ch in t):
        return "gu"

    # Check Gurmukhi (Punjabi) Unicode block
    if any("\u0a00" <= ch <= "\u0a7f" for ch in t):
        return "pa"

    # Check Odia Unicode block
    if any("\u0b00" <= ch <= "\u0b7f" for ch in t):
        return "or"

    # Check Bengali / Assamese Unicode block
    if any("\u0980" <= ch <= "\u09ff" for ch in t):
        if any(ch in t for ch in ["ৰ", "ৱ", "নেকি", "কিমান"]):
            return "as"
        return "bn"

    # Check Devanagari Unicode block
    devanagari_chars = [ch for ch in t if "\u0900" <= ch <= "\u097f"]
    if len(devanagari_chars) >= 2:
        words = set(re.findall(r"[\u0900-\u097F]+", t))
        mr_count = len(words.intersection(MARATHI_MARKERS))
        hi_count = len(words.intersection(HINDI_MARKERS))

        if any(marker in t for marker in ["ळ", "आहे", "काय", "च्या", "विकू", "थांबू", "सांग", "जिंकले", "शहरात", "तुरीचा", "कांद्याचा"]):
            return "mr"
        if mr_count > hi_count:
            return "mr"
        return "hi"

    # Latin Script (Hinglish vs Marathish vs English)
    words = set(re.findall(r"[a-zA-Z]+", t.lower()))
    mr_score = len(words.intersection(MARATHISH_WORDS))
    hi_score = len(words.intersection(HINGLISH_WORDS))
    en_score = len(words.intersection(ENGLISH_WORDS))

    if mr_score > 0 and mr_score >= hi_score:
        return "mr"
    if hi_score > 0 and hi_score >= en_score:
        return "hi"
    if en_score > 0:
        return "en"

    return "en"


def normalize_crop(name: str) -> Optional[str]:
    """
    Normalize any crop alias (Hindi/Marathi/Gujarati/Tamil/English/Hinglish)
    to the canonical English crop name.
    """
    if not name:
        return None

    name_clean = name.strip().lower()
    glossary = _load_glossary()

    for canonical, details in glossary.items():
        if canonical.lower() == name_clean:
            return canonical

        aliases_by_lang = details.get("aliases", {})
        for lang, alias_list in aliases_by_lang.items():
            for alias in alias_list:
                if alias.lower() == name_clean or alias.lower() in name_clean:
                    return canonical

    return None


def extract_query(text: str, detected_lang: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract crop, district, mandi, quantity, and intent from user message.
    Intents: price_check, sell_or_hold, best_mandi, set_alert, weather, general, off_topic.
    """
    DEV_TO_ASCII = str.maketrans("०१२३४५६७८९", "0123456789")
    t_clean = text.translate(DEV_TO_ASCII)
    lang = detected_lang or detect_language(t_clean)
    t_lower = t_clean.lower()

    # 1. Check Off-Topic
    if any(kw.lower() in t_lower for kw in OFF_TOPIC_KEYWORDS):
        return {
            "crop": None,
            "district": None,
            "mandi": None,
            "quantity": None,
            "intent": "off_topic",
            "language": lang,
            "missing_fields": []
        }

    # 2. Extract Crop
    detected_crop = None
    glossary = _load_glossary()
    
    for canonical, details in glossary.items():
        aliases_by_lang = details.get("aliases", {})
        for l, alias_list in aliases_by_lang.items():
            for alias in alias_list:
                a_clean = alias.strip().lower()
                if not a_clean:
                    continue
                if a_clean.isascii() and a_clean.isalpha():
                    if re.search(rf"\b{re.escape(a_clean)}\b", t_lower):
                        detected_crop = canonical
                        break
                else:
                    if a_clean in t_lower:
                        detected_crop = canonical
                        break
            if detected_crop:
                break
        if detected_crop:
            break

    # 3. Extract Mandi / District
    KNOWN_LOCATIONS = {
        "nashik": "Nashik", "नासिक": "Nashik", "नाशिक": "Nashik", "नाशिकमध्ये": "Nashik", "નાશિક": "Nashik",
        "lasalgaon": "Lasalgaon", "लासलगाव": "Lasalgaon", "लासलगांव": "Lasalgaon",
        "pimpalgaon": "Pimpalgaon", "पिंपळगाव": "Pimpalgaon",
        "pune": "Pune", "पुणे": "Pune", "पुण्यात": "Pune", "पुणेमध्ये": "Pune", "પુણે": "Pune",
        "latur": "Latur", "लातूर": "Latur", "लातूरमध्ये": "Latur", "લાતૂર": "Latur",
        "solapur": "Solapur", "सोलापूर": "Solapur", "सोलापूरमध्ये": "Solapur",
        "ahmednagar": "Ahmednagar", "अहमदनगर": "Ahmednagar",
        "nagpur": "Nagpur", "नागपूर": "Nagpur",
        "rajkot": "Rajkot", "राजकोट": "Rajkot", "રાજકોટ": "Rajkot", "રાજકોટમાં": "Rajkot",
        "gondal": "Gondal", "ગोंडल": "Gondal", "ગોંડલ": "Gondal",
        "surat": "Surat", "सूरत": "Surat", "સુરત": "Surat",
        "indore": "Indore", "इंदौर": "Indore",
        "ujjain": "Ujjain", "उज्जैन": "Ujjain",
        "agra": "Agra", "आगरा": "Agra",
        "khanna": "Khanna", "खन्ना": "Khanna", "ਖੰਨਾ": "Khanna",
        "ludhiana": "Ludhiana", "लुधियाना": "Ludhiana", "ਲੁਧਿਆਣਾ": "Ludhiana",
        "madurai": "Madurai", "மதுரை": "Madurai", "மதுரையில்": "Madurai",
        "warangal": "Warangal", "వరంగల్": "Warangal", "వరంగల్‌లో": "Warangal",
        "dharwad": "Dharwad", "ಧಾರವಾಡ": "Dharwad", "ಧಾರವಾಡದಲ್ಲಿ": "Dharwad",
        "palakkad": "Palakkad", "പാലക്കാട്": "Palakkad",
        "burdwan": "Burdwan", "বর্ধমান": "Burdwan",
        "cuttack": "Cuttack", "କଟକ": "Cuttack", "କଟକରେ": "Cuttack",
        "nagaon": "Nagaon", "নগাঁও": "Nagaon", "নগাঁৱত": "Nagaon"
    }

    detected_district = None
    for token, loc_name in KNOWN_LOCATIONS.items():
        if token.lower() in t_lower:
            detected_district = loc_name
            break

    # 4. Extract Quantity (Explicit units required!)
    quantity = None
    qty_match = re.search(r"(\d+)\s*(क्विंटल|quintal|qtl|किलो|kg|kilo|बोरी|bags|टन|ton)\b", t_clean, re.IGNORECASE)
    if qty_match:
        val = int(qty_match.group(1))
        unit = qty_match.group(2)
        quantity = f"{val} {unit}"

    # 5. Extract Target Price (Alert target)
    target_price = None
    alert_keywords = ["alert", "अलर्ट", "cross", "crosses", "पार", "झाले की", "होते ही", "सांग", "पोहचल्यावर", "ਐਲਰਟ", "সতর্কবার্তা", "ଆଲର୍ଟ"]
    is_alert_context = any(k in t_lower for k in alert_keywords)

    if is_alert_context:
        # Find all numbers
        nums = re.findall(r"\b\d+\b", t_clean)
        for n in nums:
            val = float(n)
            if quantity and str(int(val)) in str(quantity):
                continue
            if val <= 100:  # e.g. 25 rs/kg or 40 rs/kg
                val = val * 100.0  # normalize to per-quintal rate
            target_price = val
            break

    # 6. Determine Intent
    intent = "general"
    if is_alert_context:
        intent = "set_alert"
    elif any(k in t_lower for k in [
        "विकू की थांबू", "बेचूं या रुकूं", "sell or hold", "विकू", "थांबू", "बेचूं", "रुकूं", "wait or sell",
        "વેચવું કે રોકાવું", "રોકાવું", "விற்கலாமா", "வைக்கலாமா", "అమ్మాలా ఆగాలా", "అమ్మాలా",
        "ಮಾರಾಟ ಮಾಡಬೇಕೇ", "ಮಾರಬೇಕೆ", "വിൽക്കണോ", "കാത്തിരിക്കണോ", "বিক্রি করব না রাখব", "বিক্রি করব",
        "ਵੇਚਾਂ ਜਾਂ ਰੁਕਾਂ", "ବିକ୍ରି କରିବି ନା ରଖିବି", "ବିକ୍ରି କରିବି", "বিক্ৰী কৰিম নে ৰাখিম", "বিক্ৰী কৰিম"
    ]):
        intent = "sell_or_hold"
    elif any(k in t_lower for k in ["सबसे अच्छी मंडी", "चांगली बाजारपेठ", "best mandi", "nearby mandi", "कोणती मंडी", "कहाँ ले जाऊं", "ਸਭ ਤੋਂ ਵਧੀਆ ਮੰਡੀ"]):
        intent = "best_mandi"
    elif any(k in t_lower for k in [
        "weather", "हवामान", "मौसम", "बारिश", "पाऊस", "rain",
        "વરસાદ", "வானிலை", "వాతావరణం", "ಹವಾಮಾನ", "കാലാവസ്ഥ", "আবহাওয়া", "ਮੌਸਮ", "ପାଣିପାଗ", "বতৰ"
    ]):
        intent = "weather"
    elif any(k in t_lower for k in [
        "भाव", "दाम", "rate", "price", "rate kya", "bhav kay", "bhav",
        "ભાવ", "કિંમત", "விலை", "ధర", "బేల", "ಬೆಲೆ", "വില", "നിരക്ക്", "দাম", "দর", "দৰ", "ਭਾਅ", "ଦର"
    ]):
        intent = "price_check"
    elif detected_crop:
        intent = "price_check"

    # Identify missing fields
    missing_fields = []
    if intent in ["price_check", "sell_or_hold", "best_mandi", "set_alert"]:
        if not detected_crop:
            missing_fields.append("crop")
        if not detected_district:
            missing_fields.append("location")

    return {
        "crop": detected_crop,
        "district": detected_district,
        "mandi": detected_district,
        "quantity": quantity,
        "target_price": target_price,
        "intent": intent,
        "language": lang,
        "missing_fields": missing_fields
    }


SCRIPT_RANGES = {
    "en": [(0x0041, 0x005A), (0x0061, 0x007A)],
    "hi": [(0x0900, 0x097F)],
    "mr": [(0x0900, 0x097F)],
    "gu": [(0x0A80, 0x0AFF)],
    "ta": [(0x0B80, 0x0BFF)],
    "te": [(0x0C00, 0x0C7F)],
    "kn": [(0x0C80, 0x0CFF)],
    "ml": [(0x0D00, 0x0D7F)],
    "bn": [(0x0980, 0x09FF)],
    "pa": [(0x0A00, 0x0A7F)],
    "or": [(0x0B00, 0x0B7F)],
    "as": [(0x0980, 0x09FF)],
}


def check_script_purity(reply: str, target_lang: str) -> float:
    """
    Returns ratio (0.0 to 1.0) of alphabetic characters in reply that match target script.
    Ignores digits, punctuation, ₹, and brand/source names like KisanSaathi.
    """
    cleaned = (reply
        .replace("KisanSaathi", "")
        .replace("Agmarknet", "")
        .replace("Agro-Benchmark", "")
        .replace("Open-Meteo", "")
        .replace("FRP", "")
        .replace("MSP", "")
        .replace("WhatsApp", "")
    )
    ranges = SCRIPT_RANGES.get(target_lang, [])
    if not ranges:
        return 1.0

    total_letters = 0
    target_letters = 0

    for ch in cleaned:
        code = ord(ch)
        if code in [0x0964, 0x0965]:  # Standard Indic danda / double danda punctuation
            continue
        if ch.isalpha() or (0x0900 <= code <= 0x0D7F and not ('0' <= ch <= '9')):
            total_letters += 1
            if any(start <= code <= end for start, end in ranges):
                target_letters += 1

    if total_letters == 0:
        return 1.0
    return target_letters / total_letters

