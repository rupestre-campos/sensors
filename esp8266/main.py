import esp
esp.osdebug(None)
import gc
import read_bme
import con
import urequests as requests
import time

# Initialize connection and sensor
connection = con.connection('wifi_name', 'wifi_password')
measure = read_bme.ReadBME()
api_url = "http://pi-host-ip:5000/sensor-data/"

def main():
    while True:
        try:
            # Read sensor data
            data = measure.read_sensor()
            if not isinstance(data, dict):
                raise Exception("Data is not dict")
            # Send POST request
            response = requests.post(api_url, json=data)
            print("POST request sent. Status code:", response.status_code)
            response.close()

        except Exception as e:
            print("Error:", e)

        # Garbage collection
        gc.collect()

        # Wait for 5 seconds
        time.sleep(5)
