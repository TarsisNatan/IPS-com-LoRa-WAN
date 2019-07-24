#	Author Társis Natan Boff da Silva
#	Versão beta
#	Cadastra lugares e salas em um espaço indoor e constroi modelos preditivos (KNN e SVM) para aprender a localizar 
#	o nó móvel de uma rede num espaço indoor utilizando dados RSSI fornecidos poruma rede LoRaWAN
#  Funções do programa um + programa dois e plotagem dos resultados  

import numpy as np
import matplotlib.pyplot as plt
from sklearn import svm
import pandas as pd
from matplotlib import style
from sklearn import datasets, svm, metrics
from sklearn.preprocessing import StandardScaler 
from mpl_toolkits.mplot3d import Axes3D
from sklearn.metrics import classification_report, confusion_matrix
import pickle 
from sklearn.neighbors import KNeighborsClassifier

import paho.mqtt.client as mqtt
import json
import base64
import time
import iso8601
from datetime import datetime
import os.path


si = 0;
X = np.zeros((125,5),dtype='int')
p = np.zeros((5,4),dtype = 'int')
pasta_raiz = "salas2/"
n_medidas = 3
medida = 0
n_amostras = 1
locais = ["Sala","Corredor","Banheiro","Quarto","Cozinha"]
local_i = 0
n_locais = 0
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

n_locais = 0

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
    global g1i
    global g2i
    global g3i
    global g4i
    global n_locais
    global locais
    global n_amostras
    global n_medidas
    global medida
    global local_i
    global start
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
    if(g1i < n_amostras):
        if (gtw_id) == "eui-b827ebffff6155c1":
            if(g1i == n_amostras):
                print("gateway 1 com: " + str(g1i) + "amostras")
            else:
                print("g1: " + str(g1i) + str(rssi))
                g1i = g1i + 1  
            if(gravar_dataset == True):
                arquivo = open(pasta_raiz + locais[local_i]+ "/" + 'G1.txt', 'a')
                arquivo.write(str(rssi) + ", " + str(local_i) + "\n")
                arquivo.close()
            else: p[g1i-1,0] = rssi				
    if(g2i < n_amostras):
        if (gtw_id) == "eui-b827ebffff95e2c7":
            if(g2i == n_amostras):
                print("gateway 2 com: " + str(g2i) + "amostras")
            else:
                print("g2: " + str(g2i) + str(rssi))             
                g2i = g2i + 1
            if(gravar_dataset == True):
                arquivo = open(str(pasta_raiz) + str(locais[local_i])+ "/" +'G2.txt', 'a')
                arquivo.write(str(rssi) + ", " + str(local_i) + "\n")
                arquivo.close()
            else: p[g2i-1,1] = rssi	
    if(g3i < n_amostras):        
        if (gtw_id) == "eui-b827ebffff4436f1":
            if(g3i == n_amostras):
                print("gateway 3 com: " + str(g3i) + "amostras")
            else:
                 print("g3: " + str(g3i) + str(rssi))
                 g3i = g3i + 1
            if(gravar_dataset == True):
                arquivo = open(str(pasta_raiz) + str(locais[local_i])+ "/" +'G3.txt', 'a')
                arquivo.write(str(rssi) + ", " + str(local_i) + "\n")
                arquivo.close()
            else: p[g3i-1,2] = rssi			
    if(g4i < n_amostras):        
        if (gtw_id) == "eui-b827ebffff270e92":
            if(g4i == n_amostras):
                print("gateway 4 com: " + str(g4i) + "amostras")
            else:
                print("g4: " + str(g4i) + str(rssi))
                g4i = g4i + 1
            if(gravar_dataset == True):
                arquivo = open(str(pasta_raiz) + str(locais[local_i])+ "/" +'G4.txt', 'a')
                arquivo.write(str(rssi) + ", " + str(local_i) + "\n")
                arquivo.close()
            else: p[g4i-1,3] = rssi
    if(g4i == n_amostras and g3i == n_amostras and g2i == n_amostras and g1i == n_amostras):
        start = 'N'
        
        
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

def cria_diretorios():
    global locais
    global n_locais
    global pasta_raiz
    if not os.path.exists(pasta_raiz):
        os.makedirs(pasta_raiz)

    if n_locais == 0:
        n_locais = int(input('Entre com o número de locais: '))
        
    locais =  ["-" for x in range(n_locais)]
    for i in range (0,n_locais):
        locais[i] = input('Entre com o nome da local: ' + str(i + 1)  + ": ")
        pasta = pasta_raiz + str(locais[i]) + "/"
        os.makedirs(pasta)
        #locais = input('qual o número de locais em cada local?')
        arquivo = open(pasta +'G1.txt', 'a')
        arquivo = open(pasta +'G2.txt', 'a')
        arquivo = open(pasta +'G3.txt', 'a')
        arquivo = open(pasta +'G4.txt', 'a')
        print('local nº ' + str(i + 1) + ": " + str(locais[i]))
        
