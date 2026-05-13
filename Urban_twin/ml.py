import math
import joblib
import pandas as pd

# Define known choke points in Bengaluru with their coordinates
CHOKE_POINTS = [
    {"name": "Silk Board Junction", "latitude": 12.9176, "longitude": 77.6235},
    {"name": "KR Puram", "latitude": 13.0019, "longitude": 77.6835},
    {"name": "Marathahalli", "latitude": 12.9569, "longitude": 77.7011},
    {"name": "Electronic City", "latitude": 12.8399, "longitude": 77.6770},
    {"name": "Tin Factory", "latitude": 12.9961, "longitude": 77.6620}
]

# Graph Network defining adjacent choke points for spatial propagation
CHOKE_POINT_GRAPH = {
    "Silk Board Junction": ["Electronic City", "Marathahalli"],
    "Electronic City": ["Silk Board Junction"],
    "Marathahalli": ["Silk Board Junction", "KR Puram"],
    "KR Puram": ["Marathahalli", "Tin Factory"],
    "Tin Factory": ["KR Puram"]
}

# Try loading the True ML Models
try:
    models = joblib.load('model.pkl')
    clf_traffic = models['traffic']
    clf_infra = models['infra']
    clf_crowd = models['crowd']
    ML_ENABLED = True
except Exception as e:
    print(f"ML Model Error: {e}")
    ML_ENABLED = False

def calculate_distance(lat1, lon1, lat2, lon2):
    x = (lon2 - lon1) * math.cos(math.radians((lat1 + lat2) / 2))
    y = (lat2 - lat1)
    distance = math.sqrt(x * x + y * y) * 111
    return distance

def map_risk_int_to_str(risk_int):
    if risk_int == 2: return "High"
    if risk_int == 1: return "Medium"
    return "Low"

def predict_risks(weather_condition: str, temperature: float, recent_incidents: list):
    cascading_alerts = []
    recommendation = "Normal operations."

    is_raining = "rain" in weather_condition.lower() or "storm" in weather_condition.lower()
    
    # Evaluate aggregate incident features for the ML model
    max_severity = 0
    is_festival = 0
    for incident in recent_incidents:
        inc_type = incident.type.lower()
        if incident.severity.lower() == "high" or "flood" in inc_type:
            max_severity = 2
        elif incident.severity.lower() == "medium" and max_severity < 2:
            max_severity = 1
        if "festival" in inc_type or "gathering" in inc_type or "protest" in inc_type or "event" in inc_type:
            is_festival = 1

    # --- TRUE MACHINE LEARNING INFERENCE ---
    if ML_ENABLED:
        input_data = pd.DataFrame([{
            'Temperature': temperature,
            'Is_Raining': 1 if is_raining else 0,
            'Incident_Severity': max_severity,
            'Is_Festival': is_festival
        }])
        traffic_risk = map_risk_int_to_str(clf_traffic.predict(input_data)[0])
        infra_risk = map_risk_int_to_str(clf_infra.predict(input_data)[0])
        crowd_risk = map_risk_int_to_str(clf_crowd.predict(input_data)[0])
    else:
        # Fallback basic logic
        traffic_risk = "Low"
        infra_risk = "Low"
        crowd_risk = "Low"

    # Set recommendations based on ML output
    if traffic_risk == "High":
        recommendation = "High traffic expected. Deploy traffic police."
    if infra_risk == "High" or traffic_risk == "High" and max_severity == 2:
        recommendation = "EMERGENCY: Immediate response required. Re-route traffic."
    if crowd_risk == "High":
        recommendation = "High crowd density predicted by ML model. Manage crowd flow."

    # --- SPATIAL PROPAGATION ALGORITHM ---
    # Initialize all choke points to ML's base traffic risk
    choke_point_status = {cp["name"]: {"data": cp, "risk": "Low"} for cp in CHOKE_POINTS}
    
    for cp in CHOKE_POINTS:
        choke_point_status[cp["name"]]["risk"] = traffic_risk if traffic_risk != "High" else "Medium"

    # Step 1: Assign direct risks from nearby incidents
    high_risk_nodes = []
    for incident in recent_incidents:
        inc_type = incident.type.lower()
        
        # Cascading Event Logic
        if is_raining and ("blockage" in inc_type or "drain" in inc_type or "water" in inc_type):
            infra_risk = "High"
            alert = "⚠️ Cascading Risk: Rainfall combined with reported blockages is highly likely to cause severe localized flooding, leading to pothole formation and road damage."
            if alert not in cascading_alerts: cascading_alerts.append(alert)
                
        if is_raining and is_festival:
            alert = "⚠️ Cascading Risk: Sudden rainfall during a large public gathering will trigger rapid, chaotic crowd dispersal, severely stressing local transit infrastructure."
            if alert not in cascading_alerts: cascading_alerts.append(alert)

        for cp in CHOKE_POINTS:
            dist = calculate_distance(incident.latitude, incident.longitude, cp["latitude"], cp["longitude"])
            if dist < 3.0: 
                if incident.severity.lower() == "high" or "flood" in inc_type:
                    choke_point_status[cp["name"]]["risk"] = "High"
                    high_risk_nodes.append(cp["name"])
                elif incident.severity.lower() == "medium" and choke_point_status[cp["name"]]["risk"] != "High":
                    choke_point_status[cp["name"]]["risk"] = "Medium"
                elif choke_point_status[cp["name"]]["risk"] == "Low":
                    choke_point_status[cp["name"]]["risk"] = "Medium"

    # Step 2: Network Propagation (BFS)
    # If a node is High, its neighbors become Medium due to ripple effects
    for node in high_risk_nodes:
        for neighbor in CHOKE_POINT_GRAPH.get(node, []):
            if choke_point_status[neighbor]["risk"] != "High":
                choke_point_status[neighbor]["risk"] = "Medium"
                alert = f"📍 Network Propagation: Severe traffic at {node} is cascading backwards, causing Medium risk at {neighbor}."
                if alert not in cascading_alerts:
                    cascading_alerts.append(alert)

    # Format return list
    choke_point_risks = []
    for cp_name, status in choke_point_status.items():
        choke_point_risks.append({
            "name": status["data"]["name"],
            "latitude": status["data"]["latitude"],
            "longitude": status["data"]["longitude"],
            "risk_level": status["risk"]
        })

    return {
        "traffic_congestion_risk": traffic_risk,
        "infrastructure_risk": infra_risk,
        "crowd_risk": crowd_risk,
        "recommendation": recommendation,
        "choke_points": choke_point_risks,
        "cascading_alerts": cascading_alerts
    }
