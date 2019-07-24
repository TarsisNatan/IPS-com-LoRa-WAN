#Author: Társis Natan Boff da SIlva
#	Utiliza dados obtidos no "programa um" e constroi modelos ML (SVM e KNN) 
# para predição da posição no espaço do end node em relação aos gateways de uma rede LoRa 
# 4 gateways utilizados

import numpy as np
import matplotlib.pyplot as plt
from sklearn import svm
import pandas as pd
from matplotlib import style
from sklearn import datasets, svm, metrics
from sklearn.preprocessing import StandardScaler 
from mpl_toolkits.mplot3d import Axes3D
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.neighbors import KNeighborsClassifier
import pickle

#Array com todas as amostras e classes
data10 = np.loadtxt('10classes.csv', delimiter=";", dtype='int')

# número de amostras
n_amostras = 1000 
# número correspondente a 80% das amostras
n_treino = 800
def svm_():
    global data10, n_amostras, n_treino
    print("Algoritmo SVM")
    #embaralha array
    np.random.shuffle(data10)
    #separa entradas e saídas para treino
    Xtrain = data10[:n_treino, :4]
    ytrain = data10[:n_treino, 4::]
    ytrain = ytrain.ravel()
    #separa entradas e saídas para testes
    Xtest = data10[n_treino:n_amostras, :4]
    ytest = data10[n_treino:n_amostras, 4::]
    ytest = ytest.ravel()
    #aprendizagem e predição do algoritmo
    clf = svm.SVC(kernel="linear")
    clf.fit(Xtrain,ytrain)
    y_pred = clf.predict(Xtest)
    #salva modelo em formato pickle
    with open('SVM_10classes','wb') as f:
        pickle.dump(clf, f)
 
    #resultados
     print("Classification report for classifier %s:\n%s\n"
          % (clf, metrics.classification_report(ytest, y_pred)))

    print("Confusion matrix:\n%s" % metrics.confusion_matrix(ytest, y_pred))
    

def kkn_10classes():
    global data10, n_amostras, n_treino
    print("Algoritmo KNN")
    #embaralha array
    np.random.shuffle(data10)
    #separa entradas e saídas para treino
    Xtrain = data10[:n_treino, :4]
    ytrain = data10[:n_treino, 4::]
    ytrain = ytrain.ravel()
    #separa entradas e saídas para testes
    Xtest = data10[n_treino:n_amostras, :4]
    ytest = data10[n_treino:n_amostras, 4::]
    ytest = ytest.ravel()
    #aprendizagem e predição do algoritmo
    classifier = KNeighborsClassifier(n_neighbors = 5)  
    classifier.fit(Xtrain, ytrain)  
    y_pred = classifier.predict(Xtest)
    #salva modelo em formato pickle
    with open('KNN_10classes','wb') as f:
        pickle.dump(classifier, f)

    #resultados    
    print("Classification report for classifier %s:\n%s\n"
          % (classifier, metrics.classification_report(ytest, y_pred)))

    print("Confusion matrix:\n%s" % metrics.confusion_matrix(ytest, y_pred))

    
    
svm_()
kkn_10classes()
