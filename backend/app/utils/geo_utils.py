import json
import math
from typing import Optional, List, Tuple

try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False

try:
    from shapely.geometry import Point, Polygon
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False


def geocode_address(address: str, city: str = "", state: str = "") -> Tuple[Optional[float], Optional[float]]:
    """Return (latitude, longitude) for the given address using Nominatim."""
    if not GEOPY_AVAILABLE:
        return None, None
    query_parts = [p for p in [address, city, state, "Brasil"] if p]
    query = ", ".join(query_parts)
    try:
        geolocator = Nominatim(user_agent="lead-platform-mvp/1.0")
        location = geolocator.geocode(query, timeout=10)
        if location:
            return location.latitude, location.longitude
    except GeocoderTimedOut:
        pass
    except Exception:
        pass
    return None, None


def _point_in_polygon_ray_cast(lat: float, lng: float, polygon: List[List[float]]) -> bool:
    """Ray-casting algorithm fallback when Shapely is unavailable."""
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i][1], polygon[i][0]  # lng, lat
        xj, yj = polygon[j][1], polygon[j][0]
        intersect = ((yi > lng) != (yj > lng)) and (lat < (xj - xi) * (lng - yi) / (yj - yi + 1e-10) + xi)
        if intersect:
            inside = not inside
        j = i
    return inside


def find_territory(lat: float, lng: float, territories) -> Optional[int]:
    """Return the id of the first territory whose polygon contains (lat, lng)."""
    for territory in territories:
        if not territory.polygon:
            continue
        try:
            polygon_coords = json.loads(territory.polygon)  # [[lat, lng], ...]
        except (json.JSONDecodeError, TypeError):
            continue
        if len(polygon_coords) < 3:
            continue
        if SHAPELY_AVAILABLE:
            try:
                point = Point(lng, lat)
                poly = Polygon([(c[1], c[0]) for c in polygon_coords])
                if poly.contains(point):
                    return territory.id
            except Exception:
                pass
        else:
            if _point_in_polygon_ray_cast(lat, lng, polygon_coords):
                return territory.id
    return None


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Return great-circle distance in km between two points."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
