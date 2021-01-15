# Auther Pitias Fessahaie
# Email selamptsegu@gmail.com 
# Nov 28, 2020
# information Display    512k ESP8266 with SSD1306 OLED 128x64


import math
import ssd1306
from machine import Pin,I2C,Timer
from time import sleep_ms,sleep_us,sleep
import time

gyro_x = 0.00
gyro_y = 0.00
gyro_z = 0.00
acc_x = 0.00
acc_y = 0.00
acc_z = 0.00
gyro_x_er = 0.00
gyro_y_er = 0.00
gyro_z_er = 0.00
acc_x_er = 0.00
acc_y_er = 0.00

current = 0.00
elapsed = 0.00

acc_angle_x = 0.00
acc_angle_y = 0.00
gy_angle_x =0.00
gy_angle_y = 0.00
yaw = 0.00
roll = 0.00
pitch = 0.00
temp = 0.00

DISPLAY_WIDTH  = 128  # Width of display in pixels.
DISPLAY_HEIGHT = 64   # Height of display in pixels.


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
LSBG = 131.0



def init(i2c):
    i2c.writeto_mem(MPU6050_ADDR,MPU6050_PWR_MGMT_1,bytes([0]))


def register(h, l):
    if not h[0] & 0x80:
        return h[0] << 8 | l[0]
    return -(((h[0] ^ 255) << 8) |  (l[0] ^ 255) + 1)
            

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





def imu_error(i2c,gyro_x_cal=0.00,gyro_y_cal=0.00,gyro_z_cal=0.00,acc_x_cal=0.00,acc_y_cal=0.00,acc_z_cal=0.00,acc_err_x=0.00,acc_err_y=0.00):
    
    #Calibrating gyro
    gyro_x_cal -= gyroscope(i2c)[0]
    gyro_y_cal -= gyroscope(i2c)[1]
    gyro_z_cal -= gyroscope(i2c)[2]
   
    
    
    for _ in range(200):
        gyro_x_cal += gyroscope(i2c)[0]
        gyro_y_cal += gyroscope(i2c)[1]
        gyro_z_cal += gyroscope(i2c)[2]
        #sleep_us(3)
                                                                            #Divide the gyro_x_cal variable by 200 to get the avarage offset
    gyro_x_cal /= 200
    gyro_y_cal /= 200                                                       #Divide the gyro_y_cal variable by 200 to get the avarage offset
    gyro_z_cal /= 200
    
    acc_x_cal -= acceleration(i2c)[0]
    acc_y_cal -= acceleration(i2c)[1]
    acc_z_cal -= acceleration(i2c)[2]
    
    for _ in range(200):
        acc_x_cal += acceleration(i2c)[0]
        acc_y_cal += acceleration(i2c)[1]
        acc_z_cal += acceleration(i2c)[2]
        #sleep_us(3)
                                                                        #Generation Error value after filtering to get calibrated output (stable result Angle)        
        acc_err_x = acc_err_x + (math.atan((acc_y_cal)/ math.sqrt((acc_x_cal**2)+(acc_z_cal**2)))) * 180/3.142
        acc_err_y = acc_err_y + (math.atan(-1*(acc_x_cal) / math.sqrt((acc_y_cal**2)+(acc_z_cal**2)))) * 180/3.142
        
    
    acc_err_x = acc_err_x / 200
    acc_err_y = acc_err_y / 200
    
    
    return [gyro_x_cal,gyro_y_cal,gyro_z_cal,acc_err_x,acc_err_y]     #Error for Gyro x,y,z and Acc x,y
    
        
def translate(value, leftMin, leftMax, rightMin, rightMax):   # pservo = translate(pitch,-90,90,20,110) for servo.duty(int(pservo))
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)        
        
    

if __name__ == "__main__":
    
    i2c = I2C(scl=Pin(5), sda = Pin(4))
    display = ssd1306.SSD1306_I2C(DISPLAY_WIDTH, DISPLAY_HEIGHT, i2c)

    init(i2c)
    
    gyro_x_er -= imu_error(i2c)[0]                                               #Subtract the offset calibration value from the raw gyro_x value
    gyro_y_er -= imu_error(i2c)[1]                                               #Subtract the offset calibration value from the raw gyro_y value
    gyro_z_er -= imu_error(i2c)[2]
    acc_x_er -= imu_error(i2c)[3]
    acc_y_er-= imu_error(i2c)[4]
    
    
    print(gyro_x_er)
    print(gyro_y_er)
    print(gyro_z_er)
    print(acc_x_er)
    print(acc_y_er)
    
    while True:
        
        acc_x = acceleration(i2c)[0]
        acc_y = acceleration(i2c)[1]
        acc_z = acceleration(i2c)[2]
        
        acc_angle_x = (math.atan(acc_y/ math.sqrt((acc_x**2)+(acc_z**2))) * 180/3.142) + 3.1    #if the result is negative add the error else subtract the error (ERROR CORRECTION)
        acc_angle_y = (math.atan(-1*acc_x / math.sqrt((acc_y**2)+(acc_z**2))) * 180/3.142) - 1
        
        current = time.ticks_ms()
        elapsed = time.ticks_diff(time.ticks_ms(), current) / 1000
        
        gyro_x = gyroscope(i2c)[0]
        gyro_y = gyroscope(i2c)[1]
        gyro_z = gyroscope(i2c)[2]
        
        gyro_x = gyro_x + 1.45                             #if the result is negative add the error else subtract the error
        gyro_y = gyro_y + 3.26                             # calibrate from output
        gyro_z = gyro_z + 0.26
        
        #Row value are in degree/sec we need to multiply by second to get the (degree value)
        gy_angle_x = gy_angle_x + (gyro_x * elapsed)
        gy_angle_y = gy_angle_y + (gyro_y * elapsed)
        yaw = yaw + (gyro_z * elapsed)
        
        roll = (0.9 * gy_angle_x + 0.1 * acc_angle_x)*10
        pitch = (0.9 * gy_angle_y + 0.1 * acc_angle_y)*10
        temp = temperature(i2c)
        
        
        display.fill(0)
        
        display.text("Roll(X):"+str(roll),0,0,2)
        display.text("Pitch(Y):"+str(pitch),0,16,2)
        display.text("Yaw(Z):"+str(yaw),0,34,2)
        display.text("Temp:"+str(temp)+"°C",0,50,2)
        sleep_ms(300)
        
     
        display.show()
        



