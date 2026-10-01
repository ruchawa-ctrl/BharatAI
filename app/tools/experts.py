"""KisanSaathi: Agricultural Expert Directory and Kisan Call Centre Locator
Provides official government agronomic contacts (KVKs and Kisan Call Centre 1800-180-1551).
"""

from typing import Dict, Any, Optional

# Verified Government Toll-Free Helpline
KISAN_CALL_CENTRE = {
    "toll_free": "1800-180-1551",
    "name": "Kisan Call Centre (भारत सरकार)",
    "timings": "6:00 AM - 10:00 PM (All 7 Days)",
    "languages": "All 22 Official Indian Languages"
}

# District-level Krishi Vigyan Kendra (KVK) Directory
KVK_DIRECTORY = {
    "nashik": {
        "kvk_name": "KVK YCMOU, Nashik",
        "district": "Nashik",
        "state": "Maharashtra",
        "phone": "0253-2230717",
        "address": "Yashwantrao Chavan Maharashtra Open University Campus, Dnyangangotri, Nashik - 422222"
    },
    "pune": {
        "kvk_name": "KVK Baramati, Pune",
        "district": "Pune",
        "state": "Maharashtra",
        "phone": "02112-255207",
        "address": "Agricultural Development Trust, Shardanagar, Baramati, Pune - 413115"
    },
    "latur": {
        "kvk_name": "KVK VNMKV, Latur",
        "district": "Latur",
        "state": "Maharashtra",
        "phone": "02382-243224",
        "address": "College of Agriculture Campus, Latur - 413512"
    },
    "solapur": {
        "kvk_name": "KVK Mohol, Solapur",
        "district": "Solapur",
        "state": "Maharashtra",
        "phone": "02189-255018",
        "address": "Dryland Agriculture Research Station, Mohol, Solapur - 413213"
    },
    "ahmednagar": {
        "kvk_name": "KVK Babhaleshwar, Ahmednagar",
        "district": "Ahmednagar",
        "state": "Maharashtra",
        "phone": "02422-252414",
        "address": "Pravara Rural Education Society, Babhaleshwar, Rahata - 413737"
    },
    "indore": {
        "kvk_name": "KVK Kasturbagram, Indore",
        "district": "Indore",
        "state": "Madhya Pradesh",
        "phone": "0731-2788118",
        "address": "Kasturbagram Rural Institute, Khandwa Road, Indore - 452020"
    },
    "ujjain": {
        "kvk_name": "KVK Ujjain",
        "district": "Ujjain",
        "state": "Madhya Pradesh",
        "phone": "0734-2511411",
        "address": "RVSKVV Agriculture Research Station, Dewas Road, Ujjain - 456010"
    },
    "agra": {
        "kvk_name": "KVK Bichpuri, Agra",
        "district": "Agra",
        "state": "Uttar Pradesh",
        "phone": "0562-2636440",
        "address": "R.B.S. College, Bichpuri Campus, Agra - 283105"
    },
    "kanpur": {
        "kvk_name": "KVK CSAUK, Kanpur",
        "district": "Kanpur",
        "state": "Uttar Pradesh",
        "phone": "0512-2534156",
        "address": "Chandra Shekhar Azad University of Agriculture & Technology, Kanpur - 208002"
    },
    "rajkot": {
        "kvk_name": "KVK Targhadia, Rajkot",
        "district": "Rajkot",
        "state": "Gujarat",
        "phone": "0281-2784242",
        "address": "Main Dry Farming Research Station, JAU, Targhadia, Rajkot - 360003"
    },
    "ludhiana": {
        "kvk_name": "KVK PAU, Ludhiana",
        "district": "Ludhiana",
        "state": "Punjab",
        "phone": "0161-2401960",
        "address": "Punjab Agricultural University Campus, Ferozepur Road, Ludhiana - 141004"
    },
    "madurai": {
        "kvk_name": "KVK AC&RI, Madurai",
        "district": "Madurai",
        "state": "Tamil Nadu",
        "phone": "0452-2422955",
        "address": "Agricultural College and Research Institute, TNAU, Othakadai, Madurai - 625104"
    },
    "warangal": {
        "kvk_name": "KVK Malyal, Warangal",
        "district": "Warangal",
        "state": "Telangana",
        "phone": "08719-240200",
        "address": "PJTSAU Regional Agricultural Research Station, Malyal, Mahabubabad - 506101"
    },
    "dharwad": {
        "kvk_name": "KVK UAS, Dharwad",
        "district": "Dharwad",
        "state": "Karnataka",
        "phone": "0836-2447494",
        "address": "University of Agricultural Sciences Campus, Dharwad - 580005"
    },
    "palakkad": {
        "kvk_name": "KVK Mele Pattambi, Palakkad",
        "district": "Palakkad",
        "state": "Kerala",
        "phone": "0466-2212279",
        "address": "Regional Agricultural Research Station, KAU, Mele Pattambi, Palakkad - 679306"
    },
    "burdwan": {
        "kvk_name": "KVK Budbud, Purba Bardhaman",
        "district": "Burdwan",
        "state": "West Bengal",
        "phone": "0343-2513663",
        "address": "ICAR-CRIJAF Research Complex, Budbud, Purba Bardhaman - 713403"
    },
    "cuttack": {
        "kvk_name": "KVK Santhapur, Cuttack",
        "district": "Cuttack",
        "state": "Odisha",
        "phone": "0671-2367757",
        "address": "ICAR-National Rice Research Institute (NRRI) Campus, Bidyadharpur, Cuttack - 753006"
    },
    "nagaon": {
        "kvk_name": "KVK Simaluguri, Nagaon",
        "district": "Nagaon",
        "state": "Assam",
        "phone": "03672-240200",
        "address": "Assam Agricultural University Centre, Simaluguri, Nagaon - 782001"
    }
}

