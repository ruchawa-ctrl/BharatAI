import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

PLACES_DATA = {
  "Nashik": {
    "canonical": "Nashik",
    "type": "district_and_mandi",
    "state": "Maharashtra",
    "lat": 19.9975,
    "lon": 73.7898,
    "names": {
      "en": "Nashik",
      "mr": "नाशिक",
      "hi": "नासिक",
      "gu": "નાસિક",
      "ta": "நாசிக்",
      "te": "నాసిక్",
      "kn": "ನಾಸಿಕ್",
      "ml": "നാസിക്",
      "bn": "নাসিক",
      "pa": "ਨਾਸਿਕ",
      "or": "ନାସିକ",
      "as": "নাচিক"
    }
  },
  "Lasalgaon": {
    "canonical": "Lasalgaon",
    "type": "mandi",
    "district": "Nashik",
    "state": "Maharashtra",
    "lat": 20.1472,
    "lon": 74.2253,
    "names": {
      "en": "Lasalgaon",
      "mr": "लासलगाव",
      "hi": "लासलगांव",
      "gu": "લાસલગાવ",
      "ta": "லாசல்காவ்",
      "te": "లాసల్‌గావ్",
      "kn": "ಲಾಸಲ್‌ಗಾಂವ್",
      "ml": "ലാസൽഗാവ്",
      "bn": "লাসালগাঁও",
      "pa": "ਲਾਸਲਗਾਂਵ",
      "or": "ଲାସଲଗାଓଁ",
      "as": "লাচালগাঁও"
    }
  },
  "Pune": {
    "canonical": "Pune",
    "type": "district_and_mandi",
    "state": "Maharashtra",
    "lat": 18.5204,
    "lon": 73.8567,
    "names": {
      "en": "Pune",
      "mr": "पुणे",
      "hi": "पुणे",
      "gu": "પુણે",
      "ta": "புனே",
      "te": "పూణే",
      "kn": "ಪುಣೆ",
      "ml": "പൂനെ",
      "bn": "পুনে",
      "pa": "ਪੁਣੇ",
      "or": "ପୁଣେ",
      "as": "পুনে"
    }
  },
  "Latur": {
    "canonical": "Latur",
    "type": "district_and_mandi",
    "state": "Maharashtra",
    "lat": 18.4088,
    "lon": 76.5604,
    "names": {
      "en": "Latur",
      "mr": "लातूर",
      "hi": "लातूर",
      "gu": "લાતૂર",
      "ta": "லாத்தூர்",
      "te": "లాతూర్",
      "kn": "ಲಾತೂರ್",
      "ml": "ലാത്തൂർ",
      "bn": "লাতুর",
      "pa": "ਲਾਤੂਰ",
      "or": "ଲାତୁର",
      "as": "লাতুৰ"
    }
  },
  "Solapur": {
    "canonical": "Solapur",
    "type": "district_and_mandi",
    "state": "Maharashtra",
    "lat": 17.6599,
    "lon": 75.9064,
    "names": {
      "en": "Solapur",
      "mr": "सोलापूर",
      "hi": "सोलापुर",
      "gu": "સોલાપુર",
      "ta": "சோலாப்பூர்",
      "te": "షోలాపూర్",
      "kn": "ಸೊಲ್ಲಾಪುರ",
      "ml": "ഷോലാപൂർ",
      "bn": "সোলাপুর",
      "pa": "ਸੋਲਾਪੁਰ",
      "or": "ସୋଲାପୁର",
      "as": "ছোলাপুৰ"
    }
  },
  "Ahmednagar": {
    "canonical": "Ahmednagar",
    "type": "district_and_mandi",
    "state": "Maharashtra",
    "lat": 19.0948,
    "lon": 74.7480,
    "names": {
      "en": "Ahmednagar",
      "mr": "अहमदनगर",
      "hi": "अहमदनगर",
      "gu": "અમદાવાદનગર",
      "ta": "அகமதுநகர்",
      "te": "అహ్మద్‌నగర్",
      "kn": "ಅಹಮದ್‌ನಗರ",
      "ml": "അഹമ്മദ്‌നഗർ",
      "bn": "আহমেদনগর",
      "pa": "ਅਹਿਮਦਨਗਰ",
      "or": "ଅହମ୍ମଦନଗର",
      "as": "আহমেদনাগৰ"
    }
  },
  "Nagpur": {
    "canonical": "Nagpur",
    "type": "district_and_mandi",
    "state": "Maharashtra",
    "lat": 21.1458,
    "lon": 79.0882,
    "names": {
      "en": "Nagpur",
      "mr": "नागपूर",
      "hi": "नागपुर",
      "gu": "નાગપુર",
      "ta": "நாக்பூர்",
      "te": "నాగ్‌పూర్",
      "kn": "ನಾಗಪುರ",
      "ml": "നാഗ്പൂർ",
      "bn": "নাগপুর",
      "pa": "ਨਾਗਪੁਰ",
      "or": "ନାଗପୁର",
      "as": "নাগপুৰ"
    }
  },
  "Rajkot": {
    "canonical": "Rajkot",
    "type": "district_and_mandi",
    "state": "Gujarat",
    "lat": 22.3039,
    "lon": 70.8022,
    "names": {
      "en": "Rajkot",
      "mr": "राजकोट",
      "hi": "राजकोट",
      "gu": "રાજકોટ",
      "ta": "ராஜ்கோட்",
      "te": "రాజ్‌కోట్",
      "kn": "ರಾಜ್‌ಕೋಟ್",
      "ml": "രാജ്കോട്ട്",
      "bn": "রাজকোট",
      "pa": "ਰਾਜਕੋਟ",
      "or": "ରାଜକୋଟ",
      "as": "ৰাজকোট"
    }
  },
  "Gondal": {
    "canonical": "Gondal",
    "type": "mandi",
    "district": "Rajkot",
    "state": "Gujarat",
    "lat": 21.9619,
    "lon": 70.7923,
    "names": {
      "en": "Gondal",
      "mr": "गोंडल",
      "hi": "गोंडल",
      "gu": "ગોંડલ",
      "ta": "கோண்டல்",
      "te": "గోండల్",
      "kn": "ಗೊಂಡಲ್",
      "ml": "ഗോണ്ടൽ",
      "bn": "গোন্ডাল",
      "pa": "ਗੋਂਡਲ",
      "or": "ଗୋଣ୍ଡାଲ",
      "as": "গোন্দাল"
    }
  },
  "Surat": {
    "canonical": "Surat",
    "type": "district_and_mandi",
    "state": "Gujarat",
    "lat": 21.1702,
    "lon": 72.8311,
    "names": {
      "en": "Surat",
      "mr": "सुरत",
      "hi": "सूरत",
      "gu": "સુરત",
      "ta": "சூரத்",
      "te": "సూరత్",
      "kn": "ಸೂರತ್",
      "ml": "സൂററ്റ്",
      "bn": "সুরাট",
      "pa": "ਸੂਰਤ",
      "or": "ସୁରଟ",
      "as": "চুৰাট"
    }
  },
  "Indore": {
    "canonical": "Indore",
    "type": "district_and_mandi",
    "state": "Madhya Pradesh",
    "lat": 22.7196,
    "lon": 75.8577,
    "names": {
      "en": "Indore",
      "mr": "इंदूर",
      "hi": "इंदौर",
      "gu": "ઇન્દોર",
      "ta": "இந்தூர்",
      "te": "ఇండోర్",
      "kn": "ಇಂದೋರ್",
      "ml": "ഇൻഡോർ",
      "bn": "ইন্দোর",
      "pa": "ਇੰਦੌਰ",
      "or": "ଇନ୍ଦୋର",
      "as": "ইন্দোৰ"
    }
  },
  "Ujjain": {
    "canonical": "Ujjain",
    "type": "district_and_mandi",
    "state": "Madhya Pradesh",
    "lat": 23.1765,
    "lon": 75.7885,
    "names": {
      "en": "Ujjain",
      "mr": "उज्जैन",
      "hi": "उज्जैन",
      "gu": "ઉજ્જૈન",
      "ta": "உஜ்ஜைன்",
      "te": "ఉజ్జయిని",
      "kn": "ಉಜ್ಜಯಿನಿ",
      "ml": "ഉജ്ജയിൻ",
      "bn": "উজ্জয়িনী",
      "pa": "ਉਜੈਨ",
      "or": "ଉଜ୍ଜୟିନୀ",
      "as": "উজ্বয়িনী"
    }
  },
  "Agra": {
    "canonical": "Agra",
    "type": "district_and_mandi",
    "state": "Uttar Pradesh",
    "lat": 27.1767,
    "lon": 78.0081,
    "names": {
      "en": "Agra",
      "mr": "आग्रा",
      "hi": "आगरा",
      "gu": "આગ્રા",
      "ta": "ஆக்ரா",
      "te": "ఆగ్రా",
      "kn": "ಆಗ್ರಾ",
      "ml": "ആഗ്ര",
      "bn": "আগ্রা",
      "pa": "ਆਗਰਾ",
      "or": "ଆଗ୍ରା",
      "as": "আগ্ৰা"
    }
  },
  "Khanna": {
    "canonical": "Khanna",
    "type": "mandi",
    "district": "Ludhiana",
    "state": "Punjab",
    "lat": 30.7071,
    "lon": 76.2168,
    "names": {
      "en": "Khanna",
      "mr": "खन्ना",
      "hi": "खन्ना",
      "gu": "ખન્ના",
      "ta": "கன்னா",
      "te": "ఖన్నా",
      "kn": "ಖನ್ನಾ",
      "ml": "ഖന്ന",
      "bn": "খান্না",
      "pa": "ਖੰਨਾ",
      "or": "ଖାନ୍ନା",
      "as": "খান্না"
    }
  },
  "Ludhiana": {
    "canonical": "Ludhiana",
    "type": "district_and_mandi",
    "state": "Punjab",
    "lat": 30.9010,
    "lon": 75.8573,
    "names": {
      "en": "Ludhiana",
      "mr": "लुधियाना",
      "hi": "लुधियाना",
      "gu": "લુધિયાણા",
      "ta": "லூதியானா",
      "te": "లూధియానా",
      "kn": "ಲುಧಿಯಾನ",
      "ml": "ലുധിയാന",
      "bn": "লুধিয়ানা",
      "pa": "ਲੁਧਿਆਣਾ",
      "or": "ଲୁଧିଆନା",
      "as": "লুধিয়ানা"
    }
  }
}

target_path = os.path.join(DATA_DIR, "places_localized.json")
with open(target_path, "w", encoding="utf-8") as f:
    json.dump(PLACES_DATA, f, ensure_ascii=False, indent=2)

print(f"Generated {target_path} with {len(PLACES_DATA)} localized places in all 12 languages.")
