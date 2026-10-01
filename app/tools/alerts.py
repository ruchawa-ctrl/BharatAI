from typing import Dict, Any, List, Optional
from app.db import add_alert, get_active_alerts, mark_alert_triggered
from app.tools.prices import get_mandi_prices


def create_price_alert(
    user_id: str,
    crop: str,
    target_price: float,
    mandi: Optional[str] = None,
    condition: str = "above"
) -> Dict[str, Any]:
    """
    Action Tool: Creates a price alert stored in SQLite.
    When the crop price crosses target_price, an alert will be triggered.
    """
    alert_id = add_alert(
        user_id=user_id,
        crop=crop,
        target_price=target_price,
        mandi=mandi,
        condition=condition
    )
    return {
        "status": "success",
        "alert_id": alert_id,
        "user_id": user_id,
        "crop": crop,
        "mandi": mandi or "All Mandis",
        "target_price": target_price,
        "condition": condition,
        "message": f"Alert activated! You will be notified when {crop} price reaches ₹{target_price}/qtl."
    }


def check_alerts() -> List[Dict[str, Any]]:
    """
    Background action: Checks all active alerts against latest market prices.
    Marks triggered alerts in SQLite.
    """
    active_alerts = get_active_alerts()
    triggered = []

    for alert in active_alerts:
        crop = alert["crop"]
        mandi = alert["mandi"]
        target = float(alert["target_price"])
        cond = alert.get("condition", "above")

        # Get latest price
        price_data = get_mandi_prices(crop=crop, mandi=mandi, district=mandi)
        curr_price = float(price_data.get("modal_price", 0.0))

        should_trigger = False
        if cond == "above" and curr_price >= target:
            should_trigger = True
        elif cond == "below" and curr_price <= target:
            should_trigger = True

        if should_trigger:
            mark_alert_triggered(alert["id"], curr_price)
            triggered.append({
                "alert_id": alert["id"],
                "user_id": alert["user_id"],
                "crop": crop,
                "mandi": mandi or price_data.get("mandi"),
                "target_price": target,
                "current_price": curr_price,
                "date": price_data.get("as_of_date")
            })

    return triggered