LOCALIZED_OFFICE_LABELS = {
    "en": "Krishi Vigyan Kendra & Agriculture Department",
    "hi": "कृषि विज्ञान केंद्र एवं कृषि विभाग",
    "mr": "कृषी विज्ञान केंद्र आणि कृषी विभाग",
    "gu": "કૃષિ વિજ્ઞાન કેન્દ્ર અને કૃષિ વિભાગ",
    "ta": "வேளாண் அறிவியல் மையம் மற்றும் வேளாண் துறை",
    "te": "వ్యవసాయ విజ్ఞాన కేంద్రం మరియు వ్యవసాయ శాఖ",
    "kn": "ಕೃಷಿ ವಿಜ್ಞಾನ ಕೇಂದ್ರ ಮತ್ತು ಕೃಷಿ ಇಲಾಖೆ",
    "ml": "കൃഷി വിജ്ഞാൻ കേന്ദ്രവും കൃഷി വകുപ്പും",
    "bn": "কৃষি বিজ্ঞান কেন্দ্র ও কৃষি বিভাগ",
    "pa": "ਕ੍ਰਿਸ਼ੀ ਵਿਗਿਆਨ ਕੇਂਦਰ ਅਤੇ ਖੇਤੀਬਾੜੀ ਵਿਭਾਗ",
    "or": "କୃଷି ବିଜ୍ଞାନ କେନ୍ଦ୍ର ଏବଂ କୃଷି ବିଭାଗ",
    "as": "কৃষি বিজ্ঞান কেন্দ্ৰ আৰু কৃষি বিভাগ"
}

