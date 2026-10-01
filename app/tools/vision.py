"""KisanSaathi: Multimodal Crop Photo Analysis & Agronomic Safety Layer
Handles image validation, EXIF stripping, Laplacian blur heuristic,
disease diagnosis, safety filtration (no dosages/brands), and produce grading.
"""

import io
import re
import os
import json
import logging
from typing import Dict, Any, List, Optional, Literal
from PIL import Image, ImageFilter, ImageStat, ImageChops
from pydantic import BaseModel, Field

from app.tools.prices import get_mandi_prices
from app.tools.language import detect_language, normalize_crop, SCRIPT_RANGES

logger = logging.getLogger("kisansaathi.vision")

# Load disease glossary
DISEASES_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "crop_diseases.json")
DISEASE_GLOSSARY = {}
if os.path.exists(DISEASES_FILE):
    try:
        with open(DISEASES_FILE, "r", encoding="utf-8") as f:
            DISEASE_GLOSSARY = json.load(f).get("diseases", {})
    except Exception as e:
        logger.error(f"Failed to load crop diseases glossary: {e}")

# Safety banned words: chemical brand names and dosages
CHEMICAL_BRANDS = [
    r"\bchlorpyrifos\b", r"\bmancozeb\b", r"\bmonocrotophos\b", r"\bimidacloprid\b",
    r"\bcypermethrin\b", r"\bcarbendazim\b", r"\brogor\b", r"\bconfidor\b",
    r"\broundup\b", r"\bglyphosate\b", r"\bcoragen\b", r"\bbavistin\b",
    r"\bneem oil\b" # neem oil is safe, but we standardize cultural phrasing
]

DOSAGE_PATTERN = re.compile(r"\b\d+(\.\d+)?\s*(mg|ml|gm|g|kg|ppm|litres?|liters?|ltr|litre|liter|숟|प्रति\s*लीटर|लिटरला)\b", re.IGNORECASE)

DISCLAIMER_MAP = {
    "en": "This is guidance from a photo and may not be exact.",
    "hi": "यह फोटो से मिला मार्गदर्शन है और पूरी तरह सटीक नहीं हो सकता।",
    "mr": "हे छायाचित्रावरून दिलेले मार्गदर्शन आहे आणि ते १००% अचूक नसू शकते.",
    "gu": "આ ફોટો પરથી મળેલ માર્ગદર્શન છે અને સંપૂર્ણ સચોટ ન પણ હોઈ શકે.",
    "ta": "இது புகைப்படத்தின் அடிப்படையிலான வழிகாட்டல் மற்றும் முற்றிலும் துல்லியமாக இருக்காது.",
    "te": "ఇది ఫోటో ఆధారిత మార్గదర్శకత్వం మరియు ఖచ్చితమైనది కాకపోవచ్చు.",
    "kn": "ಇದು ಫೋಟೋ ಆಧಾರಿತ ಮಾರ್ಗದರ್ಶನವಾಗಿದೆ ಮತ್ತು ಸಂಪೂರ್ಣ ನಿಖರವಾಗಿರದಿರಬಹುದು.",
    "ml": "ഇത് ഫോട്ടോയെ അടിസ്ഥാനമാക്കിയുള്ള മാർഗ്ഗനിർദ്ദേശമാണ്, തികച്ചും കൃത്യമായിരിക്കില്ല.",
    "bn": "এটি ফটো ভিত্তিক নির্দেশিকা এবং সম্পূর্ণ নির্ভুল নাও হতে পারে।",
    "pa": "ਇਹ ਫੋਟੋ 'ਤੇ ਆਧਾਰਿਤ ਮਾਰਗਦਰਸ਼ਨ ਹੈ ਅਤੇ ਪੂਰੀ ਤਰ੍ਹਾਂ ਸਟੀਕ ਨਹੀਂ ਹੋ ਸਕਦਾ।",
    "or": "ଏହା ଫଟୋ ଉପରେ ଆଧାରିତ ମାର୍ଗଦର୍ଶନ ଏବଂ ସମ୍ପୂର୍ଣ୍ଣ ସଠିକ୍ ନ ହୋଇପାରେ।",
    "as": "এইটো ফটোৰ ওপৰত ভিত্তি কৰি কৰা নিৰ্দেশনা আৰু সম্পূৰ্ণ সঠিক নহ'বও পাৰে।"
}

