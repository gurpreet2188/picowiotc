import network
import wifi_creds
import time
import gc
import micropython

ssid = ''
password = ''

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wifi_networks = wlan.scan()

networks = []

for wn in wifi_networks:
    wn = wn[0].decode('utf-8')
    if wn in wifi_creds.creds:
        networks.append(wn)
    

if len(networks) > 1:
    connected = False
    for n in networks:
        if wifi_creds.creds[n]['preferred']:
            ssid = n
            password = wifi_creds.creds[n]['password']
            connected = True
            
    if not connected: # connect to first available network in list
        ssid = networks[0]
        password = wifi_creds.creds[networks[0]]['password']
    
    del connected
else:
    ssid = networks[0]
    password = wifi_creds.creds[networks[0]]['password']
    
  
del networks
del wifi_networks
gc.collect()
max_wait = 20
if ssid != '':
    wlan.connect(ssid,password)
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)


# Handle connection error
def connect ():
    try:
        if ssid == '':
            return False
        #_connect(wifi_creds.creds['HOME']['ssid'],wifi_creds.creds['HOME']['password'])
        status = wlan.ifconfig()
        print( 'ip = ' + status[0] )
        if status[0] == '0.0.0.0':
            return False 
        return True
    except:
        return False
        
connect()
