# 
# Author: Társis Natan Boff da Silva
# Get date from MQTT server
# Acquisition of RSSI data from a LoRa network between mobile node and gateways

import paho.mqtt.client as mqtt
import json
import base64
import time
import iso8601
from datetime import datetime


now = datetime.now()
APPEUI = "70B3D57ED001B5DF"
APPID  = "tccteste2"
PSW    = 'ttn-account-v2.I9nmkZIDsgIPgoccEs4XdO94YJt-4Wy2rDULg99CKgA'
g_id = 0
t = time.localtime()
data = str(t.tm_mday) + "," + str(t.tm_hour) + "," + str(t.tm_min) + "," + str(t.tm_sec)
experiment = str(t.tm_year) + str(t.tm_mon) + str(t.tm_mday) + str(t.tm_hour) + str(t.tm_min) + str(t.tm_sec)	
packets_count = [0]
packets_sent = [0]
last_counter = []
ids = []
index = 0
amostras = 100;
g1i = 0
g2i = 0
g3i = 0
g4i = 0

#Call back functions 

# gives connection message
def on_connect(mqttc, mosq, obj,rc):
    print("Connected with result code:"+str(rc))
    # subscribe for all devices of user
    mqttc.subscribe('+/devices/+/up')

# gives message from device
def on_message(mqttc,obj,msg):
    global g1i, g2i, g3i, g4i, amostras
    if msg._topic.count(b"payload"):
        return
    x = json.loads(msg.payload.decode('utf-8'))
    device = x["dev_id"]
    payload_raw = x["payload_raw"]
    payload_plain = base64.b64decode(payload_raw)
    datetime = x["metadata"]["time"]
    counter = x["counter"]
    freq = x["metadata"]["frequency"]
    rssi = x["metadata"]["gateways"][0]["rssi"] 
    snr = x["metadata"]["gateways"][0]["snr"]
    rf_chain = x["metadata"]["gateways"][0]["rf_chain"]
    timestamp = x["metadata"]["gateways"][0]["timestamp"]
    timestring = x["metadata"]["gateways"][0]["time"]
    gtw_id = x["metadata"]["gateways"][0]["gtw_id"]
    
    if(g1i < amostras):
        if (gtw_id) == "eui-b827ebffff6155c1":
            arquivo = open('G1.txt', 'a')
            arquivo.write(str(rssi) + ",\n")
            arquivo.close()
            g1i = g1i + 1
            if(g1i == amostras -1):
                print("gateway1 com: " + str(g1i) + "amostras")
    if(g2i < amostras):       
        if (gtw_id) == "eui-b827ebffff95e2c7":
            arquivo = open('G2.txt', 'a')
            arquivo.write(str(rssi) + ",\n")
            arquivo.close()
            g2i = g2i + 1
            if(g2i == amostras -1):
                print("gateway2 com: " + str(g2i) + "amostras")
    if(g3i < amostras):        
        if (gtw_id) == "eui-b827ebffff4436f1":
            arquivo = open('G3.txt', 'a')
            arquivo.write(str(rssi) + ",\n")
            arquivo.close()
            g3i = g3i + 1
            if(g3i == amostras -1):
                print("gatewa3 com: " + str(g3i) + "amostras")
    if(g4i < amostras):        
        if (gtw_id) == "eui-b827ebffff270e92":
            arquivo = open('G4.txt', 'a')
            arquivo.write(str(rssi) + ",\n")
            arquivo.close()
            g4i = g4i + 1
            if(g4i == amostras -1):
                print("gatewa4 com: " + str(g4i) + "amostras")


        
    ts = iso8601.parse_date(timestring)
    
    ts = time.mktime(ts.timetuple())
    
    global last_counter,packets_count,packets_sent,index
    if ids.count(device) == 0:
        ids.insert(index,device)
        index = index+1
        

    idx = ids.index(device)
    if not last_counter:
        last_counter.insert(idx,counter)
        # packets_sent.insert(idx,0)
        # packets_count.insert(idx,1)
    if last_counter[idx] != counter:
        cnt = counter-last_counter[idx]
        if cnt < 0:
            cnt = cnt + 65536
        packets_sent[idx] = packets_sent[idx] + cnt
        res = "\n" + str(packets_sent[idx]) + "," + str(packets_count[idx]) + ","  + str(snr) + "," + str(rssi) + ","  \
        + str(freq) + ","  + str(rf_chain) + ","  + str(counter) + ","  + str(ts) + ","  + str(payload_plain)
        fname = str(device) + "_" + str(experiment) + "unique.txt"
        with open(fname, "a") as myfile:
            myfile.write(res)
        myfile.close()

    packets_count[idx] = packets_count[idx] + 1
    last_counter[idx] = counter
    #rssi = -1
    #print(device + ": " + payload_raw + " ==> " + payload_plain + ", RSSI ["+ str(rssi) + "] @" + datetime )
    res = "\n" + str(packets_sent[idx]) + "," + str(packets_count[idx]) + ","  + str(snr) + "," + str(rssi) + ","  \
    + str(freq) + ","  + str(rf_chain) + ","  + str(counter) + ","  + str(ts) + ","  + str(payload_plain)
    print(res)
    fname = str(device) + "_" + str(experiment) + ".txt"
    with open(fname, "a") as myfile:
        myfile.write(res)
    myfile.close()
    
def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))
    

def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mqttc,obj,level,buf):
    print("message:" + str(buf))
    print("userdata:" + str(obj))
    
mqttc= mqtt.Client()

# Assign event callbacks
mqttc.on_connect=on_connect
mqttc.on_message=on_message

mqttc.username_pw_set(APPID, PSW)
mqttc.connect("brazil.thethings.network",1883,60)

# and listen to server
run = True

while run:
    mqttc.loop_forever()
    
