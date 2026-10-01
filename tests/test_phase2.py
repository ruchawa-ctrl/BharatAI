import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tools.prices import get_mandi_prices
from app.tools.msp import get_msp
from app.tools.weather import get_weather_forecast
from app.tools.trend import get_price_trend

def test_phase2_data_layer():
    print("--- [TEST PHASE 2: DATA LAYER - PRICES, MSP, WEATHER, TRENDS] ---")

    test_crops = ["Onion", "Tomato", "Wheat"]

    for crop in test_crops:
        print(f"\n>> Testing Crop: {crop}")
        
        # 1. Mandi Prices
        prices = get_mandi_prices(crop=crop, district="Nashik" if crop != "Wheat" else "Ludhiana")
        assert prices is not None, f"Failed to get mandi prices for {crop}"
        assert prices["modal_price"] > 0, f"Invalid modal price for {crop}"
        assert "source" in prices and "as_of_date" in prices, f"Missing source or as_of_date for {crop}"
        print(f"  [OK] Mandi Price: ₹{prices['modal_price']}/qtl (₹{prices['price_per_kg']}/kg) | Mandi: {prices['mandi']} | Date: {prices['as_of_date']} | Source: {prices['source']}")

        # 2. MSP Lookup
        msp = get_msp(crop=crop)
        assert msp is not None, f"Failed to get MSP for {crop}"
        if crop == "Wheat":
            assert msp["has_msp"] is True, "Wheat must have MSP"
            assert msp["msp_price_per_quintal"] >= 2200, "Wheat MSP mismatch"
            print(f"  [OK] MSP: ₹{msp['msp_price_per_quintal']}/qtl (Year: {msp['year']}) | Perishability: {msp['perishability']}")
        else:
            assert msp["has_msp"] is False, f"{crop} should not have central MSP"
            print(f"  [OK] MSP: No statutory MSP (Market-driven) | Perishability: {msp['perishability']}")

        # 3. Weather Forecast
        district = "Nashik" if crop == "Onion" else ("Pune" if crop == "Tomato" else "Ludhiana")
        weather = get_weather_forecast(district=district)
        assert weather is not None, f"Failed to get weather for {district}"
        assert "heavy_rain_next_48h" in weather, "Missing heavy_rain_next_48h in weather"
        assert len(weather.get("days", [])) == 5, "Weather should provide 5-day forecast"
        print(f"  [OK] Weather ({district}): 48h Heavy Rain Risk: {weather['heavy_rain_next_48h']} | 5-day Rain: {weather['total_rain_5d_mm']}mm | {weather['summary'][:60]}...")

        # 4. Price Trend
        trend = get_price_trend(crop=crop, district=district)
        assert trend is not None, f"Failed to get trend for {crop}"
        assert "direction" in trend and "pct_change_7d" in trend, "Missing trend parameters"
        print(f"  [OK] Trend: {trend['direction']} (7-day: {trend['pct_change_7d']:+0.1f}%, 30-day: {trend['pct_change_30d']:+0.1f}%) | Volatility: ₹{trend['volatility']}")

    print("\n[ALL PASS] PHASE 2 DATA LAYER TESTS PASSED COMPLETELY!\n")

if __name__ == "__main__":
    test_phase2_data_layer()
