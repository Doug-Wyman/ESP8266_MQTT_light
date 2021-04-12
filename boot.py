### boot for light ###
import gc
import machine
from machine import Pin, PWM
import network
import esp
import ujson
import webrepl

webrepl.start()
esp.osdebug(None)

gc.collect()

paramsfile = open('params', 'r')
json_params = paramsfile.read()
set_params = ujson.loads(json_params)
### boot for light ###
HOSTNAME = set_params['hostname']
NETADDRESS = set_params['address']
SSID = set_params['ssid']
PASSWORD = set_params['password']
BROKER_ADDRESS = set_params['broker']
TMP_TOPIC = set_params['topic']
ROOT_TOPIC = TMP_TOPIC.encode()
#CLIENT_ID = set_params['clientid']
CLIENT_ID = hex(int.from_bytes(machine.unique_id(), 'big'))
SWITCH_PIN = machine.Pin(int(set_params['switch']), machine.Pin.OUT)
FREQUENCY = set_params['freq']
# PWM PINS = PWM(Pin(12, 13,14,15), FREQUENCY)
BUSY = False
WHITE_PIN = PWM(Pin(set_params['white']), FREQUENCY)
RED_PIN = PWM(Pin(set_params['red']), FREQUENCY)
GREEN_PIN = PWM(Pin(set_params['green']), FREQUENCY)
BLUE_PIN = PWM(Pin(set_params['blue']), FREQUENCY)
RED_PIN.duty(0)
GREEN_PIN.duty(0)
BLUE_PIN.duty(0)
WHITE_PIN.duty(0)
CTRL_WHITE = machine.Pin(set_params['ctrl_white'], machine.Pin.IN)
CTRL_MOOD = machine.Pin(set_params['ctrl_mood'], machine.Pin.IN)

NTP_DELTA = 3155698800
ntphost = "pool.ntp.org"

paramsfile.close()
print("read" + str(set_params))
### boot for light ###

try:
  statusfile = open('status')
  myread = statusfile.read()
  status = ujson.loads(myread)

except OSError as exc:
  print('-----------')
  print(str(exc))
  print("can't load status")
  status = {
      'rgb': {
          "brightness": 512,
          "brightness_scale": 1024,
          "color": {
              "r": 1024,
              "g": 0,
              "b": 200,
              },
          "state": "ON",
          "transition": 2,
          },
      'white':{
          "brightness": 512,
          "brightness_scale": 1024,
          "state": "ON",
          "transition": 2,
          }
      }
SWITCH_PIN.value(0)
### boot for light ###
if status['rgb']['state'] == 'ON':
    BRIGHTMULTIPLIER = float(status['rgb']['brightness'] / 1024)
    red = (int(float(status['rgb']['color']['r']) * BRIGHTMULTIPLIER))
    green = (int(float(status['rgb']['color']['g']) * BRIGHTMULTIPLIER))
    blue = (int(float(status['rgb']['color']['b']) * BRIGHTMULTIPLIER))
    RED_PIN.duty(red)
    GREEN_PIN.duty(green)
    BLUE_PIN.duty(blue)
else:
    RED_PIN.duty(0)
    GREEN_PIN.duty(0)
    BLUE_PIN.duty(0)
if status['white']['state'] == 'ON':
    WHITE_PIN.duty(status['white']['brightness'])
else:
    WHITE_PIN.duty(0)
last_message = 0
message_interval = 5
time_interval = 600
counter = 0
### boot for light ###
STATION = network.WLAN(network.STA_IF)
STATION.active(True)
STATION.config(dhcp_hostname=HOSTNAME)
STATION.ifconfig(NETADDRESS)
STATION.connect(SSID, PASSWORD)

while STATION.isconnected() == False:
  pass

print('Connection successful')
print(STATION.ifconfig())
### boot for light ###

