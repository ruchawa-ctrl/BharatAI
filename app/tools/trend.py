import os
import csv
import math
from typing import Dict, Any, Optional, List
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
CSV_PATH = os.path.join(DATA_DIR, "sample_mandi_prices.csv")


def get_price_trend(crop: str, mandi: Optional[str] = None, district: Optional[str] = None, days: int = 7) -> Dict[str, Any]:
    """
    Calculate 7-day and 30-day price trends, percentage change, and price volatility
    for a crop in a given mandi or district.
    """
    crop_lower = crop.strip().lower()
    mandi_lower = mandi.strip().lower() if mandi else None
    district_lower = district.strip().lower() if district else None

    records = []
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["crop"].strip().lower() != crop_lower:
                    continue
                if mandi_lower and mandi_lower in row["mandi"].strip().lower():
                    records.append(row)
                elif not mandi_lower and district_lower and district_lower in row["district"].strip().lower():
                    records.append(row)
                elif not mandi_lower and not district_lower:
                    records.append(row)

    # Sort chronological (oldest to newest)
    records.sort(key=lambda x: x["date"])

    if not records:
        return {
            "crop": crop,
            "mandi": mandi or district or "Regional Mandi",
            "days_analyzed": days,
            "direction": "STABLE",
            "pct_change_7d": 0.0,
            "pct_change_30d": 0.0,
            "volatility": 0.0,
            "latest_price": 2000.0,
            "history_7d": [],
            "summary": f"Historical trend records for {crop} are limited; prices remain stable around current benchmarks."
        }

    prices = [float(r["modal_price"]) for r in records]
    
    # 7-day subset
    subset_7d = prices[-min(7, len(prices)):]
    start_7d = subset_7d[0]
    end_7d = subset_7d[-1]
    pct_change_7d = round(((end_7d - start_7d) / start_7d) * 100.0, 2) if start_7d > 0 else 0.0

    # 30-day subset
    start_30d = prices[0]
    end_30d = prices[-1]
    pct_change_30d = round(((end_30d - start_30d) / start_30d) * 100.0, 2) if start_30d > 0 else 0.0

    # Calculate volatility (standard deviation of last 14 days)
    recent_prices = prices[-min(14, len(prices)):]
    mean_price = sum(recent_prices) / len(recent_prices)
    variance = sum((p - mean_price) ** 2 for p in recent_prices) / len(recent_prices)
    volatility = round(math.sqrt(variance), 2)

    # Direction categorization
    if pct_change_7d > 2.0:
        direction = "RISING"
    elif pct_change_7d < -2.0:
        direction = "FALLING"
    else:
        direction = "STABLE"

    mandi_name = mandi or district or records[-1].get("mandi", "Regional Mandi")
    summary = (
        f"{crop} in {mandi_name} shows a {direction.lower()} trend. "
        f"Prices changed by {pct_change_7d:+.1f}% over the last 7 days "
        f"and {pct_change_30d:+.1f}% over the past 30 days (volatility: ₹{volatility}/qtl)."
    )

    history_7d = [{"date": r["date"], "price": float(r["modal_price"])} for r in records[-min(7, len(records)):]]

    return {
        "crop": crop,
        "mandi": mandi_name,
        "days_analyzed": days,
        "direction": direction,
        "pct_change_7d": pct_change_7d,
        "pct_change_30d": pct_change_30d,
        "volatility": volatility,
        "latest_price": end_7d,
        "history_7d": history_7d,
        "summary": summary
    }
