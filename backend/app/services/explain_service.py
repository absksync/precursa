import logging
from math import sqrt
from typing import Dict, List

from app.services.ais_service import get_vessels_snapshot
from app.services.gemini_service import generate_risk_insight
from app.services.weather_service import get_primary_zone, get_weather, get_weather_zones


logger = logging.getLogger(__name__)


def _clamp(value: float, low: int = 0, high: int = 100) -> int:
    return int(max(low, min(high, round(value))))


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: object, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    from math import atan2, cos, radians, sin

    radius = 6371.0
    lat1_r, lon1_r, lat2_r, lon2_r = map(radians, [lat1, lon1, lat2, lon2])
    delta_lat = lat2_r - lat1_r
    delta_lon = lon2_r - lon1_r
    a = sin(delta_lat / 2) ** 2 + cos(lat1_r) * cos(lat2_r) * sin(delta_lon / 2) ** 2
    return 2 * radius * atan2(sqrt(a), sqrt(1 - a))


def _route_points(shipment: Dict[str, object]) -> List[List[float]]:
    route_coords = shipment.get("route_coords") or []
    points = []
    if isinstance(route_coords, list):
        for item in route_coords:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                lat = _safe_float(item[0], default=0.0)
                lon = _safe_float(item[1], default=0.0)
                points.append([lat, lon])

    if not points:
        points.append([
            _safe_float(shipment.get("lat"), default=0.0),
            _safe_float(shipment.get("lon"), default=0.0),
        ])

    return points


def _mean_point(points: List[List[float]]) -> List[float]:
    if not points:
        return [0.0, 0.0]
    lat = sum(point[0] for point in points) / len(points)
    lon = sum(point[1] for point in points) / len(points)
    return [lat, lon]


def _weather_impact(weather: Dict[str, object]) -> int:
    wind_speed = _safe_float(weather.get("wind_speed") or weather.get("wind_kph"), 0.0)
    rain = _safe_float(weather.get("rain"), 0.0)
    visibility = _safe_float(weather.get("visibility"), 10.0)

    wind_score = min(100.0, wind_speed * 3.2)
    rain_score = min(100.0, rain * 9.0)
    visibility_score = min(100.0, max(0.0, 100.0 - (visibility * 10.0)))

    return _clamp(wind_score * 0.38 + rain_score * 0.37 + visibility_score * 0.25)


def _nearby_vessels(route_points: List[List[float]], vessels: List[Dict[str, object]], radius_km: float = 20.0) -> List[Dict[str, object]]:
    nearby = []
    for vessel in vessels:
        lat = _safe_float(vessel.get("lat"), 0.0)
        lon = _safe_float(vessel.get("lon"), 0.0)
        min_distance = min(_haversine_km(lat, lon, point[0], point[1]) for point in route_points)
        if min_distance <= radius_km:
            nearby.append({**vessel, "distance_km": min_distance})
    return nearby


def _congestion_impact(route_points: List[List[float]], vessels: List[Dict[str, object]], nearby_vessels: List[Dict[str, object]]) -> int:
    if not nearby_vessels:
        return 0

    proximity_score = sum(max(0.0, 1.0 - (float(v.get("distance_km", 20.0)) / 20.0)) for v in nearby_vessels) / len(nearby_vessels)
    sog_pressure = sum(min(1.0, _safe_float(v.get("sog"), 0.0) / 15.0) for v in nearby_vessels) / len(nearby_vessels)
    density_pressure = min(100.0, len(nearby_vessels) * 7.5)

    return _clamp(density_pressure * 0.45 + proximity_score * 100.0 * 0.35 + sog_pressure * 100.0 * 0.2)


def _route_density(route_points: List[List[float]], nearby_vessels: List[Dict[str, object]]) -> int:
    if not nearby_vessels:
        return 0

    buckets: Dict[tuple[float, float], int] = {}
    for vessel in nearby_vessels:
        lat = _safe_float(vessel.get("lat"), 0.0)
        lon = _safe_float(vessel.get("lon"), 0.0)
        bucket = (round(lat, 1), round(lon, 1))
        buckets[bucket] = buckets.get(bucket, 0) + 1

    largest_cluster = max(buckets.values()) if buckets else 0
    cluster_ratio = largest_cluster / len(nearby_vessels)
    route_span = 0.0
    if len(route_points) > 1:
        route_span = sum(
            _haversine_km(route_points[index][0], route_points[index][1], route_points[index + 1][0], route_points[index + 1][1])
            for index in range(len(route_points) - 1)
        )

    span_pressure = min(100.0, route_span / 6.0)
    density = len(nearby_vessels) * 5.0 + cluster_ratio * 30.0 + span_pressure * 0.2
    return _clamp(density)


def _carrier_impact(shipment: Dict[str, object]) -> int:
    factors = shipment.get("factors") or []
    if isinstance(factors, list):
        for factor in factors:
            if isinstance(factor, dict) and str(factor.get("name", "")).lower() == "carrier risk":
                return _clamp(_safe_float(factor.get("value"), 0.0))

    cargo = str(shipment.get("cargo", "general")).lower()
    biases = {
        "electronics": 8,
        "pharma": 10,
        "automotive": 12,
        "apparel": 6,
    }
    return _clamp(biases.get(cargo, 7))


def _level_from_dri(dri: int) -> str:
    if dri >= 80:
        return "Critical"
    if dri >= 65:
        return "High"
    if dri >= 45:
        return "Medium"
    return "Low"


def _weather_details(weather: Dict[str, object]) -> Dict[str, str]:
    return {
        "wind": f"{_safe_float(weather.get('wind_speed') or weather.get('wind_kph'), 0.0):.0f} km/h",
        "rain": f"{_safe_float(weather.get('rain'), 0.0):.0f} mm/hr",
        "visibility": f"{_safe_float(weather.get('visibility'), 0.0):.0f} km",
    }