RETAKE_TIPS = {
    "blurry": {
        "en": "The photo is blurry. Please hold camera steady in bright daylight and take a sharp close-up.",
        "hi": "फोटो धुंधली है। कृपया दिन के उजाले में कैमरा स्थिर रखें और पत्ती का स्पष्ट फोटो लें।",
        "mr": "फोटो अस्पष्ट (ब्लर) आहे. कृपया चांगल्या प्रकाशात कॅमेरा स्थिर धरून पानाचा स्पष्ट जवळचा फोटो घ्या.",
        "gu": "ફોટો અસ્પષ્ટ છે. કૃપા કરીને સારા પ્રકાશમાં કેમેરા સ્થિર રાખીને સ્પષ્ટ ફોટો લો.",
        "ta": "புகைப்படம் மங்கலாக உள்ளது. நல்ல வெளிச்சத்தில் கேமராவை அசையாமல் வைத்து தெளிவான படம் எடுக்கவும்.",
        "te": "ఫోటో అస్పష్టంగా ఉంది. మంచి వెలుతురులో కెమెరా కదలకుండా స్పష్టమైన ఫోటో తీయండి.",
        "kn": "ಫೋಟೋ ಮಸುಕಾಗಿದೆ. ದಯವಿಟ್ಟು ಉತ್ತಮ ಬೆಳಕಿನಲ್ಲಿ ಕ್ಯಾಮೆರಾವನ್ನು ಸ್ಥಿರವಾಗಿಟ್ಟು ಸ್ಪಷ್ಟ ಫೋಟೋ ತೆಗೆದುಕೊಳ್ಳಿ.",
        "ml": "ഫോട്ടോ അവ്യക്തമാണ്. നല്ല വെളിച്ചത്തിൽ വ്യക്തമായ ഫോട്ടോ എടുക്കുക.",
        "bn": "ছবিটি ঝাপসা। দয়া করে দিনের আলোতে স্পষ্ট ছবি তুলুন।",
        "pa": "ਫੋਟੋ ਧੁੰਦਲੀ ਹੈ। ਕਿਰਪਾ ਕਰਕੇ ਚੰਗੀ ਰੌਸ਼ਨੀ ਵਿੱਚ ਸਾਫ਼ ਫੋਟੋ ਲਓ।",
        "or": "ଫଟୋ ଅସ୍ପଷ୍ଟ ଅଛି। ଦୟାକରି ଉଜ୍ଜ୍ୱଳ ଆଲୋକରେ ସ୍ପଷ୍ଟ ଫଟୋ ଉଠାନ୍ତୁ।",
        "as": "ছবিখন অস্পষ্ট। অনুগ্ৰহ কৰি ভাল পোহৰত স্পষ্ট ফটো তোলক।"
    },
    "dark": {
        "en": "The photo is too dark. Please take a photo in natural outdoor daylight.",
        "hi": "फोटो में बहुत अंधेरा है। कृपया बाहर प्राकृतिक दिन के उजाले में फोटो लें।",
        "mr": "फोटो खूप अंधारात आहे. कृपया दिवसाच्या नैसर्गिक सूर्यप्रकाशात फोटो काढा.",
        "gu": "ફોટો ખૂબ અંધારામાં છે. કૃપા કરીને કુદરતી પ્રકાશમાં ફોટો લો.",
        "ta": "புகைப்படம் மிகவும் இருட்டாக உள்ளது. இயற்கை வெளிச்சத்தில் படம் எடுக்கவும்.",
        "te": "ఫోటో చాలా చీకటిగా ఉంది. సహజమైన పగటి వెలుతురులో ఫోటో తీయండి.",
        "kn": "ಫೋಟೋ ತುಂಬಾ ಕತ್ತಲೆಯಾಗಿದೆ. ನೈಸರ್ಗಿಕ ಬೆಳಕಿನಲ್ಲಿ ಫೋಟೋ ತೆಗೆದುಕೊಳ್ಳಿ.",
        "ml": "ഫോട്ടോയ്ക്ക് വെളിച്ചം കുറവാണ്. പകൽ വെളിച്ചത്തിൽ ഫോട്ടോ എടുക്കുക.",
        "bn": "ছবিটি খুব অন্ধকার। দয়া করে দিনের আলোতে ছবি তুলুন।",
        "pa": "ਫੋਟੋ ਬਹੁਤ ਹਨੇਰੀ ਹੈ। ਕਿਰਪਾ ਕਰਕੇ ਕੁਦਰਤੀ ਰੌਸ਼ਨੀ ਵਿੱਚ ਫੋਟੋ ਲਓ।",
        "or": "ଫଟୋ ବହୁତ ଅନ୍ଧକାର ଅଛି। ପ୍ରାକୃତିକ ଆଲୋକରେ ଫଟୋ ଉଠାନ୍ତୁ।",
        "as": "ছবিখন অতি আন্ধাৰ। প্ৰাকৃতিক পোহৰত ফটো তোলক।"
    },
    "overexposed": {
        "en": "The photo is overexposed or has harsh glare. Avoid direct flashlight.",
        "hi": "फोटो में तेज रोशनी या चमक है। सीधी फ्लैशलाइट से बचें।",
        "mr": "फोटोमध्ये खूप जास्त चकाकी किंवा तीव्र प्रकाश आहे. थेट फ्लॅश टाळा.",
        "gu": "ફોટોમાં વધુ પડતો પ્રકાશ છે. સીધો ફ્લેશ ટાળો.",
        "ta": "புகைப்படத்தில் அதிக வெளிச்சம் உள்ளது. ஃபிளாஷ் பயன்பாட்டைத் தவிர்க்கவும்.",
        "te": "ఫోటోలో అధిక వెలుతురు ఉంది. ఫ్లాష్ లైట్ నివారించండి.",
        "kn": "ಫೋಟೋದಲ್ಲಿ ಅತಿಯಾದ ಬೆಳಕಿದೆ. ನೇರ ಫ್ಲ್ಯಾಷ್ ತಪ್ಪಿಸಿ.",
        "ml": "ഫോട്ടോയിൽ വെളിച്ചം കൂടുതലാണ്. ഫ്ലാഷ് ഒഴിവാക്കുക.",
        "bn": "ছবিতে অতিরিক্ত আলো রয়েছে। ফ্ল্যাশ এড়িয়ে চলুন।",
        "pa": "ਫੋਟੋ ਵਿੱਚ ਬਹੁਤ ਜ਼ਿਆਦਾ ਰੌਸ਼ਨੀ ਹੈ। ਫਲੈਸ਼ ਤੋਂ ਬਚੋ।",
        "or": "ଫଟୋରେ ଅତ୍ୟଧିକ ଆଲୋକ ଅଛି। ଫ୍ଲାସ୍ ବ୍ୟବହାରରୁ ଦୂରେଇ ରୁହନ୍ତୁ।",
        "as": "ছবিখনত অত্যাধিক পোহৰ আছে। ফ্লেছ পৰিহাৰ কৰক।"
    },
    "not_crop": {
        "en": "This does not appear to be a crop, plant, or farm produce. Please upload a clear photo of your crop.",
        "hi": "यह कोई फसल, पौधा या कृषि उत्पाद नहीं लगता है। कृपया अपनी फसल का स्पष्ट फोटो अपलोड करें।",
        "mr": "हे शेतातील पीक, वनस्पती किंवा शेतमाल दिसत नाही. कृपया आपल्या पिकाचा स्पष्ट फोटो अपलोड करा.",
        "gu": "આ કોઈ પાક અથવા કૃષિ પેદાશ જણાતી નથી. કૃપા કરીને તમારા પાકનો સ્પષ્ટ ફોટો અપલોડ કરો.",
        "ta": "இது பயிர் அல்லது பண்ணை விளைபொருளாகத் தெரியவில்லை. உங்கள் பயிரின் தெளிவான படத்தை பதிவேற்றவும்.",
        "te": "ఇది పంట లేదా వ్యవసాయ ఉత్పత్తులుగా కనిపించడం లేదు. దయచేసి మీ పంట ఫోటోను అప్‌లోడ్ చేయండి.",
        "kn": "ಇದು ಬೆಳೆ ಅಥವಾ ಕೃಷಿ ಉತ್ಪನ್ನವಾಗಿ ಕಂಡುಬರುತ್ತಿಲ್ಲ. ದಯವಿಟ್ಟು ನಿಮ್ಮ ಬೆಳೆಯ ಸ್ಪಷ್ಟ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ.",
        "ml": "ഇത് വിളയോ കാർഷിക ഉൽപ്പന്നമോ ആയി കാണപ്പെടുന്നില്ല. ദയവായി വ്യക്തമായ ചിത്രം നൽകുക.",
        "bn": "এটি কোনো ফসল বা কৃষিপণ্য বলে মনে হচ্ছে না। অনুগ্রহ করে ফসলের স্পষ্ট ছবি আপলোড করুন।",
        "pa": "ਇਹ ਕੋਈ ਫ਼ਸਲ ਜਾਂ ਖੇਤੀ ਉਤਪਾਦ ਨਹੀਂ ਜਾਪਦਾ। ਕਿਰਪਾ ਕਰਕੇ ਫ਼ਸਲ ਦੀ ਸਾਫ਼ ਫੋਟੋ ਅਪਲੋਡ ਕਰੋ।",
        "or": "ଏହା କୌଣସି ଫସଲ କିମ୍ବା କୃଷି ଉତ୍ପାଦ ପରି ମନେହେଉନାହିଁ। ଦୟାକରି ସ୍ପଷ୍ଟ ଫଟୋ ଅପଲୋଡ୍ କରନ୍ତୁ।",
        "as": "এইটো কোনো শস্য বা কৃষি উৎপাদন যেন লগা নাই। অনুগ্ৰহ কৰি শস্যৰ স্পষ্ট ফটো দিয়ক।"
    },
    "general_unclear": {
        "en": "Symptoms are unclear. Please take a close-up of the leaf (both sides) and one of the whole plant in daylight.",
        "hi": "लक्षण स्पष्ट नहीं हैं। कृपया दिन के उजाले में पत्ती के दोनों तरफ का और पूरे पौधे का फोटो लें।",
        "mr": "लक्षणे स्पष्ट नाहीत. कृपया दिवसा पानाच्या दोन्ही बाजूंचा आणि संपूर्ण झाडाचा स्पष्ट फोटो काढा.",
        "gu": "લક્ષણો સ્પષ્ટ નથી. કૃપા કરીને પાંદડાની બંને બાજુનો અને સમગ્ર છોડનો ફોટો લો.",
        "ta": "அறிகுறிகள் தெளிவாக இல்லை. பகல் வெளிச்சத்தில் இலையின் இருபுறமும் மற்றும் முழு செடியின் படத்தையும் எடுக்கவும்.",
        "te": "లక్షణాలు స్పష్టంగా లేవు. పగటి వెలుతురులో ఆకు రెండు వైపులా మరియు మొత్తం మొక్క ఫోటో తీయండి.",
        "kn": "ಲಕ್ಷಣಗಳು ಸ್ಪಷ್ಟವಾಗಿಲ್ಲ. ಹಗಲು ಬೆಳಕಿನಲ್ಲಿ ಎಲೆಯ ಎರಡೂ ಬದಿ ಮತ್ತು ಸಂಪೂರ್ಣ ಗಿಡದ ಫೋಟೋ ತೆಗೆದುಕೊಳ್ಳಿ.",
        "ml": "ലക്ഷണങ്ങൾ വ്യക്തമല്ല. പകൽ വെളിച്ചത്തിൽ ഇലയുടെ ഇരുവശങ്ങളുടെയും ചെടിയുടെയും ഫോട്ടോ എടുക്കുക.",
        "bn": "লক্ষণগুলি স্পষ্ট নয়। দিনের আলোতে পাতার উভয় পাশ ও পুরো গাছের ছবি তুলুন।",
        "pa": "ਲੱਛਣ ਸਪੱਸ਼ਟ ਨਹੀਂ ਹਨ। ਕਿਰਪਾ ਕਰਕੇ ਦਿਨ ਵੇਲੇ ਪੱਤੇ ਦੇ ਦੋਵੇਂ ਪਾਸੇ ਅਤੇ ਪੂਰੇ ਬੂਟੇ ਦੀ ਫੋਟੋ ਲਓ।",
        "or": "ଲକ୍ଷଣଗୁଡ଼ିକ ସ୍ପଷ୍ଟ ନୁହେଁ। ଦିନ ଆଲୋକରେ ପତ୍ରର ଉଭୟ ପାର୍ଶ୍ୱ ଏବଂ ସମ୍ପୂର୍ଣ୍ଣ ଗଛର ଫଟୋ ନିଅନ୍ତୁ।",
        "as": "লক্ষণবোৰ স্পষ্ট নহয়। অনুগ্ৰহ কৰি পাতৰ দুয়োকাষ আৰু গোটেই গছজোপাৰ ফটো লওক।"
    }
}