def org_dados():
    global pasta_raiz
    global locais
    global X
    global X_cheio
    global si
    for i in range(0,5):#0 até numero de classes
        a = np.loadtxt(pasta_raiz + locais[i] + '/G1.txt', delimiter=",", dtype='int')
        b = np.loadtxt(pasta_raiz + locais[i] + '/G2.txt', delimiter=",", dtype='int')
        c = np.loadtxt(pasta_raiz + locais[i] + '/G3.txt', delimiter=",", dtype='int')
        d = np.loadtxt(pasta_raiz + locais[i] + '/G4.txt', delimiter=",", dtype='int')
        
        
        X [si:(25*(i+1)),:1]  = a[:len(a), :1]
        X [si:(25*(i+1)),1:2] = b[:len(b), :1]
        X [si:(25*(i+1)),2:3] = c[:len(c), :1]
        X [si:(25*(i+1)),3:4] = d[:len(d), :1]

        X [si:(25*(i+1)),4:]  = a[:len(a), 1:]
        si = si + 25
    X_cheio = True
    
def treinamentoKNN(k):
    global X
    X = X.astype(np.int)
    x = X
    np.random.shuffle(x)
    np.random.shuffle(x)
    np.random.shuffle(x)
    np.random.shuffle(x)
    Xtrain = x[:99, :4]
    ytrain = x[:99, 4::]

    Xtest = x[100:, :4]
    ytest = x[100:, 4::]
    
    classifier = KNeighborsClassifier(n_neighbors = 5)  
    classifier.fit(Xtrain, ytrain)  
    y_pred = classifier.predict(Xtest)
    with open('KNN_Salas_model','wb') as f:
        pickle.dump(classifier, f)
    print(confusion_matrix(ytest, y_pred))  
    print(classification_report(ytest, y_pred))
    
def medidaP():
    global med_P, start, locais,gravar_dataset
    gravar_dataset = False
    #start = input('deseja iniciar uma medida ? (S/N)')
    start = 'S'
    g1i = 0
    g2i = 0
    g3i = 0
    g4i = 0
    while(str(start) == 'S'):
        mqttc.loop_start()
    print(p)    
    pickle_in = open('KNN_Salas_model','rb')
    classifier = pickle.load(pickle_in)
    lugar_pred = classifier.predict(p)
    print(lugar_pred)

