import os
import glob
import time
import requests
import datetime as dt
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

print("starting temp.py")

# Define the Reset Pin
oled_reset = digitalio.DigitalInOut(board.D4)

# Change these
# to the right size for your display!
WIDTH = 128
HEIGHT = 32     # Change to 64 if needed
BORDER = 2

# Use for I2C.
i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3c, reset=oled_reset)

# Use for SPI
#spi = board.SPI()
#oled_cs = digitalio.DigitalInOut(board.D5)
#oled_dc = digitalio.DigitalInOut(board.D6)
#oled = adafruit_ssd1306.SSD1306_SPI(WIDTH, HEIGHT, spi, oled_dc, oled_reset, oled_cs)

# Clear display.
oled.fill(0)
oled.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new('1', (oled.width, oled.height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)


os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'

device_folder = glob.glob(base_dir + '28*')
device_file = '/w1_slave'
iftttkey = os.environ['IFTTTKEY']
def turn_onoff(onoff):
    print("Turned " + onoff)
    requests.post("https://maker.ifttt.com/trigger/turn_" + onoff + "_fan_request/with/key/"+iftttkey)


def read_temp_raw(filen):
    f = open(filen, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp(filen):
    lines = read_temp_raw(filen)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f

	
import numpy as np
N = 100
#indoor_t = np.zeros(N)
#outdoor_t = np.zeros(N)
data = np.zeros((3,N), dtype=object)
iidx = 0
oidx = 0
NAVG = 100
first_iter = True
print("entering infinite loop")
while True:
    if first_iter and iidx < NAVG:
        navg = iidx
    else:
        navg = NAVG

    #for j in device_folder:
    #    print(j+": ",read_temp(j+device_file)[1])
    # Draw a white background
    draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)

    # Draw a smaller inner rectangle
    draw.rectangle((BORDER, BORDER, oled.width - BORDER - 1, oled.height - BORDER - 1),
                           outline=0, fill=0)

    # Load default font.
    font = ImageFont.load_default()

    # Draw Some Text
    #indoor_t[iidx] 
    data[0,iidx] = read_temp(device_folder[0]+device_file)[1]
    #outdoor_t[oidx] 
    data[1,iidx] = read_temp(device_folder[1]+device_file)[1]
    data[2, iidx] = dt.datetime.today()
    
    imean = np.mean(data[0,iidx-navg:iidx+1])
    text = "Indoor Temp: {:.2f}".format(imean)
    print(text)
    (font_width, font_height) = font.getsize(text)
    draw.text((oled.width//2 - font_width//2, 5), text, font=font, fill=255)

    # Draw Some Text
    omean = np.mean(data[1,oidx-navg:oidx+1])
    text = "Outdoor Temp: {:.2f}".format(omean)
    print(text)
    (font_width, font_height) = font.getsize(text)
    draw.text((oled.width//2 - font_width//2, oled.height//2), text, font=font, fill=255)

    # Display image
    oled.image(image)
    oled.show()
   

    if (iidx % 100 == 1):
        if (imean > omean and imean > 68 and omean < 90):
            turn_onoff("on")
        else:
            turn_onoff("off")

    iidx += 1
    oidx += 1
    if (iidx == N):
        iidx = 0
        oidx = 0
        np.save("/home/pi/Documents/raspitemp/data2/data_{}.npy".format(time.strftime("%Y%m%d-%H%M%S")), data)
        #np.save("/home/pi/Documents/temp/data/outdoor_temps_{}.npy".format(time.strftime("%Y%m%d-%H%M%S")),outdoor_t)
