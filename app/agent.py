import os
from typing import Dict, Any, Optional, List
from app.db import log_query
from app.prompts import get_system_prompt, get_clarifying_question
from app.llm import llm_client
from app.tools import (
    detect_language,
    normalize_crop,
    extract_query,
    get_mandi_prices,
    get_price_trend,
    compare_nearby_mandis,
    get_weather_forecast,
    get_msp,
    recommend_action,
    create_price_alert,
    make_share_summary
)
from app.tools.places import get_localized_crop, get_localized_place

SUPPORTED_LANGUAGES = ["en", "hi", "mr", "gu", "ta", "te", "kn", "ml", "bn", "pa", "or", "as"]


async def run_agent(user_id: str, message: str, language: str = "mr") -> Dict[str, Any]:
    """
    KisanSaathi autonomous agent loop executing:
    Understand -> Reason -> Plan -> Use Tools -> Act -> Deliver
    The selected language is the single source of truth.
    """
    steps: List[Dict[str, Any]] = []
    actions: List[Dict[str, Any]] = []
    recommendation = None

    # ==========================================
    # 1. UNDERSTAND
    # ==========================================
    # The selected language is the absolute source of truth
    if language in SUPPORTED_LANGUAGES:
        target_lang = language
    else:
        detected = detect_language(message)
        target_lang = detected if detected in SUPPORTED_LANGUAGES else "mr"

    steps.append({
        "tool": "detect_language",
        "args": {"message_sample": message[:40]},
        "result_summary": f"Target response language: {target_lang.upper()}"
    })

    # Entity and Intent Extraction
    extracted = extract_query(message, target_lang)
    crop = extracted.get("crop")
    district = extracted.get("district")
    intent = extracted.get("intent", "general")
    quantity = extracted.get("quantity")
    target_price = extracted.get("target_price")
    missing_fields = extracted.get("missing_fields", [])

    steps.append({
        "tool": "extract_query",
        "args": {"text": message},
        "result_summary": f"Intent: {intent} | Crop: {crop or 'None'} | Location: {district or 'None'} | Missing: {missing_fields or 'None'}"
    })

    # Canonicalize crop if recognized
    if crop:
        canonical_crop = normalize_crop(crop)
        if canonical_crop:
            crop = canonical_crop

    # ==========================================
    # 2. REASON & HANDLE AMBIGUITY / OFF-TOPIC
    # ==========================================
    if intent == "off_topic":
        clarifying_reply = get_clarifying_question("off_topic", target_lang)
        log_query(user_id, message, clarifying_reply, target_lang, "off_topic")
        return {
            "reply": clarifying_reply,
            "language": target_lang,
            "steps": steps,
            "what_we_checked": [],
            "recommendation": None,
            "actions": []
        }

    # Missing essential entity handling (ONE clarifying question)
    if "crop" in missing_fields and intent != "weather":
        clarifying_reply = get_clarifying_question("missing_crop", target_lang)
        steps.append({
            "tool": "reason_missing_crop",
            "args": {"missing": "crop"},
            "result_summary": "Crop name missing. Asking single clarifying question to farmer."
        })
        log_query(user_id, message, clarifying_reply, target_lang, intent, crop=None, mandi=district)
        return {
            "reply": clarifying_reply,
            "language": target_lang,
            "steps": steps,
            "what_we_checked": [],
            "recommendation": None,
            "actions": []
        }

    if "location" in missing_fields and intent in ["price_check", "sell_or_hold", "best_mandi"]:
        clarifying_reply = get_clarifying_question("missing_location", target_lang)
        steps.append({
            "tool": "reason_missing_location",
            "args": {"missing": "location"},
            "result_summary": "Mandi/district missing. Asking single clarifying question to farmer."
        })
        log_query(user_id, message, clarifying_reply, target_lang, intent, crop=crop, mandi=None)
        return {
            "reply": clarifying_reply,
            "language": target_lang,
            "steps": steps,
            "what_we_checked": [],
            "recommendation": None,
            "actions": []
        }

    active_district = district or "Nashik"
    active_crop = crop or "Onion"

    # ==========================================
    # 3. PLAN & 4. USE TOOLS
    # ==========================================
    price_info = None
    trend_info = None
    weather_info = None
    msp_info = None
    nearby_mandis_info = None
    what_we_checked: List[str] = []

    # Step: Mandi Prices
    if intent in ["price_check", "sell_or_hold", "best_mandi", "set_alert", "general"]:
        price_info = get_mandi_prices(crop=active_crop, district=active_district, mandi=active_district)
        freshness_note = "Older than 3 days / fallback" if price_info.get("days_old", 0) > 3 or price_info.get("is_fallback") else "Fresh daily arrival"
        steps.append({
            "tool": "get_mandi_prices",
            "args": {
                "crop": active_crop,
                "district": active_district,
                "modal": price_info["modal_price"],
                "min": price_info["min_price"],
                "max": price_info["max_price"]
            },
            "result_summary": f"Modal: ₹{price_info['modal_price']}/qtl (₹{price_info['price_per_kg']}/kg) | Range: ₹{price_info['min_price']} - ₹{price_info['max_price']} at {price_info['mandi']} on {price_info['as_of_date']} ({price_info['source']}) [{freshness_note}]"
        })
        what_we_checked.append("check_prices")

    # Step: Price Trend
    if intent in ["price_check", "sell_or_hold", "general"]:
        trend_info = get_price_trend(crop=active_crop, district=active_district, mandi=active_district)
        steps.append({
            "tool": "get_price_trend",
            "args": {"crop": active_crop, "district": active_district},
            "result_summary": f"7-day trend: {trend_info['pct_change_7d']:+.1f}% ({trend_info['direction']}), Volatility: ₹{trend_info['volatility']}"
        })
        what_we_checked.append("check_trend")

    # Step: Weather Forecast
    if intent in ["sell_or_hold", "weather", "general"]:
        weather_info = get_weather_forecast(district=active_district)
        steps.append({
            "tool": "get_weather_forecast",
            "args": {"district": active_district},
            "result_summary": f"48h Heavy Rain: {weather_info['heavy_rain_next_48h']} | 5-day Rain: {weather_info['total_rain_5d_mm']}mm"
        })
        what_we_checked.append("check_weather")

    # Step: MSP Lookup
    if intent in ["sell_or_hold", "price_check", "general"]:
        msp_info = get_msp(crop=active_crop)
        msp_disp = f"₹{msp_info['msp_price_per_quintal']}/qtl" if msp_info["has_msp"] else "None"
        steps.append({
            "tool": "get_msp",
            "args": {"crop": active_crop},
            "result_summary": f"Statutory MSP: {msp_disp} | Perishability: {msp_info['perishability']}"
        })
        what_we_checked.append("check_msp")

    # Step: Nearby Mandi Comparison
    if intent in ["best_mandi", "sell_or_hold"]:
        nearby_mandis_info = compare_nearby_mandis(crop=active_crop, district=active_district)
        best_m = nearby_mandis_info.get("best_mandi", {})
        steps.append({
            "tool": "compare_nearby_mandis",
            "args": {"crop": active_crop, "district": active_district, "radius_km": 150},
            "result_summary": f"Top Mandi: {best_m.get('mandi', 'Local')} | Net: ₹{best_m.get('net_price')}/qtl | Gain: +₹{nearby_mandis_info.get('potential_gain_per_qtl', 0)}/qtl"
        })
        what_we_checked.append("check_mandis")

    # ==========================================
    # 5. ACT (DECISIONS & REAL ACTIONS)
    # ==========================================
    if intent == "set_alert":
        alert_target = target_price or (price_info["modal_price"] * 1.1 if price_info else 3000.0)
        alert_res = create_price_alert(
            user_id=user_id,
            crop=active_crop,
            target_price=alert_target,
            mandi=active_district
        )
        actions.append({
            "type": "create_price_alert",
            "alert_id": alert_res["alert_id"],
            "target_price": alert_target,
            "crop": active_crop,
            "status": "active"
        })
        steps.append({
            "tool": "create_price_alert",
            "args": {"crop": active_crop, "target_price": alert_target, "mandi": active_district},
            "result_summary": f"Price alert registered in SQLite for ₹{alert_target}/qtl"
        })

    if price_info and (intent in ["sell_or_hold", "price_check", "general"]):
        trend_pct = trend_info["pct_change_7d"] if trend_info else 0.0
        trend_dir = trend_info["direction"] if trend_info else "STABLE"
        heavy_rain = weather_info["heavy_rain_next_48h"] if weather_info else False
        has_msp = msp_info["has_msp"] if msp_info else False
        msp_rate = msp_info.get("msp_price_per_quintal") if msp_info else None
        perishability = msp_info.get("perishability", "medium") if msp_info else "medium"

        recommendation = recommend_action(
            crop=active_crop,
            modal_price=price_info["modal_price"],
            trend_pct_7d=trend_pct,
            trend_direction=trend_dir,
            heavy_rain_next_48h=heavy_rain,
            has_msp=has_msp,
            msp_price=msp_rate,
            perishability=perishability
        )
        steps.append({
            "tool": "recommend_action",
            "args": {"crop": active_crop, "modal_price": price_info["modal_price"], "trend": trend_dir},
            "result_summary": f"Recommendation: {recommendation['action']} (Confidence: {int(recommendation['confidence']*100)}%)"
        })

    # WhatsApp Share action
    if price_info:
        action_val = recommendation["action"] if recommendation else "PRICE_INFO"
        primary_reason = recommendation["primary_reason"] if recommendation else f"Current market rate at {price_info['mandi']}"
        share_data = make_share_summary(
            crop=active_crop,
            action=action_val,
            price=price_info["modal_price"],
            mandi=price_info["mandi"],
            trend_pct=trend_info["pct_change_7d"] if trend_info else 0.0,
            primary_reason=primary_reason,
            language=target_lang
        )
        actions.append({
            "type": "whatsapp_share",
            "text": share_data["text"],
            "url": share_data["whatsapp_url"]
        })

    # ==========================================
    # 6. DELIVER (GROUNDED SYNTHESIS IN TARGET LANGUAGE)
    # ==========================================
    llm_reply = None
    if llm_client.is_available():
        system_inst = get_system_prompt(target_lang)
        context_payload = {
            "target_language": target_lang,
            "crop": active_crop,
            "mandi": active_district,
            "price_data": price_info,
            "trend_data": trend_info,
            "weather_data": weather_info,
            "msp_data": msp_info,
            "nearby_mandis": nearby_mandis_info,
            "recommendation": recommendation
        }
        prompt = (
            f"You are KisanSaathi. Formulate the final response for the farmer strictly using this verified data:\n"
            f"{context_payload}\n"
            f"Respond ONLY in {target_lang} using native script. Cite exact numbers, sources, and dates."
        )
        llm_reply = llm_client.generate(prompt=prompt, system_instruction=system_inst)

    if not llm_reply:
        llm_reply = _synthesize_grounded_reply_12lang(
            language=target_lang,
            intent=intent,
            crop=active_crop,
            district=active_district,
            price_info=price_info,
            trend_info=trend_info,
            weather_info=weather_info,
            msp_info=msp_info,
            nearby_mandis_info=nearby_mandis_info,
            recommendation=recommendation,
            target_price=target_price,
            quantity=quantity
        )

    log_query(user_id, message, llm_reply, target_lang, intent, crop=active_crop, mandi=active_district)

    return {
        "reply": llm_reply,
        "language": target_lang,
        "crop": active_crop,
        "district": active_district,
        "steps": steps,
        "what_we_checked": what_we_checked,
        "recommendation": recommendation,
        "price_info": price_info,
        "trend_info": trend_info,
        "nearby_mandis": nearby_mandis_info,
        "weather": weather_info,
        "actions": actions
    }


