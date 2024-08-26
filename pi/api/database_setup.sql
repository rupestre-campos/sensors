-- create database on your postgres
CREATE DATABASE sensors;

-- Then switch to new created database to run following commands

CREATE TABLE sensor_data (
    id UUID PRIMARY KEY,
    temperature FLOAT NOT NULL,
    pressure FLOAT NOT NULL,
    humidity FLOAT NOT NULL,
    datetime TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX sensor_data_datetime ON sensor_data (datetime);