from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime



app = FastAPI()

class Incident(BaseModel):
    type: str
    location: str
    severity: str
    reported_by: str
    

incidents = []

@app.get("/")
def home():
    return incidents

@app.post("/incidents")
def report_incident(incident: Incident):
    incident_dict = incident.model_dump()
    incident_dict["reported_at"] = datetime.now().isoformat()
    incident_dict["id"] = len(incidents) +1
    incidents.append(incident_dict)
    return { "message" : "incident reported!","incident": incident_dict}

@app.get("/incidents/{id}")
def get_incident(id:int):
    for incident in incidents:
        if incident["id"] == id:
            return incident
    return {"error": "incident not found"}