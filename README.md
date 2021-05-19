# ESP8266_MQTT_light
Micropython code for controlling an RGB and White light 
using an ESP8266 controller board of my design

This code is poorly written alpha code to control a 12 VDC RGB light 
and a 12 VDC white light using MQTT. It works but needs improvement. 

The switches control on/off with a short press and dimming/brightening 
when they are held down.  

OSH Park is making my controller board (click on image)
<a href="https://oshpark.com/shared_projects/GQtievsf">
<img src="https://644db4de3505c40a0444-327723bce298e3ff5813fb42baeefbaa.ssl.cf1.rackcdn.com/5d04d3145cb8d8d68e20611b7c08b1a4.png" alt="OSH Park"></img></a>.  
The design is an Eagle cad design but there is a caveat!!
The switches come with 4 pins two pair of bussed through hole.
However even though the foot print is identical there are 
two varieties.  With the opposite connections. The board traces
will show the bussed pairs.

Being very new to ESP8266 and micropython it seems as though the code 
is near the memory limit of the ESP8266.
So I have eliminated all comments and extras.  
I welcome suggestions and corrections.  

The entire project is for a Home-Assistant installation.
I have 4 sets of lights working. I was experiencing disconnect fails 
when either the HASS server or the Mosquitto server was rebooted 
so I wrote the code so it reboots the ESP8266
GPIO-16 controlls the blue LED on the ESP8266 board I am using so the
code turns it on during boot then off once booted.  So it acts as an
indicator of when the board is in boot mode.

I have included a sample configuration for Home Assistant control of the module.
The script will return the version which will fill the sensor value.

The Code:
boot.py starts by loading the webrepl which probably won't be needed in production.
The parameters file is loaded and contains data for the WiFi connection, 
the MQTT instance, the pin data for the ESP8266 and such.

The status file is essentially the JSON state last saved so the light on boot 
is set to the last known state. 

Boot then calls main.  Main starts by opening the MQTT connection.
If there is an error in connecting, the program flashes the LED on the ESP8266 three times 
in a one second on one second off and exits.

On a good MQTT connection , the routine sets a callback address for received messages 
and returns the connected client.

The code enters the main loop. It does an MQTT message check first then 
the state of the switches is checked.  A short press/release will toggle the on/off state.
After the button is held down for a period longer than the counter is set for,
the light goes into a brighten/dim cycle.

After any change in state, the state file is updated and an MQTT status message is sent.
The last thing in the loop is a check to see when we sent the last status and
to send an update when timed out.






