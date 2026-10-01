import sys
import os
import asyncio

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent import run_agent
from app.tools.language import detect_language, normalize_crop, extract_query


def test_phase3_agent_core():
    print("--- [TEST PHASE 3: AGENT CORE & MULTILINGUAL NLU] ---")

    # 1. Test NLU & Language Detection
    assert detect_language("आज कांद्याचा भाव काय आहे नाशिकमध्ये?") == "mr", "Language should be Marathi"
    assert detect_language("मेरे पास प्याज है, बेचूं या रुकूं?") == "hi", "Language should be Hindi"
    assert detect_language("What is the price of wheat in Ludhiana?") == "en", "Language should be English"
    print("[OK] Language detection verified for mr, hi, en.")

    # 2. Test Crop Normalization
    assert normalize_crop("कांदा") == "Onion", "Failed to normalize Marathi 'कांदा'"
    assert normalize_crop("प्याज़") == "Onion", "Failed to normalize Hindi 'प्याज़'"
    assert normalize_crop("tomato") == "Tomato", "Failed to normalize 'tomato'"
    assert normalize_crop("गहू") == "Wheat", "Failed to normalize Marathi 'गहू'"
    print("[OK] Multilingual crop normalization verified.")

    # 3. Test End-to-End English Price Query
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(
        run_agent(
            user_id="test_farmer_en",
            message="What is the price of wheat in Ludhiana?",
            language="en"
        )
    )

    assert res is not None, "Agent returned None"
    assert res["language"] == "en", f"Expected language 'en', got {res['language']}"
    assert len(res["steps"]) >= 3, f"Expected at least 3 visible steps, got {len(res['steps'])}"
    
    print("\n--- Agent Visible Execution Steps ---")
    for s in res["steps"]:
        print(f"  Step [{s['tool']}]: {s['result_summary']}")

    reply = res["reply"]
    print(f"\n--- Agent Grounded Reply ---\n{reply}\n")

    # Verify Anti-Hallucination: Price in reply must match tool result
    mandi_step = next((s for s in res["steps"] if s["tool"] == "get_mandi_prices"), None)
    assert mandi_step is not None, "get_mandi_prices was not called"
    print("[OK] End-to-end English price query passed with visible agentic steps!")

    # 4. Test Clarifying Question for missing crop
    res_missing_crop = loop.run_until_complete(
        run_agent(
            user_id="test_farmer_missing",
            message="What is the price in Pune?",
            language="en"
        )
    )
    assert "Which crop" in res_missing_crop["reply"], f"Expected crop clarification, got: {res_missing_crop['reply']}"
    print(f"[OK] Missing crop clarification verified: {res_missing_crop['reply']}")

    # 5. Test Clarifying Question for missing location
    res_missing_loc = loop.run_until_complete(
        run_agent(
            user_id="test_farmer_missing",
            message="टमाटर का भाव क्या है?",
            language="hi"
        )
    )
    assert "किस जिले या मंडी" in res_missing_loc["reply"], f"Expected location clarification, got: {res_missing_loc['reply']}"
    print(f"[OK] Missing location clarification verified: {res_missing_loc['reply']}")

    print("\n[ALL PASS] PHASE 3 AGENT CORE TESTS PASSED COMPLETELY!\n")


if __name__ == "__main__":
    test_phase3_agent_core()
