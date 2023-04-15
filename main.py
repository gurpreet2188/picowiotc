from machine import Pin, SoftI2C
import utime as time
from sh1106 import SH1106_I2C
from DHT22 import PicoDHT22
import wifi_con
import sgp30
import iotcentral
import gc
import iot_msg


        
#Connect to DHT22 Temperature and Humidity sensor
dht22 = PicoDHT22(Pin(1,Pin.IN,Pin.PULL_UP))

#Detect and Connect AQ Sensor -SGP30
i2c_sgp = SoftI2C(scl=Pin(14), sda=Pin(15), freq=200000)
sgp30 = sgp30.Adafruit_SGP30(i2c_sgp)

#Connect to Onboard LED
led = Pin('LED', machine.Pin.OUT)

#Set width and height of OLED screen
WIDTH  = 128                                            
HEIGHT = 64                                             

#Detect and Connect SH1106 1.3" OLED Screen
i2c_oled = SoftI2C(scl=Pin(16), sda=Pin(17), freq=200000)
oled = SH1106_I2C(WIDTH, HEIGHT, i2c_oled)


#Func to create a simple OLED/Display message
#message words is in array, each index will create new line (4 is limit).
def oled_msg (msg, pwr_off=True, timer=2):
    oled.init_display()
    y = 0
    for i,m in enumerate(msg):
        y += 11 if i > 0 else 0 
        oled.text(m, 0, y)
        if i > 3:
            break
    oled.show()
    gc.collect()
    time.sleep(timer)
    if pwr_off:
        oled.poweroff()

oled_msg(["Starting..."])
oled_msg(["Sensors", "...detected"])
wifi_connection = wifi_con.connect()
oled_msg(["WiFi", "Connected :)" if wifi_connection else "Failed :("])

if wifi_connection:           
    try:
        oled_msg(["Connecting to", "...IoT Central"], pwr_off=False)
        iotcentral.connect()
        oled_msg(["Connected! :)"])
    except ValueError as e:
        oled_msg(["Connection", "...Failed!"], pwr_off=False)
        print(e)
    
count = 0
send_telemetry_timer = 0

T = []
H = []
CO2 = []
TVOC = []

def get_avg(sensor_value_list):
    total = 0
    for i in sensor_value_list:
        total += i
    return round(total / len(sensor_value_list), 1)

oled_msg(["Reading","sensors","data..."])

while True:
    t, h = dht22.read()
    co2eq, tvoc = sgp30.iaq_measure()
    T.append(t)
    H.append(h)
    CO2.append(co2eq)
    TVOC.append(tvoc)
    
    #IoTC Commands, blink onboard LED
    if iot_msg.MSG_ENQ["msg"] != {}:
        if "led" in iot_msg.MSG_ENQ["msg"]:
            if iot_msg.MSG_ENQ["msg"]["led"] == "on":
                for i in range(4):
                    led.on()
                    time.sleep(0.5)
                    led.off()
                    time.sleep(0.5)
                
            elif iot_msg.MSG_ENQ["msg"]["led"] == "off":
                led.off()
                
        #IoTC Commands, display message on screen
        if "oled" in iot_msg.MSG_ENQ["msg"]:
            oled_msg(iot_msg.MSG_ENQ["msg"]["oled"], timer=5)
        
    if t and co2eq and tvoc is None:
        oled_msg("Sensor Error")
    else:
        print(send_telemetry_timer)
        
        if wifi_connection and iotcentral.is_connected():
            print("testing", iotcentral.listen())
            time.sleep(1)
            if (send_telemetry_timer == 60):
                msg_dict = {
                 "temperature": get_avg(T),
                 "humidity": int(get_avg(H)),
                 "eco2":int(get_avg(CO2)),
                 "tvoc":int(get_avg(TVOC))
                 }
                oled_msg(["sending", "telemetry to", "IoT Central."])
                iotcentral.send_telemetry(msg_dict)
                
                oled_msg(["Telemetry", "...sent!"])
                T = []
                H = []
                CO2 = []
                TVOC = []
                send_telemetry_timer = 0
                gc.collect()
            
        oled_msg([f"T: {t}", f"H: {h}", f"eCO2: {co2eq} ppm", f"TVOC: {tvoc} ppb"])
        
    time.sleep(6)
    send_telemetry_timer += 10
