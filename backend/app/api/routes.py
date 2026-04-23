from datetime import datetime, timezone
from typing import Dict, List

from fastapi import APIRouter

from app.models.shipment_data import SHIPMENTS
from app.schemas.shipment_schema import ApiResponse, DashboardOverview, ExplainRequest, ExplainRiskResponse, ShipmentOut
from app.services.ais_service import get_vessels_snapshot
from app.services.global_risk_service import build_global_risk_intelligence
from app.services.dri_service import calculate_dri
from app.services.reroute_service import get_best_route
from app.services.explain_service import explain_risk
from app.core.config import settings
from app.services.weather_service import get_primary_zone, get_weather, get_weather_zones


router = APIRouter(prefix="", tags=["precursa"])


DEFAULT_WEATHER_ZONE = get_primary_zone()


def _build_shipments() -> List[ShipmentOut]:
    shipments: List[ShipmentOut] = []

    for raw in SHIPMENTS:
        dri_data = calculate_dri(raw)
        weather = dri_data["weather"]

        enriched: Dict[str, object] = {
            **raw,
            "dri": int(dri_data["dri"]),
            "rule_dri": int(dri_data.get("rule_dri", dri_data["dri"])),
            "ml_dri": int(dri_data.get("ml_dri", dri_data["dri"])),
            "xgb_dri": int(dri_data.get("xgb_dri", dri_data.get("ml_dri", dri_data["dri"]))),
            "lstm_dri": int(dri_data.get("lstm_dri", dri_data["dri"])),
            "trend": str(dri_data.get("trend", "stable")),
            "time_aware_prediction": bool(dri_data.get("time_aware_prediction", False)),
            "confidence": float(dri_data.get("confidence", 0.0)),
            "prediction_engine": dri_data.get("prediction_engine", "Rule-based fallback"),
            "factors": dri_data["factors"],
            "weather_risk": int(weather["risk"]),
            "weather": weather,
            "route_coords": get_best_route(raw["origin"], raw["destination"]),
            "rerouted": int(dri_data["dri"]) >= 75,
        }
        shipments.append(ShipmentOut(**enriched))

    return shipments


@router.get("/health", response_model=ApiResponse)
def health() -> ApiResponse:
    return ApiResponse(data={"service": "precursa-api", "healthy": True})


@router.get("/health/system", response_model=ApiResponse)
def system_health() -> ApiResponse:
    weather_snapshot = get_weather(DEFAULT_WEATHER_ZONE["lat"], DEFAULT_WEATHER_ZONE["lon"], zone_name=DEFAULT_WEATHER_ZONE["name"])
    vessels = get_vessels_snapshot()
    now = datetime.now(timezone.utc).isoformat()

    data = {
        "generated_at": now,
        "services": {
            "weather": {
                "status": "online" if weather_snapshot else "degraded",
                "source": weather_snapshot.get("source", "unknown"),
                "last_sync": weather_snapshot.get("timestamp", now),
            },
            "ais": {
                "status": "streaming" if len(vessels) > 0 else "awaiting-stream",
                "vessels": len(vessels),
                "last_sync": vessels[0].get("timestamp") if vessels and isinstance(vessels[0], dict) else now,
            },
            "gemini": {
                "status": "ready" if settings.GEMINI_API_KEY else "disabled",
                "model": settings.GEMINI_MODEL,
                "last_sync": now,
            },
        },
    }

    return ApiResponse(data=data)


@router.get("/shipments", response_model=ApiResponse)
def get_shipments() -> ApiResponse:
    shipments = _build_shipments()
    return ApiResponse(data=[item.model_dump() for item in shipments])


@router.get("/vessels", response_model=ApiResponse)
def get_vessels() -> ApiResponse:
    return ApiResponse(data=get_vessels_snapshot())


@router.get("/weather", response_model=ApiResponse)
def get_weather_endpoint(lat: float = DEFAULT_WEATHER_ZONE["lat"], lon: float = DEFAULT_WEATHER_ZONE["lon"]) -> ApiResponse:
    return ApiResponse(data=get_weather(lat, lon))


