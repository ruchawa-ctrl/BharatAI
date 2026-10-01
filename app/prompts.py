from typing import Dict

SYSTEM_PROMPT_TEMPLATE = """You are KisanSaathi (KisanSaathi / {native_brand_name}), an empathetic, trusted agricultural advisor for Indian farmers.

CORE DIRECTIVES:
1. STRICT LANGUAGE PURITY: Respond ONLY in {language_name} using its native script. Do not mix in English or Hindi words, except unavoidable proper nouns, which you must transliterate into the native script. Use simple, respectful everyday farmer vocabulary. Numbers and units must follow local conventions (e.g. ₹ प्रति क्विंटल / ₹ per quintal).
2. ZERO PRICE HALLUCINATION: Never invent or assume any market price. Every price cited MUST come strictly from verified tool outputs. You must explicitly display the market name, typical price (per quintal and per kg), date of arrival, and source. If data is older than 3 days or comes from historical fallback, state this transparently.
3. CONSERVATIVE PROJECTIONS: Never promise or guarantee future market prices. Use grounded phrases such as "based on the past 7 days".
4. ONE CLARIFYING QUESTION: If the user query is missing essential parameters (such as the crop name or the farmer's district/mandi), ask EXACTLY ONE polite, concise clarifying question in {language_name}.
5. RECOMMENDATION STRUCTURE:
   - Begin with the clear, direct recommendation badge: [SELL NOW / HOLD / SHIFT MANDI] in the native language.
   - Provide the top 2-3 grounded reasons (crop perishability, price trend, upcoming rainfall/weather, MSP gap).
   - Display the key numbers (typical price, 7-day trend %, MSP comparison).
6. ADVISORY DISCLAIMER: Conclude with a brief advisory note: This is market guidance, not a financial guarantee. Please confirm with your local mandi trader before dispatch.
7. STRICT BOUNDARIES: For off-topic questions (movies, politics, cricket, etc.), politely redirect the user back to crops, mandi prices, and weather. Do NOT provide pesticide chemical dosages or medical/human healthcare advice.
"""

