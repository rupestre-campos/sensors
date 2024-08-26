import BME280
from machine import Pin, I2C
from timestamp import get_time
import gc

i2c = I2C(scl=Pin(5), sda=Pin(4), freq=10000)

class Airt:
    def __init__(self):
        self.bme = BME280.BME280(i2c=i2c)
        self.min = 10000.0
        self.min_time = ''
        self.max = -10000.0
        self.max_time = ''
        self.temp = 0.0
        self.hum = 0.0
        self.pres = 0.0
        self.msg = ''

    def reset_min_max(self):
        self.min = 10000.0
        self.min_time = ''
        self.max = -10000.0
        self.max_time = ''

    def timestamp(self):
        return get_time()

    def strftime(self):
        (Y, m, d, H, M, S, weekday, yearday) = self.timestamp()
        return '{}-{}-{} T {}:{}:{}'.format(Y, m, d, H, M, S)

    def read_sensor(self):
        try:
            time_read = self.strftime()
            self.temp = float(self.bme.temperature)
            self.hum = float(self.bme.humidity)
            self.pres = float(self.bme.pressure)
            if self.temp == self.hum:
                self.bme = BME280.BME280(i2c=i2c)
            print("Temperature: {}, Humidity: {}, Pressure: {}".format(self.temp, self.hum, self.pres))

            if self.temp < self.min:
                self.min = self.temp
                self.min_time = time_read
            if self.temp > self.max:
                self.max = self.temp
                self.max_time = time_read

            self.msg = ';'.join([
                'DateTime: {}'.format(time_read),
                'T   (oC): {:.3f}'.format(self.temp),
                'Tmin(oC): {:.3f}'.format(self.min),
                'Tmin (H): {}'.format(self.min_time),
                'Tmax(oC): {:.3f}'.format(self.max),
                'Tmax (H): {}'.format(self.max_time),
                'H    (%): {:.3f}'.format(self.hum),
                'P  (hPa): {:.3f}'.format(self.pres)
            ])
            gc.collect()
            return self.msg
        except Exception as e:
            gc.collect()
            self.bme = BME280.BME280(i2c=i2c)
            print("Failed to read sensor: {}".format(e))
            return 'Failed to read sensor. {}'.format(e)
