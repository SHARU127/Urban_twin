from pydantic import BaseModel

from typing import List

class IncidentCreate(BaseModel):
    type: str
    location: str
    severity: str
    reported_by: str

class ChokePointRisk(BaseModel):
    name: str
    latitude: float
    longitude: float
    risk_level: str

class PredictionResponse(BaseModel):
    traffic_congestion_risk: str
    infrastructure_risk: str
    crowd_risk: str
    recommendation: str
    choke_points: List[ChokePointRisk] = []
    cascading_alerts: List[str] = []