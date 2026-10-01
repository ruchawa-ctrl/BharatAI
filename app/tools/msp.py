import os
import json
from typing import Dict, Any, Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
MSP_PATH = os.path.join(DATA_DIR, "msp.json")

_msp_cache = None


def _load_msp_data() -> Dict[str, Any]:
    global _msp_cache
    if _msp_cache is None:
        if os.path.exists(MSP_PATH):
            with open(MSP_PATH, "r", encoding="utf-8") as f:
                _msp_cache = json.load(f)
        else:
            _msp_cache = {}
    return _msp_cache


def get_msp(crop: str) -> Dict[str, Any]:
    """
    Lookup government Minimum Support Price (MSP) for a crop.
    Returns MSP rate per quintal, year, perishability, and policy classification.
    """
    msp_data = _load_msp_data()
    crop_title = crop.strip().capitalize()
    
    # Direct match or case-insensitive search
    matched_entry = msp_data.get(crop_title)
    if not matched_entry:
        for k, v in msp_data.items():
            if k.lower() == crop.strip().lower():
                matched_entry = v
                crop_title = k
                break

    if matched_entry:
        msp_price = matched_entry.get("msp_price_per_quintal")
        has_msp = msp_price is not None
        return {
            "crop": crop_title,
            "has_msp": has_msp,
            "msp_price_per_quintal": msp_price,
            "year": matched_entry.get("year", "2024-25"),
            "season": matched_entry.get("season", "Kharif/Rabi"),
            "perishability": matched_entry.get("perishability", "medium"),
            "description": matched_entry.get("description", "")
        }

    return {
        "crop": crop_title,
        "has_msp": False,
        "msp_price_per_quintal": None,
        "year": "2024-25",
        "season": "Open Market",
        "perishability": "medium",
        "description": f"No statutory central MSP announced for {crop_title}."
    }