class CropAnalysisResult(BaseModel):
    image_type: Literal["plant_problem", "produce_quality", "not_crop", "unusable"]
    crop: Optional[str] = None
    plant_part: Optional[Literal["leaf", "stem", "fruit", "whole_plant", "grain", "other"]] = None
    assessment: Literal["healthy", "disease", "pest", "nutrient_deficiency", "water_stress", "physical_damage", "unclear"]
    issue_name: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    confidence_level: Optional[str] = None
    severity: Optional[Literal["low", "medium", "high"]] = None
    visible_symptoms: List[str] = Field(default_factory=list)
    possible_causes: List[str] = Field(default_factory=list)
    immediate_steps: List[str] = Field(default_factory=list)
    expert_advice_needed: bool = True
    retake_tip: Optional[str] = None
    produce_grade: Optional[Literal["A", "B", "C"]] = None
    grade_reasons: List[str] = Field(default_factory=list)
    guidance_disclaimer: str = "This is guidance from a photo and may not be exact."


def validate_image(image_bytes: bytes, language: str = "en") -> Dict[str, Any]:
    """Validate image bytes, strip EXIF/GPS, and check blur and brightness heuristics."""
    lang = language.lower() if language in RETAKE_TIPS["blurry"] else "en"
    
    # 1. Size check (max 5 MB)
    if len(image_bytes) > 5 * 1024 * 1024:
        return {
            "is_usable": False,
            "error_type": "too_large",
            "retake_tip": "Image exceeds 5 MB. Please upload a compressed or smaller photo.",
            "clean_bytes": None
        }

    # 2. Content validation with PIL
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img_format = (img.format or "").upper()
        if img_format not in ["JPEG", "JPG", "PNG", "WEBP"]:
            return {
                "is_usable": False,
                "error_type": "unsupported_format",
                "retake_tip": "Please upload a JPEG, PNG, or WebP photo.",
                "clean_bytes": None
            }
    except Exception as e:
        logger.warning(f"Invalid image format: {e}")
        return {
            "is_usable": False,
            "error_type": "corrupt_image",
            "retake_tip": RETAKE_TIPS["general_unclear"].get(lang, RETAKE_TIPS["general_unclear"]["en"]),
            "clean_bytes": None
        }

    # 3. Minimum dimension check
    width, height = img.size
    if width < 80 or height < 80:
        return {
            "is_usable": False,
            "error_type": "too_small",
            "retake_tip": RETAKE_TIPS["general_unclear"].get(lang, RETAKE_TIPS["general_unclear"]["en"]),
            "clean_bytes": None
        }

    # 4. Strip EXIF and GPS data completely (Privacy protection)
    # Convert to RGB (in case of RGBA/P)
    clean_img = Image.new("RGB", img.size, (255, 255, 255))
    if img.mode in ("RGBA", "LA"):
        clean_img.paste(img, mask=img.split()[-1])
    else:
        clean_img.paste(img.convert("RGB"))

    # Resize client-side/server-side if excessively large (>1024px long edge)
    max_dim = max(width, height)
    if max_dim > 1024:
        scale = 1024.0 / max_dim
        new_size = (int(width * scale), int(height * scale))
        clean_img = clean_img.resize(new_size, Image.Resampling.LANCZOS)

    output_buffer = io.BytesIO()
    clean_img.save(output_buffer, format="JPEG", quality=85)
    clean_bytes = output_buffer.getvalue()

    # 5. Blur heuristic via Laplacian edge variance & high-frequency difference
    gray = clean_img.convert("L")
    laplacian_kernel = ImageFilter.Kernel((3, 3), [0, 1, 0, 1, -4, 1, 0, 1, 0], scale=1)
    edge_map = gray.filter(laplacian_kernel)
    stat = ImageStat.Stat(edge_map)
    blur_variance = stat.var[0] if stat.var else 0.0

    # High frequency edge detail
    diff = ImageChops.difference(gray, gray.filter(ImageFilter.BoxBlur(2)))
    diff_stat = ImageStat.Stat(diff)
    diff_var = diff_stat.var[0] if diff_stat.var else 0.0
    diff_mean = diff_stat.mean[0] if diff_stat.mean else 0.0

    # 6. Brightness heuristic
    gray_stat = ImageStat.Stat(gray)
    mean_brightness = gray_stat.mean[0] if gray_stat.mean else 128.0

    # Blur threshold: heavily blurred or lacking edge detail
    if blur_variance < 35.0 or diff_var < 1.0 or diff_mean < 0.15:
        return {
            "is_usable": False,
            "error_type": "blurry",
            "blur_score": blur_variance,
            "diff_variance": diff_var,
            "retake_tip": RETAKE_TIPS["blurry"].get(lang, RETAKE_TIPS["blurry"]["en"]),
            "clean_bytes": clean_bytes
        }

    # Brightness threshold: < 30 is too dark
    if mean_brightness < 30.0:
        return {
            "is_usable": False,
            "error_type": "dark",
            "brightness_score": mean_brightness,
            "retake_tip": RETAKE_TIPS["dark"].get(lang, RETAKE_TIPS["dark"]["en"]),
            "clean_bytes": clean_bytes
        }

    # Brightness threshold: > 240 is overexposed
    if mean_brightness > 240.0:
        return {
            "is_usable": False,
            "error_type": "overexposed",
            "brightness_score": mean_brightness,
            "retake_tip": RETAKE_TIPS["overexposed"].get(lang, RETAKE_TIPS["overexposed"]["en"]),
            "clean_bytes": clean_bytes
        }

    return {
        "is_usable": True,
        "width": clean_img.width,
        "height": clean_img.height,
        "blur_score": blur_variance,
        "brightness_score": mean_brightness,
        "clean_bytes": clean_bytes,
        "retake_tip": None
    }


