import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app
from app.db import init_db, add_alert, get_user_alerts

def test_phase1_scaffold():
    print("--- [TEST PHASE 1: SCAFFOLD & SYSTEM HEALTH] ---")
    
    # 1. Test DB initialization
    init_db()
    print("[OK] SQLite database initialized successfully.")

    # 2. Test Alert DB Operations
    alert_id = add_alert(user_id="test_farmer_1", crop="Onion", target_price=2500.0, mandi="Nashik")
    assert alert_id is not None, "Failed to insert test alert"
    alerts = get_user_alerts("test_farmer_1")
    assert len(alerts) >= 1, "Failed to retrieve user alerts"
    print(f"[OK] SQLite alerts read/write verified. Inserted alert id={alert_id}.")

    # 3. Test FastAPI TestClient
    client = TestClient(app)
    
    # Check /health
    health_resp = client.get("/health")
    assert health_resp.status_code == 200, f"Expected 200, got {health_resp.status_code}"
    health_data = health_resp.json()
    assert health_data.get("status") == "ok", f"Health status not ok: {health_data}"
    print(f"[OK] /health endpoint verified: {health_data}")

    # Check /alerts/{user_id}
    alerts_resp = client.get("/alerts/test_farmer_1")
    assert alerts_resp.status_code == 200
    assert len(alerts_resp.json().get("alerts", [])) >= 1
    print(f"[OK] /alerts/test_farmer_1 verified: retrieved {len(alerts_resp.json()['alerts'])} alerts")

    # Check /
    index_resp = client.get("/")
    assert index_resp.status_code == 200
    print(f"[OK] Static frontend / route verified: status={index_resp.status_code}")

    print("\n[ALL PASS] PHASE 1 TESTS PASSED COMPLETELY!\n")

if __name__ == "__main__":
    test_phase1_scaffold()
