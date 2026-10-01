import os
import time
import logging
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

from app.db import (
    init_db, get_user_alerts, add_alert, get_active_alerts, mark_alert_triggered,
    add_reminder, get_user_reminders, delete_reminder, save_crop_history
)

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("kisansaathi")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing KisanSaathi SQLite database...")
    init_db()
    logger.info("KisanSaathi startup complete.")
    yield


app = FastAPI(
    title="KisanSaathi API",
    description="Multilingual Mandi Advisory Agent for Indian Farmers (BharatAgentic Hackathon)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lightweight in-memory rate limiter (max 60 requests per minute per client)
_rate_limits = defaultdict(list)


@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    # Rate limit chat, analyze-crop, and voice endpoints
    if request.url.path in ["/chat", "/analyze-crop", "/voice/chat"]:
        client_ip = request.client.host if request.client else "anonymous"
        now = time.time()
        # Keep requests within last 60 seconds
        _rate_limits[client_ip] = [t for t in _rate_limits[client_ip] if now - t < 60]
        if len(_rate_limits[client_ip]) > 60:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"error": "Too many requests. Please wait a moment."}
            )
        _rate_limits[client_ip].append(now)

    response = await call_next(request)
    return response


# Request and response models
class ChatRequest(BaseModel):
    user_id: str = Field(default="farmer_default", max_length=100, description="Unique farmer or session ID")
    message: str = Field(..., min_length=1, max_length=2000, description="User query in Hindi, Marathi, English, Gujarati, or Tamil")
    language: str = Field(default="auto", description="hi|mr|en|gu|ta|auto")

    @field_validator("message")
    def message_must_not_be_blank(cls, v):
        if not v or not v.strip():
            raise ValueError("Message cannot be empty or whitespace only")
        return v.strip()


class AgentStep(BaseModel):
    tool: str
    args: Dict[str, Any]
    result_summary: str


class ChatResponse(BaseModel):
    reply: str
    language: str
    crop: Optional[str] = None
    district: Optional[str] = None
    steps: List[AgentStep] = []
    what_we_checked: List[str] = []
    recommendation: Optional[Dict[str, Any]] = None
    price_info: Optional[Dict[str, Any]] = None
    trend_info: Optional[Dict[str, Any]] = None
    nearby_mandis: Optional[Dict[str, Any]] = None
    weather: Optional[Dict[str, Any]] = None
    actions: List[Dict[str, Any]] = []


class AlertCreateRequest(BaseModel):
    user_id: str = Field(..., max_length=100)
    crop: str = Field(..., min_length=1, max_length=100)
    target_price: float = Field(..., gt=0, lt=100000)
    mandi: Optional[str] = Field(default=None, max_length=100)
    condition: str = Field(default="above")


@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "ok",
        "app": "KisanSaathi",
        "version": "1.0.0",
        "db": "connected",
        "timestamp": int(time.time())
    }


@app.get("/api/mandi-rates", tags=["Rates"])
async def get_mandi_rates_snapshot(district: str = "Nashik"):
    """
    Returns today's snapshot of commodity rates for the selected district or state.
    """
    from app.tools.prices import get_mandi_prices
    from app.tools.trend import get_price_trend

    featured_crops = ["Onion", "Tomato", "Potato", "Wheat", "Soybean", "Cotton", "Tur"]
    rates = []
    for crop in featured_crops:
        p = get_mandi_prices(crop=crop, district=district)
        t = get_price_trend(crop=crop, district=district, days=7)
        rates.append({
            "crop": crop,
            "mandi": p.get("mandi", district),
            "district": p.get("district", district),
            "modal_price": p.get("modal_price", 0),
            "trend_pct_7d": t.get("pct_change_7d", 0.0),
            "direction": t.get("direction", "STABLE"),
            "as_of_date": p.get("as_of_date", "2026-09-30"),
            "source": p.get("source", "Agmarknet")
        })
    return {"district": district, "rates": rates}


