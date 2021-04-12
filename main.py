#import machine
from machine import RTC
import time
from time import sleep
import socket
import os
import ujson
from umqttsimple import MQTTClient
################# main for light ########################
def savestate():
  global status, BUSY
  statusfile = open('status', 'w')
  myjson = ujson.dumps(status)
  statusfile.write(str(myjson))
  statusfile.close()
  print("saved" + str(status))
  
def received(topic, inmsg):
  global status, BUSY, ROOT_TOPIC
  if not BUSY and topic != ROOT_TOPIC + b'white/state' and topic != ROOT_TOPIC + b'rgb/state':
    BUSY = True
    #print(topic, inmsg)
    msg = inmsg.decode('utf-8')
    print(msg)
    ##############WHITE######################
    if topic == ROOT_TOPIC + b'white/switch':
      print('ESP received switch')
      
      newset = ujson.loads(msg)
      print(newset)
      status['white']['state'] = newset.get('state', status['white']['state'])
      status['white']['brightness'] = newset.get('brightness', status['white']['brightness'])
      if status['white']['state'] == 'ON':
        WHITE_PIN.duty(status['white']['brightness'])
      else:
        WHITE_PIN.duty(0)
      client.publish(ROOT_TOPIC + b'white/state', str(ujson.dumps(status['white'])))
      savestate()
    ########################rgb#######################
    if topic == ROOT_TOPIC + b'version?':
      print('ESP version request')
      client.publish(ROOT_TOPIC + b'version', 'Version 2021.001')
    if topic == ROOT_TOPIC + b'rgb/switch':
      print('RGB received switch')
      newset = ujson.loads(msg)
      print(newset)
      status['rgb']['state'] = newset.get('state', status['rgb']['state'])
      status['rgb']['brightness'] = newset.get('brightness', status['rgb']['brightness'])
      status['rgb']['color'] = newset.get('color', status['rgb']['color'])
      if status['rgb']['state'] == 'ON':
        BRIGHTMULTIPLIER = float(status['rgb']['brightness'] / 1024)
        red = int(float(status['rgb']['color']['r'] /255) *1024)
        red = int(red * BRIGHTMULTIPLIER )
        green = int(float(status['rgb']['color']['g'] /255) * 1024)
        green = int(green * BRIGHTMULTIPLIER)
        blue = int(float(status['rgb']['color']['b'] /255) * 1025)
        blue = int(blue *  BRIGHTMULTIPLIER)
        print("red is:" + str(red))
        print("green is:" + str(green))
        print("blue is:" + str(blue))
        RED_PIN.duty(int(red))
        GREEN_PIN.duty(int(green))
        BLUE_PIN.duty(int(blue))
      else:
        RED_PIN.duty(0)
        GREEN_PIN.duty(0)
        BLUE_PIN.duty(0)
      client.publish(ROOT_TOPIC + b'rgb/state', str(ujson.dumps(status['rgb'])))
      savestate()
    BUSY = False
  else:
    print('.', end='')

def connect_and_subscribe():
  global CLIENT_ID, BROKER_ADDRESS, ROOT_TOPIC, client, SWITCH_PIN
  try:
    SWITCH_PIN.value(0)
    client = MQTTClient(CLIENT_ID, BROKER_ADDRESS)
    client.set_callback(received)
    client.connect()
    time.sleep(2)
    print("connecting")
    client.subscribe(ROOT_TOPIC + b'#')
    print('Connected to %s MQTT broker, subscribed to %s topic' % (BROKER_ADDRESS, ROOT_TOPIC))
    SWITCH_PIN.value(1)
    return client
  except:
    SWITCH_PIN.value(1)
    time.sleep(1)
    SWITCH_PIN.value(0)
    time.sleep(1)
    SWITCH_PIN.value(1)
    time.sleep(1)
    SWITCH_PIN.value(0)
    time.sleep(1)
    SWITCH_PIN.value(1)
    time.sleep(1)
    SWITCH_PIN.value(0)
    return None

################# main for light ########################
print("Loading.............")
client = connect_and_subscribe()
sleep(2)
last_message = 0
message_interval = 30
time_interval = 3600
#wdt.feed()
lastin = 1
counting = False
sw1count = 0
savtime = ''
#wdt.feed()
#print(dir(client.ping))
short_time = 5
down_time = 50

ctrlw_down = 0
ctrlw_raise = False
ctrlw_short = 0
ctrlw_level = 0

ctrlm_down = 0
ctrlm_raise = False
ctrlm_short = 0
ctrlm_level = 0
while 1:
  try:
    try:
        client.check_msg()
    except:
        print("error checking")
        client = connect_and_subscribe()
