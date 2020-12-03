# Auther Pitias Fessahaie
# Email selamptsegu@gmail.com 
# Nov 28, 2020
# information Display    512k ESP8266 with Double SSD1306 OLED 128x64

import math
import ssd1306
from machine import Pin,I2C,Timer
from time import sleep_ms,sleep_us,sleep
import urequests
import network

gyro_x = 0.00
gyro_y = 0.00
gyro_z = 0.00
angle_pitch = 0.00
angle_roll = 0.00
acc_total_vector = 0.00
angle_pitch_acc = 0.00
angle_roll_acc = 0.00
set_gyro_angles = False
angle_roll = 0.00
angle_pitch = 0.00
angle_pitch_output = 0.00
angle_roll_output = 0.00

ssid='iPhone'
password = 'pitias126345'
# Other configuration:
DISPLAY_WIDTH  = 128  # Width of display in pixels.
DISPLAY_HEIGHT = 64   # Height of display in pixels.
FONT_WIDTH     = 8    # Width of font characters in pixels.
FONT_HEIGHT    = 12    # Height of the font characters in pixels.
AMPLITUDE      = DISPLAY_HEIGHT - FONT_HEIGHT  # Amplitude of sine wave, in pixels.
FREQUENCY      = 3    # Sine wave frequency, how often it repeats across screen.

MPU6050_ADDR = 0x68
MPU6050_TEMP_OUT_H = 0x41
MPU6050_TEMP_OUT_L = 0x42
MPU6050_PWR_MGMT_1 = 0x6B
MPU6050_LSBC = 340.0
MPU6050_TEMP_OFFSET = 36.53

MPU6050_ACC_X_OUT_H = 0x3B
MPU6050_ACC_X_OUT_L = 0x3C
MPU6050_ACC_Y_OUT_H = 0x3D
MPU6050_ACC_Y_OUT_L = 0x3E
MPU6050_ACC_Z_OUT_H = 0x3F
MPU6050_ACC_Z_OUT_L = 0x40

MPU6050_GYR_X_OUT_H = 0x43
MPU6050_GYR_X_OUT_L = 0x44
MPU6050_GYR_Y_OUT_H = 0x45
MPU6050_GYR_Y_OUT_L = 0x46
MPU6050_GYR_Z_OUT_H = 0x47
MPU6050_GYR_Z_OUT_L = 0x48

LSBA = 16384.0
LSBG =131.0



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

def acceleration(i2c):                         #reading data from the accelerometer
    acc_x_h = i2c.readfrom_mem(MPU6050_ADDR, MPU6050_ACC_X_OUT_H, 1)
    acc_x_l = i2c.readfrom_mem(MPU6050_ADDR, MPU6050_ACC_X_OUT_L, 1)
    acc_y_h = i2c.readfrom_mem(MPU6050_ADDR, MPU6050_ACC_Y_OUT_H, 1)
    acc_y_l = i2c.readfrom_mem(MPU6050_ADDR, MPU6050_ACC_Y_OUT_L, 1)
    acc_z_h = i2c.readfrom_mem(MPU6050_ADDR, MPU6050_ACC_Z_OUT_H, 1)
    acc_z_l = i2c.readfrom_mem(MPU6050_ADDR, MPU6050_ACC_Z_OUT_L, 1)

    return [register(acc_x_h,acc_x_l)/LSBA,   #Divide by LSBA in normal process
            register(acc_y_h,acc_y_l)/LSBA,
            register(acc_z_h,acc_z_l)/LSBA]

def gyroscope(i2c):                            #reading data from the gyroscope
    gyr_x_h = i2c.readfrom_mem(MPU6050_ADDR, MPU6050_GYR_X_OUT_H, 1)
    gyr_x_l = i2c.readfrom_mem(MPU6050_ADDR, MPU6050_GYR_X_OUT_L, 1)
    gyr_y_h = i2c.readfrom_mem(MPU6050_ADDR, MPU6050_GYR_Y_OUT_H, 1)
    gyr_y_l = i2c.readfrom_mem(MPU6050_ADDR, MPU6050_GYR_Y_OUT_L, 1)
    gyr_z_h = i2c.readfrom_mem(MPU6050_ADDR, MPU6050_GYR_Z_OUT_H, 1)
    gyr_z_l = i2c.readfrom_mem(MPU6050_ADDR, MPU6050_GYR_Z_OUT_L, 1)

    return [register(gyr_x_h,gyr_x_l)/LSBG,    #Divide by LSBG in normal process
            register(gyr_y_h,gyr_y_l)/LSBG,
            register(gyr_z_h,gyr_z_l)/LSBG]


