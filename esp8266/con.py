import network
import gc
import time

class connection:
    def __init__(self,ssid='',pwd=''):
        self.sta_if = network.WLAN(network.STA_IF)
        self.ssid = 'wifi_name'
        self.pwd = 'wifi_hard_password'
        self.do_connect()

    def do_connect(self):
        if not self.sta_if.isconnected():
            self.sta_if.active(True)
            self.sta_if.connect(self.ssid, self.pwd)
            print('Conectando a rede', self.ssid +"...")
            while True:
                if self.sta_if.isconnected():
                    break
                time.sleep(1)
                gc.collect()

        print(
            'Configuracao de rede (IP/netmask/gw/DNS):',
            self.sta_if.ifconfig())

    def test_connection(self):
        if not self.sta_if.isconnected():
            self.do_connect()
