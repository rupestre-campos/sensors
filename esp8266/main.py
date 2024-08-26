import esp
esp.osdebug(None)
import gc
gc.collect()
import airtemp
import uasyncio
import machine
import con
import time
connection = con.connection()

led = machine.Pin(2, machine.Pin.OUT)
for i in range(3):
    led.value(0)
    time.sleep(0.3)
    led.value(1)
    time.sleep(0.3)

try:
    import usocket as socket
except:
    import socket

message = ''
measure = airtemp.Airt()

async def loop_reading():
    global message, measure, connection
    while True:
        connection.test_connection()
        message = measure.read_sensor()
        await uasyncio.sleep_ms(5000)
        gc.collect()

def web_page():
    global message
    m = message.split(';')
    m = '\n'.join(['<div>{}</div>'.format(x) for x in m])
    html = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="refresh" content="10;URL='http://192.168.8.136'" />
    <style>body{padding: 20px; margin: auto; width: 50%; text-align: center;}
    .progress{background-color: #F5F5F5;}
    p{position: absolute; font-size: 1.5rem; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 5;}</style></head>
    <body><h1 style="color:blue;">Weather station</h1> <h2 style="color:green;">BME280 Sensor</h2>
    <div class="temp">
    <p><div>"""+\
    m+\
    """</div></p>
    <form action="/reset">
        <input type="submit" value="Reset Min/Max Temperature" style="padding: 10px 20px; margin-top: 20px;"/>
    </form>
    </div></body></html>"""

    return html

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
    return s

async def serve_temp():
    print('starting socket server')
    global led
    led.value(0)
    await uasyncio.sleep_ms(100)
    led.value(1)
    s = start_server()
    while True:
        try:
            conn, addr = s.accept()
            print('Got a connection from %s' % str(addr))
            request = conn.recv(1024).decode('utf-8')

            if '/reset' in request:
                measure.reset_min_max()

            response = web_page()
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
            conn.close()
            gc.collect()

        except Exception as e:
            print('error main loop'.format(e))
            s.close()
            gc.collect()

        await uasyncio.sleep_ms(100)

def main():
    loop = uasyncio.get_event_loop()
    loop.create_task(loop_reading())
    loop.create_task(serve_temp())
    loop.run_forever()
    gc.collect()
