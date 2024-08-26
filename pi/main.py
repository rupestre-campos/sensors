from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Float, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from uuid_extensions import uuid7str
import os

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost/sensors")

# SQLAlchemy setup with async engine
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
Base = declarative_base()

# Database model
class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid7str())
    temperature = Column(Float, nullable=False)
    pressure = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    datetime = Column(TIMESTAMP(timezone=True), server_default=func.now())

# Create tables
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Pydantic model
class SensorDataCreate(BaseModel):
    temperature: float
    pressure: float
    humidity: float

app = FastAPI(on_startup=[init_models])

# Dependency to get DB session
async def get_db():
    async with SessionLocal() as db:
        yield db

@app.post("/sensor-data/")
async def create_sensor_data(data: SensorDataCreate, db: AsyncSession = Depends(get_db)):
    sensor_data = SensorData(
        temperature=data.temperature,
        pressure=data.pressure,
        humidity=data.humidity
    )
    db.add(sensor_data)
    await db.commit()
    await db.refresh(sensor_data)
    return sensor_data