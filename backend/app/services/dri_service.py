import hashlib
import logging
import random
from typing import Dict

from app.services.ais_service import get_vessels_snapshot
from app.services.weather_service import get_weather


logger = logging.getLogger(__name__)


def _bounded(value: float, low: int = 0, high: int = 100) -> int:
    return int(max(low, min(high, round(value))))


def _seeded_random(shipment_id: str, origin: str, destination: str) -> random.Random:
    seed_input = f"{shipment_id}:{origin}:{destination}"
    seed = int(hashlib.sha256(seed_input.encode("utf-8")).hexdigest()[:12], 16)
    return random.Random(seed)


def _congestion_score(vessel_count: int) -> int:
    # Logistic-style ramp translated into simple bounded curve.
    score = 100 * (1 - (2.718281828 ** (-vessel_count / 28)))
    return _bounded(score)


def calculate_dri(shipment: Dict[str, object]) -> Dict[str, object]:
    lat = float(shipment.get("lat", 0.0))
    lon = float(shipment.get("lon", 0.0))

    shipment_id = str(shipment.get("id", "UNKNOWN"))
    origin = str(shipment.get("origin", ""))
    destination = str(shipment.get("destination", ""))
    cargo = str(shipment.get("cargo", "general")).lower()

    weather = get_weather(lat, lon)
    vessel_count = len(get_vessels_snapshot())

    rng = _seeded_random(shipment_id=shipment_id, origin=origin, destination=destination)

    cargo_tariff_bias = {
        "electronics": 6,
        "pharma": 8,
        "automotive": 10,
        "apparel": 4,
    }.get(cargo, 5)

    tariff_risk = _bounded(rng.uniform(20, 45) + cargo_tariff_bias + random.uniform(-4, 7))
    carrier_risk = _bounded(rng.uniform(18, 40) + random.uniform(-6, 9))
    congestion = _congestion_score(vessel_count)
    weather_severity = int(weather["weather_severity"])
    base_risk = _bounded(congestion * 0.42 + tariff_risk * 0.33 + carrier_risk * 0.25)

    dri = _bounded(base_risk + (weather_severity * 0.25))

    factors = [
        {"name": "Port Congestion", "value": congestion},
        {"name": "Weather Severity", "value": weather_severity},
        {"name": "Tariff Risk", "value": tariff_risk},
        {"name": "Carrier Risk", "value": carrier_risk},
        {"name": "Base Risk", "value": base_risk},
        {"name": "Live Vessel Count", "value": vessel_count},
    ]

    logger.debug(
        "DRI calculation shipment=%s dri=%s vessel_count=%s weather=%s tariff=%s carrier=%s",
        shipment_id,
        dri,
        vessel_count,
        weather_severity,
        tariff_risk,
        carrier_risk,
    )

    return {
        "dri": dri,
        "base_risk": base_risk,
        "weather_severity": weather_severity,
        "factors": factors,
        "weather": weather,
    }