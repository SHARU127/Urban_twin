def predict_risks(weather_condition: str, temperature: float, recent_incidents: list):
    # Default values
    traffic_risk = "Low"
    infra_risk = "Low"
    recommendation = "Normal operations."

    # Rule 1: Weather Impact
    if "rain" in weather_condition.lower() or "storm" in weather_condition.lower():
        traffic_risk = "High"
        recommendation = "High traffic expected due to rain. Deploy traffic police."
    
    # Rule 2: Heat Impact
    if temperature > 35:
        infra_risk = "Medium"
        recommendation = "Monitor power grids for overheating."

    # Rule 3: Incident Impact
    for incident in recent_incidents:
        if incident.type.lower() == "flood" or incident.severity.lower() == "high":
            traffic_risk = "High"
            infra_risk = "High"
            recommendation = "EMERGENCY: Immediate response required. Re-route traffic."
            break # Stop checking, risk is already maxed out

    return {
        "traffic_congestion_risk": traffic_risk,
        "infrastructure_risk": infra_risk,
        "recommendation": recommendation
    }
