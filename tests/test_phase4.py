import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tools.recommend import recommend_action
from app.tools.mandis import compare_nearby_mandis
from app.tools.alerts import create_price_alert, check_alerts
from app.tools.share import make_share_summary
from app.db import init_db


def test_phase4_decisions_and_actions():
    print("--- [TEST PHASE 4: DECISION ENGINE & REAL ACTIONS] ---")
    init_db()

    # 1. Test Decision Engine: High Perishability (Tomato)
    rec_tomato = recommend_action(
        crop="Tomato",
        modal_price=1600.0,
        trend_pct_7d=-5.0,
        trend_direction="FALLING",
        heavy_rain_next_48h=False,
        has_msp=False,
        perishability="high"
    )
    assert rec_tomato["action"] == "SELL_NOW", "Tomato with falling price must recommend SELL_NOW"
    assert rec_tomato["confidence"] >= 0.85, "Confidence should be high for perishable crop"
    assert len(rec_tomato["reasons"]) >= 2, "Must provide at least 2 reasons"
    print(f"[OK] Decision: Tomato -> {rec_tomato['action']} (Confidence: {rec_tomato['confidence']*100:.0f}%) | Primary Reason: {rec_tomato['primary_reason']}")

    # 2. Test Decision Engine: Below MSP (Soybean)
    rec_soybean = recommend_action(
        crop="Soybean",
        modal_price=4200.0,
        trend_pct_7d=-1.0,
        trend_direction="FALLING",
        heavy_rain_next_48h=False,
        has_msp=True,
        msp_price=4892.0,
        perishability="low"
    )
    assert rec_soybean["action"] == "HOLD", "Crop below MSP must recommend HOLD"
    assert "MSP" in rec_soybean["primary_reason"], "Reason must cite MSP gap"
    print(f"[OK] Decision: Soybean below MSP -> {rec_soybean['action']} (Confidence: {rec_soybean['confidence']*100:.0f}%) | Primary Reason: {rec_soybean['primary_reason']}")

    # 3. Test Decision Engine: Weather Impact (Heavy rain shifting medium perishability)
    rec_onion_rain = recommend_action(
        crop="Onion",
        modal_price=2800.0,
        trend_pct_7d=3.0,
        trend_direction="RISING",
        heavy_rain_next_48h=True,
        has_msp=False,
        perishability="medium"
    )
    assert rec_onion_rain["action"] == "SELL_NOW", "Heavy rain in 48h must shift Onion to SELL_NOW"
    assert any("rain" in r.lower() or "पाऊस" in r.lower() for r in rec_onion_rain["reasons"]), "Reasons must mention rain risk"
    print(f"[OK] Decision: Onion with 48h Rain Alert -> {rec_onion_rain['action']} | Reason: {rec_onion_rain['primary_reason']}")

    # 4. Test Nearby Mandi Comparison
    mandi_comp = compare_nearby_mandis(crop="Onion", district="Nashik", radius_km=150.0)
    assert mandi_comp is not None, "Failed to compare nearby mandis"
    assert "best_mandi" in mandi_comp and "mandis" in mandi_comp, "Missing comparison keys"
    assert len(mandi_comp["mandis"]) > 0, "No nearby mandis found"
    best_m = mandi_comp["best_mandi"]
    print(f"[OK] Mandi Comparison (Onion, Nashik): Best Mandi: {best_m['mandi']} | Net: ₹{best_m['net_price']}/qtl (Transport: ₹{best_m['transport_cost_per_qtl']}) | Gain: +₹{mandi_comp['potential_gain_per_qtl']}/qtl")

    # 5. Test Action Tool: Create Price Alert in SQLite
    alert_res = create_price_alert(
        user_id="farmer_nashik_42",
        crop="Onion",
        target_price=2800.0,
        mandi="Nashik"
    )
    assert alert_res["status"] == "success", "Failed to create price alert"
    assert alert_res["alert_id"] > 0, "Invalid alert ID"
    print(f"[OK] Action: Price Alert created in SQLite -> ID={alert_res['alert_id']} ({alert_res['message']})")

    # 6. Test Action Tool: Check Alerts
    triggered = check_alerts()
    print(f"[OK] Action: check_alerts evaluated active alerts -> {len(triggered)} triggered against current prices.")

    # 7. Test Action Tool: WhatsApp Share Summary
    share_mr = make_share_summary(
        crop="कांदा",
        action="HOLD",
        price=2900.0,
        mandi="नाशिक",
        trend_pct=5.2,
        primary_reason="७ दिवसांत भावात चांगली वाढ होत आहे.",
        language="mr"
    )
    assert "whatsapp.com" in share_mr["whatsapp_url"], "Invalid WhatsApp URL"
    assert "किसानसाथी" in share_mr["text"], "Expected Marathi branding in share text"
    print(f"[OK] Action: WhatsApp summary generated for Marathi:\n{share_mr['text'][:120]}...\n")

    print("\n[ALL PASS] PHASE 4 DECISIONS AND ACTIONS TESTS PASSED COMPLETELY!\n")


if __name__ == "__main__":
    test_phase4_decisions_and_actions()
