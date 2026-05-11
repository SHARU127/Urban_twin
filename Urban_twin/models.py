from sqlalchemy import Column, Integer, String, DateTime, Float
from datetime import datetime
from database import Base

class Incident(Base):
    __tablename__ = "incidents"
    id = Column(Integer,primary_key=True,index=True)
    type = Column(String)
    location = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    severity = Column(String)
    reported_by = Column(String)
    image_url = Column(String, nullable=True) 
    reported_at = Column(DateTime,default = datetime.now)

class WeatherRecord(Base):
    __tablename__ = "weather_records"
    id = Column(Integer,primary_key=True,index=True)
    city = Column(String)
    temperature = Column(Float)
    humidity = Column(Integer)
    condition = Column(String)
    recorded_at = Column(DateTime,default=datetime.now) 