@app.post("/chat", response_model=ChatResponse, tags=["Agent"])
async def chat_endpoint(request: ChatRequest):
    try:
        from app.agent import run_agent
        result = await run_agent(
            user_id=request.user_id,
            message=request.message,
            language=request.language
        )
        return result
    except Exception as e:
        logger.error(f"Unexpected error in /chat endpoint: {e}", exc_info=True)
        # Never crash: return resilient fallback advisory
        return ChatResponse(
            reply="माफ करा, तांत्रिक कारणास्तव माहिती लोड होण्यास वेळ लागत आहे. कृपया आपला प्रश्न पुन्हा विचारा. (Technical error handled safely).",
            language=request.language if request.language != "auto" else "mr",
            steps=[AgentStep(tool="exception_fallback", args={"error": str(e)}, result_summary="Graceful fallback recovery triggered.")],
            what_we_checked=[],
            recommendation=None,
            price_info=None,
            trend_info=None,
            nearby_mandis=None,
            weather=None,
            actions=[]
        )


@app.get("/alerts/{user_id}", tags=["Alerts"])
async def get_alerts_endpoint(user_id: str):
    alerts = get_user_alerts(user_id)
    return {"user_id": user_id, "alerts": alerts}


@app.post("/alerts", tags=["Alerts"])
async def create_alert_endpoint(req: AlertCreateRequest):
    alert_id = add_alert(
        user_id=req.user_id,
        crop=req.crop,
        target_price=req.target_price,
        mandi=req.mandi,
        condition=req.condition
    )
    return {"status": "success", "alert_id": alert_id, "message": f"Alert set for {req.crop} at ₹{req.target_price}"}


@app.post("/alerts/check", tags=["Alerts"])
async def check_alerts_endpoint():
    try:
        from app.tools.alerts import check_alerts
        triggered = check_alerts()
        return {"status": "checked", "triggered_count": len(triggered), "triggered_alerts": triggered}
    except Exception as e:
        logger.error(f"Error in check_alerts: {e}")
        return {"status": "checked", "triggered_count": 0, "triggered_alerts": [], "note": str(e)}


class ReminderCreateRequest(BaseModel):
    user_id: str = Field(default="farmer_default", max_length=100)
    crop: str = Field(..., max_length=100)
    issue_name: Optional[str] = None
    note: Optional[str] = None
    days: int = Field(default=3, ge=1, le=30)


@app.post("/analyze-crop", tags=["Vision"])
async def analyze_crop_endpoint(
    image: UploadFile = File(...),
    language: str = Form("en"),
    crop_hint: Optional[str] = Form(None),
    note: Optional[str] = Form(None),
    district: Optional[str] = Form(None),
    user_id: str = Form("default_farmer")
):
    try:
        from app.tools.vision import validate_image, analyze_crop_image, estimate_price_for_grade
        from app.tools.experts import find_expert_help
        from app.tools.recommend import recommend_action

        image_bytes = await image.read()
        steps = []

        # Step 1: Image validation and EXIF stripping
        val = validate_image(image_bytes, language=language)
        steps.append({
            "tool": "validate_image",
            "args": {"size_bytes": len(image_bytes), "filename": image.filename},
            "result_summary": f"Usable: {val['is_usable']}, Blur score: {round(val.get('blur_score', 0), 1)}"
        })

        # Step 2: Multimodal crop analysis
        analysis = analyze_crop_image(
            image_bytes=image_bytes,
            language=language,
            crop_hint=crop_hint,
            note=note,
            filename=image.filename
        )
        steps.append({
            "tool": "analyze_crop_image",
            "args": {"crop_hint": crop_hint, "language": language},
            "result_summary": f"Type: {analysis.image_type}, Assessment: {analysis.assessment}, Issue: {analysis.issue_name or 'N/A'}"
        })

        recommendation = None
        grade_pricing = None
        expert_help = None
        actions = []

        if analysis.image_type == "produce_quality":
            grade = analysis.produce_grade or "A"
            crop_to_price = analysis.crop or "Onion"
            grade_pricing = estimate_price_for_grade(
                crop=crop_to_price,
                mandi=district,
                grade=grade,
                language=language
            )
            steps.append({
                "tool": "estimate_price_for_grade",
                "args": {"crop": crop_to_price, "grade": grade},
                "result_summary": f"Grade {grade} estimated at {grade_pricing['price_range']} per qtl"
            })
            recommendation = recommend_action(
                crop=crop_to_price,
                modal_price=grade_pricing["estimated_price"],
                trend="STABLE" if grade != "C" else "FALLING",
                msp=None,
                weather_risk=(grade == "C")
            )
            steps.append({
                "tool": "recommend_action",
                "args": {"grade": grade, "estimated_price": grade_pricing["estimated_price"]},
                "result_summary": f"Recommendation: {recommendation['action']}"
            })
        elif analysis.image_type == "plant_problem":
            expert_help = find_expert_help(district=district, language=language)
            steps.append({
                "tool": "find_expert_help",
                "args": {"district": district, "language": language},
                "result_summary": f"KCC 1800-180-1551 & {expert_help['kvk_name']}"
            })
            if analysis.issue_name:
                share_summary = f"🌾 *KisanSaathi Crop Diagnosis*\nCrop: {analysis.crop or 'Crop'}\nIssue: {analysis.issue_name} ({analysis.confidence_level})\nSteps: {', '.join(analysis.immediate_steps[:2])}\nExpert Help: 1800-180-1551"
                actions.append({
                    "type": "whatsapp_share",
                    "text": share_summary,
                    "url": f"https://api.whatsapp.com/send?text={share_summary}"
                })
        elif analysis.image_type in ["not_crop", "unusable"]:
            steps.append({
                "tool": "retake_guidance",
                "args": {"type": analysis.image_type},
                "result_summary": "Guided farmer to upload a clear agricultural crop photo"
            })

        return {
            "analysis": analysis.dict(),
            "steps": steps,
            "recommendation": recommendation,
            "grade_pricing": grade_pricing,
            "expert_help": expert_help,
            "actions": actions
        }
    except Exception as e:
        logger.error(f"Error in /analyze-crop: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to analyze image: {str(e)}"}
        )