CLARIFYING_PROMPTS = {
    "missing_location": {
        "en": "Which district or mandi are you asking for? Please mention your nearest market.",
        "mr": "तुम्ही कोणत्या जिल्ह्यातील किंवा कोणत्या मंडीतील भाव विचारत आहात? कृपया आपले शहर/मंडी सांगा.",
        "hi": "आप किस जिले या मंडी का भाव जानना चाहते हैं? कृपया अपना शहर या मंडी बताएं।",
        "gu": "તમે કયા જિલ્લા કે માર્કેટ યાર્ડનો ભાવ જાણવા માંગો છો? કૃપા કરીને જણાવો.",
        "ta": "நீங்கள் எந்த மாவட்டம் அல்லது சந்தை விலையை அறிய விரும்புகிறீர்கள்? தயவுசெய்து குறிப்பிடவும்.",
        "te": "మీరు ఏ జిల్లా లేదా మార్కెట్ యార్డ్ ధర తెలుసుకోవాలనుకుంటున్నారు? దయచేసి తెలపండి.",
        "kn": "ನೀವು ಯಾವ ಜಿಲ್ಲೆ ಅಥವಾ ಮಾರುಕಟ್ಟೆಯ ದರವನ್ನು ತಿಳಿಯಲು ಬಯಸುತ್ತೀರಿ? ದಯವಿಟ್ಟು ತಿಳಿಸಿ.",
        "ml": "ഏത് ജില്ലയിലെ അല്ലെങ്കിൽ മാർക്കറ്റിലെ വിലയാണ് അറിയേണ്ടത്? ദയവായി വ്യക്തമാക്കുക.",
        "bn": "আপনি কোন জেলা বা মন্ডির দর জানতে চান? দয়া করে আপনার নিকটবর্তী বাজারটি বলুন।",
        "pa": "ਤੁਸੀਂ ਕਿਹੜੇ ਜ਼ਿਲ੍ਹੇ ਜਾਂ ਮੰਡੀ ਦਾ ਭਾਅ ਜਾਣਨਾ ਚਾਹੁੰਦੇ ਹੋ? ਕਿਰਪਾ ਕਰਕੇ ਦੱਸੋ।",
        "or": "ଆପଣ କେଉଁ ଜିଲ୍ଲା କିମ୍ବା ମଣ୍ଡିର ଦର ଜାଣିବାକୁ ଚାହୁଁଛନ୍ତି? ଦୟାକରି ଜଣାନ୍ତୁ।",
        "as": "আপুনি কোনখন জিলা বা বজাৰৰ দৰ জানিব বিচাৰিছে? অনুগ্ৰহ কৰি জনাওক।"
    },
    "missing_crop": {
        "en": "Which crop or produce do you want to check? (e.g. Onion, Tomato, Wheat, Soybean)",
        "mr": "तुम्हाला कोणत्या पिकाचा भाव पाहायचा आहे? (उदा. कांदा, टोमॅटो, गहू, सोयाबीन)",
        "hi": "आप किस फसल का भाव जानना चाहते हैं? (जैसे: प्याज, टमाटर, गेहूं, सोयाबीन)",
        "gu": "તમે કયા પાકનો ભાવ જાણવા માંગો છો? (દા.ત. ડુંગળી, ટામેટાં, ઘઉં, કપાસ)",
        "ta": "நீங்கள் எந்த பயிரின் விலையை அறிய விரும்புகிறீர்கள்? (எ.கா. வெங்காயம், தக்காளி, கோதுமை)",
        "te": "మీరు ఏ పంట ధర తెలుసుకోవాలనుకుంటున్నారు? (ఉదా. ఉల్లి, టమోటా, పత్తి, గోధుమ)",
        "kn": "ನೀವು ಯಾವ ಬೆಳೆಯ ದರವನ್ನು ಪರಿಶೀಲಿಸಲು ಬಯಸುತ್ತೀರಿ? (ಉದಾ. ಈರುಳ್ಳಿ, ಟೊಮೆಟೊ, ಗೋಧಿ)",
        "ml": "ഏത് വിളയുടെ വിലയാണ് അറിയേണ്ടത്? (ഉദാ. ഉള്ളി, തക്കാളി, പച്ചക്കറികൾ)",
        "bn": "আপনি কোন ফসলের দর জানতে চান? (যেমন: আলু, পিঁয়াজ, ধান, গম)",
        "pa": "ਤੁਸੀਂ ਕਿਹੜੀ ਫ਼ਸਲ ਦਾ ਭਾਅ ਪਤਾ ਕਰਨਾ ਚਾਹੁੰਦੇ ਹੋ? (ਜਿਵੇਂ: ਕਣਕ, ਝੋਨਾ, ਆਲੂ, ਨਰਮਾ)",
        "or": "ଆପଣ କେଉଁ ଫସଲର ଦର ଜାଣିବାକୁ ଚାହୁଁଛନ୍ତି? (ଯଥା: ଧାନ, ପିଆଜ, ଗହମ, ଆଳୁ)",
        "as": "আপুনি কোনবিধ শস্যৰ দৰ জানিব বিচাৰিছে? (যেনে: ধান, আলু, ঘেঁহু, সৰিয়হ)"
    },
    "off_topic": {
        "en": "I can only assist with agriculture, mandi prices, sell/hold advisory, and weather. Please ask a farming-related question.",
        "mr": "माफ करा, मी फक्त शेती, मंडी भाव, पीक विक्री सल्ला आणि हवामानाबद्दल मदत करू शकतो. कृपया शेतीविषयक प्रश्न विचारा.",
        "hi": "क्षमा करें, मैं केवल कृषि, मंडी भाव, फसल बेचने की सलाह और मौसम की जानकारी दे सकता हूँ। कृपया खेती से जुड़ा प्रश्न पूछें।",
        "gu": "માફ કરશો, હું ફક્ત ખેતી, માર્કેટ યાર્ડના ભાવ અને હવામાન અંગે મદદ કરી શકું છું. કૃપા કરીને ખેતી સંબંધિત પ્રશ્ન પૂછો.",
        "ta": "மன்னிக்கவும், என்னால் விவசாயம், சந்தை விலை, பயிர் விற்பனை மற்றும் வானிலை சார்ந்த கேள்விகளுக்கு மட்டுமே உதவ முடியும்.",
        "te": "క్షమించండి, నేను వ్యవసాయం, మార్కెట్ ధరలు మరియు వాతావరణం గురించి మాత్రమే సహాయం చేయగలను. దయచేసి వ్యవసాయానికి సంబంధించిన ప్రశ్న అడగండి.",
        "kn": "ಕ್ಷಮಿಸಿ, ನಾನು ಕೃಷಿ, ಮಾರುಕಟ್ಟೆ ದರಗಳು ಮತ್ತು ಹವಾಮಾನಕ್ಕೆ ಸಂಬಂಧಿಸಿದ ಪ್ರಶ್ನೆಗಳಿಗೆ ಮಾತ್ರ ಉತ್ತರಿಸಬಲ್ಲೆ.",
        "ml": "ക്ഷമിക്കണം, കൃഷി, വിപണി വില, കാലാവസ്ഥ എന്നിവ സംബന്ധിച്ച വിവരങ്ങൾ മാത്രമേ ഞാൻ നൽകൂ.",
        "bn": "দুঃখিত, আমি শুধুমাত্র কৃষি, মন্ডির দর, ফসল বিক্রির পরামর্শ এবং আবহাওয়া সংক্রান্ত তথ্যে সহায়তা করতে পারি।",
        "pa": "ਮੁਆਫ਼ ਕਰਨਾ, ਮੈਂ ਸਿਰਫ਼ ਖੇਤੀਬਾੜੀ, ਮੰਡੀ ਭਾਅ ਅਤੇ ਮੌਸਮ ਬਾਰੇ ਜਾਣਕਾਰੀ ਦੇ ਸਕਦਾ ਹਾਂ।",
        "or": "କ୍ଷମା କରିବେ, ମୁଁ କେବଳ କୃଷି, ମଣ୍ଡି ଦର ଏବଂ ପାଣିପାଗ ସମ୍ପର୍କିତ ସୂଚନା ଦେଇପାରିବି।",
        "as": "ক্ষমা কৰিব, মই কেৱল কৃষি, বজাৰ দৰ আৰু বতৰ সম্পৰ্কীয় বিষয়তহে সহায় কৰিব পাৰোঁ।"
    }
}

