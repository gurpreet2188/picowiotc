import network
import wifi_creds
import utime as time

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(wifi_creds.ssid, wifi_creds.password)

max_wait = 20
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

# Handle connection error
def connect ():
    try:
        status = wlan.ifconfig()
        print( 'ip = ' + status[0] )
        if status[0] == '0.0.0.0':
            return "Connection Failed" 
        return "Connected :)"
    except ValueError (e):
        print(e)
        return "Connection Failed"
   
#uncomment to test Wifi     
#connect()