LOCALIZED_NOTE = {
    "en": "Contact your local Krishi Vigyan Kendra (KVK) or call the toll-free Kisan Call Centre for certified advice before applying treatments.",
    "hi": "रासायनिक उपचार लागू करने से पहले प्रमाणित सलाह के लिए अपने स्थानीय कृषि विज्ञान केंद्र (KVK) या टोल-फ्री किसान कॉल सेंटर से संपर्क करें।",
    "mr": "उपचार लागू करण्यापूर्वी अधिकृत सल्ल्यासाठी तुमच्या स्थानिक कृषी विज्ञान केंद्र (KVK) किंवा टोल-फ्री किसान कॉल सेंटरशी संपर्क साधा.",
    "gu": "સારવાર લાગુ કરતાં પહેલાં સત્તાવાર સલાહ માટે તમારા સ્થાનિક કૃષિ વિજ્ઞાન કેન્દ્ર (KVK) અથવા ટોલ-ફ્રી કિસાન કૉલ સેન્ટરનો સંપર્ક કરો.",
    "ta": "சிகிச்சைகளைப் பயன்படுத்துவதற்கு முன் சான்றளிக்கப்பட்ட ஆலோசனைக்கு உங்கள் உள்ளூர் வேளாண் அறிவியல் மையம் (KVK) அல்லது கட்டணமில்லா உழவர் அழைப்பு மையத்தைத் தொடர்பு கொள்ளவும்.",
    "te": "చికిత్సలను వర్తించే ముందు ధృవీకరించబడిన సలహా కోసం మీ స్థానిక కృషి విజ్ఞాన కేంద్రం (KVK) లేదా టోల్-ఫ్రీ కిసాన్ కాల్ సెంటర్‌ను సంప్రదించండి.",
    "kn": "ಚಿಕಿತ್ಸೆಗಳನ್ನು ಅನ್ವಯಿಸುವ ಮೊದಲು ಪ್ರಮಾಣೀಕೃತ ಸಲಹೆಗಾಗಿ ನಿಮ್ಮ ಸ್ಥಳೀಯ ಕೃಷಿ ವಿಜ್ಞಾನ ಕೇಂದ್ರ (KVK) ಅಥವಾ ಟೋಲ್-ಫ್ರೀ ಕಿಸಾನ್ ಕಾಲ್ ಸೆಂಟರ್ ಅನ್ನು ಸಂಪರ್ಕಿಸಿ.",
    "ml": "ചികിത്സകൾ നൽകുന്നതിന് മുമ്പ് സാക്ഷ്യപ്പെടുത്തിയ ഉപദേശത്തിനായി നിങ്ങളുടെ പ്രാദേശിക കൃഷി വിജ്ഞാൻ കേന്ദ്രവുമായോ (KVK) അല്ലെങ്കിൽ ടോൾ ഫ്രീ കിസാൻ കോൾ സെന്ററുമായോ ബന്ധപ്പെടുക.",
    "bn": "চিকিৎসা প্রয়োগের আগে প্রত্যয়িত পরামর্শের জন্য আপনার স্থানীয় কৃষি বিজ্ঞান কেন্দ্র (KVK) বা টোল-ফ্রি কিষাণ কল সেন্টারে যোগাযোগ করুন।",
    "pa": "ਇਲਾਜ ਲਾਗੂ ਕਰਨ ਤੋਂ ਪਹਿਲਾਂ ਪ੍ਰਮਾਣਿਤ ਸਲਾਹ ਲਈ ਆਪਣੇ ਸਥਾਨਕ ਕ੍ਰਿਸ਼ੀ ਵਿਗਿਆਨ ਕੇਂਦਰ (KVK) ਜਾਂ ਟੋਲ-ਫ੍ਰੀ ਕਿਸਾਨ ਕਾਲ ਸੈਂਟਰ ਨਾਲ ਸੰਪਰਕ ਕਰੋ।",
    "or": "ଚିକିତ୍ସା ପ୍ରୟୋଗ କରିବା ପୂର୍ବରୁ ପ୍ରମାଣିତ ପରାମର୍ଶ ପାଇଁ ଆପଣଙ୍କର ସ୍ଥାନୀୟ କୃଷି ବିଜ୍ଞାନ କେନ୍ଦ୍ର (KVK) କିମ୍ବା ଟୋଲ-ଫ୍ରି କିଷାନ କଲ୍ ସେଣ୍ଟର ସହିତ ଯୋଗାଯୋଗ କରନ୍ତୁ।",
    "as": "চিকিৎসা প্ৰয়োগ কৰাৰ আগতে প্ৰমাণিত পৰামৰ্শৰ বাবে আপোনাৰ স্থানীয় কৃষি বিজ্ঞান কেন্দ্ৰ (KVK) বা টোল-ফ্ৰী কিষাণ কল চেণ্টাৰৰ সৈতে যোগাযোগ কৰক।"
}


def find_expert_help(district: Optional[str] = None, state: Optional[str] = None, language: str = "en") -> Dict[str, Any]:
    """Return Kisan Call Centre details and nearest Krishi Vigyan Kendra."""
    lang = language.lower() if language and language.lower() in LOCALIZED_NOTE else "en"
    
    district_clean = district.lower().strip() if district else ""
    kvk_info = None
    
    for key, info in KVK_DIRECTORY.items():
        if key in district_clean or district_clean in key:
            kvk_info = info
            break
            
    if not kvk_info:
        # Default fallback to national / premier institute
        kvk_info = {
            "kvk_name": "Krishi Vigyan Kendra (ICAR / State Agri Dept)",
            "district": district.title() if district else "Local District",
            "state": state.title() if state else "India",
            "phone": "1800-180-1551",
            "address": "Nearest Block Agriculture Development Office / KVK Campus"
        }

    return {
        "toll_free": KISAN_CALL_CENTRE["toll_free"],
        "toll_free_name": KISAN_CALL_CENTRE["name"],
        "timings": KISAN_CALL_CENTRE["timings"],
        "kvk_name": kvk_info["kvk_name"],
        "district": kvk_info["district"],
        "office_title": LOCALIZED_OFFICE_LABELS.get(lang, LOCALIZED_OFFICE_LABELS["en"]),
        "phone": kvk_info["phone"],
        "address": kvk_info["address"],
        "advice_note": LOCALIZED_NOTE.get(lang, LOCALIZED_NOTE["en"])
    }
