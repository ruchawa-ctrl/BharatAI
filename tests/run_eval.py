import sys
import os
import json
import asyncio
import re

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent import run_agent

EVAL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eval_queries.json")


def verify_no_hallucination(reply: str, steps: list) -> bool:
    """
    Ensure every price mentioned in reply actually appears in the tool outputs or args.
    """
    price_matches = re.findall(r"₹\s*([\d,]+(?:\.\d+)?)", reply)
    if not price_matches:
        return True

    tool_tokens = []
    for s in steps:
        tool_tokens.append(str(s.get("result_summary", "")))
        for k, v in s.get("args", {}).items():
            tool_tokens.append(str(v))
    all_tool_text = " ".join(tool_tokens)

    for p in price_matches:
        p_clean = p.replace(",", "")
        try:
            val = float(p_clean)
            if val < 5:
                continue
            int_str = str(int(val))
            float_str = f"{val:.1f}"
            # Check if integer part or float part exists in tool text
            if int_str not in all_tool_text and float_str not in all_tool_text:
                return False
        except ValueError:
            pass

    return True


SCRIPT_RANGES = {
    "en": [(0x0041, 0x005A), (0x0061, 0x007A)],
    "hi": [(0x0900, 0x097F)],
    "mr": [(0x0900, 0x097F)],
    "gu": [(0x0A80, 0x0AFF)],
    "ta": [(0x0B80, 0x0BFF)],
    "te": [(0x0C00, 0x0C7F)],
    "kn": [(0x0C80, 0x0CFF)],
    "ml": [(0x0D00, 0x0D7F)],
    "bn": [(0x0980, 0x09FF)],
    "pa": [(0x0A00, 0x0A7F)],
    "or": [(0x0B00, 0x0B7F)],
    "as": [(0x0980, 0x09FF)],
}


def check_script_purity(reply: str, target_lang: str) -> float:
    """
    Returns ratio (0.0 to 1.0) of alphabetic characters in reply that match target script.
    Ignores digits, punctuation, ₹, and brand/source names like KisanSaathi.
    """
    cleaned = (reply
        .replace("KisanSaathi", "")
        .replace("Agmarknet", "")
        .replace("Agro-Benchmark", "")
        .replace("Open-Meteo", "")
        .replace("FRP", "")
        .replace("MSP", "")
        .replace("WhatsApp", "")
    )
    ranges = SCRIPT_RANGES.get(target_lang, [])
    if not ranges:
        return 1.0

    total_letters = 0
    target_letters = 0

    for ch in cleaned:
        code = ord(ch)
        if code in [0x0964, 0x0965]:  # Standard Indic danda / double danda punctuation
            continue
        if ch.isalpha() or (0x0900 <= code <= 0x0D7F and not ('0' <= ch <= '9')):
            total_letters += 1
            if any(start <= code <= end for start, end in ranges):
                target_letters += 1

    if total_letters == 0:
        return 1.0
    return target_letters / total_letters


async def main():
    print("=" * 65)
    print("🌾 KISANSAATHI: COMPREHENSIVE MULTILINGUAL EVALUATION SUITE")
    print("=" * 65)

    with open(EVAL_PATH, "r", encoding="utf-8") as f:
        queries = json.load(f)

    total = len(queries)
    passed = 0
    failed = 0
    failures = []

    for item in queries:
        qid = item["id"]
        query = item["query"]
        exp_lang = item["expected_language"]
        exp_intent = item["expected_intent"]
        requires_clarification = item.get("requires_clarification", False)
        exp_tools = item.get("expected_tools", [])

        res = await run_agent(user_id=f"eval_user_{qid}", message=query, language="auto")
        reply = res["reply"]
        actual_lang = res["language"]
        steps = res.get("steps", [])
        tools_called = [s["tool"] for s in steps]

        # Extract detected intent from extract_query step
        extract_step = next((s for s in steps if s["tool"] == "extract_query"), None)
        detected_intent = None
        if extract_step:
            summary = extract_step["result_summary"]
            m = re.search(r"Intent:\s*(\w+)", summary)
            if m:
                detected_intent = m.group(1)

        # 1. Language check
        lang_ok = (actual_lang == exp_lang)

        # 2. Intent check
        intent_ok = (detected_intent == exp_intent) or (exp_intent == "price_check" and detected_intent in ["price_check", "general"])

        # 3. Clarification check
        clarification_ok = True
        if requires_clarification:
            clarification_ok = ("?" in reply or "कृपया" in reply or "सांगा" in reply or "बताएं" in reply or "జిల్లా" in reply or "மாவட்டம்" in reply or "only assist" in reply.lower())
        
        # 4. Expected tools check
        tools_ok = True
        for t in exp_tools:
            if t not in tools_called:
                tools_ok = False
                break

        # 5. Anti-Hallucination check
        hallucination_ok = verify_no_hallucination(reply, steps)

        # 6. Script Purity check (>= 95% letters in target script)
        purity = check_script_purity(reply, exp_lang)
        purity_ok = (purity >= 0.95)

        all_ok = lang_ok and intent_ok and clarification_ok and tools_ok and hallucination_ok and purity_ok

        if all_ok:
            passed += 1
            print(f"[PASS] Q{qid:02d} ({exp_lang.upper()} | {exp_intent} | purity: {purity*100:.1f}%): '{query[:35]}...'")
        else:
            failed += 1
            reason = []
            if not lang_ok:
                reason.append(f"Lang mismatch (exp {exp_lang}, got {actual_lang})")
            if not intent_ok:
                reason.append(f"Intent mismatch (exp {exp_intent}, got {detected_intent})")
            if not clarification_ok:
                reason.append("Failed clarification requirement")
            if not tools_ok:
                reason.append(f"Missing tools (called {tools_called}, expected {exp_tools})")
            if not hallucination_ok:
                reason.append("Hallucination detected in price")
            if not purity_ok:
                reason.append(f"Script purity low: {purity*100:.1f}% (required >=95%)")
            
            err_msg = f"[FAIL] Q{qid:02d}: '{query}' -> {', '.join(reason)}"
            print(err_msg)
            failures.append(err_msg)

    print("=" * 65)
    print(f"📊 EVALUATION SUMMARY: Total: {total} | PASSED: {passed} | FAILED: {failed} | SUCCESS RATE: {(passed/total)*100:.1f}%")
    print("=" * 65)

    if failed > 0:
        print("\nFailures:")
        for f in failures:
            print("  - " + f)
        sys.exit(1)
    else:
        print("\n✅ ALL 32 EVALUATION QUERIES PASSED WITH 100% SUCCESS RATE!\n")


if __name__ == "__main__":
    asyncio.run(main())
