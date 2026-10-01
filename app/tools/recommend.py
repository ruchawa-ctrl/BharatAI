from typing import Dict, Any, Optional, List


def recommend_action(
    crop: str,
    modal_price: float,
    trend_pct_7d: float,
    trend_direction: str,
    heavy_rain_next_48h: bool,
    has_msp: bool,
    msp_price: Optional[float] = None,
    perishability: str = "medium"
) -> Dict[str, Any]:
    """
    Produce a grounded SELL_NOW, HOLD, or SHIFT_MANDI recommendation
    based on agricultural economics, crop perishability, price momentum,
    MSP benchmark gap, and 48-hour weather risks.
    """
    reasons = []
    confidence = 0.85
    action = "SELL_NOW"
    
    perishability_lower = perishability.lower()

    # Rule 1: High Perishability (e.g. Tomato)
    if perishability_lower == "high":
        if trend_pct_7d > 5.0 and not heavy_rain_next_48h:
            action = "HOLD"
            confidence = 0.75
            reasons.append(f"Price is experiencing a strong short-term upward momentum ({trend_pct_7d:+.1f}% in 7 days).")
            reasons.append("Temporary hold (1-2 days max) may fetch higher returns if cold storage or shaded cover is available.")
        else:
            action = "SELL_NOW"
            confidence = 0.90
            reasons.append(f"{crop} is a highly perishable crop with high risk of spoilage if held.")
            if trend_direction == "FALLING":
                reasons.append(f"Price trend is falling ({trend_pct_7d:+.1f}% in 7 days); selling now prevents further loss.")
            else:
                reasons.append(f"Current price of ₹{modal_price}/qtl offers safe immediate realization.")

    # Rule 2: Low Perishability / Grains & Oilseeds (e.g. Wheat, Soybean, Cotton, Tur)
    elif perishability_lower == "low":
        # Check MSP comparison
        if has_msp and msp_price:
            msp_diff_pct = ((modal_price - msp_price) / msp_price) * 100.0
            if modal_price < msp_price:
                action = "HOLD"
                confidence = 0.85
                reasons.append(f"Current mandi price (₹{modal_price}/qtl) is below statutory MSP (₹{msp_price}/qtl) by {abs(msp_diff_pct):.1f}%.")
                reasons.append("Holding produce in dry storage is recommended until market prices recover or government procurement centers open.")
            elif trend_direction == "FALLING" and trend_pct_7d < -3.0:
                action = "SELL_NOW"
                confidence = 0.80
                reasons.append(f"Prices are softening ({trend_pct_7d:+.1f}% in 7 days) and currently above MSP (₹{msp_price}/qtl).")
                reasons.append("Locking in profits now is safer than risking prolonged price erosion.")
            else:
                action = "HOLD"
                confidence = 0.80
                reasons.append(f"Prices are steady and produce is safely storable for 6-12 months.")
                reasons.append(f"Modal rate is ₹{modal_price}/qtl (well above MSP ₹{msp_price}/qtl).")
        else:
            if trend_direction == "RISING":
                action = "HOLD"
                confidence = 0.80
                reasons.append(f"Upward price trajectory ({trend_pct_7d:+.1f}% in 7 days) favors holding.")
            else:
                action = "SELL_NOW"
                confidence = 0.75
                reasons.append(f"Fair market value at ₹{modal_price}/qtl with stable demand.")

    # Rule 3: Medium Perishability (e.g. Onion, Potato)
    else:
        if trend_direction == "RISING" and not heavy_rain_next_48h:
            action = "HOLD"
            confidence = 0.85
            reasons.append(f"Strong 7-day rising trend ({trend_pct_7d:+.1f}%) in major trading mandis.")
            reasons.append("Weather is clear for the next 48 hours; dry aeration storage allows waiting for higher peaks.")
        elif heavy_rain_next_48h:
            action = "SELL_NOW"
            confidence = 0.90
            reasons.append("Heavy rainfall is forecast within the next 48 hours, creating severe humidity and rot risk.")
            reasons.append(f"Selling today at current modal rate (₹{modal_price}/qtl) avoids wet damage in transit or storage.")
        elif trend_direction == "FALLING":
            action = "SELL_NOW"
            confidence = 0.85
            reasons.append(f"Price is dropping ({trend_pct_7d:+.1f}% over 7 days); supply arrivals are increasing.")
            reasons.append("Immediate offloading protects your profit margins.")
        else:
            action = "SELL_NOW"
            confidence = 0.80
            reasons.append(f"Current price of ₹{modal_price}/qtl is healthy and stable.")
            reasons.append("Holding carries storage shrink loss without guaranteed price gains.")

    # Weather impact adjustment
    if heavy_rain_next_48h and action == "HOLD" and perishability_lower != "low":
        action = "SELL_NOW"
        confidence = 0.85
        reasons.insert(0, "Weather Alert: Heavy rain forecast in 48 hours shifts recommendation to SELL NOW to prevent post-harvest spoilage.")

    return {
        "action": action,
        "confidence": confidence,
        "primary_reason": reasons[0] if reasons else "Based on current market trend and perishability.",
        "reasons": reasons,
        "perishability": perishability,
        "modal_price": modal_price,
        "trend_pct_7d": trend_pct_7d
    }
