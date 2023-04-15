from machine import Pin, SoftI2C
from sh1106 import SH1106_I2C
import time

WIDTH  = 128                                            # oled display width
HEIGHT = 64                                             # oled display height

i2c = SoftI2C(scl=Pin(16), sda=Pin(17), freq=200000)    # Init I2C using pins GP16 & GP17

oled = SH1106_I2C(WIDTH, HEIGHT, i2c)

def oled_msg (msg, pwr_off=True, timer=2):
    oled.init_display()
    y = 0
    for i,m in enumerate(msg):
        y += 11 if i > 0 else 0 
        oled.text(m, 0, y)
        if i > 3:
            break
        
    oled.show()
    time.sleep(timer)
    
    if pwr_off:
        oled.poweroff()

oled_msg(["test","test","test","test","test"])


