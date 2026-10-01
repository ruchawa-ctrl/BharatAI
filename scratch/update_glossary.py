import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

CROPS_DATA = {
  "Onion": {
    "canonical": "Onion",
    "category": "vegetable",
    "perishability": "medium",
    "storable_days": 60,
    "aliases": {
      "en": ["onion", "onions", "red onion", "white onion"],
      "mr": ["कांदा", "कांद्याचा", "कांद्याचे", "कांद्याची", "कांदे", "kanda"],
      "hi": ["प्याज", "प्याज़", "कांदा", "pyaj", "pyaaj"],
      "gu": ["ડુંગળી", "કાંદા", "dungli"],
      "ta": ["வெங்காயம்", "vengayam"],
      "te": ["ఉల్లిపాయ", "ఉల్లి", "ullipaya", "ulli"],
      "kn": ["ಈರುಳ್ಳಿ", "eerulli"],
      "ml": ["ഉള്ളി", "സവാള", "ulli", "savala"],
      "bn": ["পিঁয়াজ", "পেঁয়াজ", "peyaj"],
      "pa": ["ਪਿਆਜ਼", "ਗੰਢਾ", "pyaj", "gandha"],
      "or": ["ପିଆଜ", "piaja"],
      "as": ["পিয়াঁজ", "piyaj"]
    }
  },
  "Tomato": {
    "canonical": "Tomato",
    "category": "vegetable",
    "perishability": "high",
    "storable_days": 4,
    "aliases": {
      "en": ["tomato", "tomatoes"],
      "mr": ["टोमॅटो", "टोमॅटोचे", "टोमॅटोचा", "tomato"],
      "hi": ["टमाटर", "tamatar", "tamaatar"],
      "gu": ["ટામેટાં", "ટમેટા", "tameta"],
      "ta": ["தக்காளி", "thakkali"],
      "te": ["టమోటా", "టమాట", "tamata", "tomato"],
      "kn": ["ಟೊಮೆಟೊ", "tomato"],
      "ml": ["തക്കാളി", "thakkali"],
      "bn": ["টমেটো", "টমেটো", "tomato"],
      "pa": ["ਟਮਾਟਰ", "tamatar"],
      "or": ["ଟମାଟୋ", "tomato"],
      "as": ["বিলাহী", "bilahi"]
    }
  },
  "Potato": {
    "canonical": "Potato",
    "category": "vegetable",
    "perishability": "medium",
    "storable_days": 90,
    "aliases": {
      "en": ["potato", "potatoes", "aloo"],
      "mr": ["बटाटा", "बटाटे", "बटाट्याचा", "batata"],
      "hi": ["आलू", "आलु", "aloo", "aalu"],
      "gu": ["બટાટા", "બટાકા", "bataka"],
      "ta": ["உருளைக்கிழங்கு", "urulaikizhangu"],
      "te": ["బంగాళాదుంప", "ఆలూ", "bangaladumpa", "aloo"],
      "kn": ["ಆಲೂಗಡ್ಡೆ", "aloogadde"],
      "ml": ["ഉരുളക്കിഴങ്ങ്", "urula kizhangu"],
      "bn": ["আলু", "alu"],
      "pa": ["ਆਲੂ", "aloo"],
      "or": ["ଆଳୁ", "alu"],
      "as": ["আলু", "alu"]
    }
  },
  "Wheat": {
    "canonical": "Wheat",
    "category": "cereal",
    "perishability": "low",
    "storable_days": 365,
    "aliases": {
      "en": ["wheat", "gehu", "kanak"],
      "mr": ["गहू", "गव्हाचा", "गव्हाचे", "gahu"],
      "hi": ["गेहूं", "गेहुं", "gehu", "gehun"],
      "gu": ["ઘઉં", "ghau"],
      "ta": ["கோதுமை", "gothumai"],
      "te": ["గోధుమలు", "గోధుమ", "godhumalu"],
      "kn": ["ಗೋಧಿ", "godhi"],
      "ml": ["ഗോതമ്പ്", "gothambu"],
      "bn": ["গম", "gom"],
      "pa": ["ਕਣਕ", "kanak"],
      "or": ["ଗହମ", "gahama"],
      "as": ["ঘেঁহু", "ghenhu"]
    }
  },
  "Soybean": {
    "canonical": "Soybean",
    "category": "oilseed",
    "perishability": "low",
    "storable_days": 240,
    "aliases": {
      "en": ["soybean", "soya", "soyabean"],
      "mr": ["सोयाबीन", "सोया", "soyabean"],
      "hi": ["सोयाबीन", "सोया", "soyabean"],
      "gu": ["સોયાબીન", "soyabean"],
      "ta": ["சோயாபீன்", "soya"],
      "te": ["సోయాబీన్", "సోయా", "soyabean"],
      "kn": ["ಸೋಯಾಬೀನ್", "soyabean"],
      "ml": ["സോയാബീൻ", "soyabean"],
      "bn": ["সয়াবিন", "soyabean"],
      "pa": ["ਸੋਇਆਬੀਨ", "soyabean"],
      "or": ["ସୋୟାବିନ୍", "soyabean"],
      "as": ["চয়াবিন", "soyabean"]
    }
  },
  "Cotton": {
    "canonical": "Cotton",
    "category": "fiber",
    "perishability": "low",
    "storable_days": 300,
    "aliases": {
      "en": ["cotton", "kapas", "raw cotton"],
      "mr": ["कापूस", "कपाशीचा", "kapus", "kapas"],
      "hi": ["कपास", "रूई", "kapas"],
      "gu": ["કપાસ", "રૂ", "kapas"],
      "ta": ["பருத்தி", "paruthi"],
      "te": ["పత్తి", "దూది", "patthi"],
      "kn": ["ಹತ್ತಿ", "hatti"],
      "ml": ["പരുത്തി", "paruthi"],
      "bn": ["তুলা", "কাপাস", "tula"],
      "pa": ["ਕਪਾਹ", "ਨਰਮਾ", "kapah", "narma"],
      "or": ["କପା", "kapa"],
      "as": ["কপাহ", "kopah"]
    }
  },
  "Tur": {
    "canonical": "Tur",
    "category": "pulse",
    "perishability": "low",
    "storable_days": 365,
    "aliases": {
      "en": ["tur", "arhar", "pigeon pea", "toor"],
      "mr": ["तूर", "तुरीचा", "तुरीचे", "tur"],
      "hi": ["अरहर", "तूर", "arhar", "tur"],
      "gu": ["તુવેર", "tuver"],
      "ta": ["துவரை", "துவரம் பருப்பு", "thuvarai"],
      "te": ["కందులు", "కందిపప్పు", "kandulu"],
      "kn": ["ತೊಗರಿ", "ತೊಗರಿಬೇಳೆ", "togari"],
      "ml": ["തുവരപ്പരിപ്പ്", "തുവര", "thuvara"],
      "bn": ["অড়হর", "arhar"],
      "pa": ["ਤੂਰ", "ਅਰਹਰ", "toor"],
      "or": ["ହରଡ଼", "harada"],
      "as": ["ৰহৰ", "rohor"]
    }
  },
  "Paddy": {
    "canonical": "Paddy",
    "category": "cereal",
    "perishability": "low",
    "storable_days": 365,
    "aliases": {
      "en": ["paddy", "rice", "dhan"],
      "mr": ["भात", "धान", "तांदूळ", "dhan", "bhat"],
      "hi": ["धान", "चावल", "dhan", "chawal"],
      "gu": ["ડાંગર", "ચોખા", "dangar"],
      "ta": ["நெல்", "அரிசி", "nel", "arisi"],
      "te": ["వరి", "ధాన్యం", "బియ్యం", "vari", "dhanyam"],
      "kn": ["ಭತ್ತ", "ಅಕ್ಕಿ", "bhatta", "akki"],
      "ml": ["നെല്ല്", "അരി", "nellu", "ari"],
      "bn": ["ধান", "চাল", "dhan", "chal"],
      "pa": ["ਝੋਨਾ", "ਚੌਲ", "jhona", "chawal"],
      "or": ["ଧାନ", "ଚାଉଳ", "dhana"],
      "as": ["ধান", "চাউল", "dhan"]
    }
  },
  "Maize": {
    "canonical": "Maize",
    "category": "cereal",
    "perishability": "low",
    "storable_days": 270,
    "aliases": {
      "en": ["maize", "corn", "makka"],
      "mr": ["मका", "मकाचे", "maka"],
      "hi": ["मक्का", "भुट्टा", "makka", "bhutta"],
      "gu": ["મકાઈ", "makai"],
      "ta": ["மக்காச்சோளம்", "makkacholam"],
      "te": ["మొక్కజొన్న", "mokkajonna"],
      "kn": ["ಮೆಕ್ಕೆಜೋಳ", "mekkejola"],
      "ml": ["ചോളം", "cholam"],
      "bn": ["ভুট্টা", "bhutta"],
      "pa": ["ਮੱਕੀ", "chhalli", "makki"],
      "or": ["ମକା", "maka"],
      "as": ["গোমধান", "ভুট্টা", "gomdhan"]
    }
  },
  "Gram": {
    "canonical": "Gram",
    "category": "pulse",
    "perishability": "low",
    "storable_days": 365,
    "aliases": {
      "en": ["gram", "chana", "chickpea"],
      "mr": ["हरभरा", "चना", "harbhara"],
      "hi": ["चना", "छोला", "chana"],
      "gu": ["ચણા", "chana"],
      "ta": ["கொண்டைக்கடலை", "கடலை", "kadalai"],
      "te": ["శనగలు", "శనగ", "senagalu"],
      "kn": ["ಕಡಲೆ", "kadale"],
      "ml": ["കടല", "kadala"],
      "bn": ["ছোলা", "chhola"],
      "pa": ["ਛੋਲੇ", "ਚਣੇ", "chhole"],
      "or": ["ବୁଟ", "ଚଣା", "buta"],
      "as": ["বুট", "বুঁট", "but"]
    }
  },
  "Mustard": {
    "canonical": "Mustard",
    "category": "oilseed",
    "perishability": "low",
    "storable_days": 300,
    "aliases": {
      "en": ["mustard", "sarson", "rai"],
      "mr": ["मोहरी", "राई", "mohari"],
      "hi": ["सरसों", "राई", "sarson"],
      "gu": ["રાઈ", "સરસવ", "rai"],
      "ta": ["கடுகு", "kadugu"],
      "te": ["ఆవాలు", "aavalu"],
      "kn": ["ಸಾಸಿವೆ", "sasive"],
      "ml": ["കടുക്", "kaduku"],
      "bn": ["সরিষা", "সর্ষে", "sorisha"],
      "pa": ["ਸਰ੍ਹੋਂ", "ਰਾਈ", "sarhon"],
      "or": ["ସୋରିଷ", "sorisa"],
      "as": ["সৰিয়হ", "soriyoh"]
    }
  },
  "Sugarcane": {
    "canonical": "Sugarcane",
    "category": "cash_crop",
    "perishability": "high",
    "storable_days": 2,
    "aliases": {
      "en": ["sugarcane", "cane", "ganna"],
      "mr": ["ऊस", "ऊसाचा", "us"],
      "hi": ["गन्ना", "ईख", "ganna"],
      "gu": ["શેરડી", "sherdi"],
      "ta": ["கரும்பு", "karumbu"],
      "te": ["చెరకు", "cheraku"],
      "kn": ["ಕಬ್ಬು", "kabbu"],
      "ml": ["കരിമ്പ്", "karimbu"],
      "bn": ["আখ", "ইক্ষু", "aakh"],
      "pa": ["ਗੰਨਾ", "ਕਮਾਦ", "ganna", "kamaad"],
      "or": ["ଆଖୁ", "akhu"],
      "as": ["কুঁহিয়াৰ", "kuhiyar"]
    }
  },
  "Chilli": {
    "canonical": "Chilli",
    "category": "spice",
    "perishability": "medium",
    "storable_days": 30,
    "aliases": {
      "en": ["chilli", "chili", "red chilli", "green chilli", "mirchi"],
      "mr": ["मिरची", "लाल मिरची", "mirchi"],
      "hi": ["मिर्च", "हरी मिर्च", "लाल मिर्च", "mirch"],
      "gu": ["મરચાં", "મરચું", "marcha"],
      "ta": ["மிளகாய்", "milagai"],
      "te": ["మిరపకాయ", "మిరప", "mirapakaya"],
      "kn": ["ಮೆಣಸಿನಕಾಯಿ", "menasinakayi"],
      "ml": ["പച്ചമുളക്", "മുളക്", "mulaku"],
      "bn": ["লঙ্কা", "মরিচ", "lonka"],
      "pa": ["ਮਿਰਚ", "ਹਰੀ ਮਿਰਚ", "mirch"],
      "or": ["ଲଙ୍କା", "lanka"],
      "as": ["জলকীয়া", "জ্বলা", "jolokiya"]
    }
  },
  "Groundnut": {
    "canonical": "Groundnut",
    "category": "oilseed",
    "perishability": "low",
    "storable_days": 180,
    "aliases": {
      "en": ["groundnut", "peanut", "mungfali"],
      "mr": ["भुईमूग", "शेंगदाणा", "bhuimug"],
      "hi": ["मूंगफली", "मूंगफली दाना", "mungfali"],
      "gu": ["મગફળી", "સીંગદાણા", "magfali"],
      "ta": ["நிலக்கடலை", "வேர்க்கடலை", "nilakadalai"],
      "te": ["వేరుశెనగ", "పల్లీలు", "verusenaga"],
      "kn": ["ಕಡಲೆಕಾಯಿ", "ನೆಲಗಡಲೆ", "kadalekayi"],
      "ml": ["നിലക്കടല", "കപ്പലണ്ടി", "nilakkadala"],
      "bn": ["চিনাবাদাম", "chinabadam"],
      "pa": ["ਮੂੰਗਫਲੀ", "moongphali"],
      "or": ["ଚିନାବାଦାମ", "chinabadama"],
      "as": ["বাদাম", "চীনা বাদাম", "badam"]
    }
  },
  "Garlic": {
    "canonical": "Garlic",
    "category": "spice",
    "perishability": "medium",
    "storable_days": 120,
    "aliases": {
      "en": ["garlic", "lahsun"],
      "mr": ["लसूण", "लसणाचा", "lasun"],
      "hi": ["लहसुन", "लहसून", "lahsun"],
      "gu": ["લસણ", "lasan"],
      "ta": ["பூண்டு", "poondu"],
      "te": ["వెల్లుల్లి", "vellulli"],
      "kn": ["ಬೆಳ್ಳುಳ್ಳಿ", "bellulli"],
      "ml": ["വെളുത്തുള്ളി", "veluthulli"],
      "bn": ["রসুন", "roshun"],
      "pa": ["ਲਸਣ", "lasun"],
      "or": ["ରସୁଣ", "rasuna"],
      "as": ["নহৰু", "nohoru"]
    }
  }
}

target_path = os.path.join(DATA_DIR, "crops_glossary.json")
with open(target_path, "w", encoding="utf-8") as f:
    json.dump(CROPS_DATA, f, ensure_ascii=False, indent=2)

print(f"Updated {target_path} with {len(CROPS_DATA)} crops in all 12 languages.")
