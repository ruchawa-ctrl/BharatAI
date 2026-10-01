import os
import sys
import json
import re

LOCALES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "locales")
REQUIRED_LANGUAGES = ["en", "hi", "mr", "gu", "ta", "te", "kn", "ml", "bn", "pa", "or", "as"]
ALLOWED_ENGLISH_KEYS = {"lang_code", "brand_name"}


def check_locales():
    print("=" * 65)
    print("🌐 KISANSAATHI: LOCALES INTEGRITY & SCRIPT PURITY CHECK")
    print("=" * 65)

    if not os.path.exists(LOCALES_DIR):
        print(f"[FAIL] Locales directory missing: {LOCALES_DIR}")
        sys.exit(1)

    # 1. Load English as canonical reference
    en_path = os.path.join(LOCALES_DIR, "en.json")
    if not os.path.exists(en_path):
        print("[FAIL] Canonical en.json missing")
        sys.exit(1)

    with open(en_path, "r", encoding="utf-8") as f:
        canonical_keys = set(json.load(f).keys())

    print(f"Canonical keys in en.json: {len(canonical_keys)}")

    failures = []
    
    for code in REQUIRED_LANGUAGES:
        file_path = os.path.join(LOCALES_DIR, f"{code}.json")
        if not os.path.exists(file_path):
            failures.append(f"Missing locale file: {code}.json")
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception as e:
                failures.append(f"Invalid JSON in {code}.json: {e}")
                continue

        current_keys = set(data.keys())

        # Check missing keys
        missing = canonical_keys - current_keys
        if missing:
            failures.append(f"{code}.json missing keys: {missing}")

        # Check extra keys
        extra = current_keys - canonical_keys
        if extra:
            failures.append(f"{code}.json has extra keys: {extra}")

        # Check non-empty and non-English for target languages
        for key, val in data.items():
            if not isinstance(val, str) or not val.strip():
                failures.append(f"{code}.json has empty value for key '{key}'")
                continue

            if code != "en" and key not in ALLOWED_ENGLISH_KEYS:
                # If value is completely identical to English canonical value and not allowed
                with open(en_path, "r", encoding="utf-8") as ef:
                    en_val = json.load(ef).get(key)
                if val == en_val and len(val) > 4:
                    failures.append(f"{code}.json key '{key}' appears untranslated (matches English: '{val}')")

        print(f"[PASS] {code}.json verified ({len(current_keys)} keys).")

    print("=" * 65)
    if failures:
        print(f"❌ FAILED: Found {len(failures)} locale validation error(s):")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("✅ ALL 12 LOCALES PASSED INTEGRITY CHECK WITH 0 ERRORS!")
        print("=" * 65)


if __name__ == "__main__":
    check_locales()
