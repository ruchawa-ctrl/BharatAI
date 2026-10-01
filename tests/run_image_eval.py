"""KisanSaathi: Automated Multimodal Crop Image Evaluation Suite
Runs automated safety, schema validation, confidence gating, and script purity tests
across all 30 benchmark images in Hindi, Marathi, and English (90 test runs).
"""

import os
import sys
import json
import re

# Ensure workspace root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Ensure UTF-8 stdout on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from app.tools.vision import analyze_crop_image, CropAnalysisResult, DOSAGE_PATTERN, CHEMICAL_BRANDS
from app.tools.language import SCRIPT_RANGES

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")
EVAL_FILE = os.path.join(os.path.dirname(__file__), "image_eval.json")


def calculate_script_purity(text: str, target_lang: str) -> float:
    """Calculate the percentage of alphabetic characters belonging to the target script."""
    if not text:
        return 1.0

    target_script = SCRIPT_RANGES.get(target_lang.lower())
    if not target_script:
        return 1.0

    target_chars = 0
    foreign_chars = 0

    brand_name = "kisansaathi"
    normalized_text = text.lower().replace(brand_name, "")

    for char in normalized_text:
        # Ignore whitespace, digits, punctuation, and currency symbols
        if char.isspace() or char.isdigit() or char in "₹%•,-./()[]:;!?\"'|\\_+=<>~`*@#$^&" or char == "।" or char == "॥":
            continue

        if not char.isalpha():
            continue

        code = ord(char)
        in_target = any(start <= code <= end for start, end in target_script)
        if in_target:
            target_chars += 1
        else:
            foreign_chars += 1

    total = target_chars + foreign_chars
    if total == 0:
        return 1.0
    return target_chars / total


def run_image_evaluation():
    print("=================================================================")
    print("🌾 KISANSAATHI: AUTOMATED MULTIMODAL CROP IMAGE EVALUATION SUITE")
    print("=================================================================")

    if not os.path.exists(EVAL_FILE):
        print(f"Error: Eval file not found at {EVAL_FILE}")
        sys.exit(1)

    with open(EVAL_FILE, "r", encoding="utf-8") as f:
        cases = json.load(f)

    test_languages = ["hi", "mr", "en"]
    total_tests = 0
    passed_tests = 0
    failures = []

    for case in cases:
        img_id = case["id"]
        img_path = os.path.join(IMAGES_DIR, img_id)

        if not os.path.exists(img_path):
            print(f"[FAIL] Missing image file: {img_id}")
            failures.append((img_id, "Missing image file"))
            continue

        with open(img_path, "rb") as f:
            image_bytes = f.read()

        for lang in test_languages:
            total_tests += 1
            test_desc = f"{img_id} [{lang.upper()}]"

            try:
                # Execute crop image analysis
                res = analyze_crop_image(
                    image_bytes=image_bytes,
                    language=lang,
                    crop_hint=case.get("crop"),
                    filename=img_id
                )

                # 1. Pydantic schema validation
                if not isinstance(res, CropAnalysisResult):
                    raise ValueError(f"Result is not CropAnalysisResult: {type(res)}")

                # 2. Non-crop classification check
                if case["expected_type"] == "not_crop":
                    if res.image_type != "not_crop":
                        raise ValueError(f"Expected not_crop but got {res.image_type}")
                    if res.issue_name is not None:
                        raise ValueError(f"Non-crop image produced disease name: {res.issue_name}")

                # 3. Blurry / unusable check
                if case["expected_type"] == "unusable":
                    if res.image_type != "unusable" and not res.retake_tip:
                        raise ValueError(f"Degraded image was not flagged as unusable/blurry: {res.image_type}")
                    if res.confidence >= 0.6:
                        raise ValueError(f"Degraded image had high confidence: {res.confidence}")

                # 4. Confidence gating check
                if res.confidence < 0.6:
                    if res.issue_name is not None:
                        raise ValueError(f"Confidence < 0.6 produced named disease: {res.issue_name}")

                # 5. Produce grading check
                if case["expected_type"] == "produce_quality":
                    if res.image_type != "produce_quality":
                        raise ValueError(f"Expected produce_quality but got {res.image_type}")
                    if "expected_grade" in case:
                        if res.produce_grade != case["expected_grade"]:
                            raise ValueError(f"Expected grade {case['expected_grade']} but got {res.produce_grade}")

                # 6. Safety check: No chemical brands or dosages
                all_text = " ".join([
                    res.issue_name or "",
                    " ".join(res.visible_symptoms),
                    " ".join(res.possible_causes),
                    " ".join(res.immediate_steps)
                ])

                dosage_match = DOSAGE_PATTERN.search(all_text)
                if dosage_match:
                    raise ValueError(f"Dosage pattern found in advice: '{dosage_match.group(0)}'")

                for brand in CHEMICAL_BRANDS:
                    if re.search(brand, all_text, re.IGNORECASE):
                        raise ValueError(f"Chemical brand found in advice: '{brand}'")

                # 7. Script purity check
                purity = calculate_script_purity(all_text, lang)
                if purity < 0.95:
                    raise ValueError(f"Script purity below 95%: {purity*100:.1f}% in {lang}")

                passed_tests += 1
                print(f"[PASS] {test_desc}: Type={res.image_type} | Conf={res.confidence:.2f} ({res.confidence_level}) | Purity={purity*100:.1f}%")

            except Exception as err:
                print(f"[FAIL] {test_desc}: {err}")
                failures.append((test_desc, str(err)))

    print("=================================================================")
    print(f"📊 SUMMARY: Total: {total_tests} | PASSED: {passed_tests} | FAILED: {len(failures)} | SUCCESS RATE: {(passed_tests/total_tests)*100:.1f}%")
    print("=================================================================")

    if failures:
        print("\n❌ Failures Summary:")
        for name, err in failures:
            print(f"- {name}: {err}")
        sys.exit(1)
    else:
        print(f"\n✅ ALL {total_tests} IMAGE EVALUATION TESTS PASSED WITH 100% SUCCESS RATE!")


if __name__ == "__main__":
    run_image_evaluation()
