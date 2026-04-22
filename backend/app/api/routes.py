from fastapi import APIRouter
from app.models.shipment_data import SHIPMENTS
from app.services.dri_service import calculate_dri
from app.services.reroute_service import get_best_route
from app.services.ais_service import VESSELS

# ✅ DEFINE ROUTER FIRST
router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/shipments")
def get_shipments():
    response = []

    for s in SHIPMENTS:
        dri_data = calculate_dri(s)

        shipment = s.copy()
        shipment["dri"] = dri_data["dri"]
        shipment["factors"] = dri_data["factors"]

        # 🌦 extract weather
        weather_factor = next(
            (f["value"] for f in dri_data["factors"] if f["name"] == "Weather Risk"),
            20
        )

        shipment["weather_risk"] = weather_factor

        route_coords = get_best_route(
            shipment["origin"],
            shipment["destination"]
        )

        shipment["route_coords"] = route_coords
        shipment["rerouted"] = shipment["dri"] > 75

        response.append(shipment)

    return response


@router.get("/vessels")
def get_vessels():
    return VESSELS
from app.services.copilot_service import get_ai_explanation


@router.post("/explain")
def explain(shipment: dict):
    explanation = get_ai_explanation(shipment)
    return {"explanation": explanation}