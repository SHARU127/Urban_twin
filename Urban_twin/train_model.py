import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# 1. Generate Synthetic Data
# We will generate 5000 rows of historical data
print("Generating synthetic historical data for Bengaluru...")
np.random.seed(42)
num_samples = 5000

# Features:
# - Temperature (Float: 15 to 40)
# - Is_Raining (Int: 0 or 1)
# - Incident_Severity_Level (Int: 0=Low, 1=Medium, 2=High)
# - Is_Festival_Or_Event (Int: 0 or 1)

temperatures = np.random.uniform(15, 42, num_samples)
is_raining = np.random.choice([0, 1], num_samples, p=[0.8, 0.2])
incident_severity = np.random.choice([0, 1, 2], num_samples, p=[0.6, 0.3, 0.1])
is_festival = np.random.choice([0, 1], num_samples, p=[0.9, 0.1])

# Targets:
# - Traffic_Risk (Int: 0=Low, 1=Medium, 2=High)
# - Infra_Risk (Int: 0=Low, 1=Medium, 2=High)
# - Crowd_Risk (Int: 0=Low, 1=Medium, 2=High)

traffic_risk = []
infra_risk = []
crowd_risk = []

for i in range(num_samples):
    t_risk = 0
    i_risk = 0
    c_risk = 0
    
    # Logic to simulate real-world data patterns
    if is_raining[i] == 1:
        t_risk = np.random.choice([1, 2], p=[0.3, 0.7]) # Rain likely causes High traffic
        i_risk = np.random.choice([0, 1], p=[0.6, 0.4]) # Rain might cause medium infra risk
        
    if incident_severity[i] == 2: # High severity incident
        t_risk = 2
        i_risk = np.random.choice([1, 2], p=[0.5, 0.5])
        
    if is_festival[i] == 1:
        c_risk = 2
        t_risk = max(t_risk, 1) # At least medium traffic
        
    if temperatures[i] > 35:
        i_risk = max(i_risk, 1) # Heat causes infra stress

    # Add some noise/randomness so it's not a perfect deterministic rule
    if np.random.rand() < 0.05:
        t_risk = np.random.choice([0, 1, 2])
    if np.random.rand() < 0.05:
        i_risk = np.random.choice([0, 1, 2])
    if np.random.rand() < 0.05:
        c_risk = np.random.choice([0, 1, 2])
        
    traffic_risk.append(t_risk)
    infra_risk.append(i_risk)
    crowd_risk.append(c_risk)

df = pd.DataFrame({
    'Temperature': temperatures,
    'Is_Raining': is_raining,
    'Incident_Severity': incident_severity,
    'Is_Festival': is_festival,
    'Traffic_Risk': traffic_risk,
    'Infra_Risk': infra_risk,
    'Crowd_Risk': crowd_risk
})

print(f"Generated {num_samples} rows of data.")

# 2. Train the Model
# We'll use a MultiOutput structure via three separate Random Forest classifiers
# or just train one for each target to keep it simple and explicit.

X = df[['Temperature', 'Is_Raining', 'Incident_Severity', 'Is_Festival']]

print("Training Traffic Risk Model...")
clf_traffic = RandomForestClassifier(n_estimators=50, random_state=42)
clf_traffic.fit(X, df['Traffic_Risk'])

print("Training Infrastructure Risk Model...")
clf_infra = RandomForestClassifier(n_estimators=50, random_state=42)
clf_infra.fit(X, df['Infra_Risk'])

print("Training Crowd Risk Model...")
clf_crowd = RandomForestClassifier(n_estimators=50, random_state=42)
clf_crowd.fit(X, df['Crowd_Risk'])

# 3. Save the Models
print("Saving models to model.pkl...")
models = {
    'traffic': clf_traffic,
    'infra': clf_infra,
    'crowd': clf_crowd
}
joblib.dump(models, 'model.pkl')
print("Model training and saving complete! Saved as model.pkl")