LANGUAGE_NAMES = {
    "en": ("English", "Farmer's Friend"),
    "hi": ("Hindi", "किसान साथी"),
    "mr": ("Marathi", "शेतकरी मित्र"),
    "gu": ("Gujarati", "કિસાન સાથી"),
    "ta": ("Tamil", "விவசாயி நண்பன்"),
    "te": ("Telugu", "రైతు మిత్రుడు"),
    "kn": ("Kannada", "ರೈತ ಮಿತ್ರ"),
    "ml": ("Malayalam", "കർഷക മിത്രം"),
    "bn": ("Bengali", "কৃষক বন্ধু"),
    "pa": ("Punjabi", "ਕਿਸਾਨ ਸਾਥੀ"),
    "or": ("Odia", "କୃଷକ ସାଥୀ"),
    "as": ("Assamese", "কৃষক বন্ধু")
}


def get_system_prompt(lang: str = "mr") -> str:
    lang_name, native_brand = LANGUAGE_NAMES.get(lang, ("Marathi", "शेतकरी मित्र"))
    return SYSTEM_PROMPT_TEMPLATE.format(language_name=lang_name, native_brand_name=native_brand)


def get_clarifying_question(missing_field: str, language: str = "mr") -> str:
    lang = language if language in CLARIFYING_PROMPTS.get(missing_field, {}) else "mr"
    return CLARIFYING_PROMPTS.get(missing_field, {}).get(lang, CLARIFYING_PROMPTS.get(missing_field, {})["mr"])
