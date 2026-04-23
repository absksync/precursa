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
    rule_dri: int
    ml_dri: int
    xgb_dri: int | None = None
    lstm_dri: int | None = None
    trend: str | None = None
    time_aware_prediction: bool | None = None
    confidence: float
    prediction_engine: str
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
    rule_dri: int | None = None
    ml_dri: int | None = None
    xgb_dri: int | None = None
    lstm_dri: int | None = None
    trend: str | None = None
    time_aware_prediction: bool | None = None
    confidence: float | None = None
    prediction_engine: str | None = None
    weather_risk: int
    weather: WeatherSnapshot
    factors: List[Factor]
    rerouted: bool
    route_coords: List[List[float]]


class ExplainWeatherInput(BaseModel):
    temperature: float
    wind_speed: float
    rain: float
    visibility: float
    severity: int


class ExplainRequest(BaseModel):
    id: str
    origin: str
    destination: str
    route: str
    dri: int
    weather: ExplainWeatherInput
    congestion: int
    risk_level: str
    lat: float | None = None
    lon: float | None = None
    route_coords: List[List[float]] | None = None
    cargo: str | None = None
    factors: List[Factor] | None = None
    rule_dri: int | None = None
    ml_dri: int | None = None
    xgb_dri: int | None = None
    lstm_dri: int | None = None
    trend: str | None = None
    time_aware_prediction: bool | None = None
    confidence: float | None = None
    prediction_engine: str | None = None


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


class GlobalRiskArticle(BaseModel):
    headline: str
    region: str
    risk_level: str
    reasoning: str
    impact_summary: str
    published_at: str
    timestamp: str
    source: str
    url: str | None = None


class GlobalRiskSummary(BaseModel):
    total_articles: int
    high_risk_articles: int
    medium_risk_articles: int
    low_risk_articles: int
    dominant_region: str
    top_signal: str
    source: str


class GlobalRiskResponse(BaseModel):
    generated_at: str
    window: str
    source: str
    status: str
    search_terms: List[str]
    summary: GlobalRiskSummary
    events: List[GlobalRiskArticle]