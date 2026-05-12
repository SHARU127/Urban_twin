import database
from fastapi import FastAPI, Depends, File, UploadFile, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import Base, engine, get_db
import models
import schemas
from datetime import datetime
import requests
import ml
import os
import shutil
WEATHER_API_KEY = "bd77055daf16806610093476912bd24d"

app = FastAPI()

# Create uploads folder if it doesn't exist
os.makedirs("uploads", exist_ok=True)
# Tell FastAPI to serve the uploads folder
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

Base.metadata.create_all(bind=engine)

@app.get("/")
def home(db: Session = Depends(get_db)):
    return db.query(models.Incident).all()

@app.post("/incidents")
def report_incident(
    type: str = Form(...),
    location: str = Form(...),
    severity: str = Form(...),
    reported_by: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    lat = 12.9716
    lon = 77.5946
    # Ask OpenStreetMap (Nominatim) for the exact GPS of the typed location
    geo_url = f"https://nominatim.openstreetmap.org/search?q={location},+Bengaluru&format=json"
    headers = {"User-Agent": "UrbanTwinApp/1.0"}  # OpenStreetMap requires this header
    
    try:
        geo_response = requests.get(geo_url, headers = headers)
        geo_data = geo_response.json()
        
        if len(geo_data) > 0:
            lat = float(geo_data[0]["lat"])
            lon = float(geo_data[0]["lon"])
    
    except:
        pass

    # Save the image if one was uploaded
    image_url_path = None
    if image is not None and image.filename != "":
        file_location = f"uploads/{image.filename}"
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(image.file, file_object)
        image_url_path = f"/uploads/{image.filename}"

    new_incident = models.Incident(
        type = type,
        location = location,
        latitude = lat,
        longitude = lon,
        severity = severity,
        reported_by = reported_by,
        image_url = image_url_path,
        reported_at = datetime.now()
    )
        
    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)
    return {"message":"incident reported","incident":new_incident}

@app.get("/incidents/{id}")
def get_incident(id:int,db:Session = Depends(get_db)):
    incident = db.query(models.Incident).filter(models.Incident.id == id).first()
    if not incident:
        return {"error":"incident not found"}
    return incident

@app.get("/weather")
def get_weather(db:Session = Depends(get_db)):
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Bengaluru&appid=bd77055daf16806610093476912bd24d&units=metric"
    response = requests.get(url)
    data = response.json()
    record = models.WeatherRecord (
        city= data["name"],
        temperature=data["main"]["temp"],
        humidity=data["main"]["humidity"],
        condition = data["weather"][0]["description"]
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

@app.get("/weather/history")
def get_weather_history(db:Session = Depends(get_db)):
    return db.query(models.WeatherRecord).all()


@app.get("/predict",response_model=schemas.PredictionResponse)
def get_predictions(db: Session = Depends(get_db)):
    
    #fetch latest weather record from the DB
    latest_weather = db.query(models.WeatherRecord).order_by(models.WeatherRecord.recorded_at.desc()).first()
    #fetch all the incidents
    all_incidents = db.query(models.Incident).all()

#fallback if no weather data is exists yet  
    if not latest_weather:
        return {
            "traffic_congestion_risk": "unknown",
            "infrastructure_risk":"unknown",
            "crowd_risk":"unknown",
            "recommendation":"NO weather data available. call /weather first."
        }

    prediction = ml.predict_risks(
        weather_condition = latest_weather.condition,
        temperature = latest_weather.temperature,
        recent_incidents = all_incidents,
    )

    return prediction

@app.get("/dashboard")
def serve_dashboard():
    return FileResponse("templates/index.html")