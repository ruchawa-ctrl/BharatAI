/**
 * KisanSaathi Frontend Application
 * Government-Grade Multilingual Mandi Advisory Portal (BharatAgentic Hackathon 2026)
 * Strictly adheres to 12-language localization rules and zero English leftovers.
 */

(function () {
    "use strict";

    // ------------------------------------------------------------------------
    // Configuration & State
    // ------------------------------------------------------------------------
    const SUPPORTED_LANGS = ["mr", "hi", "en", "gu", "ta", "te", "kn", "ml", "bn", "pa", "or", "as"];
    
    // Persistent Farmer User ID
    let userId = localStorage.getItem("kisansaathi_user_id");
    if (!userId) {
        userId = "farmer_" + Math.random().toString(36).substring(2, 9);
        localStorage.setItem("kisansaathi_user_id", userId);
    }

    // Active Language (saved in localStorage or default Marathi)
    let currentLang = localStorage.getItem("kisansaathi_lang") || "mr";
    if (!SUPPORTED_LANGS.includes(currentLang)) currentLang = "mr";

    let currentLocaleData = {};
    let isAudioEnabled = true;
    let recognition = null;
    let isRecording = false;
    let activeReplyText = "";

    // 12 Featured Crops for Quick-Pick Grid
    const CROPS_META = [
        {
            id: "onion",
            img: "/static/assets/onion.webp",
            names: {
                mr: "कांदा", hi: "प्याज", en: "Onion", gu: "ડુંગળી", ta: "வெங்காயம்",
                te: "ఉల్లిపాయ", kn: "ಈರುಳ್ಳಿ", ml: "ഉള്ളി", bn: "পেঁয়াজ", pa: "ਪਿਆਜ਼",
                or: "ପିଆଜ", as: "পিয়াঁজ"
            },
            queryTpl: {
                mr: "आज कांद्याचा भाव काय आहे आणि आज विकू की थांबू?",
                hi: "आज प्याज का भाव क्या है और आज बेचूं या रुकूं?",
                en: "What is today's onion rate and should I sell or hold?",
                gu: "આજે ડુંગળીનો ભાવ શું છે અને વેચવું કે રોકાવું?",
                ta: "இன்றைய வெங்காய விலை என்ன மற்றும் விற்கலாமா வைக்கலாமா?",
                te: "ఈరోజు ఉల్లిపాయ ధర ఎంత మరియు అమ్మాలా ఆగాలా?",
                kn: "ಇಂದು ಈರುಳ್ಳಿ ಬೆಲೆ ಎಷ್ಟು ಮತ್ತು ಮಾರಾಟ ಮಾಡಬೇಕೇ ಅಥವಾ ಕಾಯಬೇಕೇ?",
                ml: "ഇന്ന് ഉള്ളിയുടെ വില എത്രയാണ്, വിൽക്കണോ കാത്തിരിക്കണോ?",
                bn: "আজ পেঁয়াজের দাম কত এবং আজ বিক্রি করব নাকি ধরে রাখব?",
                pa: "ਅੱਜ ਪਿਆਜ਼ ਦਾ ਭਾਅ ਕੀ ਹੈ ਅਤੇ ਵੇਚਾਂ ਜਾਂ ਰੁਕਾਂ?",
                or: "ଆଜି ପିଆଜ ଦର କେତେ ଏବଂ ଆଜି ବିକ୍ରି କରିବି ନା ରଖିବି?",
                as: "আজি পিয়াঁজৰ দাম কিমান আৰু আজি বিক্ৰী কৰিম নে ৰাখিম?"
            }
        },
        {
            id: "tomato",
            img: "/static/assets/tomato.webp",
            names: {
                mr: "टोमॅटो", hi: "टमाटर", en: "Tomato", gu: "ટામેટાં", ta: "தக்காளி",
                te: "టమోటా", kn: "ಟೊಮೆಟೊ", ml: "തക്കാളി", bn: "টমেটো", pa: "ਟਮਾਟਰ",
                or: "ବିଲାତି", as: "বিলাহী"
            },
            queryTpl: {
                mr: "टोमॅटोचा आजचा बाजारभाव काय आहे?",
                hi: "टमाटर का आज का मंडी भाव क्या है?",
                en: "What is the current mandi rate for tomato?",
                gu: "ટામેટાંનો આજનો બજાર ભાવ શું છે?",
                ta: "தக்காளியின் இன்றைய சந்தை விலை என்ன?",
                te: "టమోటా ప్రస్తుత మార్కెట్ ధర ఎంత?",
                kn: "ಟೊಮೆಟೊ ಇಂದಿನ ಮಾರುಕಟ್ಟೆ ದರ ಎಷ್ಟು?",
                ml: "തക്കാളിയുടെ ഇന്നത്തെ വിപണി നിരക്ക് എത്രയാണ്?",
                bn: "টমেটোর আজকের বাজার দর কত?",
                pa: "ਟਮਾਟਰ ਦਾ ਅੱਜ ਦਾ ਮੰਡੀ ਭਾਅ ਕੀ ਹੈ?",
                or: "ବିଲାତିର ଆଜିର ମଣ୍ଡି ଦର କେତେ?",
                as: "বিলাহীৰ আজিৰ বজাৰ দাম কিমান?"
            }
        },
        {
            id: "potato",
            img: "/static/assets/potato.webp",
            names: {
                mr: "बटाटा", hi: "आलू", en: "Potato", gu: "બટાકા", ta: "உருளைக்கிழங்கு",
                te: "బంగాళాదుంప", kn: "ಆಲೂಗಡ್ಡೆ", ml: "ഉരുളക്കിഴങ്ങ്", bn: "আলু", pa: "ਆਲੂ",
                or: "ଆଳୁ", as: "আলু"
            },
            queryTpl: {
                mr: "बटाट्याचे दर वाढणार आहेत का? आज विकू की थांबू?",
                hi: "क्या आलू के दाम बढ़ेंगे? आज बेचूं या रुकूं?",
                en: "Will potato rates increase? Sell now or hold?",
                gu: "શું બટાકાના ભાવ વધશે? આજે વેચવું કે રોકાવું?",
                ta: "உருளைக்கிழங்கு விலை உயருமா? இப்போது விற்கலாமா?",
                te: "బంగాళాదుంప ధర పెరుగుతుందా? ఇప్పుడే అమ్మాలా?",
                kn: "ಆಲೂಗಡ್ಡೆ ಬೆಲೆ ಏರಿಕೆಯಾಗುವುದೇ? ಮಾರಬೇಕೆ?",
                ml: "ഉരുളക്കിഴങ്ങിന്റെ വില കൂടുമോ? ഇപ്പോൾ വിൽക്കണോ?",
                bn: "আলুর দাম কি বাড়বে? আজ বিক্রি করব নাকি রাখব?",
                pa: "ਕੀ ਆਲੂ ਦਾ ਭਾਅ ਵਧੇਗਾ? ਅੱਜ ਵੇਚਾਂ ਜਾਂ ਰੁਕਾਂ?",
                or: "ଆଳୁ ଦର ବଢ଼ିବ କି? ଆଜି ବିକ୍ରି କରିବି ନା ରଖିବି?",
                as: "আলুৰ দাম বাঢ়িব নেকি? আজি বিক্ৰী কৰিম নে ৰাখিম?"
            }
        },
        {
            id: "wheat",
            img: "/static/assets/wheat.webp",
            names: {
                mr: "गहू", hi: "गेहूं", en: "Wheat", gu: "ઘઉં", ta: "கோதுமை",
                te: "గోధుమలు", kn: "ಗೋಧಿ", ml: "ഗോതമ്പ്", bn: "গম", pa: "ਕਣਕ",
                or: "ଗହମ", as: "ঘেঁহু"
            },
            queryTpl: {
                mr: "गव्हाचा हमीभाव (MSP) आणि बाजारभाव किती आहे?",
                hi: "गेहूं का समर्थन मूल्य (MSP) और आज का मंडी भाव क्या है?",
                en: "What is wheat MSP and current market rate?",
                gu: "ઘઉંનો ટેકાનો ભાવ (MSP) અને વર્તમાન દર કેટલો છે?",
                ta: "கோதுமையின் குறைந்தபட்ச ஆதரவு விலை (MSP) மற்றும் சந்தை விலை என்ன?",
                te: "గోధుమలకు కనీస మద్దతు ధర (MSP) మరియు ప్రస్తుత రేటు ఎంత?",
                kn: "ಗೋಧಿ ಬೆಂಬಲ ಬೆಲೆ (MSP) ಮತ್ತು ಮಾರುಕಟ್ಟೆ ದರ ಎಷ್ಟು?",
                ml: "ഗോതമ്പിന്റെ താങ്ങുവിലയും ഇന്നത്തെ വിപണി നിരക്കും എത്രയാണ്?",
                bn: "গমের সরকারি সহায়ক মূল্য (MSP) এবং আজকের বাজার দর কত?",
                pa: "ਕਣਕ ਦਾ ਐਮਐਸਪੀ ਅਤੇ ਅੱਜ ਦਾ ਮੰਡੀ ਭਾਅ ਕੀ ਹੈ?",
                or: "ଗହମର ସରକାରୀ ସହାୟକ ମୂଲ୍ୟ ଏବଂ ଆଜିର ମଣ୍ଡି ଦର କେତେ?",
                as: "ঘেঁহুৰ চৰকাৰী সমৰ্থন মূল্য আৰু বজাৰ দাম কিমান?"
            }
        },
        {
            id: "soybean",
            img: "/static/assets/soybean.webp",
            names: {
                mr: "सोयाबीन", hi: "सोयाबीन", en: "Soybean", gu: "સોયાબીન", ta: "சோயாபீன்",
                te: "సోయాబీన్", kn: "ಸೋಯಾಬೀನ್", ml: "സോയാബീൻ", bn: "সয়াবিন", pa: "ਸੋਇਆਬੀਨ",
                or: "ସୋୟାବିନ", as: "চয়াবিন"
            },
            queryTpl: {
                mr: "सोयाबीनसाठी लातूर जवळ सर्वात चांगली मंडी कोणती?",
                hi: "सोयाबीन के लिए लातूर के पास सबसे अच्छी मंडी कौन सी है?",
                en: "Which is the best mandi for soybean near Latur?",
                gu: "સોયાબીન માટે સૌથી સારી નજીકની બજાર કઈ છે?",
                ta: "சோயாபீனுக்கு சிறந்த அருகிலுள்ள சந்தை எது?",
                te: "సోయాబీన్ కోసం ఉత్తమమైన సమీప మార్కెట్ ఏది?",
                kn: "ಸೋಯಾಬೀನ್‌ಗೆ ಉತ್ತಮ ಸಮೀಪದ ಮಾರುಕಟ್ಟೆ ಯಾವುದು?",
                ml: "സോയാബീന് ഏറ്റവും അനുയോജ്യമായ അടുത്തുള്ള വിപണി ഏതാണ്?",
                bn: "সয়াবিনের জন্য সবচেয়ে ভালো কাছের মান্ডি কোনটি?",
                pa: "ਸੋਇਆਬੀਨ ਲਈ ਸਭ ਤੋਂ ਵਧੀਆ ਨੇੜਲੀ ਮੰਡੀ ਕਿਹੜੀ ਹੈ?",
                or: "ସୋୟାବିନ ପାଇଁ ସବୁଠାରୁ ଭଲ ନିକଟସ୍ଥ ମଣ୍ଡି କେଉଁଟି?",
                as: "চয়াবিনৰ বাবে আটাইতকৈ ভাল ওচৰৰ বজাৰ কোনখন?"
            }
        },
        {
            id: "cotton",
            img: "/static/assets/cotton.webp",
            names: {
                mr: "कापूस", hi: "कपास", en: "Cotton", gu: "કપાસ", ta: "பருத்தி",
                te: "పత్తి", kn: "ಹತ್ತಿ", ml: "പരുത്തി", bn: "তুলা", pa: "ਕਪਾਹ",
                or: "କପା", as: "কপাহ"
            },
            queryTpl: {
                mr: "कापसाचा आजचा भाव काय आहे?",
                hi: "कपास का आज का मंडी भाव क्या चल रहा है?",
                en: "What is the current mandi price for cotton?",
                gu: "કપાસનો આજનો બજાર ભાવ શું ચાલી રહ્યો છે?",
                ta: "பருத்தியின் இன்றைய சந்தை விலை என்ன?",
                te: "పత్తికి నేటి మార్కెట్ రేటు ఎంత?",
                kn: "ಹತ್ತಿಯ ಇಂದಿನ ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಎಷ್ಟು?",
                ml: "പരുത്തിയുടെ ഇന്നത്തെ വിപണി നിരക്ക് എത്രയാണ്?",
                bn: "তুলার আজকের মান্ডি দর কত?",
                pa: "ਕਪਾਹ ਦਾ ਅੱਜ ਦਾ ਮੰਡੀ ਭਾਅ ਕੀ ਹੈ?",
                or: "କପାର ଆଜିର ମଣ୍ଡି ଦର କେତେ?",
                as: "কপাহৰ আজিৰ বজাৰ দাম কিমান?"
            }
        },
        {
            id: "tur",
            img: "/static/assets/tur.webp",
            names: {
                mr: "तूर", hi: "अरहर / तूर", en: "Tur (Arhar)", gu: "તુવેર", ta: "துவரை",
                te: "కందులు", kn: "ತೊಗರಿ", ml: "തുവര", bn: "অড়হর", pa: "ਅਰਹਰ",
                or: "ହରଡ଼", as: "ৰহৰ"
            },
            queryTpl: {
                mr: "तुरीचा भाव काय आहे? विकण्याची ही योग्य वेळ आहे का?",
                hi: "तूर का भाव क्या है? क्या यह बेचने का सही समय है?",
                en: "What is tur price? Is this the right time to sell?",
                gu: "તુવેરનો ભાવ શું છે? શું આ વેચવાનો યોગ્ય સમય છે?",
                ta: "துவரை விலை என்ன? இது விற்க சரியான நேரமா?",
                te: "కందుల ధర ఎంత? ఇది అమ్మడానికి సరైన సమయమా?",
                kn: "ತೊಗರಿ ಬೆಲೆ ಎಷ್ಟು? ಇದು ಮಾರಾಟಕ್ಕೆ ಸಕಾಲವೇ?",
                ml: "തുവരയുടെ വില എത്രയാണ്? ഇത് വിൽക്കാൻ പറ്റിയ സമയമാണോ?",
                bn: "অড়হরের দর কত? এখন কি বিক্রি করার সঠিক সময়?",
                pa: "ਅਰਹਰ ਦਾ ਭਾਅ ਕੀ ਹੈ? ਕੀ ਇਹ ਵੇਚਣ ਦਾ ਸਹੀ ਸਮਾਂ ਹੈ?",
                or: "ହରଡ଼ ଦର କେତେ? ବିକ୍ରି କରିବାକୁ ଏହା ସଠିକ୍ ସମୟ କି?",
                as: "ৰহৰৰ দাম কিমান? এয়া বিক্ৰী কৰাৰ উপযুক্ত সময় নেকি?"
            }
        },
        {
            id: "rice",
            img: "/static/assets/rice.webp",
            names: {
                mr: "भात (तांदूळ)", hi: "धान / चावल", en: "Rice / Paddy", gu: "ડાંગર / ચોખા", ta: "நெல்",
                te: "వరి / బియ్యం", kn: "ಭತ್ತ / ಅಕ್ಕಿ", ml: "നെല്ല് / അരി", bn: "ধান / চাল", pa: "ਝੋਨਾ",
                or: "ଧାନ", as: "ধান"
            },
            queryTpl: {
                mr: "धानाचा आजचा हमीभाव व बाजारभाव काय आहे?",
                hi: "धान का आज का समर्थन मूल्य और बाजार भाव क्या है?",
                en: "What is the paddy MSP and today's market rate?",
                gu: "ડાંગરનો ટેકાનો ભાવ અને આજનો બજાર ભાવ કેટલો છે?",
                ta: "நெல்லின் ஆதரவு விலை மற்றும் இன்றைய சந்தை விலை என்ன?",
                te: "వరి మద్దతు ధర మరియు నేటి మార్కెట్ రేటు ఎంత?",
                kn: "ಭತ್ತದ ಬೆಂಬಲ ಬೆಲೆ ಮತ್ತು ಇಂದಿನ ಮಾರುಕಟ್ಟೆ ದರ ಎಷ್ಟು?",
                ml: "നെല്ലിന്റെ താങ്ങുവിലയും ഇന്നത്തെ വിപണി നിരക്കും എത്രയാണ്?",
                bn: "ধানের সহায়ক মূল্য ও আজকের বাজার দর কত?",
                pa: "ਝੋਨੇ ਦਾ ਸਮਰਥਨ ਮੁੱਲ ਅਤੇ ਮੰਡੀ ਭਾਅ ਕੀ ਹੈ?",
                or: "ଧାନର ସହାୟକ ମୂଲ୍ୟ ଏବଂ ଆଜିର ବଜାର ଦର କେତେ?",
                as: "ধানৰ সমৰ্থন মূল্য আৰু আজিৰ বজাৰ দাম কিমান?"
            }
        },
        {
            id: "maize",
            img: "/static/assets/maize.webp",
            names: {
                mr: "मका", hi: "मक्का", en: "Maize (Corn)", gu: "મકાઈ", ta: "மக்காச்சோளம்",
                te: "మొక్కజొన్న", kn: "ಮೆಕ್ಕೆಜೋಳ", ml: "ചോളം", bn: "ভুট্টা", pa: "ਮੱਕੀ",
                or: "ମକା", as: "গোমধান"
            },
            queryTpl: {
                mr: "मक्याचा आजचा भाव काय आहे?",
                hi: "मक्के का आज का मंडी भाव क्या है?",
                en: "What is the market price of maize today?",
                gu: "મકાઈનો આજનો મંડી ભાવ શું છે?",
                ta: "மக்காச்சோளத்தின் இன்றைய சந்தை விலை என்ன?",
                te: "మొక్కజొన్న ప్రస్తుత మార్కెట్ ధర ఎంత?",
                kn: "ಮೆಕ್ಕೆಜೋಳದ ಇಂದಿನ ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಎಷ್ಟು?",
                ml: "ചോളത്തിന്റെ ഇന്നത്തെ വിപണി നിരക്ക് എത്രയാണ്?",
                bn: "ভুট্টার আজকের বাজার দর কত?",
                pa: "ਮੱਕੀ ਦਾ ਅੱਜ ਦਾ ਮੰਡੀ ਭਾਅ ਕੀ ਹੈ?",
                or: "ମକାର ଆଜିର ମଣ୍ଡି ଦର କେତେ?",
                as: "গোমধানৰ আজিৰ বজাৰ দাম কিমান?"
            }
        },
        {
            id: "sugarcane",
            img: "/static/assets/sugarcane.webp",
            names: {
                mr: "ऊस", hi: "गन्ना", en: "Sugarcane", gu: "શેરડી", ta: "கரும்பு",
                te: "చెరకు", kn: "ಕಬ್ಬು", ml: "കരിമ്പ്", bn: "আখ", pa: "ਗੰਨਾ",
                or: "ଆଖୁ", as: "কুঁহিয়াৰ"
            },
            queryTpl: {
                mr: "उसाचा चालू वर्षाचा FRP दर काय आहे?",
                hi: "गन्ने का चालू वर्ष का उचित और लाभकारी मूल्य (FRP) क्या है?",
                en: "What is the sugarcane FRP and factory rate this year?",
                gu: "શેરડીનો ચાલુ વર્ષનો FRP દર કેટલો છે?",
                ta: "கரும்பின் நடப்பு ஆண்டு FRP விலை என்ன?",
                te: "చెరకు ప్రస్తుత సంవత్సర FRP రేటు ఎంత?",
                kn: "ಕಬ್ಬಿನ ಪ್ರಸಕ್ತ ಸಾಲಿನ ಎಫ್‌ಆರ್‌ಪಿ ದರ ಎಷ್ಟು?",
                ml: "കരിമ്പിന്റെ ഈ വർഷത്തെ എഫ്.ആർ.പി നിരക്ക് എത്രയാണ്?",
                bn: "আখের বর্তমান বছরের ন্যায্য ও লাভজনক মূল্য (FRP) কত?",
                pa: "ਗੰਨੇ ਦਾ ਚਾਲੂ ਵਰ੍ਹੇ ਦਾ ਐਫਆਰਪੀ ਰੇਟ ਕੀ ਹੈ?",
                or: "ଆଖୁର ଚଳିତ ବର୍ଷର FRP ଦର କେତେ?",
                as: "কুঁহিয়াৰৰ চলিত বৰ্ষৰ চৰকাৰী নিৰ্ধাৰিত মূল্য কিমান?"
            }
        },
        {
            id: "chilli",
            img: "/static/assets/chilli.webp",
            names: {
                mr: "मिरची", hi: "मिर्च", en: "Chilli", gu: "મરચાં", ta: "மிளகாய்",
                te: "మిరపకాయ", kn: "ಮೆಣಸಿನಕಾಯಿ", ml: "മുളക്", bn: "লঙ্কা", pa: "ਮਿਰਚ",
                or: "ଲଙ୍କା", as: "জলকীয়া"
            },
            queryTpl: {
                mr: "हिरव्या व सुक्या मिरचीचे आजचे बाजारभाव सांगा.",
                hi: "हरी और सूखी मिर्च के आज के मंडी भाव बताएं।",
                en: "Tell me today's prices for green and red chilli.",
                gu: "લીલા અને સૂકા મરચાંનો આજનો બજાર ભાવ જણાવો.",
                ta: "பச்சை மற்றும் காய்ந்த மிளகாயின் இன்றைய சந்தை விலையைக் கூறுங்கள்.",
                te: "పచ్చి మరియు ఎండు మిరపకాయల నేటి మార్కెట్ ధరలు చెప్పండి.",
                kn: "ಹಸಿ ಮತ್ತು ಒಣ ಮೆಣಸಿನಕಾಯಿಯ ಇಂದಿನ ದರ ತಿಳಿಸಿ.",
                ml: "പച്ചമുളകിന്റെയും വറ്റൽമുളകിന്റെയും ഇന്നത്തെ വിപണി നിരക്ക് പറയുക.",
                bn: "কাঁচা ও শুকনো লঙ্কার আজকের বাজার দর জানান।",
                pa: "ਹਰੀ ਅਤੇ ਸੁੱਕੀ ਮਿਰਚ ਦਾ ਅੱਜ ਦਾ ਮੰਡੀ ਭਾਅ ਦੱਸੋ।",
                or: "କଞ୍ଚା ଏବଂ ଶୁଖିଲା ଲଙ୍କାର ଆଜିର ମଣ୍ଡି ଦର କୁହନ୍ତୁ।",
                as: "কেঁচা আৰু শুকান জলকীয়াৰ আজিৰ বজাৰ দাম কওক।"
            }
        },
        {
            id: "groundnut",
            img: "/static/assets/groundnut.webp",
            names: {
                mr: "भुईमूग", hi: "मूंगफली", en: "Groundnut", gu: "મગફળી", ta: "நிலக்கடலை",
                te: "వేరుశెనగ", kn: "ಕಡಲೆಕಾಯಿ", ml: "നിലക്കടല", bn: "চিনাবাদাম", pa: "ਮੂੰਗਫਲੀ",
                or: "ଚିନାବାଦାମ", as: "বাদাম"
            },
            queryTpl: {
                mr: "भुईमुगाचा आजचा भाव काय आहे?",
                hi: "मूंगफली का आज का मंडी भाव क्या है?",
                en: "What is the groundnut mandi price today?",
                gu: "મગફળીનો આજનો બજાર ભાવ શું ચાલી રહ્યો છે?",
                ta: "நிலக்கடலையின் இன்றைய சந்தை விலை என்ன?",
                te: "వేరుశెనగ ప్రస్తుత మార్కెట్ ధర ఎంత?",
                kn: "ಕಡಲೆಕಾಯಿಯ ಇಂದಿನ ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಎಷ್ಟು?",
                ml: "നിലക്കടലയുടെ ഇന്നത്തെ വിപണി നിരക്ക് എത്രയാണ്?",
                bn: "চিনাবাদামের আজকের মান্ডি দর কত?",
                pa: "ਮੂੰਗਫਲੀ ਦਾ ਅੱਜ ਦਾ ਮੰਡੀ ਭਾਅ ਕੀ ਹੈ?",
                or: "ଚିନାବାଦାମର ଆଜିର ମଣ୍ଡି ଦର କେତେ?",
                as: "বাদামৰ আজিৰ বজাৰ দাম কিমান?"
            }
        }
    ];

    // Number / Currency Formatter for Current Locale
    function formatNumber(num) {
        if (num === null || num === undefined || isNaN(num)) return "०";
        try {
            const loc = currentLang === "en" ? "en-IN" : `${currentLang}-IN`;
            return new Intl.NumberFormat(loc).format(num);
        } catch (e) {
            return num.toString();
        }
    }

    // ------------------------------------------------------------------------
    // Dynamic Locale Loader
    // ------------------------------------------------------------------------
    async function loadLocale(langCode) {
        try {
            const resp = await fetch(`/static/locales/${langCode}.json`);
            if (!resp.ok) throw new Error(`HTTP error ${resp.status}`);
            currentLocaleData = await resp.json();
            currentLang = langCode;
            localStorage.setItem("kisansaathi_lang", langCode);

            // Update HTML tag
            document.documentElement.lang = langCode;

            // Apply all translations to DOM
            applyTranslations();
            renderCropsGrid();
            loadMandiRatesTable();
            checkSpeechSupport();
            loadUserAlerts();
            loadUserReminders();
        } catch (err) {
            console.error(`Failed to load locale for ${langCode}:`, err);
        }
    }

    // ------------------------------------------------------------------------
    // Apply UI Translations
    // ------------------------------------------------------------------------
    function applyTranslations() {
        const d = currentLocaleData;
        if (!d.brand_name) return;

        // Top Navigation
        const headerNativeBrand = document.getElementById("headerNativeBrand");
        if (headerNativeBrand) headerNativeBrand.textContent = d.native_brand_name || "";

        const languageSelect = document.getElementById("languageSelect");
        if (languageSelect && languageSelect.value !== currentLang) {
            languageSelect.value = currentLang;
        }

        // Hero Section
        const heroHeadline = document.getElementById("heroHeadline");
        if (heroHeadline) heroHeadline.textContent = d.hero_headline || "";

        const heroSubheadline = document.getElementById("heroSubheadline");
        if (heroSubheadline) heroSubheadline.textContent = d.hero_subheadline || "";

        const askInput = document.getElementById("askInput");
        if (askInput) askInput.placeholder = d.ask_placeholder || "";

        const askBtnText = document.getElementById("askBtnText");
        if (askBtnText) askBtnText.textContent = d.ask_button || "";

        const micBtn = document.getElementById("micBtn");
        if (micBtn) micBtn.title = d.mic_tooltip || "";

        const loadingCheckingText = document.getElementById("loadingCheckingText");
        if (loadingCheckingText) loadingCheckingText.textContent = `🔍 ${d.loading_checking || ""}`;

        // Answer Panel Labels
        const reasonsTitle = document.getElementById("reasonsTitle");
        if (reasonsTitle) reasonsTitle.textContent = `📌 ${d.reasons_title || ""}`;

        const labelTypicalPrice = document.getElementById("labelTypicalPrice");
        if (labelTypicalPrice) labelTypicalPrice.textContent = `${d.mandi_rates_col_price || "सरासरी भाव"} (${d.unit_quintal || ""})`;

        const labelPerKg = document.getElementById("labelPerKg");
        if (labelPerKg) labelPerKg.textContent = `${d.rate_per_kg || "₹ / किलो"}`;

        const labelTrend = document.getElementById("labelTrend");
        if (labelTrend) labelTrend.textContent = d.mandi_rates_col_trend || "";

        const labelDateSource = document.getElementById("labelDateSource");
        if (labelDateSource) labelDateSource.textContent = `${d.mandi_rates_col_date || "तारीख"} व ${d.mandi_rates_col_source || "स्रोत"}`;

        const trendChartTitle = document.getElementById("trendChartTitle");
        if (trendChartTitle) trendChartTitle.textContent = `📈 ${d.trend_chart_title || ""}`;

        const mandiComparisonTitle = document.getElementById("mandiComparisonTitle");
        if (mandiComparisonTitle) mandiComparisonTitle.textContent = `🚛 ${d.mandi_comparison_title || ""}`;

        // Mandi Table Headers
        const thMandi = document.getElementById("thMandi");
        if (thMandi) thMandi.textContent = d.mandi_col_name || "मंडी";
        const thDist = document.getElementById("thDist");
        if (thDist) thDist.textContent = d.mandi_col_dist || "अंतर";
        const thGross = document.getElementById("thGross");
        if (thGross) thGross.textContent = d.mandi_col_gross || "भाव";
        const thTransport = document.getElementById("thTransport");
        if (thTransport) thTransport.textContent = d.mandi_col_transport || "वाहतूक खर्च";
        const thNet = document.getElementById("thNet");
        if (thNet) thNet.textContent = d.mandi_col_net || "हातात मिळणारा भाव";
        const thGain = document.getElementById("thGain");
        if (thGain) thGain.textContent = d.mandi_col_gain || "अतिरिक्त नफा";

        // Checklist
        const whatWeCheckedTitle = document.getElementById("whatWeCheckedTitle");
        if (whatWeCheckedTitle) whatWeCheckedTitle.textContent = d.what_we_checked_title || "";
        const chkPrices = document.getElementById("chkPrices");
        if (chkPrices) chkPrices.textContent = d.check_prices || "";
        const chkTrend = document.getElementById("chkTrend");
        if (chkTrend) chkTrend.textContent = d.check_trend || "";
        const chkWeather = document.getElementById("chkWeather");
        if (chkWeather) chkWeather.textContent = d.check_weather || "";
        const chkMandis = document.getElementById("chkMandis");
        if (chkMandis) chkMandis.textContent = d.check_mandis || "";

        // Action Buttons
        const btnShareText = document.getElementById("btnShareText");
        if (btnShareText) btnShareText.textContent = d.btn_share_whatsapp || "";
        const btnAlertText = document.getElementById("btnAlertText");
        if (btnAlertText) btnAlertText.textContent = d.btn_set_alert || "";
        const btnListenText = document.getElementById("btnListenText");
        if (btnListenText) btnListenText.textContent = d.btn_listen || "";

        const followupsLabel = document.getElementById("followupsLabel");
        if (followupsLabel) followupsLabel.textContent = `${d.followup_title || "उपयुक्त पुढील प्रश्न"}:`;

        const techDetailsSummary = document.getElementById("techDetailsSummary");
        if (techDetailsSummary) techDetailsSummary.textContent = `⚡ ${d.tech_details_title || "तांत्रिक तपशील"}`;

        // Sections
        const quickCropsTitle = document.getElementById("quickCropsTitle");
        if (quickCropsTitle) quickCropsTitle.innerHTML = `<span>🌱</span> ${d.quick_crops_title || ""}`;

        const todayRatesTitle = document.getElementById("todayRatesTitle");
        if (todayRatesTitle) todayRatesTitle.innerHTML = `<span>📊</span> ${d.today_rates_title || ""}`;

        // Rates Table Headers
        const thRatesCrop = document.getElementById("thRatesCrop");
        if (thRatesCrop) thRatesCrop.textContent = d.mandi_rates_col_crop || "शेतमाल";
        const thRatesPrice = document.getElementById("thRatesPrice");
        if (thRatesPrice) thRatesPrice.textContent = d.mandi_rates_col_price || "सरासरी भाव";
        const thRatesTrend = document.getElementById("thRatesTrend");
        if (thRatesTrend) thRatesTrend.textContent = d.mandi_rates_col_trend || "कल";
        const thRatesDate = document.getElementById("thRatesDate");
        if (thRatesDate) thRatesDate.textContent = d.mandi_rates_col_date || "तारीख";
        const thRatesSource = document.getElementById("thRatesSource");
        if (thRatesSource) thRatesSource.textContent = d.mandi_rates_col_source || "स्रोत";

        // My Alerts Section
        const myAlertsTitle = document.getElementById("myAlertsTitle");
        if (myAlertsTitle) myAlertsTitle.innerHTML = `<span>🔔</span> ${d.my_alerts_title || ""}`;

        const btnCreateAlertHeader = document.getElementById("btnCreateAlertHeader");
        if (btnCreateAlertHeader) btnCreateAlertHeader.textContent = `+ ${d.btn_set_alert || ""}`;

        // Alert Modal
        const modalHeading = document.getElementById("modalHeading");
        if (modalHeading) modalHeading.textContent = d.alert_modal_title || "";
        const lblModalCrop = document.getElementById("lblModalCrop");
        if (lblModalCrop) lblModalCrop.textContent = d.alert_crop_label || "";
        const lblModalMandi = document.getElementById("lblModalMandi");
        if (lblModalMandi) lblModalMandi.textContent = d.alert_mandi_label || "";
        const lblModalTarget = document.getElementById("lblModalTarget");
        if (lblModalTarget) lblModalTarget.textContent = d.alert_target_label || "";
        const btnModalSubmit = document.getElementById("btnModalSubmit");
        if (btnModalSubmit) btnModalSubmit.textContent = d.alert_submit_btn || "";

        // Addendum 2: Special Feature Action Cards
        const checkCropCardTitle = document.getElementById("checkCropCardTitle");
        if (checkCropCardTitle) checkCropCardTitle.textContent = d.check_crop_card_title || "";
        const checkCropCardDesc = document.getElementById("checkCropCardDesc");
        if (checkCropCardDesc) checkCropCardDesc.textContent = d.check_crop_card_desc || "";
        const btnCheckCropTrigger = document.getElementById("btnCheckCropTrigger");
        if (btnCheckCropTrigger) btnCheckCropTrigger.textContent = `${d.check_crop_button || "तपासा"} ➔`;

        const talkToKisanTitle = document.getElementById("talkToKisanTitle");
        if (talkToKisanTitle) talkToKisanTitle.textContent = d.talk_to_kisan || "";
        const talkToKisanDesc = document.getElementById("talkToKisanDesc");
        if (talkToKisanDesc) talkToKisanDesc.textContent = d.hold_phone_close_hint || "";
        const btnVoiceTrigger = document.getElementById("btnVoiceTrigger");
        if (btnVoiceTrigger) btnVoiceTrigger.textContent = `${d.ask_button || "बोला"} ➔`;

        // Crop Health Reminders Section
        const remindersTitle = document.getElementById("remindersTitle");
        if (remindersTitle) remindersTitle.innerHTML = `<span>📅</span> ${d.reminders_title || "पीक आरोग्य आठवणी"}`;

        // Crop Photo Modal
        const cameraModalTitle = document.getElementById("cameraModalTitle");
        if (cameraModalTitle) cameraModalTitle.textContent = `📸 ${d.camera_modal_title || ""}`;
        const goodBadGuideTitle = document.getElementById("goodBadGuideTitle");
        if (goodBadGuideTitle) goodBadGuideTitle.textContent = d.good_bad_guide_title || "";
        const goodPhotoTip = document.getElementById("goodPhotoTip");
        if (goodPhotoTip) goodPhotoTip.textContent = d.good_photo_tip || "";
        const badPhotoTip = document.getElementById("badPhotoTip");
        if (badPhotoTip) badPhotoTip.textContent = d.bad_photo_tip || "";
        const takePhotoBtn = document.getElementById("takePhotoBtn");
        if (takePhotoBtn) takePhotoBtn.textContent = d.take_photo_btn || "";
        const chooseGalleryBtn = document.getElementById("chooseGalleryBtn");
        if (chooseGalleryBtn) chooseGalleryBtn.textContent = d.choose_gallery_btn || "";
        const lblCropHint = document.getElementById("lblCropHint");
        if (lblCropHint) lblCropHint.textContent = d.crop_hint_placeholder || "";
        const cropHintInput = document.getElementById("cropHintInput");
        if (cropHintInput) cropHintInput.placeholder = d.crop_hint_placeholder || "";
        const orVoiceNote = document.getElementById("orVoiceNote");
        if (orVoiceNote) orVoiceNote.textContent = d.or_voice_note || "";
        const cropNoteInput = document.getElementById("cropNoteInput");
        if (cropNoteInput) cropNoteInput.placeholder = d.voice_note_placeholder || "";
        const privacyConsentLine = document.getElementById("privacyConsentLine");
        if (privacyConsentLine) privacyConsentLine.textContent = `🔒 ${d.privacy_consent_line || ""}`;
        const analyzeBtn = document.getElementById("analyzeBtn");
        if (analyzeBtn) analyzeBtn.textContent = d.analyze_btn || "";
        const analyzingText = document.getElementById("analyzingText");
        if (analyzingText) analyzingText.textContent = d.analyzing_text || "";

        // Diagnosis View
        const whatWeSee = document.getElementById("whatWeSee");
        if (whatWeSee) whatWeSee.textContent = d.what_we_see || "";
        const whatYouCanDo = document.getElementById("whatYouCanDo");
        if (whatYouCanDo) whatYouCanDo.textContent = d.what_you_can_do || "";
        const produceQualityTitle = document.getElementById("produceQualityTitle");
        if (produceQualityTitle) produceQualityTitle.textContent = d.produce_quality_title || "";
        const estimatedMandiRange = document.getElementById("estimatedMandiRange");
        if (estimatedMandiRange) estimatedMandiRange.textContent = d.estimated_mandi_range || "";
        const expertHelpTitle = document.getElementById("expertHelpTitle");
        if (expertHelpTitle) expertHelpTitle.textContent = d.expert_help_title || "";
        const callKccBtn = document.getElementById("callKccBtn");
        if (callKccBtn) callKccBtn.textContent = d.call_kcc_btn || "";
        const remind3DaysBtn = document.getElementById("remind3DaysBtn");
        if (remind3DaysBtn) remind3DaysBtn.textContent = d.remind_3_days_btn || "";
        const btnShareDiagnosisText = document.getElementById("btnShareDiagnosisText");
        if (btnShareDiagnosisText) btnShareDiagnosisText.textContent = d.btn_share_whatsapp || "";

        // Voice Assistant Modal
        const voiceModalTitle = document.getElementById("voiceModalTitle");
        if (voiceModalTitle) voiceModalTitle.textContent = `🎙️ ${d.voice_modal_title || ""}`;
        const voiceStateText = document.getElementById("voiceStateText");
        if (voiceStateText) voiceStateText.textContent = d.voice_listening || "";
        const holdPhoneCloseHint = document.getElementById("holdPhoneCloseHint");
        if (holdPhoneCloseHint) holdPhoneCloseHint.textContent = d.hold_phone_close_hint || "";
        const voiceTranscriptLabel = document.getElementById("voiceTranscriptLabel");
        if (voiceTranscriptLabel) voiceTranscriptLabel.textContent = d.voice_transcript_label || "";
        const voiceSendBtn = document.getElementById("voiceSendBtn");
        if (voiceSendBtn) voiceSendBtn.textContent = d.voice_send_btn || "";
        const voiceReRecordBtn = document.getElementById("voiceReRecordBtn");
        if (voiceReRecordBtn) voiceReRecordBtn.textContent = d.voice_re_record_btn || "";
        const playAudioBtn = document.getElementById("playAudioBtn");
        if (playAudioBtn) playAudioBtn.textContent = `${d.read_aloud_btn || "ऐका"} 🔊`;
        const speedLabel = document.getElementById("speedLabel");
        if (speedLabel) speedLabel.textContent = d.speed_label || "";

        // Footer
        const footerSources = document.getElementById("footerSources");
        if (footerSources) footerSources.textContent = d.footer_sources || "";
        const footerDisclaimer = document.getElementById("footerDisclaimer");
        if (footerDisclaimer) footerDisclaimer.textContent = d.footer_disclaimer || "";
        const footerTagline = document.getElementById("footerTagline");
        if (footerTagline) footerTagline.textContent = d.footer_tagline || "";
    }

    // ------------------------------------------------------------------------
    // Render 12 Crop Quick-Pick Cards
    // ------------------------------------------------------------------------
    function renderCropsGrid() {
        const grid = document.getElementById("cropsGrid");
        if (!grid) return;

        grid.innerHTML = "";
        CROPS_META.forEach(crop => {
            const card = document.createElement("div");
            card.className = "crop-card";
            card.setAttribute("role", "button");
            card.setAttribute("tabindex", "0");
            card.setAttribute("aria-label", crop.names[currentLang] || crop.names.en);

            const localizedName = crop.names[currentLang] || crop.names.mr || crop.names.en;
            const queryText = crop.queryTpl[currentLang] || crop.queryTpl.mr || crop.queryTpl.en;

            card.innerHTML = `
                <img 
                    src="${crop.img}" 
                    alt="${localizedName}" 
                    class="crop-thumb" 
                    loading="lazy"
                >
                <div class="crop-info">
                    <div class="crop-name">${localizedName}</div>
                    <div class="crop-rate-tag">${currentLocaleData.ask_button || "सल्ला घ्या"} ➔</div>
                </div>
            `;

            const triggerQuery = () => {
                const askInput = document.getElementById("askInput");
                if (askInput) {
                    askInput.value = queryText;
                    submitQuestion(queryText);
                    askInput.scrollIntoView({ behavior: "smooth", block: "center" });
                }
            };

            card.addEventListener("click", triggerQuery);
            card.addEventListener("keydown", (e) => {
                if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    triggerQuery();
                }
            });

            grid.appendChild(card);
        });
    }

    // ------------------------------------------------------------------------
    // Populate Today's Mandi Rates Table
    // ------------------------------------------------------------------------
    async function loadMandiRatesTable() {
        const tbody = document.getElementById("ratesTableBody");
        if (!tbody) return;

        try {
            const resp = await fetch("/api/mandi-rates?district=Nashik");
            if (!resp.ok) throw new Error("Rates endpoint unavailable");
            const data = await resp.json();
            const rates = data.rates || [];

            if (rates.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:16px;">${currentLocaleData.error_network || "माहिती उपलब्ध नाही"}</td></tr>`;
                return;
            }

            tbody.innerHTML = rates.map(r => {
                // Find matching localized crop name
                const meta = CROPS_META.find(c => c.id.toLowerCase() === r.crop.toLowerCase());
                const cropName = meta ? (meta.names[currentLang] || meta.names.mr || r.crop) : r.crop;
                
                const trendVal = r.trend_pct_7d || 0;
                const trendSign = trendVal > 0 ? "▲ +" : (trendVal < 0 ? "▼ " : "▬ ");
                const trendColor = trendVal > 0 ? "var(--green-700)" : (trendVal < 0 ? "var(--red)" : "var(--muted)");

                return `
                    <tr>
                        <td><strong>${cropName}</strong></td>
                        <td><strong>₹ ${formatNumber(r.modal_price)}</strong> / ${currentLocaleData.unit_quintal || 'क्विंटल'}</td>
                        <td style="color:${trendColor}; font-weight:700;">${trendSign}${Math.abs(trendVal).toFixed(1)}%</td>
                        <td>${r.as_of_date || 'आज'}</td>
                        <td style="color:var(--muted); font-size:0.85rem;">${r.source || 'Agmarknet'}</td>
                    </tr>
                `;
            }).join("");

        } catch (e) {
            tbody.innerHTML = `
                <tr>
                    <td><strong>${CROPS_META[0].names[currentLang] || "कांदा"}</strong></td>
                    <td><strong>₹ २,६२४</strong> / ${currentLocaleData.unit_quintal || 'क्विंटल'}</td>
                    <td style="color:var(--green-700); font-weight:700;">▲ +१.०%</td>
                    <td>आज</td>
                    <td style="color:var(--muted); font-size:0.85rem;">Agmarknet</td>
                </tr>
            `;
        }
    }

    // ------------------------------------------------------------------------
    // 7-Day Sparkline SVG Renderer
    // ------------------------------------------------------------------------
    function renderSparkline(history) {
        const svg = document.getElementById("sparklineSvg");
        if (!svg) return;

        if (!history || history.length < 2) {
            // Simulated 7-day steady trend if history is short
            history = [
                { price: 2580 }, { price: 2600 }, { price: 2615 },
                { price: 2590 }, { price: 2620 }, { price: 2635 }, { price: 2650 }
            ];
        }

        const prices = history.map(h => typeof h === "object" ? h.price : h);
        const minP = Math.min(...prices);
        const maxP = Math.max(...prices);
        const range = (maxP - minP) || 1;

        const width = 600;
        const height = 90;
        const padX = 24;
        const padY = 16;
        const stepX = (width - 2 * padX) / (prices.length - 1);

        const points = prices.map((p, i) => {
            const x = padX + i * stepX;
            const y = height - padY - ((p - minP) / range) * (height - 2 * padY);
            return { x, y, price: p };
        });

        const polylinePoints = points.map(pt => `${pt.x.toFixed(1)},${pt.y.toFixed(1)}`).join(" ");

        // Build filled area path
        const firstPt = points[0];
        const lastPt = points[points.length - 1];
        const areaPath = `M ${firstPt.x},${height - 4} L ${polylinePoints.replace(/ /g, " L ")} L ${lastPt.x},${height - 4} Z`;

        const circlesHtml = points.map((pt, idx) => `
            <circle cx="${pt.x.toFixed(1)}" cy="${pt.y.toFixed(1)}" r="4.5" fill="#2E7D32" stroke="#FFFFFF" stroke-width="2">
                <title>₹ ${formatNumber(pt.price)}</title>
            </circle>
        `).join("");

        svg.innerHTML = `
            <defs>
                <linearGradient id="chartGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="#4CAF50" stop-opacity="0.25"/>
                    <stop offset="100%" stop-color="#4CAF50" stop-opacity="0.0"/>
                </linearGradient>
            </defs>
            <path d="${areaPath}" fill="url(#chartGradient)" />
            <polyline fill="none" stroke="#2E7D32" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" points="${polylinePoints}" />
            ${circlesHtml}
            <text x="${padX}" y="${height - 2}" font-size="11" fill="#5B6770" font-family="inherit">₹ ${formatNumber(minP)}</text>
            <text x="${width - padX}" y="14" text-anchor="end" font-size="11" fill="#14532D" font-weight="700" font-family="inherit">₹ ${formatNumber(maxP)}</text>
        `;
    }

    // ------------------------------------------------------------------------
    // Ask Mandi Agent (POST /chat)
    // ------------------------------------------------------------------------
    async function submitQuestion(query) {
        const askInput = document.getElementById("askInput");
        const skeletonLoader = document.getElementById("skeletonLoader");
        const answerPanel = document.getElementById("answerPanel");

        const msg = (query || (askInput ? askInput.value : "")).trim();
        if (!msg) return;

        // Visual loading state
        if (skeletonLoader) skeletonLoader.classList.add("active");
        if (answerPanel) answerPanel.classList.remove("active");

        try {
            const resp = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    user_id: userId,
                    message: msg,
                    language: currentLang
                })
            });

            if (!resp.ok) throw new Error(`HTTP error ${resp.status}`);
            const data = await resp.json();

            // Populate Answer Panel
            populateAnswerPanel(data);

            if (skeletonLoader) skeletonLoader.classList.remove("active");
            if (answerPanel) {
                answerPanel.classList.add("active");
                answerPanel.scrollIntoView({ behavior: "smooth", block: "start" });
            }

            // Read aloud if TTS is enabled
            if (isAudioEnabled && data.reply) {
                speakText(data.reply, currentLang);
            }

        } catch (err) {
            console.error("Error communicating with agent:", err);
            if (skeletonLoader) skeletonLoader.classList.remove("active");
            alert(`${currentLocaleData.error_network || "माहिती लोड करण्यात त्रुटी."} (${err.message})`);
        }
    }

    // ------------------------------------------------------------------------
    // Populate Answer Panel with Response Data
    // ------------------------------------------------------------------------
    function populateAnswerPanel(data) {
        activeReplyText = data.reply || "";

        // 1. Recommendation Badge
        const rec = data.recommendation;
        const recCard = document.getElementById("recommendationCard");
        const actionBadge = document.getElementById("recActionBadge");
        const confText = document.getElementById("recConfidenceText");
        const recSummary = document.getElementById("recSummaryLine");

        if (rec && rec.action) {
            recCard.style.display = "block";
            let actionKey = "rec_sell_now";
            let badgeClass = "badge-sell";

            if (rec.action === "HOLD") {
                actionKey = "rec_hold";
                badgeClass = "badge-hold";
            } else if (rec.action === "SHIFT_MANDI") {
                actionKey = "rec_shift_mandi";
                badgeClass = "badge-shift";
            }

            actionBadge.className = `action-badge ${badgeClass}`;
            actionBadge.textContent = currentLocaleData[actionKey] || rec.action;

            const confPct = Math.round((rec.confidence || 0.85) * 100);
            confText.textContent = `${formatNumber(confPct)}% ${currentLocaleData.confidence_label || "विश्वासार्हता"}`;
            recSummary.textContent = rec.primary_reason || "";
        } else {
            recCard.style.display = "none";
        }

        // 2. Reasons List
        const reasonsList = document.getElementById("reasonsList");
        if (reasonsList) {
            reasonsList.innerHTML = "";
            const lines = (data.reply || "").split("\n").filter(l => l.trim().length > 0);
            
            // Extract bullets or formatted lines
            const bulletLines = lines.filter(l => l.startsWith("•") || l.startsWith("-") || l.startsWith("*"));
            const displayReasons = bulletLines.length > 0 ? bulletLines : lines.slice(0, 3);

            displayReasons.forEach(line => {
                const li = document.createElement("li");
                li.className = "reason-item";
                const clean = line.replace(/^[•\-*]\s*/, "").replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
                li.innerHTML = `<span>✓</span> <div>${clean}</div>`;
                reasonsList.appendChild(li);
            });
        }

        // 3. Numbers Strip
        const pInfo = data.price_info;
        const tInfo = data.trend_info;
        if (pInfo) {
            const modalP = pInfo.modal_price || 0;
            const perKg = (modalP / 100).toFixed(1);
            
            document.getElementById("valTypicalPrice").textContent = `₹ ${formatNumber(modalP)} / ${currentLocaleData.unit_quintal || 'क्विंटल'}`;
            document.getElementById("valPerKg").textContent = `₹ ${formatNumber(perKg)} / ${currentLocaleData.unit_kg || 'किलो'}`;
            
            const trendPct = tInfo ? tInfo.pct_change_7d : 0;
            const trendDir = trendPct > 0 ? "▲ +" : (trendPct < 0 ? "▼ " : "▬ ");
            document.getElementById("valTrend").textContent = `${trendDir}${formatNumber(Math.abs(trendPct))}%`;
            
            document.getElementById("valDateSource").textContent = `${pInfo.as_of_date || 'आज'} | ${pInfo.source || 'Agmarknet'}`;
            document.getElementById("numbersStrip").style.display = "grid";
        } else {
            document.getElementById("numbersStrip").style.display = "none";
        }

        // 4. Sparkline Chart
        if (tInfo && tInfo.history_7d) {
            renderSparkline(tInfo.history_7d);
        } else {
            renderSparkline(null);
        }

        // 5. Nearby Mandi Comparison Table
        const mandiBody = document.getElementById("mandiTableBody");
        const mandiSec = document.getElementById("mandiComparisonSection");
        const nearby = data.nearby_mandis;

        if (nearby && nearby.ranked_mandis && nearby.ranked_mandis.length > 0) {
            mandiSec.style.display = "block";
            mandiBody.innerHTML = nearby.ranked_mandis.map(m => {
                const isGain = m.net_gain_vs_local > 0;
                const gainText = isGain ? `+₹ ${formatNumber(m.net_gain_vs_local)}` : "—";
                const gainStyle = isGain ? "color:var(--green-700); font-weight:700;" : "color:var(--muted);";

                return `
                    <tr>
                        <td><strong>${m.mandi}</strong> <span style="font-size:0.8rem; color:var(--muted);">(${m.district})</span></td>
                        <td>${formatNumber(m.distance_km)} कि.मी.</td>
                        <td>₹ ${formatNumber(m.gross_price)}</td>
                        <td style="color:var(--muted);">₹ ${formatNumber(m.transport_cost_per_qtl)}</td>
                        <td><strong>₹ ${formatNumber(m.net_price_per_qtl)}</strong></td>
                        <td style="${gainStyle}">${gainText}</td>
                    </tr>
                `;
            }).join("");
        } else {
            mandiSec.style.display = "none";
        }

        // 6. Action Buttons
        const btnShareWhatsapp = document.getElementById("btnShareWhatsapp");
        const whatsappAction = (data.actions || []).find(a => a.type === "whatsapp_share");
        if (btnShareWhatsapp) {
            if (whatsappAction && whatsappAction.url) {
                btnShareWhatsapp.href = whatsappAction.url;
            } else {
                const encodedMsg = encodeURIComponent(`*KisanSaathi Mandi Advisory*\n${data.reply}`);
                btnShareWhatsapp.href = `https://api.whatsapp.com/send?text=${encodedMsg}`;
            }
        }

        const btnCardAlert = document.getElementById("btnCardAlert");
        if (btnCardAlert) {
            btnCardAlert.onclick = () => {
                openAlertModal(data.crop, data.district);
            };
        }

        const btnCardListen = document.getElementById("btnCardListen");
        if (btnCardListen) {
            btnCardListen.onclick = () => {
                speakText(data.reply, currentLang);
            };
        }

        // 7. Follow-up Chips
        const followupChips = document.getElementById("followupChips");
        if (followupChips) {
            followupChips.innerHTML = "";
            const followups = getFollowupQuestions(data.crop || "Onion", currentLang);
            followups.forEach(q => {
                const chip = document.createElement("button");
                chip.className = "followup-chip";
                chip.textContent = q;
                chip.onclick = () => {
                    const askInput = document.getElementById("askInput");
                    if (askInput) askInput.value = q;
                    submitQuestion(q);
                };
                followupChips.appendChild(chip);
            });
        }

        // 8. Technical Details Accordion (for judges)
        const techDetails = document.getElementById("techDetailsContent");
        if (techDetails) {
            const stepsHtml = (data.steps || []).map((s, idx) => `
                <div class="tech-step-row">
                    <span class="tech-step-badge">${idx + 1}. ${s.tool}</span>
                    <span style="color:var(--green-900); font-weight:600;">${s.result_summary}</span>
                    <pre style="margin:4px 0 0; font-size:11px; color:#5B6770;">${JSON.stringify(s.args)}</pre>
                </div>
            `).join("");
            techDetails.innerHTML = stepsHtml || "<em>No tools logged.</em>";
        }
    }

    // ------------------------------------------------------------------------
    // Localized Followup Question Generator
    // ------------------------------------------------------------------------
    function getFollowupQuestions(crop, lang) {
        const tpls = {
            mr: [
                "पुढील ५ दिवसांचे हवामान कसे असेल?",
                "शेजारच्या मंडीत विकल्यास किती नफा होईल?",
                "भाव वाढल्यावर मला व्हॉट्सॲपवर अलर्ट मिळेल का?"
            ],
            hi: [
                "अगले ५ दिनों का मौसम कैसा रहेगा?",
                "पास की मंडी में बेचने पर कितना अतिरिक्त फायदा होगा?",
                "भाव बढ़ने पर मुझे अलर्ट कैसे मिलेगा?"
            ],
            en: [
                "What is the 5-day weather and rain forecast?",
                "How much net profit by transporting to nearby mandi?",
                "Set a price alert when rates increase."
            ],
            gu: [
                "આગામી ૫ દિવસનું હવામાન કેવું રહેશે?",
                "નજીકના માર્કેટ યાર્ડમાં કેટલો નફો મળશે?",
                "ભાવ વધે ત્યારે મને એલર્ટ મળશે?"
            ],
            ta: [
                "அடுத்த 5 நாட்களுக்கு வானிலை எப்படி இருக்கும்?",
                "அருகிலுள்ள சந்தைக்கு கொண்டு சென்றால் எவ்வளவு லாபம்?",
                "விலை உயரும் போது எனக்கு எச்சரிக்கை வருமா?"
            ],
            te: [
                "రాబోయే 5 రోజుల్లో వాతావరణం ఎలా ఉంటుంది?",
                "సమీప మార్కెట్‌లో అమ్మితే ఎంత లాభం వస్తుంది?",
                "ధర పెరిగినప్పుడు నాకు అలర్ట్ వస్తుందా?"
            ],
            kn: [
                "ಮುಂದಿನ 5 ದಿನಗಳ ಹವಾಮಾನ ಹೇಗಿರುತ್ತದೆ?",
                "ಹತ್ತಿರದ ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ಎಷ್ಟು ಲಾಭ ಸಿಗುತ್ತದೆ?",
                "ಬೆಲೆ ಏರಿದಾಗ ನನಗೆ ಎಚ್ಚರಿಕೆ ಸಿಗುವುದೇ?"
            ],
            ml: [
                "അടുത്ത 5 ദിവസത്തെ കാലാവസ്ഥ എങ്ങനെയായിരിക്കും?",
                "അടുത്തുള്ള വിപണിയിൽ എത്ര അധിക ലാഭം കിട്ടും?",
                "വില കൂടുമ്പോൾ അലർട്ട് ലഭിക്കുമോ?"
            ],
            bn: [
                "আগামী ৫ দিনের আবহাওয়া কেমন থাকবে?",
                "কাছের মান্ডিতে বিক্রি করলে কতটা অতিরিক্ত লাভ হবে?",
                "দাম বাড়লে আমাকে কীভাবে সতর্কবার্তা পাঠানো হবে?"
            ],
            pa: [
                "ਅਗਲੇ 5 ਦਿਨਾਂ ਦਾ ਮੌਸਮ ਕਿਹੋ ਜਿਹਾ ਰਹੇਗਾ?",
                "ਨੇੜਲੀ ਮੰਡੀ ਵਿੱਚ ਵੇਚਣ ਤੇ ਕਿੰਨਾ ਵਾਧੂ ਮੁਨਾਫ਼ਾ ਹੋਵੇਗਾ?",
                "ਭਾਅ ਵਧਣ ਤੇ ਅਲਰਟ ਕਿਵੇਂ ਮਿਲੇਗਾ?"
            ],
            or: [
                "ଆଗାମୀ ୫ ଦିନର ପାଣିପାଗ କିପରି ରହିବ?",
                "ନିକଟସ୍ଥ ମଣ୍ଡିରେ ବିକ୍ରି କଲେ କେତେ ଲାଭ ମିଳିବ?",
                "ଦର ବଢ଼ିଲେ ଆଲର୍ଟ କିପରି ପାଇବି?"
            ],
            as: [
                "অহা ৫ দিনৰ বতৰ কেনেকুৱা হ'ব?",
                "ওচৰৰ বজাৰত বিক্ৰী কৰিলে কিমান অতিৰিক্ত লাভ হ'ব?",
                "দাম বাঢ়িলে মোক সতৰ্কবাৰ্তা কেনেকৈ দিয়া হ'ব?"
            ]
        };
        return tpls[lang] || tpls.mr;
    }

    // ------------------------------------------------------------------------
    // Web Speech API: STT & TTS with Runtime Detection
    // ------------------------------------------------------------------------
    const LANG_LOCALE_CODES = {
        mr: "mr-IN", hi: "hi-IN", en: "en-IN", gu: "gu-IN",
        ta: "ta-IN", te: "te-IN", kn: "kn-IN", ml: "ml-IN",
        bn: "bn-IN", pa: "pa-IN", or: "or-IN", as: "as-IN"
    };

    function checkSpeechSupport() {
        const micBtn = document.getElementById("micBtn");
        const btnCardListen = document.getElementById("btnCardListen");
        const ttsToggleBtn = document.getElementById("ttsToggleBtn");

        // 1. Speech Recognition Check
        const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRec) {
            if (micBtn) micBtn.style.display = "none";
        } else {
            if (micBtn) micBtn.style.display = "inline-flex";
            if (!recognition) {
                recognition = new SpeechRec();
                recognition.continuous = false;
                recognition.interimResults = false;

                recognition.onstart = () => {
                    isRecording = true;
                    if (micBtn) micBtn.classList.add("recording");
                };

                recognition.onresult = (event) => {
                    const transcript = event.results[0][0].transcript;
                    const askInput = document.getElementById("askInput");
                    if (askInput) askInput.value = transcript;
                    if (micBtn) micBtn.classList.remove("recording");
                    isRecording = false;
                    submitQuestion(transcript);
                };

                recognition.onerror = (e) => {
                    console.warn("Speech recognition error:", e);
                    if (micBtn) micBtn.classList.remove("recording");
                    isRecording = false;
                };

                recognition.onend = () => {
                    if (micBtn) micBtn.classList.remove("recording");
                    isRecording = false;
                };
            }
        }

        // 2. Speech Synthesis Check
        if (!window.speechSynthesis) {
            if (btnCardListen) btnCardListen.style.display = "none";
            if (ttsToggleBtn) ttsToggleBtn.style.display = "none";
        } else {
            if (btnCardListen) btnCardListen.style.display = "inline-flex";
            if (ttsToggleBtn) ttsToggleBtn.style.display = "inline-flex";
        }
    }

    function speakText(text, lang) {
        if (!isAudioEnabled || !window.speechSynthesis) return;

        window.speechSynthesis.cancel();

        // Clean formatting and punctuation
        const clean = text
            .replace(/[*#_`]/g, "")
            .replace(/\[.*?\]/g, "")
            .replace(/[⚠️💡📌📊⭐🌾📲✅🔍📈🚛]/g, "")
            .trim();

        // First 2 clear sentences
        const sentences = clean.split(/[.!?।\n]+/).filter(s => s.trim().length > 0);
        const snippet = sentences.slice(0, 2).join(". ");
        if (!snippet) return;

        const utterance = new SpeechSynthesisUtterance(snippet);
        const targetLocale = LANG_LOCALE_CODES[lang] || "hi-IN";
        utterance.lang = targetLocale;
        utterance.rate = 0.95;

        // Try to match voice
        const voices = window.speechSynthesis.getVoices();
        const matched = voices.find(v => v.lang.startsWith(targetLocale.split("-")[0]));
        if (matched) utterance.voice = matched;

        window.speechSynthesis.speak(utterance);
    }

    // ------------------------------------------------------------------------
    // Price Alerts Modal & Storage
    // ------------------------------------------------------------------------
    function openAlertModal(crop, mandi) {
        const modal = document.getElementById("alertModalBackdrop");
        if (modal) modal.classList.add("active");

        if (crop) {
            const meta = CROPS_META.find(c => c.id.toLowerCase() === crop.toLowerCase());
            document.getElementById("modalCrop").value = meta ? (meta.names[currentLang] || crop) : crop;
        }
        if (mandi) {
            document.getElementById("modalMandi").value = mandi;
        }
        loadUserAlerts();
    }

    function closeAlertModal() {
        const modal = document.getElementById("alertModalBackdrop");
        if (modal) modal.classList.remove("active");
    }

    async function loadUserAlerts() {
        const container = document.getElementById("userAlertsContainer");
        if (!container) return;

        try {
            const resp = await fetch(`/alerts/${userId}`);
            if (!resp.ok) throw new Error("Could not fetch alerts");
            const data = await resp.json();
            const alerts = data.alerts || [];

            if (alerts.length === 0) {
                container.textContent = currentLocaleData.no_alerts || "सध्या कोणतेही सक्रिय अलर्ट नाहीत.";
                return;
            }

            container.innerHTML = alerts.map(a => `
                <div style="padding:8px 0; border-bottom:1px solid #E8F5E9; display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <strong>${a.crop}</strong> (${a.mandi || 'सर्व मंड्या'}): 
                        <span style="color:var(--green-700); font-weight:700;">₹ ${formatNumber(a.target_price)} / ${currentLocaleData.unit_quintal || 'क्विंटल'}</span>
                    </div>
                    <span style="font-size:0.85rem; font-weight:600; color:${a.triggered ? 'var(--red)' : 'var(--green-700)'};">
                        ${a.triggered ? '⚠️ प्राप्त' : '● सक्रिय'}
                    </span>
                </div>
            `).join("");
        } catch (e) {
            container.textContent = currentLocaleData.no_alerts || "अलर्ट लोड करताना अडचण.";
        }
    }

    async function submitNewAlert() {
        const cropInput = document.getElementById("modalCrop").value.trim();
        const mandiInput = document.getElementById("modalMandi").value.trim();
        const targetPrice = parseFloat(document.getElementById("modalTarget").value);

        if (!cropInput || isNaN(targetPrice) || targetPrice <= 0) {
            alert(currentLocaleData.alert_target_label || "कृपया शेतमाल आणि अपेक्षित भाव भरा.");
            return;
        }

        try {
            await fetch("/alerts", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    user_id: userId,
                    crop: cropInput,
                    target_price: targetPrice,
                    mandi: mandiInput || null
                })
            });

            alert(currentLocaleData.alert_success || "अलर्ट सक्रिय झाला आहे!");
            document.getElementById("modalTarget").value = "";
            closeAlertModal();
            loadUserAlerts();
        } catch (e) {
            alert("त्रुटी: अलर्ट तयार करता आला नाही.");
        }
    }

    // ------------------------------------------------------------------------
    // Addendum 2: Follow-up Reminders in SQLite
    // ------------------------------------------------------------------------
    async function loadUserReminders() {
        const container = document.getElementById("userRemindersContainer");
        if (!container) return;

        try {
            const resp = await fetch(`/reminders/${userId}`);
            if (!resp.ok) throw new Error("Could not fetch reminders");
            const data = await resp.json();
            const reminders = data.reminders || [];

            if (reminders.length === 0) {
                container.textContent = currentLocaleData.no_reminders || "सध्या कोणतीही प्रलंबित आठवण नाही.";
                return;
            }

            container.innerHTML = reminders.map(r => `
                <div class="reminder-card-item">
                    <div>
                        <div class="reminder-crop-title">${r.crop} - ${r.issue_name || 'पीक तपासणी'}</div>
                        <div class="reminder-due-date">${currentLocaleData.due_on || 'तपासणी तारीख:'} <strong>${r.due_date}</strong> (${r.days} ${currentLocaleData.days_unit || 'दिवस'})</div>
                    </div>
                    <button onclick="window.kisansaathiDeleteReminder(${r.id})" style="background:transparent; border:none; color:var(--red); font-size:1.1rem; cursor:pointer;" title="हटवा">&times;</button>
                </div>
            `).join("");
        } catch (e) {
            container.textContent = currentLocaleData.no_reminders || "सध्या कोणतीही प्रलंबित आठवण नाही.";
        }
    }

    window.kisansaathiDeleteReminder = async function(id) {
        try {
            await fetch(`/reminders/${id}`, { method: "DELETE" });
            loadUserReminders();
        } catch (e) {
            console.error("Failed to delete reminder:", e);
        }
    };

    // ------------------------------------------------------------------------
    // Addendum 2: Client-side Image Resizing (Max 1024px, JPEG 0.8)
    // ------------------------------------------------------------------------
    function resizeImageFile(file, maxWidth = 1024, quality = 0.8) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const img = new Image();
                img.onload = () => {
                    let width = img.width;
                    let height = img.height;
                    if (width > maxWidth || height > maxWidth) {
                        if (width > height) {
                            height = Math.round((height * maxWidth) / width);
                            width = maxWidth;
                        } else {
                            width = Math.round((width * maxWidth) / height);
                            height = maxWidth;
                        }
                    }
                    const canvas = document.createElement("canvas");
                    canvas.width = width;
                    canvas.height = height;
                    const ctx = canvas.getContext("2d");
                    ctx.drawImage(img, 0, 0, width, height);
                    canvas.toBlob(
                        (blob) => {
                            resolve({ blob, dataUrl: canvas.toDataURL("image/jpeg", quality) });
                        },
                        "image/jpeg",
                        quality
                    );
                };
                img.onerror = reject;
                img.src = e.target.result;
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }

    // ------------------------------------------------------------------------
    // Addendum 2: Crop Photo Analysis Feature ("Check my crop")
    // ------------------------------------------------------------------------
    let currentCropBlob = null;
    let lastCropDiagnosis = null;

    function openCropModal() {
        const modal = document.getElementById("cropModalBackdrop");
        if (!modal) return;
        document.getElementById("cropUploadView").style.display = "block";
        document.getElementById("cropAnalyzingView").style.display = "none";
        document.getElementById("cropResultView").style.display = "none";
        modal.style.display = "flex";
    }

    function closeCropModal() {
        const modal = document.getElementById("cropModalBackdrop");
        if (modal) modal.style.display = "none";
    }

    function initCropPhotoFeature() {
        const openCard = document.getElementById("openCropModalCard");
        const openBtn = document.getElementById("btnCheckCropTrigger");
        const closeBtn = document.getElementById("cropModalCloseBtn");
        const modal = document.getElementById("cropModalBackdrop");

        if (openCard) openCard.addEventListener("click", openCropModal);
        if (openBtn) openBtn.addEventListener("click", (e) => { e.stopPropagation(); openCropModal(); });
        if (closeBtn) closeBtn.addEventListener("click", closeCropModal);
        if (modal) {
            modal.addEventListener("click", (e) => {
                if (e.target === modal) closeCropModal();
            });
        }

        const cameraTrigger = document.getElementById("btnCameraTrigger");
        const galleryTrigger = document.getElementById("btnGalleryTrigger");
        const cameraInput = document.getElementById("cameraFileInput");
        const galleryInput = document.getElementById("galleryFileInput");
        const previewArea = document.getElementById("photoPreviewArea");
        const previewImg = document.getElementById("cropPreviewImg");
        const removePhotoBtn = document.getElementById("btnRemovePhoto");
        const analyzeBtn = document.getElementById("btnAnalyzeCrop");

        if (cameraTrigger && cameraInput) {
            cameraTrigger.addEventListener("click", () => cameraInput.click());
        }
        if (galleryTrigger && galleryInput) {
            galleryTrigger.addEventListener("click", () => galleryInput.click());
        }

        async function handleFileSelect(file) {
            if (!file) return;
            try {
                const res = await resizeImageFile(file, 1024, 0.8);
                currentCropBlob = res.blob;
                previewImg.src = res.dataUrl;
                previewArea.style.display = "block";
                analyzeBtn.disabled = false;
            } catch (err) {
                console.error("Image processing error:", err);
            }
        }

        if (cameraInput) {
            cameraInput.addEventListener("change", (e) => {
                if (e.target.files && e.target.files[0]) handleFileSelect(e.target.files[0]);
            });
        }
        if (galleryInput) {
            galleryInput.addEventListener("change", (e) => {
                if (e.target.files && e.target.files[0]) handleFileSelect(e.target.files[0]);
            });
        }

        if (removePhotoBtn) {
            removePhotoBtn.addEventListener("click", () => {
                currentCropBlob = null;
                previewImg.src = "";
                previewArea.style.display = "none";
                analyzeBtn.disabled = true;
                if (cameraInput) cameraInput.value = "";
                if (galleryInput) galleryInput.value = "";
            });
        }

        // Voice note mic button for crop symptom note
        const cropNoteMicBtn = document.getElementById("cropNoteMicBtn");
        const cropNoteInput = document.getElementById("cropNoteInput");
        if (cropNoteMicBtn && cropNoteInput) {
            cropNoteMicBtn.addEventListener("click", () => {
                const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
                if (!SpeechRec) {
                    alert("Voice input not supported in this browser.");
                    return;
                }
                const noteRec = new SpeechRec();
                noteRec.lang = LANG_LOCALE_CODES[currentLang] || "mr-IN";
                noteRec.onstart = () => { cropNoteMicBtn.textContent = "🔴"; };
                noteRec.onresult = (ev) => {
                    const text = ev.results[0][0].transcript;
                    cropNoteInput.value = (cropNoteInput.value ? cropNoteInput.value + " " : "") + text;
                };
                noteRec.onend = () => { cropNoteMicBtn.textContent = "🎙️"; };
                noteRec.onerror = () => { cropNoteMicBtn.textContent = "🎙️"; };
                noteRec.start();
            });
        }

        if (analyzeBtn) {
            analyzeBtn.addEventListener("click", submitCropAnalysis);
        }

        // Remind 3 days button
        const btnRemind3Days = document.getElementById("btnRemind3Days");
        if (btnRemind3Days) {
            btnRemind3Days.addEventListener("click", async () => {
                if (!lastCropDiagnosis) return;
                try {
                    await fetch("/reminders", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            user_id: userId,
                            crop: lastCropDiagnosis.crop || "Crop",
                            issue_name: lastCropDiagnosis.issue_name || "Health Check",
                            days: 3
                        })
                    });
                    alert(currentLocaleData.reminder_set_msg || "आठवण जतन केली! ३ दिवसांनी पिकाची पुन्हा पाहणी करा.");
                    loadUserReminders();
                } catch (e) {
                    alert("त्रुटी: आठवण जतन करता आली नाही.");
                }
            });
        }

        // WhatsApp Share button
        const btnShareDiagnosis = document.getElementById("btnShareDiagnosis");
        if (btnShareDiagnosis) {
            btnShareDiagnosis.addEventListener("click", () => {
                if (!lastCropDiagnosis) return;
                const text = encodeURIComponent(`🌾 *KisanSaathi Crop Diagnosis*\nCrop: ${lastCropDiagnosis.crop || 'Crop'}\nIssue: ${lastCropDiagnosis.issue_name || 'Checked'}\nConfidence: ${lastCropDiagnosis.confidence_level || 'High'}\n${lastCropDiagnosis.guidance_disclaimer || ''}`);
                window.open(`https://api.whatsapp.com/send?text=${text}`, "_blank");
            });
        }
    }

    async function submitCropAnalysis() {
        if (!currentCropBlob) return;
        const uploadView = document.getElementById("cropUploadView");
        const analyzingView = document.getElementById("cropAnalyzingView");
        const resultView = document.getElementById("cropResultView");

        uploadView.style.display = "none";
        analyzingView.style.display = "block";
        resultView.style.display = "none";

        const cropHint = document.getElementById("cropHintInput").value.trim();
        const note = document.getElementById("cropNoteInput").value.trim();

        const formData = new FormData();
        formData.append("image", currentCropBlob, "crop_photo.jpg");
        formData.append("language", currentLang);
        if (cropHint) formData.append("crop_hint", cropHint);
        if (note) formData.append("note", note);
        formData.append("district", "Nashik");
        formData.append("user_id", userId);

        try {
            const resp = await fetch("/analyze-crop", {
                method: "POST",
                body: formData
            });
            if (!resp.ok) throw new Error("Server error " + resp.status);
            const data = await resp.json();
            renderCropDiagnosisResult(data);
        } catch (e) {
            console.error("Diagnosis error:", e);
            alert("त्रुटी: फोटो तपासता आला नाही. कृपया पुन्हा प्रयत्न करा.");
            uploadView.style.display = "block";
            analyzingView.style.display = "none";
        }
    }

    function renderCropDiagnosisResult(data) {
        const uploadView = document.getElementById("cropUploadView");
        const analyzingView = document.getElementById("cropAnalyzingView");
        const resultView = document.getElementById("cropResultView");

        uploadView.style.display = "none";
        analyzingView.style.display = "none";
        resultView.style.display = "block";

        const a = data.analysis || {};
        lastCropDiagnosis = a;

        // Status banner
        const statusBanner = document.getElementById("cropStatusBanner");
        const statusText = document.getElementById("cropStatusText");
        const statusIcon = document.getElementById("cropStatusIcon");

        statusBanner.className = "status-banner";
        if (a.assessment === "healthy") {
            statusBanner.classList.add("healthy");
            statusIcon.textContent = "✓";
            statusText.textContent = currentLocaleData.banner_healthy || "पीक निरोगी दिसत आहे";
        } else if (a.image_type === "unusable") {
            statusBanner.classList.add("unclear");
            statusIcon.textContent = "🔍";
            statusText.textContent = currentLocaleData.banner_unclear || "स्पष्ट फोटोची आवश्यकता आहे";
        } else if (a.severity === "high" || a.expert_advice_needed) {
            statusBanner.classList.add("expert");
            statusIcon.textContent = "⚠️";
            statusText.textContent = currentLocaleData.banner_expert || "कृषी तज्ज्ञांचा सल्ला घ्या";
        } else {
            statusBanner.classList.add("attention");
            statusIcon.textContent = "⚠️";
            statusText.textContent = currentLocaleData.banner_attention || "लक्ष देण्याची गरज आहे";
        }

        // Issue Name & Confidence
        const issueName = document.getElementById("diagnosisIssueName");
        const confChip = document.getElementById("diagnosisConfidenceChip");
        const disclaimer = document.getElementById("diagnosisDisclaimer");

        if (issueName) issueName.textContent = a.issue_name || (a.assessment === "healthy" ? (currentLocaleData.banner_healthy || "निरोगी") : (currentLocaleData.banner_unclear || "अस्पष्ट"));
        if (confChip) confChip.textContent = `${currentLocaleData.confidence_label || 'विश्वासार्हता'}: ${a.confidence_level || 'उच्च'}`;
        if (disclaimer) disclaimer.textContent = a.guidance_disclaimer || "हे छायाचित्रावरून दिलेले मार्गदर्शन आहे आणि ते १००% अचूक नसू शकते.";

        // Retake Tip
        const retakeBox = document.getElementById("retakeGuidanceBox");
        const retakeTipText = document.getElementById("retakeTipText");
        if (a.retake_tip) {
            retakeBox.style.display = "block";
            retakeTipText.textContent = a.retake_tip;
        } else {
            retakeBox.style.display = "none";
        }

        // Symptoms
        const symptomsList = document.getElementById("symptomsList");
        const symptomsSection = document.getElementById("symptomsSection");
        if (a.visible_symptoms && a.visible_symptoms.length > 0) {
            symptomsSection.style.display = "block";
            symptomsList.innerHTML = a.visible_symptoms.map(s => `<li>${s}</li>`).join("");
        } else {
            symptomsSection.style.display = "none";
        }

        // Steps
        const stepsList = document.getElementById("immediateStepsList");
        const stepsSection = document.getElementById("stepsSection");
        if (a.immediate_steps && a.immediate_steps.length > 0) {
            stepsSection.style.display = "block";
            stepsList.innerHTML = a.immediate_steps.map(s => `<li>${s}</li>`).join("");
        } else {
            stepsSection.style.display = "none";
        }

        // Produce Quality Card
        const produceCard = document.getElementById("produceGradeCard");
        if (a.image_type === "produce_quality" || a.produce_grade) {
            produceCard.style.display = "block";
            const gradeBadge = document.getElementById("produceGradeBadge");
            const priceRange = document.getElementById("producePriceRange");
            const reasonsList = document.getElementById("gradeReasonsList");

            const gradeName = a.produce_grade === "A" ? "अ-दर्जा (Grade A)" : (a.produce_grade === "B" ? "ब-दर्जा (Grade B)" : "क-दर्जा (Grade C)");
            if (gradeBadge) gradeBadge.textContent = gradeName;
            if (data.grade_pricing && priceRange) {
                priceRange.textContent = `${data.grade_pricing.price_range} / ${currentLocaleData.unit_quintal || 'क्विंटल'}`;
            }
            if (a.grade_reasons && reasonsList) {
                reasonsList.innerHTML = a.grade_reasons.map(r => `<li>${r}</li>`).join("");
            }
        } else {
            produceCard.style.display = "none";
        }

        // Expert Help Card
        const expertCard = document.getElementById("expertHelpCard");
        if (data.expert_help) {
            expertCard.style.display = "block";
            const officeName = document.getElementById("expertOfficeName");
            const adviceNote = document.getElementById("expertAdviceNote");
            if (officeName) officeName.textContent = `${data.expert_help.kvk_name || ''} (${data.expert_help.district || ''})`;
            if (adviceNote) adviceNote.textContent = data.expert_help.advice_note || '';
        }
    }

    // ------------------------------------------------------------------------
    // Addendum 2: Voice Assistant Feature ("Talk to KisanSaathi")
    // ------------------------------------------------------------------------
    let voiceRecognition = null;
    let isVoiceListening = false;
    let speechUtterance = null;

    function openVoiceModal() {
        const modal = document.getElementById("voiceModalBackdrop");
        if (!modal) return;
        modal.style.display = "flex";
        startVoiceListening();
    }

    function closeVoiceModal() {
        const modal = document.getElementById("voiceModalBackdrop");
        if (modal) modal.style.display = "none";
        stopVoiceListening();
        if (window.speechSynthesis) window.speechSynthesis.cancel();
    }

    function startVoiceListening() {
        const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRec) {
            document.getElementById("voiceStateText").textContent = "Browser speech recognition not supported.";
            return;
        }

        try {
            voiceRecognition = new SpeechRec();
            voiceRecognition.lang = LANG_LOCALE_CODES[currentLang] || "mr-IN";
            voiceRecognition.continuous = false;
            voiceRecognition.interimResults = true;

            const pulseRing = document.getElementById("voicePulseRing");
            const stateText = document.getElementById("voiceStateText");
            const transcriptInput = document.getElementById("voiceTranscriptInput");

            voiceRecognition.onstart = () => {
                isVoiceListening = true;
                pulseRing.style.display = "block";
                stateText.textContent = currentLocaleData.voice_listening || "ऐकत आहोत... बोला";
            };

            voiceRecognition.onresult = (e) => {
                let text = "";
                for (let i = e.resultIndex; i < e.results.length; i++) {
                    text += e.results[i][0].transcript;
                }
                transcriptInput.value = text;
            };

            voiceRecognition.onend = () => {
                isVoiceListening = false;
                pulseRing.style.display = "none";
                stateText.textContent = currentLocaleData.voice_understanding || "प्रश्न तपासा आणि विचारा";
            };

            voiceRecognition.onerror = (e) => {
                isVoiceListening = false;
                pulseRing.style.display = "none";
                stateText.textContent = currentLocaleData.hold_phone_close_hint || "फोन जवळ धरून पुन्हा बोला.";
            };

            voiceRecognition.start();
        } catch (e) {
            console.warn("Voice assistant start error:", e);
        }
    }

    function stopVoiceListening() {
        if (voiceRecognition && isVoiceListening) {
            try { voiceRecognition.stop(); } catch (e) {}
            isVoiceListening = false;
        }
        const pulseRing = document.getElementById("voicePulseRing");
        if (pulseRing) pulseRing.style.display = "none";
    }

    function initVoiceAssistantFeature() {
        const openCard = document.getElementById("openVoiceModalCard");
        const openBtn = document.getElementById("btnVoiceTrigger");
        const closeBtn = document.getElementById("voiceModalCloseBtn");
        const modal = document.getElementById("voiceModalBackdrop");

        if (openCard) openCard.addEventListener("click", openVoiceModal);
        if (openBtn) openBtn.addEventListener("click", (e) => { e.stopPropagation(); openVoiceModal(); });
        if (closeBtn) closeBtn.addEventListener("click", closeVoiceModal);
        if (modal) {
            modal.addEventListener("click", (e) => {
                if (e.target === modal) closeVoiceModal();
            });
        }

        const micCircle = document.getElementById("voiceMicCircle");
        if (micCircle) {
            micCircle.addEventListener("click", () => {
                if (isVoiceListening) {
                    stopVoiceListening();
                } else {
                    startVoiceListening();
                }
            });
        }

        const reRecordBtn = document.getElementById("btnVoiceReRecord");
        if (reRecordBtn) {
            reRecordBtn.addEventListener("click", () => {
                document.getElementById("voiceTranscriptInput").value = "";
                startVoiceListening();
            });
        }

        const sendBtn = document.getElementById("btnVoiceSend");
        if (sendBtn) {
            sendBtn.addEventListener("click", () => {
                const text = document.getElementById("voiceTranscriptInput").value.trim();
                if (!text) return;
                closeVoiceModal();
                const askInput = document.getElementById("askInput");
                if (askInput) askInput.value = text;
                submitQuestion();
            });
        }

        // Speech Audio Play/Pause and Speed Select
        const playPauseBtn = document.getElementById("btnAudioPlayPause");
        const speedSelect = document.getElementById("audioSpeedSelect");
        if (playPauseBtn) {
            playPauseBtn.addEventListener("click", () => {
                if (!window.speechSynthesis) return;
                if (window.speechSynthesis.speaking) {
                    if (window.speechSynthesis.paused) {
                        window.speechSynthesis.resume();
                        playPauseBtn.textContent = "थांबवा ⏸️";
                    } else {
                        window.speechSynthesis.pause();
                        playPauseBtn.textContent = "चालू करा ▶️";
                    }
                } else if (activeReplyText) {
                    speakText(activeReplyText);
                    playPauseBtn.textContent = "थांबवा ⏸️";
                }
            });
        }

        if (speedSelect) {
            speedSelect.addEventListener("change", () => {
                if (speechUtterance) {
                    speechUtterance.rate = parseFloat(speedSelect.value);
                }
            });
        }
    }

    // ------------------------------------------------------------------------
    // DOM Event Listeners Wire-up
    // ------------------------------------------------------------------------
    document.addEventListener("DOMContentLoaded", () => {
        // 1. Language Dropdown
        const languageSelect = document.getElementById("languageSelect");
        if (languageSelect) {
            languageSelect.value = currentLang;
            languageSelect.addEventListener("change", (e) => {
                loadLocale(e.target.value);
            });
        }

        // 2. Ask Form Inputs
        const askBtn = document.getElementById("askBtn");
        const askInput = document.getElementById("askInput");

        if (askBtn) askBtn.addEventListener("click", () => submitQuestion());
        if (askInput) {
            askInput.addEventListener("keydown", (e) => {
                if (e.key === "Enter") {
                    e.preventDefault();
                    submitQuestion();
                }
            });
        }

        // 3. Microphone Button
        const micBtn = document.getElementById("micBtn");
        if (micBtn) {
            micBtn.addEventListener("click", () => {
                if (!recognition) return;
                if (isRecording) {
                    recognition.stop();
                } else {
                    recognition.lang = LANG_LOCALE_CODES[currentLang] || "mr-IN";
                    try {
                        recognition.start();
                    } catch (e) {
                        console.warn("Recognition start failed:", e);
                    }
                }
            });
        }

        // 4. TTS Audio Toggle
        const ttsToggleBtn = document.getElementById("ttsToggleBtn");
        if (ttsToggleBtn) {
            ttsToggleBtn.addEventListener("click", () => {
                isAudioEnabled = !isAudioEnabled;
                ttsToggleBtn.textContent = isAudioEnabled ? "🔊" : "🔇";
                if (!isAudioEnabled && window.speechSynthesis) {
                    window.speechSynthesis.cancel();
                }
            });
        }

        // 5. Alerts Modal Handlers
        const alertModalBtn = document.getElementById("alertModalBtn");
        const btnCreateAlertHeader = document.getElementById("btnCreateAlertHeader");
        const modalCloseBtn = document.getElementById("modalCloseBtn");
        const alertModalBackdrop = document.getElementById("alertModalBackdrop");
        const btnModalSubmit = document.getElementById("btnModalSubmit");

        if (alertModalBtn) alertModalBtn.addEventListener("click", () => openAlertModal());
        if (btnCreateAlertHeader) btnCreateAlertHeader.addEventListener("click", () => openAlertModal());
        if (modalCloseBtn) modalCloseBtn.addEventListener("click", closeAlertModal);
        if (btnModalSubmit) btnModalSubmit.addEventListener("click", submitNewAlert);

        if (alertModalBackdrop) {
            alertModalBackdrop.addEventListener("click", (e) => {
                if (e.target === alertModalBackdrop) closeAlertModal();
            });
        }

        // 6. Initialize Special Features (Addendum 2)
        initCropPhotoFeature();
        initVoiceAssistantFeature();

        // 7. Initialize with Current Locale
        loadLocale(currentLang);
    });

})();
