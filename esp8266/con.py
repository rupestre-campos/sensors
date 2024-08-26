import network
import gc
import time
import machine

class Connection:
    def __init__(self, ssid='wifi_name', pwd='wifi_hard_password'):
        self.sta_if = network.WLAN(network.STA_IF)
        self.ssid = ssid
        self.pwd = pwd
        self.connect()

    def connect(self):
        if not self.sta_if.isconnected():
            self.sta_if.active(True)
            self.sta_if.connect(self.ssid, self.pwd)
            print(f'Connecting to network: {self.ssid}...')
            start_time = time.time()
            timeout = 30

            while not self.sta_if.isconnected():
                if time.time() - start_time > timeout:
                    print('Failed to connect to network.')
                    self.restart_device()
                    return
                time.sleep(1)
                gc.collect()

            print('Network configuration (IP/netmask/gw/DNS):', self.sta_if.ifconfig())

    def test_connection(self):
        if not self.sta_if.isconnected():
            self.connect()

    def restart_device(self):
        print('Restarting device...')
        machine.reset()