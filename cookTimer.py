from machine import Pin
from time import sleep
import tm1637

led =Pin(0,Pin.OUT)
btn=Pin(2,Pin.IN,Pin.PULL_UP)
tm=tm1637.TM1637(Pin(5),Pin(4),brightness=2)

def counter():
    led.value(0)
    for i in range(4,-1,-1):
        for j in range(59,-1,-1):
            tm.numbers(i,j)
            sleep(1)
            
    led.value(1)
    sleep(2)
    led.value(0)
            
while True:
    if not btn.value():
        counter()
        
            