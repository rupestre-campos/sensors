from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Float, TIMESTAMP, func, desc, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.future import select
from uuid_extensions import uuid7str
from datetime import datetime, timezone
import uuid
import os
from dotenv import load_dotenv
load_dotenv()

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://test-user:test-password@localhost/sensors")

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

class SensorDataResponse(BaseModel):
    id: uuid.UUID
    temperature: float
    pressure: float
    humidity: float
    datetime: datetime

@app.get("/sensor-data/", response_model=List[SensorDataResponse])
async def list_sensor_data(
    start_date: Optional[datetime] = Query(None, description="Start date for filtering records"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering records"),
    limit: Optional[int] = Query(None, le=100, description="Limit the number of records returned (default: None for all records)"),
    db: AsyncSession = Depends(get_db)
):
    # Default end_date to current datetime if not provided
    if end_date is None:
        end_date = datetime.now(timezone.utc)

    # Build the base query
    query = select(SensorData).order_by(desc(SensorData.datetime))

    # Apply start_date filter if provided
    if start_date:
        query = query.where(SensorData.datetime >= start_date)

    # Apply end_date filter
    query = query.where(SensorData.datetime <= end_date)

    # Apply limit if provided
    if limit is not None:
        query = query.limit(limit)

    result = await db.execute(query)
    records = result.scalars().all()

    if not records:
        raise HTTPException(status_code=404, detail="No sensor data found")

    return [SensorDataResponse(
        id=record.id,
        temperature=record.temperature,
        pressure=record.pressure,
        humidity=record.humidity,
        datetime=record.datetime
    ) for record in records]

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

@app.delete("/sensor-data/{sensor_id}")
async def delete_sensor_data(sensor_id: str, db: AsyncSession = Depends(get_db)):
    try:
        # Convert the string to a UUID object
        sensor_id_uuid = uuid.UUID(sensor_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    # Use text() to safely include raw SQL
    sql = text("DELETE FROM sensor_data WHERE id = :sensor_id RETURNING *")

    result = await db.execute(sql, {"sensor_id": sensor_id_uuid})
    deleted = result.fetchone()
    if deleted is None:
        raise HTTPException(status_code=404, detail="Sensor data not found")

    await db.commit()
    return {"message": "Sensor data deleted successfully", "id": sensor_id}