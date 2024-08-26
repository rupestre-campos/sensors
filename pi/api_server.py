import uuid6
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Float, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

# Database URL
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database model
class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(String, primary_key=True, default=lambda: str(uuid6.uuid7()))
    temperature = Column(Float, nullable=False)
    pressure = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    datetime = Column(TIMESTAMP(timezone=True), server_default=func.now())

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic model
class SensorDataCreate(BaseModel):
    temperature: float
    pressure: float
    humidity: float

app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/sensor-data/")
async def create_sensor_data(data: SensorDataCreate, db: SessionLocal = next(get_db())):
    sensor_data = SensorData(
        temperature=data.temperature,
        pressure=data.pressure,
        humidity=data.humidity
    )
    db.add(sensor_data)
    db.commit()
    db.refresh(sensor_data)
    return sensor_data
