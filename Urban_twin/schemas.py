from pydantic import BaseModel

class IncidentCreate(BaseModel):
    type: str
    location: str
    severity: str
    reported_by: str


class PredictionResponse(BaseModel):
    traffic_congestion_risk: str
    infrastructure_risk: str
    recommendation: str