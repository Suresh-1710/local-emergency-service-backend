import math
from typing import Optional, Tuple

import requests

NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"
EARTH_RADIUS_KM = 6371.0


def geocode_address(address_text: str) -> Optional[Tuple[float, float]]:
    try:
        response = requests.get(
            NOMINATIM_SEARCH_URL,
            params={"q": address_text, "format": "json", "limit": 1},
            headers={"User-Agent": "local-emergency-service-connect/1.0"},
            timeout=5,
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
    try:
        response = requests.get(
            NOMINATIM_REVERSE_URL,
            params={"lat": latitude, "lon": longitude, "format": "json"},
            headers={"User-Agent": "local-emergency-service-connect/1.0"},
            timeout=5,
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
