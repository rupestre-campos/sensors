import BME280
from machine import Pin, I2C
import gc

i2c = I2C(scl=Pin(5), sda=Pin(4), freq=10000)

class ReadBME:
    def __init__(self):
        self.bme = BME280.BME280(i2c=i2c)

    def read_sensor(self):
        try:
            return self.bme.values
        except Exception as e:
            gc.collect()
            print("Failed to read sensor: {}".format(e))
            return 'Failed to read sensor. {}'.format(e)
