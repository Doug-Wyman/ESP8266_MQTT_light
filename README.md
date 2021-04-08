# ESP8266_MQTT_light
Micropython code for controlling an RGB and White light using an ESP8266 controller board of my design

This code is poorly written alpha code to control a 12 VDC RGB light and a 12 VDC white light over MQTT 
It works but needs improvement. The switches control on/off with a short press and dimming/brightening when
they are held sown.  The RGB dimming needs some math rewrite.  

OSH Park is making my controller board (click on it) <a href="https://oshpark.com/shared_projects/SDt1Jgl8"><img src="https://644db4de3505c40a0444-327723bce298e3ff5813fb42baeefbaa.ssl.cf1.rackcdn.com/5d04d3145cb8d8d68e20611b7c08b1a4.png" alt="OSH Park"></img></a>.  

Being very new to ESP8266 and micropython it seems as though the code is near the memory limit of the ESP8266.
So I eliminated all comments and extras.  If I get a burr in my britches, I'll upload commented code so you can try and figure out what I intended.

I welcome suggestions and corrections.  The entire project is for a Home-Assistant installation and I have 4 sets of lights working.
I was experiencing disconnect fails when the HASS server or the Mosquitto server was rebooted so I wrote the code so it reboots the ESP8266
on fail which it does from time to time in normal use.  

