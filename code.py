# Holy shit that's a lot of imports
import adafruit_display_text.bitmap_label
import board
import displayio
import digitalio
import busio
import adafruit_rgbled
import framebufferio
import rgbmatrix
import terminalio
import os
import time
import rtc
import ssl
import wifi
import socketpool
import microcontroller
import adafruit_requests
import adafruit_ntp
import math

# constants for controlling the background colour throughout the day
MIDDAY_HUE = 1.1
MIDNIGHT_HUE = 0.4
HUE_OFFSET = -0.2

MIDDAY_SATURATION = 1.0
MIDNIGHT_SATURATION = 1.0

MIDDAY_VALUE = 0.8
MIDNIGHT_VALUE = 0.4

# Lookup list for month
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# If there was a display before (protomatter, LCD, or E-paper), release it so we can create ours
displayio.release_displays()

# Connect to Wifi
wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))
pool = socketpool.SocketPool(wifi.radio)
ntp = adafruit_ntp.NTP(pool, tz_offset=0)

# Set the RTC using NTP
rtc.RTC().datetime = ntp.datetime

# Get the current time from the RTC
year, month, day, hour, minute, second, wday, yday, isdst = time.localtime()
lastsecond = second
lasthour = hour
lastday = ""

# Define the buttons on the Interstate 75 W
button_a = digitalio.DigitalInOut(board.GP14)
button_a.direction = digitalio.Direction.INPUT
button_a.pull = digitalio.Pull.UP
button_b = digitalio.DigitalInOut(board.GP15)
button_b.direction = digitalio.Direction.INPUT
button_b.pull = digitalio.Pull.UP

def button_read(button):
    return not button.value

# This next call creates the RGB Matrix object itself. It has the given width
# and height. bit_depth can range from 1 to 6; higher numbers allow more color
# shades to be displayed, but increase memory usage and slow down your Python
# code. If you just want to show primary colors plus black and white, use 1.
# Otherwise, try 3, 4 and 5 to see which effect you like best.
matrix = rgbmatrix.RGBMatrix(
    width=64, height=64, bit_depth=4,
    rgb_pins=[board.GP0, board.GP1, board.GP2, board.GP3, board.GP4, board.GP5],
    addr_pins=[board.GP6, board.GP7, board.GP8, board.GP9, board.GP10],
    clock_pin=board.GP11, latch_pin=board.GP12, output_enable_pin=board.GP13)

# Associate the RGB matrix with a Display so that we can use displayio features
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=True, rotation=90)

def from_hsv(h, s, v):
    i = math.floor(h * 6.0)
    f = h * 6.0 - i
    v *= 255.0
    p = v * (1.0 - s)
    q = v * (1.0 - f * s)
    t = v * (1.0 - (1.0 - f) * s)

    i = int(i) % 6
    if i == 0:
        return ('0x{:02x}{:02x}{:02x}').format(int(v), int(t), int(p))
    if i == 1:
        return ('0x{:02x}{:02x}{:02x}').format(int(q), int(v), int(p))
    if i == 2:
        return ('0x{:02x}{:02x}{:02x}').format(int(p), int(v), int(t))
    if i == 3:
        return ('0x{:02x}{:02x}{:02x}').format(int(p), int(q), int(v))
    if i == 4:
        return ('0x{:02x}{:02x}{:02x}').format(int(t), int(p), int(v))
    if i == 5:
        return ('0x{:02x}{:02x}{:02x}').format(int(v), int(p), int(q))
    
def set_gradient_background_colours(palette, bands):
    global hour, minute, second
    
    # Calculate the starting colour for the gradient based on the time of day
    time_through_day = (((hour * 60) + minute) * 60) + second
    percent_through_day = time_through_day / 86400
    percent_to_midday = 1.0 - ((math.cos(percent_through_day * math.pi * 2) + 1) / 2)
    hue = ((MIDDAY_HUE - MIDNIGHT_HUE) * percent_to_midday) + MIDNIGHT_HUE
    sat = ((MIDDAY_SATURATION - MIDNIGHT_SATURATION) * percent_to_midday) + MIDNIGHT_SATURATION
    val = ((MIDDAY_VALUE - MIDNIGHT_VALUE) * percent_to_midday) + MIDNIGHT_VALUE
    start_hue, start_sat, start_val, end_hue, end_sat, end_val = hue, sat, val, hue + HUE_OFFSET, sat, val

    for x in range(bands):
        hue = ((end_hue - start_hue) * (x / bands)) + start_hue
        sat = ((end_sat - start_sat) * (x / bands)) + start_sat
        val = ((end_val - start_val) * (x / bands)) + start_val
        colour = from_hsv(hue, sat, val)
        palette[x] = int(colour, 16)

def set_time_text():
    global hour, minute, second, line1, line2, line3, line4, line5, timegroup
    
    timetext = "{:02}:{:02}:{:02}".format(hour, minute, second)
    line1.text = timetext
    line2.text = timetext
    line3.text = timetext
    line4.text = timetext
    line5.text = timetext
    
    timegroup.x = int((display.width / 2) - (line5.width / 2)) - 1

