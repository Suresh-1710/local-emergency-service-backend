import math
import os
from typing import Optional, Tuple

import requests
from dotenv import load_dotenv

load_dotenv()

LOCATIONIQ_API_KEY = os.getenv("LOCATIONIQ_API_KEY")
LOCATIONIQ_SEARCH_URL = "https://us1.locationiq.com/v1/search"
LOCATIONIQ_REVERSE_URL = "https://us1.locationiq.com/v1/reverse"
EARTH_RADIUS_KM = 6371.0


def geocode_address(address_text: str) -> Optional[Tuple[float, float]]:
    if not LOCATIONIQ_API_KEY:
        return None

    try:
        response = requests.get(
            LOCATIONIQ_SEARCH_URL,
            params={"key": LOCATIONIQ_API_KEY, "q": address_text, "format": "json", "limit": 1},
            timeout=8,
        )
        response.raise_for_status()
        results = response.json()
    except (requests.RequestException, ValueError):
        return None

    if not results:
        return None

    try:
        return round(float(results[0]["lat"]), 6), round(float(results[0]["lon"]), 6)
    except (KeyError, ValueError, TypeError):
        return None


def reverse_geocode(latitude: float, longitude: float) -> Optional[str]:
    if not LOCATIONIQ_API_KEY:
        return None

    try:
        response = requests.get(
            LOCATIONIQ_REVERSE_URL,
            params={"key": LOCATIONIQ_API_KEY, "lat": latitude, "lon": longitude, "format": "json"},
            timeout=8,
        )
        response.raise_for_status()
        result = response.json()
    except (requests.RequestException, ValueError):
        return None

    return result.get("display_name")


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_KM * c
