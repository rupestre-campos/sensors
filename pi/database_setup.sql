CREATE DATABASE sensors;

CREATE TABLE sensor_data (
    id UUID PRIMARY KEY,
    temperature FLOAT NOT NULL,
    pressure FLOAT NOT NULL,
    humidity FLOAT NOT NULL,
    datetime TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
