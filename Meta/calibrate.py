# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 19:24:33 2018

@author: yunyangye
"""
import numpy as np
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error
from sklearn.cross_validation import train_test_split
import csv

#################################################
# this package is used to train and test meta models,
# and then select the best solution
#################################################

# X is the data set of variables (inputs)
# y is the data set of the energy data (output)
# X_brute is the new sample set (inputs)
# y_best is the target output value
# kernel is the kernel: 'rbf', 'linear', 'poly', 'sigmoid'
def meta_svr(X,y,X_sample,kernel):
    # split the training set and testing set
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    # train the meta model
    svr = SVR(kernel=kernel)
    
    svr.fit(X_train,y_train)
    
    # test the meta model
    pred_SVR = svr.predict(X_test)
    
    result = []
    for ind,val in enumerate(y_test):
        result.append([val,pred_SVR[ind]])
    with open('./results/meta_results_'+kernel+'.csv', 'a') as csvfile:
        data = csv.writer(csvfile, delimiter=',')
        for row in result:
            data.writerow(row)
    
    y_test_num = []
    for y in y_test:
        y_test_num.append(float(y))
        
    # calculate the Mean Squared Error
    mse = mean_squared_error(y_test_num, pred_SVR)
    
    # generate the output set of brute force sample set
    Y_SVR = svr.predict(X_sample)
    
    return Y_SVR, mse

