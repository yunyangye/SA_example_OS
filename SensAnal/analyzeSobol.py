# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 22:04:20 2018

@author: yunyangye
"""
from SALib.analyze import sobol
import numpy as np

######################################################
#conduct sensitivity analysis
######################################################
#model_results is the output from the parallelSimu.py
##[[climate,values of parameters,source EUI,site EUI]]
#Problem is the output from the sampleMORRIS.py for all the climate zones
def sensiAnal(model_results,Problem):
    weather = []
    X = []
    Y = []
    for row in model_results:
        weather.append(row[0])
        X.append(row[1:len(row)-2])
        Y.append(row[len(row)-1])

    climate = ['1A','2A','2B','3A','3B','3C','4A','4B','4C','5A','5B','6A','6B','7A','8A']
    
    S1 = []#first-order indices
    S1_conf = []#confidence of first-order indices
    ST = []#total-order indices
    ST_conf = []#confidence of total-order indices
    Name = []
    Clim = []
    
    for x in climate:
        X_clim = []
        Y_clim = []
        for ind,val in enumerate(weather):
            if val == x:
                X_clim.append(X[ind])
                Y_clim.append(Y[ind])
        for row in Problem:
            if row[0] == x:
                problem = row[1]
        if len(X_clim) > 0:
            Si = sobol.analyze(problem,np.array(Y_clim),print_to_console=False)
            
            s1_clim = Si['S1']
            s1_conf_clim = Si['S1_conf']
            st_clim = Si['ST']
            st_conf_clim = Si['ST_conf']
            name_clim = problem['names']
        
            S1.append(s1_clim)
            S1_conf.append(s1_conf_clim)
            ST.append(st_clim)
            ST_conf.append(st_conf_clim)
            Name.append(name_clim)
            Clim.append(x)
    
    return Clim,Name,S1,S1_conf,ST,ST_conf
