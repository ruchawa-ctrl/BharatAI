import os
import csv
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import httpx

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
CSV_PATH = os.path.join(DATA_DIR, "sample_mandi_prices.csv")
DATA_GOV_API_KEY = os.getenv("DATA_GOV_API_KEY", "")


def _query_csv_prices(crop: str, state: Optional[str] = None, district: Optional[str] = None, mandi: Optional[str] = None) -> List[Dict[str, Any]]:
    if not os.path.exists(CSV_PATH):
        return []

    crop_lower = crop.strip().lower()
    district_lower = district.strip().lower() if district else None
    mandi_lower = mandi.strip().lower() if mandi else None
    state_lower = state.strip().lower() if state else None

    matches = []
    with open(CSV_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["crop"].strip().lower() != crop_lower:
                continue
            if mandi_lower and mandi_lower not in row["mandi"].strip().lower():
                continue
            if district_lower and district_lower not in row["district"].strip().lower():
                continue
            if state_lower and state_lower not in row["state"].strip().lower():
                continue
            matches.append(row)

    # Sort matches by date descending
    matches.sort(key=lambda x: x["date"], reverse=True)
    return matches


def get_mandi_prices(crop: str, state: Optional[str] = None, district: Optional[str] = None, mandi: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch the latest modal, min, and max mandi prices for a given crop.
    Attempts live Agmarknet API via data.gov.in if API key is provided,
    otherwise cleanly falls back to bundled 30-day realistic Agmarknet dataset.
    Always returns source, as_of_date, and freshness information.
    """
    # Attempt live API if key is present
    if DATA_GOV_API_KEY:
        try:
            url = f"https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key={DATA_GOV_API_KEY}&format=json&filters[commodity]={crop}"
            if state:
                url += f"&filters[state]={state}"
            if district:
                url += f"&filters[district]={district}"
            
            with httpx.Client(timeout=3.0) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    records = resp.json().get("records", [])
                    if records:
                        rec = records[0]
                        arrival_date = rec.get("arrival_date", datetime.now().strftime("%Y-%m-%d"))
                        modal_price = float(rec.get("modal_price", 0))
                        min_price = float(rec.get("min_price", modal_price * 0.9))
                        max_price = float(rec.get("max_price", modal_price * 1.1))
                        
                        return {
                            "crop": crop,
                            "mandi": rec.get("market", mandi or district or "Agmarknet Central"),
                            "district": rec.get("district", district or "Unknown"),
                            "state": rec.get("state", state or "India"),
                            "variety": rec.get("variety", "Standard"),
                            "modal_price": modal_price,
                            "min_price": min_price,
                            "max_price": max_price,
                            "price_per_kg": round(modal_price / 100.0, 2),
                            "as_of_date": arrival_date,
                            "source": "Agmarknet Live (data.gov.in)",
                            "is_fallback": False,
                            "days_old": 0
                        }
        except Exception:
            # Silently fall back to bundled data on any network or API issue
            pass

    # Fallback to local 30-day CSV dataset
    matches = _query_csv_prices(crop=crop, state=state, district=district, mandi=mandi)
    
    # If no exact district match, search for crop across nearest available mandis in the state
    if not matches and district:
        matches = _query_csv_prices(crop=crop, state=state)
    
    # If still no match, search for crop generally
    if not matches:
        matches = _query_csv_prices(crop=crop)

    if matches:
        latest = matches[0]
        as_of_date = latest["date"]
        
        # Calculate days old
        try:
            d1 = datetime.strptime(as_of_date, "%Y-%m-%d")
            days_old = (datetime.now() - d1).days
        except Exception:
            days_old = 0

        modal_price = float(latest["modal_price"])
        min_price = float(latest["min_price"])
        max_price = float(latest["max_price"])

        return {
            "crop": crop,
            "mandi": latest["mandi"],
            "district": latest["district"],
            "state": latest["state"],
            "variety": latest["variety"],
            "modal_price": modal_price,
            "min_price": min_price,
            "max_price": max_price,
            "price_per_kg": round(modal_price / 100.0, 2),
            "as_of_date": as_of_date,
            "source": "Agmarknet Historical (Sample CSV)",
            "is_fallback": True,
            "days_old": max(0, days_old)
        }

    # Baseline fallback if crop is recognized but no CSV rows exist
    default_price = 2000.0
    return {
        "crop": crop,
        "mandi": mandi or district or "Standard Mandi",
        "district": district or "Central District",
        "state": state or "Maharashtra",
        "variety": "Standard",
        "modal_price": default_price,
        "min_price": default_price * 0.9,
        "max_price": default_price * 1.1,
        "price_per_kg": default_price / 100.0,
        "as_of_date": datetime.now().strftime("%Y-%m-%d"),
        "source": "Estimated Agro-Benchmark",
        "is_fallback": True,
        "days_old": 0
    }