def _synthesize_grounded_reply_12lang(
    language: str,
    intent: str,
    crop: str,
    district: str,
    price_info: Optional[Dict[str, Any]],
    trend_info: Optional[Dict[str, Any]],
    weather_info: Optional[Dict[str, Any]],
    msp_info: Optional[Dict[str, Any]],
    nearby_mandis_info: Optional[Dict[str, Any]],
    recommendation: Optional[Dict[str, Any]],
    target_price: Optional[float] = None,
    quantity: Optional[str] = None
) -> str:
    """
    Synthesize grounded, zero-hallucination advisory across all 12 Indian languages.
    """
    p = price_info or {}
    modal = p.get("modal_price", 0)
    per_kg = p.get("price_per_kg", modal / 100.0)
    date_str = p.get("as_of_date", "")
    source_str = "Agmarknet"
    days_old = p.get("days_old", 0)
    is_fallback = p.get("is_fallback", False)

    loc_crop = get_localized_crop(crop, language) or crop
    loc_mandi = get_localized_place(district, language) or district
    action = recommendation.get("action", "SELL_NOW") if recommendation else "SELL_NOW"
    reasons = recommendation.get("reasons", []) if recommendation else []
    trend_pct = trend_info.get("pct_change_7d", 0.0) if trend_info else 0.0

    # Localized action titles (Strictly in target language native script, NO English leftovers)
    ACTION_NAMES = {
        "SELL_NOW": {
            "en": "SELL NOW", "mr": "विक्री करा", "hi": "तुरंत बेचें",
            "gu": "તરત વેચો", "ta": "உடனே விற்கவும்", "te": "వెంటనే అమ్మండి",
            "kn": "ತಕ್ಷಣ ಮಾರಿ", "ml": "ഉടൻ വിൽക്കുക", "bn": "এখনই বিক্রি করুন",
            "pa": "ਹੁਣੇ ਵੇਚੋ", "or": "ଏବେ ବିକ୍ରୟ କରନ୍ତୁ", "as": "এতিয়াই বিক্ৰী কৰক"
        },
        "HOLD": {
            "en": "HOLD", "mr": "थांबा", "hi": "रुकें / प्रतीक्षा करें",
            "gu": "રાહ જુઓ", "ta": "காத்திருக்கவும்", "te": "வேచి ఉండండి",
            "kn": "ಕಾಯಿರಿ", "ml": "കാത്തിരിക്കുക", "bn": "অপেক্ষা করুন",
            "pa": "ਉਡੀਕ ਕਰੋ", "or": "ଅପେକ୍ଷା କରନ୍ତୁ", "as": "অপেক্ষা কৰক"
        },
        "SHIFT_MANDI": {
            "en": "SHIFT MANDI", "mr": "दुसऱ्या मंडीत विक्री करा", "hi": "दूसरी मंडी ले जाएं",
            "gu": "બીજા યાર્ડમાં વેચો", "ta": "வேறு சந்தையில் விற்கவும்", "te": "వేరే మార్కెట్‌లో అమ్మండి",
            "kn": "ಬೇರೆ ಮಂಡಿಯಲ್ಲಿ ಮಾರಿ", "ml": "മറ്റൊരു മാർക്കറ്റിൽ വിൽക്കുക", "bn": "অন্য মন্ডিতে বিক্রি করুন",
            "pa": "ਦੂਜੀ ਮੰਡੀ ਵਿੱਚ ਵੇਚੋ", "or": "ଅନ୍ୟ ମଣ୍ଡିରେ ବିକ୍ରୟ କରନ୍ତୁ", "as": "অন্য বজাৰত বিক্ৰী কৰক"
        }
    }

    act_str = ACTION_NAMES.get(action, {}).get(language, action)

    # 1. Price alert confirmation
    if intent == "set_alert" and target_price:
        ALERT_TEMPLATES = {
            "mr": f"✅ **अलर्ट नोंदवला गेला आहे!**\n\nजेव्हा {loc_mandi} मध्ये {loc_crop} चे दर **₹{target_price:,.0f} प्रति क्विंटल** पोहोचतील, तेव्हा तुम्हाला सूचना दिली जाईल.\n\n📊 चालू भाव: **₹{modal:,.0f}/क्विंटल** (₹{per_kg:.1f}/किलो)\n📅 तारीख: {date_str} | स्रोत: {source_str}\n\n📌 _हे मार्गदर्शन आहे, हमी नाही._",
            "hi": f"✅ **मूल्य अलर्ट सेट हो गया है!**\n\nजैसे ही {loc_mandi} में {loc_crop} का भाव **₹{target_price:,.0f} प्रति क्विंटल** पहुंचेगा, आपको सूचना मिल जाएगी।\n\n📊 वर्तमान भाव: **₹{modal:,.0f}/क्विंटल** (₹{per_kg:.1f}/किलो)\n📅 दिनांक: {date_str} | स्रोत: {source_str}\n\n📌 _यह केवल मार्गदर्शन है, गारंटी नहीं।_",
            "en": f"✅ **Price Alert Activated!**\n\nAlert registered for {loc_crop} in {loc_mandi} at **₹{target_price:,.0f}/quintal**.\n\n📊 Current Price: **₹{modal:,.0f}/quintal** (₹{per_kg:.1f}/kg)\n📅 Date: {date_str} | Source: {source_str}\n\n📌 _This is advisory guidance, not a commercial guarantee._",
            "gu": f"✅ **ભાવ એલર્ટ સક્રિય થયું છે!**\n\nજ્યારે {loc_mandi} માં {loc_crop} નો ભાવ **₹{target_price:,.0f} પ્રતિ ક્વિન્ટલ** પહોંચશે, ત્યારે તમને જાણ કરવામાં આવશે.\n\n📊 વર્તમાન ભાવ: **₹{modal:,.0f}/ક્વિન્ટલ**\n📅 તારીખ: {date_str} | સ્રોત: {source_str}\n\n📌 _આ માત્ર માર્ગદર્શન છે._",
            "ta": f"✅ **விலை எச்சரிக்கை அமைக்கப்பட்டது!**\n\n{loc_mandi} சந்தையில் {loc_crop} விலை **₹{target_price:,.0f} / குவிண்டால்** எட்டும்போது உங்களுக்கு தகவல் தெரிவிக்கப்படும்.\n\n📊 தற்போதைய விலை: **₹{modal:,.0f}/குவிண்டால்**\n📅 தேதி: {date_str} | ஆதாரம்: {source_str}\n\n📌 _இது ஒரு வழிகாட்டல் மட்டுமே._",
            "te": f"✅ **ధర హెచ్చరిక సెట్ చేయబడింది!**\n\n{loc_mandi} మార్కెట్‌లో {loc_crop} ధర **₹{target_price:,.0f} క్వింటాలుకు** చేరినప్పుడు మీకు సమాచారం అందుతుంది.\n\n📊 ప్రస్తుత ధర: **₹{modal:,.0f}/క్వింటాల్**\n📅 తేదీ: {date_str} | వనరు: {source_str}\n\n📌 _ఇది కేవలం మార్గదర్శక సలహా మాత్రమే._",
            "kn": f"✅ **ಬೆಲೆ ಎಚ್ಚರಿಕೆ ಸಕ್ರಿಯಗೊಂಡಿದೆ!**\n\n{loc_mandi} ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ {loc_crop} ದರ **₹{target_price:,.0f} ಕ್ವಿಂಟಾಲ್‌ಗೆ** ತಲುಪಿದಾಗ ನಿಮಗೆ ತಿಳಿಸಲಾಗುವುದು.\n\n📊 ಪ್ರಸ್ತುತ ದರ: **₹{modal:,.0f}/ಕ್ವಿಂಟಾಲ್**\n📅 ದಿನಾಂಕ: {date_str} | ಮೂಲ: {source_str}\n\n📌 _ಇದು ಮಾರ್ಗದರ್ಶನ ಮಾತ್ರ._",
            "ml": f"✅ **വില അലേർട്ട് സജ്ജീകരിച്ചു!**\n\n{loc_mandi} വിപണിയിൽ {loc_crop} വില **₹{target_price:,.0f} ക്വിന്റലിന്** എത്തുമ്പോൾ അറിയിപ്പ് ലഭിക്കും.\n\n📊 നിലവിലെ വില: **₹{modal:,.0f}/ക്വിന്റൽ**\n📅 തീയതി: {date_str} | സ്രോതസ്സ്: {source_str}\n\n📌 _ഇത് മാർഗ്ഗനിർദ്ദേശം മാത്രമാണ്._",
            "bn": f"✅ **মূল্য অ্যালার্ট সক্রিয় করা হয়েছে!**\n\nযখন {loc_mandi} মন্ডিতে {loc_crop} দর **₹{target_price:,.0f} প্রতি কুইন্টাল** পৌঁছাবে, তখন আপনাকে জানানো হবে।\n\n📊 বর্তমান দর: **₹{modal:,.0f}/কুইন্টাল**\n📅 তারিখ: {date_str} | তথ্যসূত্র: {source_str}\n\n📌 _এটি কেবল একটি পরামর্শ, বাণিজ্যিক গ্যারান্টি নয়।_",
            "pa": f"✅ **ਭਾਅ ਅਲਰਟ ਸੈੱਟ ਹੋ ਗਿਆ ਹੈ!**\n\nਜਦੋਂ {loc_mandi} ਵਿੱਚ {loc_crop} ਦਾ ਭਾਅ **₹{target_price:,.0f} ਪ੍ਰਤੀ ਕੁਇੰਟਲ** ਪਹੁੰਚੇਗਾ, ਤੁਹਾਨੂੰ ਸੂਚਿਤ ਕੀਤਾ ਜਾਵੇਗਾ।\n\n📊 ਮੌਜੂਦਾ ਭਾਅ: **₹{modal:,.0f}/ਕੁਇੰਟਲ**\n📅 ਤਾਰੀਖ਼: {date_str} | ਸਰੋਤ: {source_str}\n\n📌 _ਇਹ ਸਿਰਫ਼ ਸਲਾਹ ਹੈ, ਗਾਰੰਟੀ ਨਹੀਂ।_",
            "or": f"✅ **ଦର ଆଲର୍ଟ ସକ୍ରିୟ ହେଲା!**\n\nଯେତେବେଳେ {loc_mandi} ମଣ୍ଡିରେ {loc_crop} ଦର **₹{target_price:,.0f} ପ୍ରତି କ୍ୱିଣ୍ଟାଲ** ପହଞ୍ଚିବ, ଆପଣଙ୍କୁ ସୂଚନା ମିଳିବ।\n\n📊 ବର୍ତ୍ତମାନର ଦର: **₹{modal:,.0f}/କ୍ୱିଣ୍ଟାଲ**\n📅 ତାରିଖ: {date_str} | ଉତ୍ସ: {source_str}\n\n📌 _ଏହା କେବଳ ପରାମର୍ଶ ଅଟେ।_",
            "as": f"✅ **মূল্যৰ এলাৰ্ট সক্ৰিয় হ'ল!**\n\nযেতিয়া {loc_mandi} বজাৰত {loc_crop}ৰ দৰ **₹{target_price:,.0f} প্ৰতি কুইণ্টল** পাবগৈ, তেতিয়া আপোনাক জনোৱা হ'ব।\n\n📊 বৰ্তমানৰ দৰ: **₹{modal:,.0f}/কুইণ্টল**\n📅 তাৰিখ: {date_str} | উৎস: {source_str}\n\n📌 _এইটো কেৱল এক পৰামৰ্শহে।_"
        }
        return ALERT_TEMPLATES.get(language, ALERT_TEMPLATES["en"])

    # 2. Nearby Mandi Comparison
    if intent == "best_mandi" and nearby_mandis_info:
        best_m = nearby_mandis_info.get("best_mandi", {})
        loc_best_mandi = get_localized_place(best_m.get("mandi", ""), language) or best_m.get("mandi", "")
        gain = nearby_mandis_info.get("potential_gain_per_qtl", 0)

        BEST_MANDI_TEMPLATES = {
            "mr": f"📍 **सर्वोत्तम बाजारपेठ तुलना ({loc_crop}):**\n\n⭐ **शिफारस:** **{loc_best_mandi}**\n- निव्वळ भाव (वाहतूक खर्च वजा जाता): **₹{best_m.get('net_price')}/क्विंटल**\n- स्थानिक मंडीपेक्षा फायदा: **+₹{gain}/क्विंटल जास्तीचा नफा**\n\n📅 तारीख: {date_str} | स्रोत: {source_str}\n📌 _हे मार्गदर्शन आहे, हमी नाही._",
            "hi": f"📍 **नजदीकी मंडी तुलना ({loc_crop}):**\n\n⭐ **सबसे अच्छी मंडी:** **{loc_best_mandi}**\n- शुद्ध भाव (भाड़ा काटकर): **₹{best_m.get('net_price')}/क्विंटल**\n- स्थानीय मंडी से अधिक लाभ: **+₹{gain}/क्विंटल अधिक मुनाफा**\n\n📅 दिनांक: {date_str} | स्रोत: {source_str}\n📌 _यह केवल मार्गदर्शन है, गारंटी नहीं।_",
            "en": f"📍 **Nearby Mandi Comparison for {loc_crop}:**\n\n⭐ **Top Market:** **{loc_best_mandi}**\n- Net Realization (after transport): **₹{best_m.get('net_price')}/quintal**\n- Additional Gain: **+₹{gain}/quintal**\n\n📅 Date: {date_str} | Source: {source_str}\n📌 _This is advisory guidance, not a financial guarantee._",
            "gu": f"📍 **નજીકના માર્કેટ યાર્ડ સરખામણી ({loc_crop}):**\n\n⭐ **શ્રેષ્ઠ યાર્ડ:** **{loc_best_mandi}**\n- ચોખ્ખો ભાવ (ભાડું બાદ): **₹{best_m.get('net_price')}/ક્વિન્ટલ**\n- વધારાનો નફો: **+₹{gain}/ક્વિન્ટલ**\n\n📅 તારીખ: {date_str} | સ્રોત: {source_str}\n📌 _આ માત્ર માર્ગદર્શન છે._",
            "ta": f"📍 **அருகிலுள்ள சந்தைகள் ஒப்பீடு ({loc_crop}):**\n\n⭐ **சிறந்த சந்தை:** **{loc_best_mandi}**\n- நிகர விலை (போக்குவரத்து கழித்து): **₹{best_m.get('net_price')}/குவிண்டால்**\n- கூடுதல் லாபம்: **+₹{gain}/குவிண்டால்**\n\n📅 தேதி: {date_str} | ஆதாரம்: {source_str}\n📌 _இது ஒரு வழிகாட்டல் மட்டுமே._",
            "te": f"📍 **సమీప మార్కెట్ యార్డుల పోలిక ({loc_crop}):**\n\n⭐ **ఉత్తమ మార్కెట్:** **{loc_best_mandi}**\n- రవాణా ఖర్చు తీసివేసిన నికర ధర: **₹{best_m.get('net_price')}/క్వింటాల్**\n- అదనపు లాభం: **+₹{gain}/క్వింటాలుకు**\n\n📅 తేదీ: {date_str} | వనరు: {source_str}\n📌 _ఇది కేవలం మార్గదర్శక సలహా మాత్రమే._",
            "kn": f"📍 **ಹತ್ತಿರದ ಮಾರುಕಟ್ಟೆಗಳ ಹೋಲಿಕೆ ({loc_crop}):**\n\n⭐ **ಉತ್ತಮ ಮಾರುಕಟ್ಟೆ:** **{loc_best_mandi}**\n- ಸಾರಿಗೆ ವೆಚ್ಚ ಕಳೆದು ನಿವ್ವಳ ದರ: **₹{best_m.get('net_price')}/ಕ್ವಿಂಟಾಲ್**\n- ಹೆಚ್ಚುವರಿ ಲಾಭ: **+₹{gain}/ಕ್ವಿಂಟಾಲ್‌ಗೆ**\n\n📅 ದಿನಾಂಕ: {date_str} | ಮೂಲ: {source_str}\n📌 _ಇದು ಮಾರ್ಗದರ್ಶನ ಮಾತ್ರ._",
            "ml": f"📍 **സമീപത്തെ വിപണികളുടെ താരതമ്യം ({loc_crop}):**\n\n⭐ **മികച്ച മാർക്കറ്റ്:** **{loc_best_mandi}**\n- ഗതാഗതച്ചെലവ് കഴിഞ്ഞ് ലഭിക്കുന്ന തുക: **₹{best_m.get('net_price')}/ക്വിന്റൽ**\n- അധിക ലാഭം: **+₹{gain}/ക്വിന്റലിന്**\n\n📅 തീയതി: {date_str} | സ്രോതസ്സ്: {source_str}\n📌 _ഇത് മാർഗ്ഗനിർദ്ദേശം മാത്രമാണ്._",
            "bn": f"📍 **নিকটবর্তী মন্ডির তুলনা ({loc_crop}):**\n\n⭐ **সেরা মন্ডি:** **{loc_best_mandi}**\n- পরিবহন খরচ বাদ দিয়ে নিট দর: **₹{best_m.get('net_price')}/কুইন্টাল**\n- অতিরিক্ত লাভ: **+₹{gain}/কুইন্টাল**\n\n📅 তারিখ: {date_str} | তথ্যসূত্র: {source_str}\n📌 _এটি কেবল একটি পরামর্শ।_",
            "pa": f"📍 **ਨੇੜਲੀਆਂ ਮੰਡੀਆਂ ਦੀ ਤੁਲਨਾ ({loc_crop}):**\n\n⭐ **ਸਭ ਤੋਂ ਵਧੀਆ ਮੰਡੀ:** **{loc_best_mandi}**\n- ਕਿਰਾਇਆ ਕੱਟ ਕੇ ਸ਼ੁੱਧ ਭਾਅ: **₹{best_m.get('net_price')}/ਕੁਇੰਟਲ**\n- ਵਾਧੂ ਮੁਨਾਫ਼ਾ: **+₹{gain}/ਕੁਇੰਟਲ**\n\n📅 ਤਾਰੀਖ਼: {date_str} | ਸਰੋਤ: {source_str}\n📌 _ਇਹ ਸਿਰਫ਼ ਸਲਾਹ ਹੈ, ਗਾਰੰਟੀ ਨਹੀਂ।_",
            "or": f"📍 **ନିକଟସ୍ଥ ମଣ୍ଡି ତୁଳନା ({loc_crop}):**\n\n⭐ **ଶ୍ରେଷ୍ଠ ମଣ୍ଡି:** **{loc_best_mandi}**\n- ପରିବହନ ଖର୍ଚ୍ଚ ବାଦେ ନିଟ୍ ଦର: **₹{best_m.get('net_price')}/କ୍ୱିଣ୍ଟାଲ**\n- ଅତିରିକ୍ତ ଲାଭ: **+₹{gain}/କ୍ୱିଣ୍ଟାଲ**\n\n📅 ତାରିଖ: {date_str} | ଉତ୍ସ: {source_str}\n📌 _ଏହା କେବଳ ପରାମର୍ଶ ଅଟେ।_",
            "as": f"📍 **ওচৰৰ বজাৰসমূহৰ তুলনা ({loc_crop}):**\n\n⭐ **উত্তম বজাৰ:** **{loc_best_mandi}**\n- পৰিবহণ খৰচ বাদ দি নিগুট দৰ: **₹{best_m.get('net_price')}/কুইণ্টল**\n- অতিৰিক্ত লাভ: **+₹{gain}/কুইণ্টল**\n\n📅 তাৰিখ: {date_str} | উৎস: {source_str}\n📌 _এইটো কেৱল এক পৰামৰ্শহে।_"
        }
        return BEST_MANDI_TEMPLATES.get(language, BEST_MANDI_TEMPLATES["en"])

    # 3. Advisory & Price Check
    ADVISORY_TEMPLATES = {
        "mr": (
            f"💡 **सल्ला: [{act_str}]**\n\n"
            f"📊 **बाजारभाव आकडेवारी ({loc_mandi}):**\n"
            f"- सरासरी भाव: **₹{modal:,.0f}/क्विंटल** (₹{per_kg:.1f}/किलो)\n"
            f"- ७ दिवसांचा कल: **{trend_pct:+.1f}%**\n"
            f"- किमान/कमाल दर: ₹{p.get('min_price', modal):,.0f} - ₹{p.get('max_price', modal):,.0f}/क्विंटल\n"
            f"📅 तारीख: {date_str} | स्रोत: {source_str}\n\n"
            f"📌 _हे मार्गदर्शन आहे, हमी नाही. अंतिम निर्णय स्थानिक परिस्थिती पाहून घ्या._"
        ),
        "hi": (
            f"💡 **सलाह: [{act_str}]**\n\n"
            f"📊 **मंडी भाव विवरण ({loc_mandi}):**\n"
            f"- मॉडल भाव: **₹{modal:,.0f}/क्विंटल** (₹{per_kg:.1f}/किलो)\n"
            f"- 7 दिनों का रुझान: **{trend_pct:+.1f}%**\n"
            f"- न्यूनतम/अधिकतम: ₹{p.get('min_price', modal):,.0f} - ₹{p.get('max_price', modal):,.0f}/क्विंटल\n"
            f"📅 दिनांक: {date_str} | स्रोत: {source_str}\n\n"
            f"📌 _यह केवल मार्गदर्शन है, गारंटी नहीं। अंतिम फैसला अपनी सुविधा अनुसार लें।_"
        ),
        "en": (
            f"💡 **Recommendation: [{act_str}]**\n\n"
            f"📊 **Market Numbers ({loc_mandi}):**\n"
            f"- Modal Price: **₹{modal:,.0f}/quintal** (₹{per_kg:.1f}/kg)\n"
            f"- 7-Day Trend: **{trend_pct:+.1f}%**\n"
            f"- Range: ₹{p.get('min_price', modal):,.0f} - ₹{p.get('max_price', modal):,.0f}/quintal\n"
            f"📅 Date: {date_str} | Source: {source_str}\n\n"
            f"📌 _This is advisory guidance, not a financial guarantee. Please confirm with your local mandi trader before dispatch._"
        ),
        "gu": (
            f"💡 **સલાહ: [{act_str}]**\n\n"
            f"📊 **બજાર ભાવ ({loc_mandi}):**\n"
            f"- સરેરાશ ભાવ: **₹{modal:,.0f}/ક્વિન્ટલ** (₹{per_kg:.1f}/કિલો)\n"
            f"- ૭ દિવસનો ટ્રેન્ડ: **{trend_pct:+.1f}%**\n"
            f"- ન્યૂનતમ/મહત્તમ: ₹{p.get('min_price', modal):,.0f} - ₹{p.get('max_price', modal):,.0f}/ક્વિન્ટલ\n"
            f"📅 તારીખ: {date_str} | સ્રોત: {source_str}\n\n"
            f"📌 _આ માત્ર માર્ગદર્શન છે._"
        ),
        "ta": (
            f"💡 **ஆலோசனை: [{act_str}]**\n\n"
            f"📊 **சந்தை நிலவரம் ({loc_mandi}):**\n"
            f"- சராசரி விலை: **₹{modal:,.0f}/குவிண்டால்** (₹{per_kg:.1f}/கிலோ)\n"
            f"- 7 நாள் போக்கு: **{trend_pct:+.1f}%**\n"
            f"- குறைந்தபட்ச/அதிகபட்ச: ₹{p.get('min_price', modal):,.0f} - ₹{p.get('max_price', modal):,.0f}/குவிண்டால்\n"
            f"📅 தேதி: {date_str} | ஆதாரம்: {source_str}\n\n"
            f"📌 _இது ஒரு வழிகாட்டல் மட்டுமே._"
        ),
        "te": (
            f"💡 **సలహా: [{act_str}]**\n\n"
            f"📊 **మార్కెట్ ధరలు ({loc_mandi}):**\n"
            f"- సగటు ధర: **₹{modal:,.0f}/క్వింటాల్** (₹{per_kg:.1f}/కిలో)\n"
            f"- 7 రోజుల ట్రెండ్: **{trend_pct:+.1f}%**\n"
            f"- కనిష్ట/గరిష్ట: ₹{p.get('min_price', modal):,.0f} - ₹{p.get('max_price', modal):,.0f}/క్వింటాల్\n"
            f"📅 తేదీ: {date_str} | వనరు: {source_str}\n\n"
            f"📌 _ఇది కేవలం మార్గదర్శక సలహా మాత్రమే._"
        ),
        "kn": (
            f"💡 **ಸಲಹೆ: [{act_str}]**\n\n"
            f"📊 **ಮಾರುಕಟ್ಟೆ ದರಗಳು ({loc_mandi}):**\n"
            f"- ಸರಾಸರಿ ದರ: **₹{modal:,.0f}/ಕ್ವಿಂಟಾಲ್** (₹{per_kg:.1f}/ಕೆಜಿ)\n"
            f"- 7 ದಿನಗಳ ಟ್ರೆಂಡ್: **{trend_pct:+.1f}%**\n"
            f"- ಕನಿಷ್ಠ/ಗರಿಷ್ಠ: ₹{p.get('min_price', modal):,.0f} - ₹{p.get('max_price', modal):,.0f}/ಕ್ವಿಂಟಾಲ್\n"
            f"📅 ದಿನಾಂಕ: {date_str} | ಮೂಲ: {source_str}\n\n"
            f"📌 _ಇದು ಮಾರ್ಗದರ್ಶನ ಮಾತ್ರ._"
        ),
        "ml": (
            f"💡 **ഉപദേശം: [{act_str}]**\n\n"
            f"📊 **വിപണി നിരക്കുകൾ ({loc_mandi}):**\n"
            f"- ശരാശരി വില: **₹{modal:,.0f}/ക്വിന്റൽ** (₹{per_kg:.1f}/കിലോ)\n"
            f"- 7 ദിവസത്തെ മാറ്റം: **{trend_pct:+.1f}%**\n"
            f"- കുറഞ്ഞ/കൂടിയ നിരക്ക്: ₹{p.get('min_price', modal):,.0f} - ₹{p.get('max_price', modal):,.0f}/ക്വിന്റൽ\n"
            f"📅 തീയതി: {date_str} | സ്രോതസ്സ്: {source_str}\n\n"
            f"📌 _ഇത് മാർഗ്ഗനിർദ്ദേശം മാത്രമാണ്._"
        ),
        "bn": (
            f"💡 **পরামর্শ: [{act_str}]**\n\n"
            f"📊 **বাজারদর বিবরণ ({loc_mandi}):**\n"
            f"- গড় দর: **₹{modal:,.0f}/কুইন্টাল** (₹{per_kg:.1f}/কেজি)\n"
            f"- ৭ দিনের ধারা: **{trend_pct:+.1f}%**\n"
            f"- সর্বনিম্ন/সর্বোচ্চ: ₹{p.get('min_price', modal):,.0f} - ₹{p.get('max_price', modal):,.0f}/কুইন্টাল\n"
            f"📅 তারিখ: {date_str} | তথ্যসূত্র: {source_str}\n\n"
            f"📌 _এটি কেবল একটি পরামর্শ, বাণিজ্যিক গ্যারান্টি নয়।_"
        ),
        "pa": (
            f"💡 **ਸਲਾਹ: [{act_str}]**\n\n"
            f"📊 **ਮੰਡੀ ਭਾਅ ਵੇਰਵਾ ({loc_mandi}):**\n"
            f"- ਮਾਡਲ ਭਾਅ: **₹{modal:,.0f}/ਕੁਇੰਟਲ** (₹{per_kg:.1f}/ਕਿਲੋ)\n"
            f"- 7 ਦਿਨਾਂ ਦਾ ਰੁਝਾਨ: **{trend_pct:+.1f}%**\n"
            f"- ਘੱਟੋ-ਘੱਟ/ਵੱਧ ਤੋਂ ਵੱਧ: ₹{p.get('min_price', modal):,.0f} - ₹{p.get('max_price', modal):,.0f}/ਕੁਇੰਟਲ\n"
            f"📅 ਤਾਰੀਖ਼: {date_str} | ਸਰੋਤ: {source_str}\n\n"
            f"📌 _ਇਹ ਸਿਰਫ਼ ਸਲਾਹ ਹੈ, ਗਾਰੰਟੀ ਨਹੀਂ।_"
        ),
        "or": (
            f"💡 **ପରାମର୍ଶ: [{act_str}]**\n\n"
            f"📊 **ମଣ୍ଡି ଦର ବିବରଣୀ ({loc_mandi}):**\n"
            f"- ମଡେଲ ଦର: **₹{modal:,.0f}/କ୍ୱିଣ୍ଟାଲ** (₹{per_kg:.1f}/କେଜି)\n"
            f"- ୭ ଦିନର ଟ୍ରେଣ୍ଡ: **{trend_pct:+.1f}%**\n"
            f"- ସର୍ବନିମ୍ନ/ସର୍ବାଧିକ: ₹{p.get('min_price', modal):,.0f} - ₹{p.get('max_price', modal):,.0f}/କ୍ୱିଣ୍ଟାଲ\n"
            f"📅 ତାରିଖ: {date_str} | ଉତ୍ସ: {source_str}\n\n"
            f"📌 _ଏହା କେବଳ ପରାମର୍ଶ ଅଟେ।_"
        ),
        "as": (
            f"💡 **পৰামৰ্শ: [{act_str}]**\n\n"
            f"📊 **বজাৰ দৰৰ বিৱৰণ ({loc_mandi}):**\n"
            f"- গড় দৰ: **₹{modal:,.0f}/কুইণ্টল** (₹{per_kg:.1f}/কেজি)\n"
            f"- ৭ দিনৰ গতি: **{trend_pct:+.1f}%**\n"
            f"- সৰ্বনিম্ন/সৰ্বোচ্চ: ₹{p.get('min_price', modal):,.0f} - ₹{p.get('max_price', modal):,.0f}/কুইণ্টল\n"
            f"📅 তাৰিখ: {date_str} | উৎস: {source_str}\n\n"
            f"📌 _এইটো কেৱল এক পৰামৰ্শহে।_"
        )
    }

    return ADVISORY_TEMPLATES.get(language, ADVISORY_TEMPLATES["en"])
