import os
import json
from typing import Dict, Any, Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
PLACES_PATH = os.path.join(DATA_DIR, "places_localized.json")
CROPS_PATH = os.path.join(DATA_DIR, "crops_glossary.json")

_places_cache = None
_crops_cache = None


def _load_places() -> Dict[str, Any]:
    global _places_cache
    if _places_cache is None:
        if os.path.exists(PLACES_PATH):
            with open(PLACES_PATH, "r", encoding="utf-8") as f:
                _places_cache = json.load(f)
        else:
            _places_cache = {}
    return _places_cache


def _load_crops() -> Dict[str, Any]:
    global _crops_cache
    if _crops_cache is None:
        if os.path.exists(CROPS_PATH):
            with open(CROPS_PATH, "r", encoding="utf-8") as f:
                _crops_cache = json.load(f)
        else:
            _crops_cache = {}
    return _crops_cache


def get_localized_place(place_name: str, lang: str = "en") -> str:
    """
    Get localized name of a mandi or district in the target language.
    """
    if not place_name:
        return ""
    places = _load_places()
    for canonical, details in places.items():
        if canonical.lower() == place_name.lower():
            return details.get("names", {}).get(lang, place_name)
        # Check if already in another language
        for l, n in details.get("names", {}).items():
            if n.lower() == place_name.lower():
                return details.get("names", {}).get(lang, n)
    return place_name


def get_localized_crop(crop_name: str, lang: str = "en") -> str:
    """
    Get localized name of a crop in the target language.
    """
    if not crop_name:
        return ""
    crops = _load_crops()
    for canonical, details in crops.items():
        if canonical.lower() == crop_name.lower():
            aliases = details.get("aliases", {}).get(lang, [])
            return aliases[0] if aliases else canonical
        # Check aliases
        for l, alias_list in details.get("aliases", {}).items():
            if any(a.lower() == crop_name.lower() for a in alias_list):
                target_aliases = details.get("aliases", {}).get(lang, [])
                return target_aliases[0] if target_aliases else canonical
    return crop_name
