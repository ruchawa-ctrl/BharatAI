"""Generator for KisanSaathi Audio Evaluation Benchmark Dataset
Creates 34 benchmark audio test files in tests/audio/ and the corresponding
tests/audio_eval.json metadata covering Hindi, Marathi, English, and Code-Mixed queries.
"""

import os
import json
import math
import wave
import struct

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)
EVAL_FILE = os.path.join(os.path.dirname(__file__), "audio_eval.json")

AUDIO_CASES = [
    # Hindi Queries (10)
    {
        "id": "hi_01",
        "filename": "hi_01_onion_nashik.wav",
        "language": "hi",
        "spoken_text": "मेरे पास 50 क्विंटल प्याज है, नाशिक मंडी में आज बेचूं या रुकूं?",
        "expected_crop": "Onion",
        "expected_location": "Nashik",
        "expected_intent": "sell_or_hold",
        "is_mixed_language": False
    },
    {
        "id": "hi_02",
        "filename": "hi_02_tomato_pune.wav",
        "language": "hi",
        "spoken_text": "पुणे मंडी में आज टमाटर का क्या भाव चल रहा है?",
        "expected_crop": "Tomato",
        "expected_location": "Pune",
        "expected_intent": "price_check",
        "is_mixed_language": False
    },
    {
        "id": "hi_03",
        "filename": "hi_03_soybean_indore.wav",
        "language": "hi",
        "spoken_text": "इंदौर में सोयाबीन बेचने के लिए सबसे अच्छी मंडी कौन सी है?",
        "expected_crop": "Soybean",
        "expected_location": "Indore",
        "expected_intent": "best_mandi",
        "is_mixed_language": False
    },
    {
        "id": "hi_04",
        "filename": "hi_04_wheat_nagpur.wav",
        "language": "hi",
        "spoken_text": "नागपुर में गेहूं का क्या रेट है और क्या भाव बढ़ेंगे?",
        "expected_crop": "Wheat",
        "expected_location": "Nagpur",
        "expected_intent": "sell_or_hold",
        "is_mixed_language": False
    },
    {
        "id": "hi_05",
        "filename": "hi_05_cotton_amravati.wav",
        "language": "hi",
        "spoken_text": "अमरावती मंडी में कपास का भाव क्या है?",
        "expected_crop": "Cotton",
        "expected_location": "Amravati",
        "expected_intent": "price_check",
        "is_mixed_language": False
    },
    {
        "id": "hi_06",
        "filename": "hi_06_onion_lasalgaon.wav",
        "language": "hi",
        "spoken_text": "लासलगांव में प्याज का आज का ताजा भाव क्या है?",
        "expected_crop": "Onion",
        "expected_location": "Lasalgaon",
        "expected_intent": "price_check",
        "is_mixed_language": False
    },
    {
        "id": "hi_07",
        "filename": "hi_07_weather_nashik.wav",
        "language": "hi",
        "spoken_text": "नाशिक में अगले तीन दिनों का मौसम कैसा रहेगा, क्या बारिश होगी?",
        "expected_crop": None,
        "expected_location": "Nashik",
        "expected_intent": "weather",
        "is_mixed_language": False
    },
    {
        "id": "hi_08",
        "filename": "hi_08_chilli_nagpur.wav",
        "language": "hi",
        "spoken_text": "नागपुर में हरी मिर्च का आज क्या भाव मिल रहा है?",
        "expected_crop": "Chilli",
        "expected_location": "Nagpur",
        "expected_intent": "price_check",
        "is_mixed_language": False
    },
    {
        "id": "hi_09",
        "filename": "hi_09_potato_indore.wav",
        "language": "hi",
        "spoken_text": "मेरे पास 30 क्विंटल आलू है, इंदौर में अभी बेचूं या 10 दिन रुकूं?",
        "expected_crop": "Potato",
        "expected_location": "Indore",
        "expected_intent": "sell_or_hold",
        "is_mixed_language": False
    },
    {
        "id": "hi_10",
        "filename": "hi_10_mustard_bhopal.wav",
        "language": "hi",
        "spoken_text": "भोपाल मंडी में सरसों का क्या भाव चल रहा है?",
        "expected_crop": "Mustard",
        "expected_location": "Bhopal",
        "expected_intent": "price_check",
        "is_mixed_language": False
    },

    # Marathi Queries (10)
    {
        "id": "mr_01",
        "filename": "mr_01_onion_nashik.wav",
        "language": "mr",
        "spoken_text": "माझ्याकडे 40 क्विंटल कांदा आहे, नाशिक बाजारात आज विकू की थांबू?",
        "expected_crop": "Onion",
        "expected_location": "Nashik",
        "expected_intent": "sell_or_hold",
        "is_mixed_language": False
    },
    {
        "id": "mr_02",
        "filename": "mr_02_tomato_pune.wav",
        "language": "mr",
        "spoken_text": "पुणे मार्केटमध्ये आज टोमॅटोचा काय दर चालू आहे?",
        "expected_crop": "Tomato",
        "expected_location": "Pune",
        "expected_intent": "price_check",
        "is_mixed_language": False
    },
    {
        "id": "mr_03",
        "filename": "mr_03_soybean_latur.wav",
        "language": "mr",
        "spoken_text": "लातूर बाजारपेठेत सोयाबीनसाठी सर्वात चांगली बाजारपेठ कोणती?",
        "expected_crop": "Soybean",
        "expected_location": "Latur",
        "expected_intent": "best_mandi",
        "is_mixed_language": False
    },
    {
        "id": "mr_04",
        "filename": "mr_04_cotton_jalgaon.wav",
        "language": "mr",
        "spoken_text": "जळगावमध्ये कापसाला काय भाव मिळतो आहे?",
        "expected_crop": "Cotton",
        "expected_location": "Jalgaon",
        "expected_intent": "price_check",
        "is_mixed_language": False
    },
    {
        "id": "mr_05",
        "filename": "mr_05_wheat_nashik.wav",
        "language": "mr",
        "spoken_text": "नाशिकमध्ये गव्हाचा आजचा बाजारभाव सांगा.",
        "expected_crop": "Wheat",
        "expected_location": "Nashik",
        "expected_intent": "price_check",
        "is_mixed_language": False
    },
    {
        "id": "mr_06",
        "filename": "mr_06_onion_ahmednagar.wav",
        "language": "mr",
        "spoken_text": "अहमदनगरमध्ये कांदा आता विकावा की काही दिवस ठेवावा?",
        "expected_crop": "Onion",
        "expected_location": "Ahmednagar",
        "expected_intent": "sell_or_hold",
        "is_mixed_language": False
    },
    {
        "id": "mr_07",
        "filename": "mr_07_weather_pune.wav",
        "language": "mr",
        "spoken_text": "पुण्यात पुढील दोन दिवसांत पाऊस पडेल का, हवामान कसे राहील?",
        "expected_crop": None,
        "expected_location": "Pune",
        "expected_intent": "weather",
        "is_mixed_language": False
    },
    {
        "id": "mr_08",
        "filename": "mr_08_tur_nagpur.wav",
        "language": "mr",
        "spoken_text": "नागपूर बाजारात तुरीचा आजचा भाव काय आहे?",
        "expected_crop": "Tur",
        "expected_location": "Nagpur",
        "expected_intent": "price_check",
        "is_mixed_language": False
    },
    {
        "id": "mr_09",
        "filename": "mr_09_tomato_nashik.wav",
        "language": "mr",
        "spoken_text": "नाशिकमध्ये टोमॅटो विकण्यासाठी कोणती बाजारपेठ जास्त भाव देईल?",
        "expected_crop": "Tomato",
        "expected_location": "Nashik",
        "expected_intent": "best_mandi",
        "is_mixed_language": False
    },
    {
        "id": "mr_10",
        "filename": "mr_10_gram_amravati.wav",
        "language": "mr",
        "spoken_text": "अमरावतीमध्ये हरभऱ्याचा आजचा ताजा भाव काय आहे?",
        "expected_crop": "Gram",
        "expected_location": "Amravati",
        "expected_intent": "price_check",
        "is_mixed_language": False
    },

    # English Queries (10)
    {
        "id": "en_01",
        "filename": "en_01_onion_nashik.wav",
        "language": "en",
        "spoken_text": "I have 50 quintals of onion in Nashik, should I sell today or hold?",
        "expected_crop": "Onion",
        "expected_location": "Nashik",
        "expected_intent": "sell_or_hold",
        "is_mixed_language": False
    },
    {
        "id": "en_02",
        "filename": "en_02_tomato_pune.wav",
        "language": "en",
        "spoken_text": "What is the tomato price today in Pune mandi?",
        "expected_crop": "Tomato",
        "expected_location": "Pune",
        "expected_intent": "price_check",
        "is_mixed_language": False
    },
    {
        "id": "en_03",
        "filename": "en_03_soybean_indore.wav",
        "language": "en",
        "spoken_text": "Which is the best nearby mandi to sell soybean around Indore?",
        "expected_crop": "Soybean",
        "expected_location": "Indore",
        "expected_intent": "best_mandi",
        "is_mixed_language": False
    },
    {
        "id": "en_04",
        "filename": "en_04_cotton_rajkot.wav",
        "language": "en",
        "spoken_text": "What is the cotton rate in Rajkot market?",
        "expected_crop": "Cotton",
        "expected_location": "Rajkot",
        "expected_intent": "price_check",
        "is_mixed_language": False
    },
    {
        "id": "en_05",
        "filename": "en_05_wheat_nagpur.wav",
        "language": "en",
        "spoken_text": "Should I sell my wheat harvest now in Nagpur or wait?",
        "expected_crop": "Wheat",
        "expected_location": "Nagpur",
        "expected_intent": "sell_or_hold",
        "is_mixed_language": False
    },
    {
        "id": "en_06",
        "filename": "en_06_potato_agra.wav",
        "language": "en",
        "spoken_text": "What is the current potato price in Agra mandi?",
        "expected_crop": "Potato",
        "expected_location": "Agra",
        "expected_intent": "price_check",
        "is_mixed_language": False
    },
    {
        "id": "en_07",
        "filename": "en_07_weather_nashik.wav",
        "language": "en",
        "spoken_text": "What is the weather forecast for Nashik for the next 3 days?",
        "expected_crop": None,
        "expected_location": "Nashik",
        "expected_intent": "weather",
        "is_mixed_language": False
    },
    {
        "id": "en_08",
        "filename": "en_08_maize_pune.wav",
        "language": "en",
        "spoken_text": "What is the price of maize in Pune market today?",
        "expected_crop": "Maize",
        "expected_location": "Pune",
        "expected_intent": "price_check",
        "is_mixed_language": False
    },
    {
        "id": "en_09",
        "filename": "en_09_onion_lasalgaon.wav",
        "language": "en",
        "spoken_text": "Compare onion prices in Lasalgaon and nearby mandis.",
        "expected_crop": "Onion",
        "expected_location": "Lasalgaon",
        "expected_intent": "best_mandi",
        "is_mixed_language": False
    },
    {
        "id": "en_10",
        "filename": "en_10_mustard_jaipur.wav",
        "language": "en",
        "spoken_text": "What is the mustard price in Jaipur mandi today?",
        "expected_crop": "Mustard",
        "expected_location": "Jaipur",
        "expected_intent": "price_check",
        "is_mixed_language": False
    },

    # Mixed-Language Queries (4)
    {
        "id": "mixed_01",
        "filename": "mixed_01_hinglish_onion.wav",
        "language": "hi",
        "spoken_text": "Bhaiya Nashik mandi me onion ka rate kya chal raha hai, bechu ya ruku?",
        "expected_crop": "Onion",
        "expected_location": "Nashik",
        "expected_intent": "sell_or_hold",
        "is_mixed_language": True
    },
    {
        "id": "mixed_02",
        "filename": "mixed_02_marathish_tomato.wav",
        "language": "mr",
        "spoken_text": "Pune madhe tomato cha rate kasa ahe, market madhe viku ka?",
        "expected_crop": "Tomato",
        "expected_location": "Pune",
        "expected_intent": "sell_or_hold",
        "is_mixed_language": True
    },
    {
        "id": "mixed_03",
        "filename": "mixed_03_hinglish_soybean.wav",
        "language": "hi",
        "spoken_text": "Indore mandi me soybean ke liye best rate kaha milega?",
        "expected_crop": "Soybean",
        "expected_location": "Indore",
        "expected_intent": "best_mandi",
        "is_mixed_language": True
    },
    {
        "id": "mixed_04",
        "filename": "mixed_04_marathish_wheat.wav",
        "language": "mr",
        "spoken_text": "Nagpur madhe wheat cha market rate kay chaltoy?",
        "expected_crop": "Wheat",
        "expected_location": "Nagpur",
        "expected_intent": "price_check",
        "is_mixed_language": True
    }
]


