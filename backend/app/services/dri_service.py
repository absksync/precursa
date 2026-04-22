import random
from app.services.ais_service import VESSELS
from app.services.weather_service import get_weather_risk


def calculate_dri(shipment):
    lat = shipment["lat"]
    lon = shipment["lon"]

    # 🔥 REAL WEATHER
    weather = get_weather_risk(lat, lon)

    tariff = random.randint(5, 35)
    carrier = random.randint(10, 30)

    # AIS congestion
    vessel_count = len(VESSELS)

    if vessel_count > 15:
        congestion = 70
    elif vessel_count > 10:
        congestion = 50
    elif vessel_count > 5:
        congestion = 35
    else:
        congestion = 20

    dri = (
        congestion * 0.35 +
        weather * 0.25 +
        tariff * 0.20 +
        carrier * 0.20
    )

    return {
        "dri": int(dri),
        "factors": [
            {"name": "Port Congestion", "value": congestion},
            {"name": "Weather Risk", "value": weather},
            {"name": "Tariff Risk", "value": tariff},
            {"name": "Carrier Risk", "value": carrier},
            {"name": "Live Vessel Count", "value": vessel_count}
        ]
    }