@router.get("/weather/zones", response_model=ApiResponse)
def get_weather_zones_endpoint() -> ApiResponse:
    return ApiResponse(data=get_weather_zones())


@router.get("/global-risk", response_model=ApiResponse)
def global_risk_endpoint(window: str = "24h") -> ApiResponse:
    return ApiResponse(data=build_global_risk_intelligence(window=window))


@router.get("/dashboard/overview", response_model=ApiResponse)
def dashboard_overview() -> ApiResponse:
    shipments = _build_shipments()
    active_vessels = get_vessels_snapshot()

    total_shipments = len(shipments)
    high_risk_shipments = sum(1 for shipment in shipments if shipment.dri >= 65)
    average_risk = round(sum(shipment.dri for shipment in shipments) / total_shipments) if total_shipments else 0

    weather_snapshot = get_weather(DEFAULT_WEATHER_ZONE["lat"], DEFAULT_WEATHER_ZONE["lon"], zone_name=DEFAULT_WEATHER_ZONE["name"])

    risk_totals = {
        "Weather": 0,
        "Congestion": 0,
        "Tariff": 0,
        "Carrier": 0,
        "Others": 0,
    }

    for shipment in shipments:
        for factor in shipment.factors:
            if factor.name == "Weather Severity":
                risk_totals["Weather"] += factor.value
            elif factor.name == "Port Congestion":
                risk_totals["Congestion"] += factor.value
            elif factor.name == "Tariff Risk":
                risk_totals["Tariff"] += factor.value
            elif factor.name == "Carrier Risk":
                risk_totals["Carrier"] += factor.value
            else:
                risk_totals["Others"] += factor.value

    total_factor = sum(risk_totals.values()) or 1
    risk_breakdown = [
        {"name": key, "value": round(value / total_factor * 100)}
        for key, value in risk_totals.items()
    ]

    top_shipments = sorted(shipments, key=lambda shipment: shipment.dri, reverse=True)[:7]

    overview = DashboardOverview(
        total_shipments=total_shipments,
        high_risk_shipments=high_risk_shipments,
        active_vessels=len(active_vessels),
        average_risk=average_risk,
        current_weather=weather_snapshot,
        risk_breakdown=risk_breakdown,
        top_shipments=top_shipments,
    )

    return ApiResponse(data=overview.model_dump())


@router.get("/dri/test", response_model=ApiResponse)
def dri_test_endpoint() -> ApiResponse:
    sample = {
        "weather_severity": 65,
        "congestion_score": 70,
        "vessel_density": 55,
        "route_length": 5000,
        "visibility": 7,
    }

    from app.services.ml_service import predict_dri

    try:
        return ApiResponse(data=predict_dri(sample))
    except Exception:
        return ApiResponse(data={"predicted_dri": 0, "confidence": 0.0, "engine": "unavailable"})


@router.get("/dri/test/lstm", response_model=ApiResponse)
def dri_lstm_test_endpoint() -> ApiResponse:
    sample_sequence = [
        [52, 58, 44, 9],
        [55, 59, 45, 9],
        [58, 61, 46, 8.8],
        [60, 62, 48, 8.7],
        [62, 64, 49, 8.5],
        [63, 66, 51, 8.4],
        [65, 67, 52, 8.2],
        [66, 68, 54, 8.1],
        [68, 70, 55, 7.9],
        [69, 72, 57, 7.8],
    ]

    from app.services.lstm_service import predict_dri as predict_lstm_dri

    try:
        return ApiResponse(data=predict_lstm_dri(sample_sequence))
    except Exception:
        return ApiResponse(data={"lstm_dri": 0, "trend": "stable", "engine": "unavailable"})


@router.post("/explain-risk", response_model=ApiResponse)
def explain_risk_endpoint(payload: ExplainRequest) -> ApiResponse:
    analysis = explain_risk(payload.model_dump())
    return ApiResponse(data=ExplainRiskResponse(**analysis).model_dump())


@router.post("/explain", response_model=ApiResponse)
def explain(payload: ExplainRequest) -> ApiResponse:
    analysis = explain_risk(payload.model_dump())
    return ApiResponse(data=ExplainRiskResponse(**analysis).model_dump())