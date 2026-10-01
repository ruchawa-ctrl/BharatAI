import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app


def test_phase7_hardening():
    print("--- [TEST PHASE 7: HARDENING & RESILIENCE] ---")
    client = TestClient(app)

    # 1. Test Empty Message Validation
    resp_empty = client.post("/chat", json={"user_id": "test_h1", "message": "   ", "language": "hi"})
    assert resp_empty.status_code == 422, f"Expected 422 for empty message, got {resp_empty.status_code}"
    print("[OK] Empty/whitespace message correctly rejected with HTTP 422.")

    # 2. Test Large Message (1000 characters)
    large_msg = "कांदा " * 150 + "नाशिक"
    resp_large = client.post("/chat", json={"user_id": "test_h2", "message": large_msg, "language": "mr"})
    assert resp_large.status_code == 200, f"Expected 200 for large message, got {resp_large.status_code}"
    print("[OK] Large message handled without crashing.")

    # 3. Test Unknown Crop / Edge Case Input
    resp_weird = client.post("/chat", json={"user_id": "test_h3", "message": "xyzunknowncrop123456 in Pune", "language": "en"})
    assert resp_weird.status_code == 200, f"Expected 200 for unknown crop, got {resp_weird.status_code}"
    data = resp_weird.json()
    assert "reply" in data and len(data["steps"]) > 0, "Expected safe fallback reply and steps"
    print(f"[OK] Unknown entity safely handled: {data['reply'][:60]}...")

    # 4. Test Missing Location Fallback
    resp_no_loc = client.post("/chat", json={"user_id": "test_h4", "message": "What is the price of soybean?", "language": "en"})
    assert resp_no_loc.status_code == 200
    assert "Which district" in resp_no_loc.json()["reply"] or "mandi" in resp_no_loc.json()["reply"], "Expected location clarification"
    print("[OK] Missing location handled cleanly without crash.")

    print("\n[ALL PASS] PHASE 7 HARDENING TESTS PASSED COMPLETELY!\n")


if __name__ == "__main__":
    test_phase7_hardening()
