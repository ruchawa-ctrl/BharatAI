import os
import json
import math
from typing import Dict, Any, List, Optional
from app.tools.prices import get_mandi_prices

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
MANDIS_GEO_PATH = os.path.join(DATA_DIR, "mandis_geo.json")

# Transport cost constant: ₹2.00 per km per quintal
TRANSPORT_COST_PER_KM_PER_QTL = 2.0


def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0  # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)


def _load_mandis_geo() -> List[Dict[str, Any]]:
    if os.path.exists(MANDIS_GEO_PATH):
        with open(MANDIS_GEO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def compare_nearby_mandis(crop: str, district: str, radius_km: float = 150.0) -> Dict[str, Any]:
    """
    Compare and rank nearby mandis for a given crop, accounting for rough
    transport cost (₹2/km per quintal) to find the highest net-paying market.
    """
    all_mandis = _load_mandis_geo()
    d_clean = district.strip().lower()

    # Find origin mandi/district coordinates
    origin = None
    for m in all_mandis:
        if m["district"].lower() == d_clean or m["mandi"].lower() == d_clean:
            origin = m
            break

    if not origin:
        # Default origin to first mandi or Nashik
        origin = all_mandis[0] if all_mandis else {"lat": 19.9975, "lon": 73.7898, "mandi": district, "district": district}

    origin_lat, origin_lon = origin["lat"], origin["lon"]

    # Filter mandis within radius
    ranked_list = []
    for m in all_mandis:
        dist = _haversine_distance(origin_lat, origin_lon, m["lat"], m["lon"])
        if dist <= radius_km:
            # Fetch price for this mandi
            price_data = get_mandi_prices(crop=crop, state=m.get("state"), district=m["district"], mandi=m["mandi"])
            modal_price = price_data.get("modal_price", 0.0)
            
            # Transport cost = distance * cost per km per qtl (0 if local)
            transport_cost = round(dist * TRANSPORT_COST_PER_KM_PER_QTL, 2)
            net_price = round(modal_price - transport_cost, 2)

            ranked_list.append({
                "mandi": m["mandi"],
                "district": m["district"],
                "state": m.get("state", "India"),
                "distance_km": dist,
                "gross_price": modal_price,
                "transport_cost_per_qtl": transport_cost,
                "net_price": net_price,
                "date": price_data.get("as_of_date", "")
            })

    # Sort by net price descending
    ranked_list.sort(key=lambda x: x["net_price"], reverse=True)

    best_mandi = ranked_list[0] if ranked_list else None
    local_mandi = next((m for m in ranked_list if m["distance_km"] == 0), best_mandi)
    
    local_net = local_mandi["net_price"] if local_mandi else 0.0
    for m in ranked_list:
        m["net_price_per_qtl"] = m["net_price"]
        m["net_gain_vs_local"] = max(0.0, round(m["net_price"] - local_net, 2))

    potential_gain = 0.0
    if best_mandi and local_mandi:
        potential_gain = max(0.0, round(best_mandi["net_price"] - local_mandi["net_price"], 2))

    summary = ""
    if best_mandi and local_mandi and best_mandi["mandi"] != local_mandi["mandi"] and potential_gain > 0:
        summary = (
            f"Selling in {best_mandi['mandi']} ({best_mandi['distance_km']} km away) yields a net price of "
            f"₹{best_mandi['net_price']}/qtl after ₹{best_mandi['transport_cost_per_qtl']} transport cost, "
            f"earning ₹{potential_gain}/qtl MORE than your local mandi ({local_mandi['mandi']})."
        )
    elif best_mandi:
        summary = (
            f"Your nearest/local mandi ({best_mandi['mandi']}) currently offers the best net return at "
            f"₹{best_mandi['net_price']}/qtl with minimal transport friction."
        )

    return {
        "crop": crop,
        "origin_district": district,
        "origin_mandi": origin.get("mandi", district),
        "radius_km": radius_km,
        "best_mandi": best_mandi,
        "local_mandi": local_mandi,
        "potential_gain_per_qtl": potential_gain,
        "mandis": ranked_list[:5],
        "ranked_mandis": ranked_list[:5],
        "summary": summary
    }
