import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app


def test_phase6_frontend():
    print("--- [TEST PHASE 6: FRONTEND & STATIC ASSETS (ADDENDUM COMPLIANT)] ---")
    client = TestClient(app)

    # 1. Test index.html serving
    resp_index = client.get("/")
    assert resp_index.status_code == 200, f"Expected 200 for /, got {resp_index.status_code}"
    html = resp_index.text
    assert "KisanSaathi" in html, "index.html missing KisanSaathi branding"
    assert "languageSelect" in html, "index.html missing languageSelect element"
    assert "micBtn" in html, "index.html missing micBtn voice element"
    assert "askInput" in html, "index.html missing askInput element"
    assert "answerPanel" in html, "index.html missing answerPanel (Addendum layout)"
    assert "recommendationCard" in html, "index.html missing recommendationCard"
    assert "cropsGrid" in html, "index.html missing crop quick-pick grid"
    assert "sparklineSvg" in html, "index.html missing 7-day sparkline chart"
    print(f"[OK] index.html served cleanly ({len(html)} bytes)")

    # 2. Test styles.css serving
    resp_css = client.get("/static/styles.css")
    assert resp_css.status_code == 200, f"Expected 200 for styles.css, got {resp_css.status_code}"
    css = resp_css.text
    assert "--green-900" in css, "styles.css missing government-grade green-900 color token"
    assert "--green-700" in css, "styles.css missing green-700 primary button token"
    assert ".recommendation-card" in css, "styles.css missing recommendation styles"
    assert ".btn-mic.recording" in css, "styles.css missing mic pulse animation"
    print(f"[OK] styles.css served cleanly ({len(css)} bytes)")

    # 3. Test app.js serving
    resp_js = client.get("/static/app.js")
    assert resp_js.status_code == 200, f"Expected 200 for app.js, got {resp_js.status_code}"
    js = resp_js.text
    assert "SpeechRecognition" in js, "app.js missing Web Speech STT integration"
    assert "SpeechSynthesisUtterance" in js, "app.js missing Web Speech TTS integration"
    assert "loadLocale" in js, "app.js missing dynamic 12-language locale loader"
    assert "renderSparkline" in js, "app.js missing 7-day SVG sparkline chart renderer"
    print(f"[OK] app.js served cleanly ({len(js)} bytes)")

    # 4. Test 12 Locale JSON files serving
    for lang in ["mr", "hi", "en", "gu", "ta", "te", "kn", "ml", "bn", "pa", "or", "as"]:
        loc_resp = client.get(f"/static/locales/{lang}.json")
        assert loc_resp.status_code == 200, f"Missing locale JSON: {lang}.json"
        data = loc_resp.json()
        assert "brand_name" in data and "ask_placeholder" in data
    print("[OK] All 12 locale JSON files served cleanly via /static/locales/")

    # 5. Test WebP Image Assets serving
    for img in ["hero_farmer.webp", "onion.webp", "tomato.webp", "potato.webp", "wheat.webp", "soybean.webp"]:
        img_resp = client.get(f"/static/assets/{img}")
        assert img_resp.status_code == 200, f"Missing asset: {img}"
        assert len(img_resp.content) > 0
    print("[OK] WebP image assets verified and served cleanly via /static/assets/")

    print("\n[ALL PASS] PHASE 6 FRONTEND TESTS (ADDENDUM COMPLIANT) PASSED COMPLETELY!\n")


if __name__ == "__main__":
    test_phase6_frontend()