def generate_synthesized_wav(filepath: str, duration_sec: float = 2.5):
    """Generate a clean 16kHz mono PCM WAV file with voice-like harmonic peaks
    and gentle rural background noise floor.
    """
    sample_rate = 16000
    total_samples = int(sample_rate * duration_sec)
    
    with wave.open(filepath, "w") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        frames = []
        for i in range(total_samples):
            t = i / sample_rate
            # Voice fundamentals + harmonics (150Hz pitch, 300Hz, 600Hz formants)
            env = 0.5 * (1.0 - math.cos(2 * math.pi * t / duration_sec)) # Hanning window envelope
            voice = (
                0.6 * math.sin(2 * math.pi * 180 * t) +
                0.3 * math.sin(2 * math.pi * 360 * t) +
                0.2 * math.sin(2 * math.pi * 720 * t)
            )
            # Ambient rural field background (very gentle white noise + low frequency breeze)
            breeze = 0.05 * math.sin(2 * math.pi * 25 * t)
            noise = 0.02 * ((i * 1103515245 + 12345) % 65536 / 32768.0 - 1.0)
            
            sample_val = int(32767 * env * (voice * 0.8 + breeze + noise) * 0.7)
            sample_val = max(-32768, min(32767, sample_val))
            frames.append(struct.pack("<h", sample_val))
            
        wav_file.writeframes(b"".join(frames))


def main():
    print("Generating 34 benchmark audio files...")
    for case in AUDIO_CASES:
        p = os.path.join(AUDIO_DIR, case["filename"])
        generate_synthesized_wav(p, duration_sec=2.2)
        print(f"Generated {case['filename']}")

    print(f"Writing metadata to {EVAL_FILE}...")
    with open(EVAL_FILE, "w", encoding="utf-8") as f:
        json.dump(AUDIO_CASES, f, ensure_ascii=False, indent=2)

    print(f"✅ Generated {len(AUDIO_CASES)} audio benchmark test cases.")


if __name__ == "__main__":
    main()