@app.post("/voice/chat", tags=["Voice"])
async def voice_chat_endpoint(
    audio: UploadFile = File(...),
    language: str = Form("en"),
    user_id: str = Form("default_farmer")
):
    try:
        from app.tools.voice import transcribe_audio, format_voice_reply
        from app.agent import run_agent

        audio_bytes = await audio.read()
        trans_res = transcribe_audio(
            audio_bytes=audio_bytes,
            filename=audio.filename,
            language=language
        )
        transcript = trans_res.get("transcript", "")
        
        chat_res = await run_agent(
            user_id=user_id,
            message=transcript,
            language=language
        )

        recommendation = chat_res.get("recommendation") if isinstance(chat_res, dict) else getattr(chat_res, "recommendation", {})
        reply_text = chat_res.get("reply", "") if isinstance(chat_res, dict) else getattr(chat_res, "reply", "")

        voice_text = format_voice_reply(
            recommendation=recommendation or {},
            reply_text=reply_text,
            language=language
        )

        res_dict = dict(chat_res) if isinstance(chat_res, dict) else chat_res.dict()
        res_dict["transcript"] = transcript
        res_dict["voice_reply"] = voice_text
        return res_dict
    except Exception as e:
        logger.error(f"Error in /voice/chat: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process voice query: {str(e)}"}
        )


@app.post("/reminders", tags=["Reminders"])
async def create_reminder_endpoint(req: ReminderCreateRequest):
    reminder_id = add_reminder(
        user_id=req.user_id,
        crop=req.crop,
        issue_name=req.issue_name,
        note=req.note,
        days=req.days
    )
    return {
        "status": "success",
        "reminder_id": reminder_id,
        "message": f"Reminder set for {req.crop} in {req.days} days"
    }


@app.get("/reminders/{user_id}", tags=["Reminders"])
async def get_reminders_endpoint(user_id: str):
    reminders = get_user_reminders(user_id)
    return {"user_id": user_id, "reminders": reminders}


@app.delete("/reminders/{reminder_id}", tags=["Reminders"])
async def delete_reminder_endpoint(reminder_id: int):
    delete_reminder(reminder_id)
    return {"status": "success", "message": f"Reminder {reminder_id} deactivated"}


# Serve frontend static files
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/", tags=["UI"])
    async def serve_index():
        return FileResponse(os.path.join(frontend_dir, "index.html"))