#######################start white contro
    if CTRL_WHITE.value() == 0:
      #print(".", end='')
      if ctrlw_short > 0:
        print("XX", end='')
        ctrlw_short += 1
        if ctrlw_short > short_time:
          ctrlw_short = 0
          print(str(status['white']['state']) == 'OFF')
          #######Toggle state##########
          if str(status['white']['state']) == 'OFF':
              WHITE_PIN.duty(status['white']['brightness'])
              status['white']['state'] = 'ON'
          else:
              WHITE_PIN.duty(0)
              status['white']['state'] = 'OFF'            
          client.publish(ROOT_TOPIC + b'white/state', str(ujson.dumps(status['white'])))
          savestate()
    if CTRL_WHITE.value() == 1:
      print("after short2" + str(ctrlw_short))
      print("||||||", end='')
      ctrlw_down = 0
      ctrlw_level = int(status['white']['brightness'])
      if ctrlw_short > 1:
        ctrlw_raise = True
      else:
        ctrlw_dimming = True
      print(ctrlw_level)
      while CTRL_WHITE.value() == 1:
        ctrlw_down += 1
        if ctrlw_down > down_time:
          WHITE_PIN.duty(ctrlw_level)
          if ctrlw_level < 1:
            ctrlw_raise = True
          if ctrlw_raise == True:
            ctrlw_level = int(ctrlw_level) + 1
            if int(ctrlw_level) > 1024:
              print("Stop Bright")
              #ctrlw_dimming = True
              ctrlw_raise = False
              ctrlw_short = 0
            else:
              ctrlw_raise = True
          else:
            ctrlw_level -= 1
            if ctrlw_level < 1:
              ctrlw_raise = True
        sleep(.01)
      if ctrlw_down > down_time:
        ctrlw_short = 0
        ctrlw_down = 0
      else:
        ctrlw_short = 1
      ctrlw_raise = False
      ctrlw_dimming = False
      status['white']['brightness'] = ctrlw_level
      if ctrlw_down == 0: 
        client.publish(ROOT_TOPIC + b'white/state', str(ujson.dumps(status['white'])))
        savestate()
      ctrlw_raise = False
      ctrlw_dimming = False
      print("after short1" + str(ctrlw_short))
#######################logic#################################
    if CTRL_MOOD.value() == 0:
      #print(".", end='')
      if ctrlm_short > 0:
        print("XX", end='')
        ctrlm_short += 1
        if ctrlm_short > short_time:
          ctrlm_short = 0
          print(str(status['rgb']['state']) == 'OFF')
          #######Toggle state##########
          if str(status['rgb']['state']) == 'OFF':
            #WHITE_PIN.duty(status['rgb']['brightness'])
            status['rgb']['state'] = 'ON'
            BRIGHTMULTIPLIER = float(status['rgb']['brightness'] / 1024)
            red = int(float(status['rgb']['color']['r'] /255) *1024)
            red = int(red * BRIGHTMULTIPLIER )
            green = int(float(status['rgb']['color']['g'] /255) * 1024)
            green = int(green * BRIGHTMULTIPLIER)
            blue = int(float(status['rgb']['color']['b'] /255) * 1025)
            blue = int(blue *  BRIGHTMULTIPLIER)
            print("red is:" + str(red))
            print("green is:" + str(green))
            print("blue is:" + str(blue))
            RED_PIN.duty(int(red))
            GREEN_PIN.duty(int(green))
            BLUE_PIN.duty(int(blue))
          else:
            RED_PIN.duty(0)
            GREEN_PIN.duty(0)
            BLUE_PIN.duty(0)
            status['rgb']['state'] = 'OFF'
          client.publish(ROOT_TOPIC + b'rgb/state', str(ujson.dumps(status['rgb'])))
          savestate()
    if CTRL_MOOD.value() == 1:
      print("||||||", end='')
      ctrlm_down = 0
      ctrlm_level = int(status['rgb']['brightness'])
      if ctrlm_short < 1:
        ctrlm_raise = True
      else:
        ctrlm_raise = False
      while CTRL_MOOD.value() == 1:
        ctrlm_down += 1
        if ctrlm_down > down_time:
          status['rgb']['brightness'] = ctrlm_level
          BRIGHTMULTIPLIER = float(status['rgb']['brightness'] / 1024)
          red = int(float(status['rgb']['color']['r'] /255) *1024)
          red = int(red * BRIGHTMULTIPLIER )
          green = int(float(status['rgb']['color']['g'] /255) * 1024)
          green = int(green * BRIGHTMULTIPLIER)
          blue = int(float(status['rgb']['color']['b'] /255) * 1025)
          blue = int(blue *  BRIGHTMULTIPLIER)
          print("red is:" + str(red))
          print("green is:" + str(green))
          print("blue is:" + str(blue))
          RED_PIN.duty(int(red))
          GREEN_PIN.duty(int(green))
          BLUE_PIN.duty(int(blue))
          if ctrlm_level < 1:
            ctrlm_raise = True
          if ctrlm_raise == True:
            ctrlm_level += 1
            if int(ctrlm_level) > 1024:
              ctrlm_raise = False
            else:
              ctrlm_raise = True
          else:
            ctrlm_level -= 1
            if ctrlm_level < 1:
              ctrlm_raise = True
          print(str(ctrlm_level) + "--" + str(int(red)))
        sleep(.01)
      if ctrlm_down > down_time:
        ctrlm_short = 0
        ctrlm_down = 0
      else:
        ctrlm_short = 1
      ctrlm_raise = False
      status['rgb']['brightness'] = ctrlm_level
      if ctrlm_down == 0: 
        client.publish(ROOT_TOPIC + b'rgb/state', str(ujson.dumps(status['rgb'])))
        savestate()
      ctrlm_raise = False
      ctrlm_dimming = False
############################################mood######################################
    if (time.time() - last_message) > float(message_interval):
        try:
            client.publish(ROOT_TOPIC + b'white/state', str(ujson.dumps(status['white'])))
            client.publish(ROOT_TOPIC + b'rgb/state', str(ujson.dumps(status['rgb'])))
            last_message = time.time()
        except:
            print("error sending")
            client = connect_and_subscribe()    
    elif time.time() < last_message:
        last_message = time.time()
    sleep(.1)
  except KeyboardInterrupt:
    print('Interrupted')
    os._exit(0)
  except:
    machine.reset()
################# main for light ########################