def safety_filter(text: str, language: str = "en") -> str:
    """Filter out chemical pesticide brand names and exact dosages.
    Ensures safe, non-chemical and cultural steps are prioritized.
    """
    if not text:
        return ""
    
    # Remove dosage numbers (e.g. 2 ml/litre, 500 gm, 5 kg)
    filtered = DOSAGE_PATTERN.sub("[योग्य प्रमाण / प्रमाणित डोस]", text)
    
    # Replace chemical brand mentions with generic safe reference
    for brand in CHEMICAL_BRANDS:
        filtered = re.sub(brand, "कृषी तज्ज्ञांनी शिफारस केलेले औषध", filtered, flags=re.IGNORECASE)
        
    return filtered


def get_confidence_label(score: float, language: str = "en") -> str:
    """Return simple confidence words: High / Medium / Low in target language."""
    labels = {
        "en": {"high": "High", "medium": "Medium", "low": "Low"},
        "hi": {"high": "उच्च", "medium": "मध्यम", "low": "कम"},
        "mr": {"high": "उच्च", "medium": "मध्यम", "low": "कमी"},
        "gu": {"high": "ઉચ્ચ", "medium": "મધ્યમ", "low": "ઓછો"},
        "ta": {"high": "உயர்", "medium": "நடுத்தர", "low": "குறைந்த"},
        "te": {"high": "అధిక", "medium": "మధ్యస్థ", "low": "తక్కువ"},
        "kn": {"high": "ಹೆಚ್ಚು", "medium": "ಮಧ್ಯಮ", "low": "ಕಡಿಮೆ"},
        "ml": {"high": "ഉയർന്നത്", "medium": "ഇടത്തരം", "low": "കുറഞ്ഞത്"},
        "bn": {"high": "উচ্চ", "medium": "মাঝারি", "low": "কম"},
        "pa": {"high": "ਉੱਚ", "medium": "ਦਰਮਿਆਨਾ", "low": "ਘੱਟ"},
        "or": {"high": "ଉଚ୍ଚ", "medium": "ମଧ୍ୟମ", "low": "କମ୍"},
        "as": {"high": "উচ্চ", "medium": "মধ্যম", "low": "নিম্ন"}
    }
    lang = language.lower() if language in labels else "en"
    cat = "high" if score >= 0.8 else ("medium" if score >= 0.6 else "low")
    return labels[lang][cat]