def _zone_label(zone: Dict[str, object], weather: Dict[str, object], nearby_vessels: int, congestion_impact: int) -> str:
    weather_severity = _safe_float(zone.get("severity"), 0.0)
    rain = _safe_float(weather.get("rain"), 0.0)
    wind = _safe_float(weather.get("wind_speed") or weather.get("wind_kph"), 0.0)
    visibility = _safe_float(weather.get("visibility"), 10.0)

    if rain >= 8 or weather_severity >= 75:
        return "Heavy Rain"
    if wind >= 22 or weather_severity >= 70:
        return "High Wind"
    if visibility <= 6:
        return "Low Visibility"
    if nearby_vessels >= 4 or congestion_impact >= 60:
        return "Congestion"
    return "Weather Pressure"


def _zone_candidates(shipment: Dict[str, object], route_points: List[List[float]], nearby_vessels: List[Dict[str, object]], congestion_impact: int) -> List[str]:
    zones = get_weather_zones()
    if not zones:
        return []

    route_center = _mean_point(route_points)
    scored_zones = []
    for zone in zones:
        zone_weather = get_weather(zone["lat"], zone["lon"], zone_name=str(zone["name"]))
        nearby_route = _haversine_km(route_center[0], route_center[1], zone["lat"], zone["lon"]) if route_points else 0.0
        vessel_pressure = sum(1 for vessel in nearby_vessels if _haversine_km(_safe_float(vessel.get("lat"), 0.0), _safe_float(vessel.get("lon"), 0.0), zone["lat"], zone["lon"]) <= 35.0)
        score = (
            _safe_float(zone.get("severity"), 0.0) * 0.55
            + min(100.0, vessel_pressure * 15.0) * 0.25
            + max(0.0, 100.0 - min(100.0, nearby_route * 2.5)) * 0.2
        )
        scored_zones.append((score, zone, zone_weather, vessel_pressure))

    scored_zones.sort(key=lambda item: item[0], reverse=True)

    labels = []
    for _, zone, zone_weather, vessel_pressure in scored_zones[:3]:
        labels.append(f"{zone['name']} - {_zone_label(zone, zone_weather, vessel_pressure, congestion_impact)}")

    return labels


def explain_risk(shipment: Dict[str, object]) -> Dict[str, object]:
    route_points = _route_points(shipment)
    vessels = get_vessels_snapshot(limit=80)
    weather = get_weather(
        _safe_float(shipment.get("lat"), default=get_primary_zone()["lat"]),
        _safe_float(shipment.get("lon"), default=get_primary_zone()["lon"]),
    )

    nearby_vessels = _nearby_vessels(route_points, vessels)
    weather_impact = _weather_impact(weather)
    congestion_impact = _congestion_impact(route_points, vessels, nearby_vessels)
    density_impact = _route_density(route_points, nearby_vessels)
    carrier_impact = _carrier_impact(shipment)

    dri = _safe_int(shipment.get("dri"), default=_clamp(weather_impact * 0.25 + congestion_impact * 0.35 + density_impact * 0.2 + carrier_impact * 0.2))
    level = _level_from_dri(dri)

    delay_hours = (weather_impact * 0.4 + congestion_impact * 0.4 + density_impact * 0.2) * 0.5
    delay_low = max(1, int(round(delay_hours * 0.8)))
    delay_high = max(delay_low + 1, int(round(delay_hours * 1.2)))

    route_zones = _zone_candidates(shipment, route_points, nearby_vessels, congestion_impact)

    breakdown = {
        "weather": weather_impact,
        "congestion": congestion_impact,
        "density": density_impact,
        "carrier": carrier_impact,
    }

    gemini_insight = generate_risk_insight({
        "shipment": shipment,
        "weather": weather,
        "breakdown": breakdown,
        "nearby_vessels": nearby_vessels[:10],
        "route_zones": route_zones,
        "dri": dri,
        "level": level,
    })

    dominant = sorted(breakdown.items(), key=lambda item: item[1], reverse=True)
    top_factor = dominant[0][0]
    zones_text = route_zones[0] if route_zones else "route exposure"
    if top_factor == "weather":
        insight = f"High risk is driven by severe weather conditions and overlapping weather bands near {zones_text.split(' - ')[0]}."
    elif top_factor == "congestion":
        insight = f"High risk is driven by AIS congestion with {len(nearby_vessels)} nearby vessels crowding the route corridor."
    elif top_factor == "density":
        insight = f"High risk is driven by vessel clustering along a dense route corridor, especially near {zones_text.split(' - ')[0]}."
    else:
        insight = f"High risk remains elevated because carrier pressure combines with weather and AIS congestion across the route."

    if gemini_insight:
        insight = gemini_insight

    return {
        "shipment_id": shipment.get("id", "Unknown"),
        "origin": shipment.get("origin", "N/A"),
        "destination": shipment.get("destination", "N/A"),
        "route": f"{shipment.get('origin', 'N/A')} → {shipment.get('destination', 'N/A')}",
        "dri": dri,
        "level": level,
        "breakdown": breakdown,
        "delay_estimate": f"{delay_low}–{delay_high} hours",
        "zones": route_zones,
        "weather_details": _weather_details(weather),
        "insight": insight,
        "weather_risk": _safe_int(weather.get("weather_severity") or weather.get("risk"), 0),
        "congestion_score": congestion_impact,
        "vessels_nearby": len(nearby_vessels),
        "weather": weather,
        "analysis_source": "gemini" if gemini_insight else "deterministic-fallback",
    }