def grficos():
    global X
    fig = plt.figure()
    bx = plt.subplot(231)

    m = 0
    marks = ['$1$','$2$','$3$','$4$','$5$']
    while m < 5:
        bx.scatter(X[(m*5):5+(m*5), 0],X[(m*5):5+(m*5), 1],c = 'r', label= 'Sala', marker = marks[m])
        bx.scatter(X[25+(m*5):30+(m*5), 0],X[25+(m*5):30+(m*5), 1],c = 'orange', label= 'Corredor', marker = marks[m])
        bx.scatter(X[50+(m*5):55+(m*5), 0],X[50+(m*5):55+(m*5), 1],c = 'y', label= 'Banheiro', marker = marks[m])
        bx.scatter(X[75+(m*5):80+(m*5), 0],X[75+(m*5):80+(m*5), 1],c = 'green', label= 'Quarto', marker = marks[m])
        bx.scatter(X[100+(m*5):105+(m*5), 0],X[100+(m*5):105+(m*5), 1],c = 'blue', label= 'Cozinha', marker = marks[m])
        m = m +1    
    bx.set_ylabel("G2-corredor")
    bx.set_xlabel("G1-Sala")
    m = 0
    
    bx = plt.subplot(232)
    while m < 5:
        bx.scatter(X[(m*5):5+(m*5), 2],X[(m*5):5+(m*5), 1],c = 'r', label= 'Sala', marker = marks[m])
        bx.scatter(X[25+(m*5):30+(m*5), 2],X[25+(m*5):30+(m*5), 1],c = 'orange', label= 'Corredor', marker = marks[m])
        bx.scatter(X[50+(m*5):55+(m*5), 2],X[50+(m*5):55+(m*5), 1],c = 'y', label= 'Banheiro', marker = marks[m])
        bx.scatter(X[75+(m*5):80+(m*5), 2],X[75+(m*5):80+(m*5), 1],c = 'green', label= 'Quarto', marker = marks[m])
        bx.scatter(X[100+(m*5):105+(m*5), 2],X[100+(m*5):105+(m*5), 1],c = 'blue', label= 'Cozinha', marker = marks[m])
        m = m +1 
    bx.set_ylabel("G2-corredor")
    bx.set_xlabel("G3-cozinha")
    m = 0
    bx = plt.subplot(233)
    while m < 5:
        bx.scatter(X[(m*5):5+(m*5), 3],X[(m*5):5+(m*5), 1],c = 'r', label= 'Sala', marker = marks[m])
        bx.scatter(X[25+(m*5):30+(m*5), 3],X[25+(m*5):30+(m*5), 1],c = 'orange', label= 'Corredor', marker = marks[m])
        bx.scatter(X[50+(m*5):55+(m*5), 3],X[50+(m*5):55+(m*5), 1],c = 'y', label= 'Banheiro', marker = marks[m])
        bx.scatter(X[75+(m*5):80+(m*5), 3],X[75+(m*5):80+(m*5), 1],c = 'green', label= 'Quarto', marker = marks[m])
        bx.scatter(X[100+(m*5):105+(m*5), 3],X[100+(m*5):105+(m*5), 1],c = 'blue', label= 'Cozinha', marker = marks[m])
        m = m +1 
    bx.set_ylabel("G2-corredor")
    bx.set_xlabel("G4-quarto")
    m = 0
    bx = plt.subplot(234)
    while m < 5:
        bx.scatter(X[(m*5):5+(m*5), 0],X[(m*5):5+(m*5), 2],c = 'r', label= 'Sala', marker = marks[m])
        bx.scatter(X[25+(m*5):30+(m*5), 0],X[25+(m*5):30+(m*5), 2],c = 'orange', label= 'Corredor', marker = marks[m])
        bx.scatter(X[50+(m*5):55+(m*5), 0],X[50+(m*5):55+(m*5), 2],c = 'y', label= 'Banheiro', marker = marks[m])
        bx.scatter(X[75+(m*5):80+(m*5), 0],X[75+(m*5):80+(m*5), 2],c = 'green', label= 'Quarto', marker = marks[m])
        bx.scatter(X[100+(m*5):105+(m*5), 0],X[100+(m*5):105+(m*5), 2],c = 'blue', label= 'Cozinha', marker = marks[m])
        m = m +1 
    bx.set_ylabel("G3-cozinha")
    bx.set_xlabel("G1-Sala")
    m = 0
    bx = plt.subplot(235)
    while m < 5:
        bx.scatter(X[(m*5):5+(m*5), 2],X[(m*5):5+(m*5), 3],c = 'r', label= 'Sala', marker = marks[m])
        bx.scatter(X[25+(m*5):30+(m*5), 2],X[25+(m*5):30+(m*5), 3],c = 'orange', label= 'Corredor', marker = marks[m])
        bx.scatter(X[50+(m*5):55+(m*5), 2],X[50+(m*5):55+(m*5), 3],c = 'y', label= 'Banheiro', marker = marks[m])
        bx.scatter(X[75+(m*5):80+(m*5), 2],X[75+(m*5):80+(m*5), 3],c = 'green', label= 'Quarto', marker = marks[m])
        bx.scatter(X[100+(m*5):105+(m*5), 2],X[100+(m*5):105+(m*5), 3],c = 'blue', label= 'Cozinha', marker = marks[m])
        m = m +1 
    bx.set_ylabel("G4-quarto")
    bx.set_xlabel("G3-cozinha")
    m = 0
    bx = plt.subplot(236)
    while m < 5:
        bx.scatter(X[(m*5):5+(m*5), 3],X[(m*5):5+(m*5), 0],c = 'r', label= 'Sala', marker = marks[m])
        bx.scatter(X[25+(m*5):30+(m*5), 3],X[25+(m*5):30+(m*5), 0],c = 'orange', label= 'Corredor', marker = marks[m])
        bx.scatter(X[50+(m*5):55+(m*5), 3],X[50+(m*5):55+(m*5), 0],c = 'y', label= 'Banheiro', marker = marks[m])
        bx.scatter(X[75+(m*5):80+(m*5), 3],X[75+(m*5):80+(m*5), 0],c = 'green', label= 'Quarto', marker = marks[m])
        bx.scatter(X[100+(m*5):105+(m*5), 3],X[100+(m*5):105+(m*5), 0],c = 'blue', label= 'Cozinha', marker = marks[m])
        if m == 0: bx.legend()
        m = m +1 
    bx.set_ylabel("G1-Sala")
    bx.set_xlabel("G4-quarto")
    plt.show()


    
    
mqttc= mqtt.Client()

# Assign event callbacks
mqttc.on_connect=on_connect
mqttc.on_message=on_message

mqttc.username_pw_set(APPID, PSW)
mqttc.connect("brazil.thethings.network",1883,60)

# and listen to server
run = True
X_cheio = False
cria_diretorios()

while run:
#criar um menu principal 
     
    if(local_i < n_locais):
        gravar_dataset = True 
        if(medida < n_medidas):
            start = input('deseja iniciar a medida ' + str(medida + 1) + ' no local '+ str(locais[local_i]) + " ? (S/N)")
            print("medindo local:" + str(locais[local_i]))
            print("medida " + str(medida + 1) + " de " + str(n_medidas) +" medidas") 
            medida = medida + 1
            g1i = 0
            g2i = 0
            g3i = 0
            g4i = 0
            while(str(start) == 'S'):
                mqttc.loop_start()
        else: 
            medida = 0 
            local_i = local_i + 1
    else:
        if(X_cheio == False):
            print("medidas concluídas em todas as locais")
            #rotina de compilação do dataset
            org_dados()
            #rotina de treinamento do dataset
            grficos()
            treinamentoKNN(5)
            medidaP()      


