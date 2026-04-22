from pydantic import BaseModel
from typing import List, Dict


class Factor(BaseModel):
    name: str
    value: int


class Shipment(BaseModel):
    id: str
    origin: str
    destination: str
    current_location: str
    lat: float
    lon: float
    cargo: str
    dri: int
    factors: List[Factor]
    rerouted: bool
    route: List[str]