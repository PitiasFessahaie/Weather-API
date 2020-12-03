#Auther Pitias Fessahaie
#Email selamptsegu@gmail.com
#Automatic Weather Display ESP8266 and OLED 1306 with MPU6050
#use at your Own Risks


from machine import I2C,Pin
import ssd1306
from ssd1306 import SSD1306_I2C
import urequests
import network
import math
from time import sleep,sleep_ms

MPU6050_ADDR = 0x68
MPU6050_TEMP_OUT_H = 0x41
MPU6050_TEMP_OUT_L = 0x42
MPU6050_PWR_MGMT_1 = 0x6B
MPU6050_LSBC = 340.0
MPU6050_TEMP_OFFSET = 36.53

DISPLAY_WIDTH  = 128  # Width of display in pixels.
DISPLAY_HEIGHT = 64   # Height of display in pixels.
FONT_WIDTH     = 8    # Width of font characters in pixels.
FONT_HEIGHT    = 12    # Height of the font characters in pixels.
AMPLITUDE      = DISPLAY_HEIGHT - FONT_HEIGHT  # Amplitude of sine wave, in pixels.
FREQUENCY      = 3    # Sine wave frequency, how often it repeats across screen.

def init(i2c):
    i2c.writeto_mem(MPU6050_ADDR,MPU6050_PWR_MGMT_1,bytes([0]))


def register(h, l):
    if not h[0] & 0x80:
        return h[0] << 8 | l[0]
    return -((h[0] ^ 255) << 8) |  (l[0] ^ 255) + 1

def temperature(i2c):
    temp_h = i2c.readfrom_mem(MPU6050_ADDR, MPU6050_TEMP_OUT_H, 1)
    temp_l = i2c.readfrom_mem(MPU6050_ADDR, MPU6050_TEMP_OUT_L, 1)

    return (register(temp_h, temp_l) / MPU6050_LSBC) + MPU6050_TEMP_OFFSET


def scroll(i2c,msg,addr):
    init(i2c)
    
    # Global state:
    display2 = ssd1306.SSD1306_I2C(DISPLAY_WIDTH, DISPLAY_HEIGHT, i2c,addr)
    pos = DISPLAY_WIDTH  # X position of the starting character in the message.
    message_len_px = len(msg) * FONT_WIDTH  # Pixel width of the message.
    # Build a lookup table of wavy Y positions for each column.  This will speed
    # up the main loop by not constantly computing Y positions.  Remember characters
    # can be drawn off screen to the left so increase the lookup table a bit to
    # compute their Y positions too.
    lookup_y = [0] * (DISPLAY_WIDTH+FONT_WIDTH)
    for i in range(len(lookup_y)):
        t = i / (DISPLAY_WIDTH-1)  # Compute current 'time' as position along
                                   # lookup table in 0 to 1 range.
        # Use a sine wave that's offset to the range 0 to AMPLITUDE to compute
        # each character Y position at a given X.
        lookup_y[i] = int(((AMPLITUDE/2.0) * math.sin(2.0*math.pi*FREQUENCY*t)) + (AMPLITUDE/2.0))
        
    # Main loop:
    for i in range(150):
        temp = temperature(i2c)
        Fr = (temp * (9/5))+32
        # Clear the screen.
        display2.fill(0)
        # Move left a bit, then check if the entire message has scrolled past
        # and start over from far right.
        pos -= 1
        if pos <= -message_len_px:
            pos = DISPLAY_WIDTH
        # Go through each character in the message.
        for i in range(len(msg)):
            char = msg[i]
            char_x = pos + (i * FONT_WIDTH)  # Character's X position on the screen.
            if -FONT_WIDTH <= char_x < DISPLAY_WIDTH:
                display2.text(char, char_x, lookup_y[char_x+FONT_WIDTH])
        
        display2.text("Room Temperature:",0,4,2)
        display2.text("    "+str(Fr)+" F",0,16,2)
        display2.show()  

ssid='Your Wifi'
password = 'Your Password'
i2c = I2C(scl=Pin(5), sda=Pin(4))
display = SSD1306_I2C(128, 64, i2c)

wifi = network.WLAN(network.STA_IF)

if not wifi.isconnected():
    display.text("Searching Wifi",0,0)
    wifi.active(True)
    wifi.connect(ssid, password)
    display.show()
    while not wifi.isconnected():
        display.text("Connecting Wifi",0,16)
        sleep(1)
        display.show()    

             
  
#Configure the URL
woeid=[2358820,2514815,2480894]    

id = woeid[1]
url = "https://www.metaweather.com/api/location/"+str(id)+"/"
        
resp = urequests.get(url)

         
while True:
    
    
    if resp.status_code == 200:  # query successful
        display.text("Conn Successful!!.", 0, 6)
        sleep(0.4)

        # parse JSON
        app = resp.json()
        # excract data
        date = app['consolidated_weather'][0]['created']
        location = app['title']
        temp = app['consolidated_weather'][0]['the_temp']
        F = (temp * (9/5))+32
        visiblity = app['consolidated_weather'][0]['visibility']
        humidity = app['consolidated_weather'][0]['humidity']
        weather = app['consolidated_weather'][0]['weather_state_name']
        
        scroll(i2c,"This is fun Pitias!! !!!",0x3D)
        display.fill(0)
        display.text("Weather Report!!!",0,0)
        display.text(date,0,8)
        display.text(location,0,16)
        display.text(weather,0,32)
        display.text("Temp :"+str(F)+" F",0,40)
        display.text("Visiblity :"+str(visiblity),0,48)
        display.text("Humidity :"+str(humidity),0,56)
        sleep(2)
        display.show()

