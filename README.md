# Interstate-75-W-with-64x64-HUB75

This is the product of a learning exercise I've been doing teaching myself about how to code a Pico W to drive a 64x64 HUB75 LED array.

The goal at the moment is to make a clock with date and time showing in white text, outlined in black with a graduated colour background that changes throughout the day. This is based loosely on the Pimoroni example code "clock.py" although the implementation of that background is extremely different due to the differences between Micropython and Circuitpython.

I'm using a Pimoroni Interstate 75 W which has a Pico W on-board and it's connected to a 64x64 LED array which uses HUB75 connections. 

I started out using Pimoroni's Micropython which would have been entirely sufficient except for the fact that their available fonts are utterly hideous and not flexible enough to add more. So I switched to Adafruit Circuitpython which is considerably more capable, especially in the area of font support. 

This code is unfinished. It's a learning exercise and it is not the tidiest, most succint or the most elegant code I've ever created. In particular the display.refresh() function in displayio module doesn't seem to work right at all so I have to do an inelegant dance with turning off auto_refresh and then turning it on again whenever I update the display. Would love to get to the bottom of that little nasty.

Comments and suggestions are very welcome. I'm here to learn.

Also there's a bunch of unused space on my screen at the moment. Something needs to go in there!

You will need to add to your circuitpython "lib" folder the following files from the Circuitpython bundle:

- adafruit_ntp.mpy
- adafruit_requests.mpy
- adafruit_rgbled.mpy
- simpleio.mpy
- adafruit_display_text (folder)