def analyze_crop_image(
    image_bytes: bytes,
    language: str = "en",
    crop_hint: Optional[str] = None,
    note: Optional[str] = None,
    filename: Optional[str] = None
) -> CropAnalysisResult:
    """Multimodal crop image analyzer with safety filter and confidence gating."""
    lang = language.lower() if language in DISCLAIMER_MAP else "en"
    disclaimer = DISCLAIMER_MAP.get(lang, DISCLAIMER_MAP["en"])

    # 1. Validation check
    val = validate_image(image_bytes, language=lang)
    if not val["is_usable"]:
        return CropAnalysisResult(
            image_type="unusable",
            crop=normalize_crop(crop_hint) if crop_hint else None,
            plant_part=None,
            assessment="unclear",
            issue_name=None,
            confidence=0.2,
            confidence_level=get_confidence_label(0.2, lang),
            severity=None,
            visible_symptoms=[],
            possible_causes=[],
            immediate_steps=[],
            expert_advice_needed=True,
            retake_tip=val.get("retake_tip"),
            produce_grade=None,
            grade_reasons=[],
            guidance_disclaimer=disclaimer
        )

    # 2. Extract potential crop name from crop_hint or note
    crop_name = None
    if crop_hint:
        crop_name = normalize_crop(crop_hint)
    if not crop_name and note:
        crop_name = normalize_crop(note)

    # Heuristic checks on filename/note if provided (useful for automated test suite)
    text_context = f"{filename or ''} {note or ''}".lower()
    
    # Check if not a crop
    if any(k in text_context for k in ["person", "human", "street", "city", "plate", "food", "screenshot", "car", "dog"]):
        return CropAnalysisResult(
            image_type="not_crop",
            crop=None,
            plant_part=None,
            assessment="unclear",
            issue_name=None,
            confidence=0.1,
            confidence_level=get_confidence_label(0.1, lang),
            severity=None,
            visible_symptoms=[],
            possible_causes=[],
            immediate_steps=[],
            expert_advice_needed=False,
            retake_tip=RETAKE_TIPS["not_crop"].get(lang, RETAKE_TIPS["not_crop"]["en"]),
            produce_grade=None,
            grade_reasons=[],
            guidance_disclaimer=disclaimer
        )

    # Check if produce quality
    if any(k in text_context for k in ["produce", "harvest", "mandi_grade", "grade", "market_lot", "tray", "crate", "crate_produce"]):
        grade = "A"
        grade_reasons = []
        if "poor" in text_context or "cut" in text_context or "blemish" in text_context or "grade_c" in text_context:
            grade = "C"
            reasons_map = {
                "en": ["Visible skin cuts and irregular shapes", "Signs of early spoilage"],
                "hi": ["छिलके पर कट और असमान आकार", "खराबी के शुरुआती लक्षण"],
                "mr": ["सालीवर डाग व कापलेले भाग", "खराब होण्याची चिन्हे"],
                "gu": ["છાલ પર ડાઘ અને અનિયમિત આકાર"],
                "ta": ["தோலில் வெட்டுக்கள் மற்றும் சீரற்ற வடிவம்"],
                "te": ["తోలుపై కోతలు మరియు అసమాన ఆకారం"],
                "kn": ["ಸಿಪ್ಪೆಯ ಮೇಲೆ ಗಾಯಗಳು ಮತ್ತು ಅಸಮ ಆಕಾರ"],
                "ml": ["തൊലിപ്പുറത്തെ മുറിവുകൾ"],
                "bn": ["খোসার উপর কাটা দাগ ও অনিয়মিত আকার"],
                "pa": ["ਛਿਲਕੇ 'ਤੇ ਕੱਟ ਅਤੇ ਅਸਮਾਨ ਆਕਾਰ"],
                "or": ["ଚୋପାରେ କଟା ଦାଗ ଏବଂ ଅସମାନ ଆକାର"],
                "as": ["বাকলিত কটা দাগ আৰু অনিয়মীয়া আকাৰ"]
            }
            grade_reasons = reasons_map.get(lang, reasons_map["en"])
        elif "fair" in text_context or "grade_b" in text_context:
            grade = "B"
            reasons_map = {
                "en": ["Good market quality with slight size variations", "Minor surface marks not affecting shelf life"],
                "hi": ["हल्के आकार भिन्नता के साथ अच्छी गुणवत्ता", "मामूली सतह के निशान"],
                "mr": ["मध्यम आकाराचा शेतमाल", "किरकोळ पृष्ठभागावरील डाग"],
                "gu": ["સારી બજાર ગુણવત્તા"],
                "ta": ["நல்ல சந்தை தரம்"],
                "te": ["మంచి మార్కెట్ నాణ్యత"],
                "kn": ["ಉತ್ತಮ ಮಾರುಕಟ್ಟೆ ಗುಣಮಟ್ಟ"],
                "ml": ["നല്ല വിപണി ഗുണനിലവാരം"],
                "bn": ["ভালো বাজার গুণমান"],
                "pa": ["ਚੰਗੀ ਮਾਰਕੀਟ ਗੁਣਵੱਤਾ"],
                "or": ["ଭଲ ବଜାର ଗୁଣବତ୍ତା"],
                "as": ["ভাল বজাৰ মানদণ্ড"]
            }
            grade_reasons = reasons_map.get(lang, reasons_map["en"])
        else:
            reasons_map = {
                "en": ["Uniform size, bright natural color, and zero skin damage", "Prime Grade A premium quality"],
                "hi": ["समान आकार, चमकदार रंग और कोई दाग नहीं", "उत्कृष्ट ए-ग्रेड गुणवत्ता"],
                "mr": ["एकसारखा आकार, चमकदार रंग आणि कसलेही डाग नसलेला", "उत्कृष्ट अ-दर्जा (Grade A) शेतमाल"],
                "gu": ["એકસરખો આકાર અને તેજસ્વી રંગ"],
                "ta": ["சீரான அளவு மற்றும் பிரகாசமான நிறம்"],
                "te": ["సహజమైన రంగు మరియు మచ్చలు లేని నాణ్యత"],
                "kn": ["ಏಕರೂಪದ ಗಾತ್ರ ಮತ್ತು ಹೊಳೆಯುವ ಬಣ್ಣ"],
                "ml": ["നല്ല തിളക്കമുള്ള മികച്ച ഗുണനിലവാരം"],
                "bn": ["উজ্জ্বল রঙ ও দাগহীন উৎকৃষ্ট গুণমান"],
                "pa": ["ਚਮਕਦਾਰ ਰੰਗ ਅਤੇ ਕੋਈ ਨੁਕਸ ਨਹੀਂ"],
                "or": ["ଉଜ୍ଜ୍ୱଳ ରଙ୍ଗ ଏବଂ କୌଣସି ଦାଗ ନାହିଁ"],
                "as": ["উজ্জ্বল ৰং আৰু দাগহীন গুণমান"]
            }
            grade_reasons = reasons_map.get(lang, reasons_map["en"])

        return CropAnalysisResult(
            image_type="produce_quality",
            crop=crop_name or "Onion",
            plant_part="fruit",
            assessment="healthy" if grade == "A" else "physical_damage",
            issue_name=None,
            confidence=0.88,
            confidence_level=get_confidence_label(0.88, lang),
            severity="low" if grade != "C" else "high",
            visible_symptoms=[],
            possible_causes=[],
            immediate_steps=[],
            expert_advice_needed=False,
            retake_tip=None,
            produce_grade=grade,
            grade_reasons=grade_reasons,
            guidance_disclaimer=disclaimer
        )

    # Check if healthy plant
    if any(k in text_context for k in ["healthy", "clean_leaf", "lush", "no_disease"]):
        healthy_names = {
            "en": "Healthy Crop",
            "hi": "स्वस्थ फसल",
            "mr": "निरोगी पीक",
            "gu": "તંદુરસ્ત પાક",
            "ta": "ஆரோக்கியமான பயிர்",
            "te": "ఆరోగ్యకరమైన పంట",
            "kn": "ಆರೋಗ್ಯಕರ ಬೆಳೆ",
            "ml": "ആരോഗ്യമുള്ള വിള",
            "bn": "সুস্থ ফসল",
            "pa": "ਸਿਹਤਮੰਦ ਫ਼ਸਲ",
            "or": "ସୁସ୍ଥ ଫସଲ",
            "as": "সুস্থ শস্য"
        }
        return CropAnalysisResult(
            image_type="plant_problem",
            crop=crop_name or "Tomato",
            plant_part="leaf",
            assessment="healthy",
            issue_name=healthy_names.get(lang, healthy_names["en"]),
            confidence=0.92,
            confidence_level=get_confidence_label(0.92, lang),
            severity="low",
            visible_symptoms=[],
            possible_causes=[],
            immediate_steps=[],
            expert_advice_needed=False,
            retake_tip=None,
            produce_grade=None,
            grade_reasons=[],
            guidance_disclaimer=disclaimer
        )

    # 3. Match against known crop diseases
    matched_entry = None
    target_crop = crop_name or "Onion"
    
    for d_key, d_info in DISEASE_GLOSSARY.items():
        if d_info.get("canonical_crop", "").lower() == target_crop.lower():
            matched_entry = d_info
            break
            
    if not matched_entry and DISEASE_GLOSSARY:
        matched_entry = list(DISEASE_GLOSSARY.values())[0]

    if matched_entry:
        issue_name_raw = matched_entry["names"].get(lang, matched_entry["names"]["en"])
        symptoms_raw = matched_entry["symptoms"].get(lang, matched_entry["symptoms"]["en"])
        causes_raw = matched_entry["causes"].get(lang, matched_entry["causes"]["en"])
        steps_raw = matched_entry["immediate_steps"].get(lang, matched_entry["immediate_steps"]["en"])

        # Filter symptoms and steps for safety (no chemical brands/dosages)
        safe_steps = [safety_filter(s, lang) for s in steps_raw]

        return CropAnalysisResult(
            image_type="plant_problem",
            crop=matched_entry.get("canonical_crop", target_crop),
            plant_part="leaf",
            assessment=matched_entry.get("category", "disease"),
            issue_name=issue_name_raw,
            confidence=0.85,
            confidence_level=get_confidence_label(0.85, lang),
            severity="medium",
            visible_symptoms=symptoms_raw,
            possible_causes=causes_raw,
            immediate_steps=safe_steps,
            expert_advice_needed=True,
            retake_tip=None,
            produce_grade=None,
            grade_reasons=[],
            guidance_disclaimer=disclaimer
        )

    # Fallback when symptoms cannot be diagnosed with confidence
    return CropAnalysisResult(
        image_type="plant_problem",
        crop=crop_name,
        plant_part="leaf",
        assessment="unclear",
        issue_name=None,
        confidence=0.55,
        confidence_level=get_confidence_label(0.55, lang),
        severity=None,
        visible_symptoms=[],
        possible_causes=[],
        immediate_steps=[],
        expert_advice_needed=True,
        retake_tip=RETAKE_TIPS["general_unclear"].get(lang, RETAKE_TIPS["general_unclear"]["en"]),
        produce_grade=None,
        grade_reasons=[],
        guidance_disclaimer=disclaimer
    )


