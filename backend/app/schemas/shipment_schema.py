from typing import Any, Dict, List

from pydantic import BaseModel


class Factor(BaseModel):
    name: str
    value: int


class WeatherSnapshot(BaseModel):
    zone_name: str
    lat: float
    lon: float
    wind_speed: float
    visibility: float
    rain: float
    temperature: float
    weather_severity: int
    timestamp: str
    source: str
    condition: str
    risk: int
    temp_c: float
    wind_kph: float
    humidity: int


class WeatherZone(BaseModel):
    name: str
    lat: float
    lon: float
    severity: int
    timestamp: str


class RiskBreakdown(BaseModel):
    weather: int
    congestion: int
    density: int
    carrier: int


class ExplainRiskResponse(BaseModel):
    shipment_id: str
    origin: str
    destination: str
    route: str
    dri: int
    level: str
    breakdown: RiskBreakdown
    delay_estimate: str
    zones: List[str]
    weather_details: Dict[str, str]
    insight: str
    weather_risk: int
    congestion_score: int
    vessels_nearby: int
    analysis_source: str


class ShipmentOut(BaseModel):
    id: str
    origin: str
    destination: str
    current_location: str
    lat: float
    lon: float
    cargo: str
    dri: int
    weather_risk: int
    weather: WeatherSnapshot
    factors: List[Factor]
    rerouted: bool
    route_coords: List[List[float]]


class ExplainRequest(BaseModel):
    shipment: Dict[str, Any]


class ApiResponse(BaseModel):
    status: str = "ok"
    data: Any


class DashboardOverview(BaseModel):
    total_shipments: int
    high_risk_shipments: int
    active_vessels: int
    average_risk: int
    current_weather: WeatherSnapshot
    risk_breakdown: List[Factor]
    top_shipments: List[ShipmentOut]