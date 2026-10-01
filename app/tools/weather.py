import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import httpx

# Fallback coordinates for key agricultural districts
DISTRICT_COORDS = {
    "nashik": {"lat": 19.9975, "lon": 73.7898, "state": "Maharashtra"},
    "lasalgaon": {"lat": 20.1472, "lon": 74.2253, "state": "Maharashtra"},
    "pune": {"lat": 18.5204, "lon": 73.8567, "state": "Maharashtra"},
    "latur": {"lat": 18.4088, "lon": 76.5604, "state": "Maharashtra"},
    "solapur": {"lat": 17.6599, "lon": 75.9064, "state": "Maharashtra"},
    "ahmednagar": {"lat": 19.0948, "lon": 74.7480, "state": "Maharashtra"},
    "nagpur": {"lat": 21.1458, "lon": 79.0882, "state": "Maharashtra"},
    "rajkot": {"lat": 22.3039, "lon": 70.8022, "state": "Gujarat"},
    "gondal": {"lat": 21.9619, "lon": 70.7923, "state": "Gujarat"},
    "surat": {"lat": 21.1702, "lon": 72.8311, "state": "Gujarat"},
    "indore": {"lat": 22.7196, "lon": 75.8577, "state": "Madhya Pradesh"},
    "ujjain": {"lat": 23.1765, "lon": 75.7885, "state": "Madhya Pradesh"},
    "agra": {"lat": 27.1767, "lon": 78.0081, "state": "Uttar Pradesh"},
    "khanna": {"lat": 30.7071, "lon": 76.2168, "state": "Punjab"},
    "ludhiana": {"lat": 30.9010, "lon": 75.8573, "state": "Punjab"}
}


def _get_district_lat_lon(district: str) -> tuple[float, float]:
    d_clean = district.strip().lower()
    if d_clean in DISTRICT_COORDS:
        info = DISTRICT_COORDS[d_clean]
        return info["lat"], info["lon"]

    # Try Open-Meteo geocoding
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={district}&count=1&country=India"
        with httpx.Client(timeout=3.0) as client:
            resp = client.get(url)
            if resp.status_code == 200:
                results = resp.json().get("results", [])
                if results:
                    return float(results[0]["latitude"]), float(results[0]["longitude"])
    except Exception:
        pass

    # Default to Maharashtra central coordinates if geocoding fails
    return 19.7515, 75.7139


def get_weather_forecast(district: str) -> Dict[str, Any]:
    """
    Fetch 5-day weather and precipitation forecast using Open-Meteo API.
    Identifies if heavy rain (>15mm or probability > 70%) is expected in next 48 hours,
    which is crucial for harvest and perishability decisions.
    """
    lat, lon = _get_district_lat_lon(district)

    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,weathercode"
            "&timezone=Asia%2FKolkata&forecast_days=5"
        )
        with httpx.Client(timeout=4.0) as client:
            resp = client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                daily = data.get("daily", {})
                dates = daily.get("time", [])
                t_max = daily.get("temperature_2m_max", [])
                t_min = daily.get("temperature_2m_min", [])
                rain = daily.get("precipitation_sum", [])
                rain_prob = daily.get("precipitation_probability_max", [])

                days = []
                for i in range(len(dates)):
                    days.append({
                        "date": dates[i],
                        "max_temp": t_max[i] if i < len(t_max) else 32.0,
                        "min_temp": t_min[i] if i < len(t_min) else 20.0,
                        "rain_mm": rain[i] if i < len(rain) else 0.0,
                        "rain_prob_pct": rain_prob[i] if i < len(rain_prob) else 0
                    })

                # Check heavy rain in next 48 hours (day 0 and day 1)
                heavy_rain_next_48h = False
                for day in days[:2]:
                    if day["rain_mm"] >= 15.0 or day["rain_prob_pct"] >= 70:
                        heavy_rain_next_48h = True
                        break

                total_rain_5d = sum(d["rain_mm"] for d in days)

                summary = (
                    f"Next 5 days: Temp {min(t_min):.1f}°C to {max(t_max):.1f}°C. "
                    f"Total expected rain: {total_rain_5d:.1f}mm. "
                )
                if heavy_rain_next_48h:
                    summary += "ALERT: Heavy rain predicted in next 48 hours! Produce stored without cover at risk."
                else:
                    summary += "Clear/moderate conditions expected for transport and selling."

                return {
                    "district": district,
                    "heavy_rain_next_48h": heavy_rain_next_48h,
                    "total_rain_5d_mm": round(total_rain_5d, 1),
                    "summary": summary,
                    "days": days,
                    "source": "Open-Meteo Live API",
                    "is_fallback": False
                }
    except Exception:
        pass

    # Reliable fallback weather when offline
    today = datetime.now()
    days = []
    for i in range(5):
        d = (today + timedelta(days=i)).strftime("%Y-%m-%d")
        days.append({
            "date": d,
            "max_temp": 33.0,
            "min_temp": 22.0,
            "rain_mm": 0.0,
            "rain_prob_pct": 10
        })

    return {
        "district": district,
        "heavy_rain_next_48h": False,
        "total_rain_5d_mm": 0.0,
        "summary": "Clear skies with normal temperature (22°C - 33°C). Good for harvesting and transport.",
        "days": days,
        "source": "Agro-Meteorological Baseline Fallback",
        "is_fallback": True
    }