def set_date_text():
    global month, day, months, dateline1, dateline2, dateline3, dateline4, dateline5, dategroup
    
    datetext = f"{day} {months[month-1]}"
    dateline1.text = datetext
    dateline2.text = datetext
    dateline3.text = datetext
    dateline4.text = datetext
    dateline5.text = datetext

    dategroup.x = int((display.width / 2) - (dateline5.width / 2)) - 1

########
# MAIN #
########

# Create a screen group to hold everything on the screen
screen = displayio.Group()
display.show(screen)

# Create 5 labels for displaying the time
timetext = "{:02}:{:02}:{:02}".format(hour, minute, second)
line1 = adafruit_display_text.bitmap_label.Label(terminalio.FONT, color=0x000000, text=timetext)
line1.x, line1.y = 0, 1
line2 = adafruit_display_text.bitmap_label.Label(terminalio.FONT, color=0x000000, text=timetext)
line2.x, line2.y = 1, 0
line3 = adafruit_display_text.bitmap_label.Label(terminalio.FONT, color=0x000000, text=timetext)
line3.x, line3.y = 2, 1
line4 = adafruit_display_text.bitmap_label.Label(terminalio.FONT, color=0x000000, text=timetext)
line4.x, line4.y = 1, 2
line5 = adafruit_display_text.bitmap_label.Label(terminalio.FONT, color=0xFFFFFF, text=timetext)
line5.x, line5.y = 1, 1

# Create 5 labels for displaying the date
datetext = f"{day} {months[month-1]}"
dateline1 = adafruit_display_text.bitmap_label.Label(terminalio.FONT, color=0x000000, text=datetext)
dateline1.x, dateline1.y = 0, 1
dateline2 = adafruit_display_text.bitmap_label.Label(terminalio.FONT, color=0x000000, text=datetext)
dateline2.x, dateline2.y = 1, 0
dateline3 = adafruit_display_text.bitmap_label.Label(terminalio.FONT, color=0x000000, text=datetext)
dateline3.x, dateline3.y = 2, 1
dateline4 = adafruit_display_text.bitmap_label.Label(terminalio.FONT, color=0x000000, text=datetext)
dateline4.x, dateline4.y = 1, 2
dateline5 = adafruit_display_text.bitmap_label.Label(terminalio.FONT, color=0xFFFFFF, text=datetext)
dateline5.x, dateline5.y = 1, 1

# Create the palette we'll use for the background colour bands
bands = 8
palette = displayio.Palette(bands)
set_gradient_background_colours(palette, bands)

# Create all the bands for the background - each a single rectangle filled with one colour
for i in range(bands):
    bitmap=displayio.Bitmap(64 - (i*8), 64, bands)
    bitmap.fill(i)
    sprite = displayio.TileGrid(bitmap, pixel_shader=palette, x=(i*4), y=0)
    screen.append(sprite)

# Create a group for the time display
timegroup = displayio.Group()
timegroup.append(line1)
timegroup.append(line2)
timegroup.append(line3)
timegroup.append(line4)
timegroup.append(line5)
timegroup.x, timegroup.y = int((display.width / 2) - (line5.width / 2)) - 1, 8

# Create a group for the date display
dategroup = displayio.Group()
dategroup.append(dateline1)
dategroup.append(dateline2)
dategroup.append(dateline3)
dategroup.append(dateline4)
dategroup.append(dateline5)
dategroup.x, dategroup.y = int((display.width / 2) - (dateline5.width / 2)) - 1, 22

# Append the time and date display groups to the screen group
screen.append(timegroup)
screen.append(dategroup)

print("Starting at: ", line1.text)

# Main loop
while True:
    year, month, day, hour, minute, second, wday, yday, isdst = time.localtime()
    
    # Re-sync with NTP every hour
    if hour != lasthour:
        try:
            rtc.RTC().datetime = ntp.datetime
            print("Synced RTC with NTP.")
            lasthour = hour
        except:
            print("ntp.datetime took too long")
            
    # Update the time display every time the second changes
    if second != lastsecond:
        # Stop auto refresh while we're updating the display
        display.auto_refresh = False 

        # Update the time text
        set_time_text()
        
        # If we're updating the time and the day has changed then also update the date
        if day != lastday:
            set_date_text()
            lastday = day
        
        # Update the background colour palette every 30 seconds
        if second % 30 == 0:
            set_gradient_background_colours(palette, bands)
    
        # Turn auto refresh back on once we've finished updating the display
        display.auto_refresh = True 

        # Rember this second so we can compare next time around the loop
        lastsecond = second
        
        # Sleep a moment before we go around again
        time.sleep(0.1)
        
    # Check for button presses
    if button_read(button_a):
        print("Button A")
    if button_read(button_b):
        print("Button B")

