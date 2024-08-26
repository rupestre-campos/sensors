import ntptime
import time

def get_time():
    ntptime.settime()
    return time.localtime()