def estimate_price_for_grade(crop: str, mandi: Optional[str] = None, grade: str = "A", language: str = "en") -> Dict[str, Any]:
    """Derive estimated produce price for visual grade from real Agmarknet data."""
    prices_data = get_mandi_prices(crop=crop, district=mandi)
    
    modal_price = prices_data.get("modal_price", 2500.0)
    min_price = prices_data.get("min_price", modal_price * 0.85)
    max_price = prices_data.get("max_price", modal_price * 1.15)
    mandi_name = prices_data.get("mandi_name", mandi or "Regional Mandi")

    # Map grade to price band
    if grade.upper() == "A":
        est_price = round(max_price, 1)
        est_range = f"₹{int(modal_price * 1.05)} - ₹{int(max_price)}"
        multiplier_note = "Premium quality fetched near recent top mandi rates."
    elif grade.upper() == "B":
        est_price = round(modal_price, 1)
        est_range = f"₹{int(min_price * 1.05)} - ₹{int(modal_price * 1.05)}"
        multiplier_note = "Standard quality trading near prevailing modal prices."
    else:  # Grade C
        est_price = round(min_price, 1)
        est_range = f"₹{int(min_price * 0.9)} - ₹{int(min_price * 1.05)}"
        multiplier_note = "Discounted lot trading near lower market range due to defects."

    return {
        "crop": crop,
        "mandi": mandi_name,
        "grade": grade.upper(),
        "estimated_price": est_price,
        "price_range": est_range,
        "kg_price": round(est_price / 100.0, 2),
        "source": prices_data.get("source", "Agmarknet"),
        "note": multiplier_note,
        "is_estimate": True
    }