def scroll(i2c,msg,addr):
    # Global state:
    display = ssd1306.SSD1306_I2C(DISPLAY_WIDTH, DISPLAY_HEIGHT, i2c,addr)
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
        # Clear the screen.
        display.fill(0)
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
                display.text(char, char_x, lookup_y[char_x+FONT_WIDTH])
        display.show()  


def calibrate(i2c,gyro_x_cal=0.00,gyro_y_cal=0.00,gyro_z_cal=0.00):
    #Calibrating gyro
    gyro_x = gyroscope(i2c)[0]
    gyro_y = gyroscope(i2c)[1]
    gyro_z = gyroscope(i2c)[2]
    
    for _ in range(100):
        gyro_x_cal += gyroscope(i2c)[0]
        gyro_y_cal += gyroscope(i2c)[1]
        gyro_z_cal += gyroscope(i2c)[2]
        sleep_us(3)
                                                                            #Divide the gyro_x_cal variable by 2000 to get the avarage offset
    gyro_x_cal /= 100
    gyro_y_cal /= 100                                                 #Divide the gyro_y_cal variable by 2000 to get the avarage offset
    gyro_z_cal /= 100
    
    return [gyro_x_cal,gyro_y_cal,gyro_z_cal]
    
        
        
        
    

if __name__ == "__main__":
    
    i2c = I2C(scl=Pin(5), sda = Pin(4))
    display = ssd1306.SSD1306_I2C(DISPLAY_WIDTH, DISPLAY_HEIGHT, i2c)
    display2 = ssd1306.SSD1306_I2C(DISPLAY_WIDTH, DISPLAY_HEIGHT, i2c,0x3D)
    init(i2c)
    
    
    
    while True:
        gyro_x -= calibrate(i2c)[0]                                                   #Subtract the offset calibration value from the raw gyro_x value
        gyro_y -= calibrate(i2c)[1]                                               #Subtract the offset calibration value from the raw gyro_y value
        gyro_z -= calibrate(i2c)[2]
        
        #0.004 = 1 / (250Hz )
        angle_pitch += gyro_x * 0.004
        angle_roll += gyro_y * 0.004
        
        #0.00006982 = 0.004 * (3.142(PI) / 180degr)
        angle_pitch += angle_roll * math.sin(gyro_z * 0.00006982)
        angle_roll -= angle_pitch * math.sin(gyro_z * 0.00006982)
        
        acc_x = acceleration(i2c)[0]
        acc_y = acceleration(i2c)[1]
        acc_z = acceleration(i2c)[2]
        
        #Accelerometer angle calculations
        acc_total_vector = math.sqrt((acc_x*acc_x)+(acc_y*acc_y)+(acc_z*acc_z))
        
        # 57.296 = 1 / (3.142 / 180) The Arduino asin function is in radians
        angle_pitch_acc = math.sin(acc_y/acc_total_vector)* 57.296
        angle_roll_acc = math.sin(acc_x/acc_total_vector)* -57.296                      
        
        angle_pitch_acc -= 0.0
        angle_roll_acc -= 0.0
        
        if set_gyro_angles:
            angle_pitch = angle_pitch * 0.9996 + angle_pitch_acc * 0.0004
            angle_roll = angle_roll * 0.9996 + angle_roll_acc * 0.0004
        else:
            angle_pitch = angle_pitch_acc
            angle_roll = angle_roll_acc
            set_gyro_angles = True
        
        angle_pitch_output = angle_pitch_output * 0.9 + angle_pitch * 0.1
        angle_roll_output = angle_roll_output * 0.9 + angle_roll * 0.1
        
        
        
        display.fill(0)
        scroll(i2c,"Pich and Yaw Angle!! !!!",0x3D)
        display.text("Temp:"+str(temperature(i2c))+" C",0,4,2)
        display.text("Pitch Angle:"+str(angle_pitch_output),0,20,2)
        display.text("Yaw Angle:"+str(angle_roll_output),0,36,2)                        
        sleep_ms(500)
        
     
        display.show()
        
