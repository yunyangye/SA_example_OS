# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 22:04:20 2018

@author: yunyangye
"""
from SALib.analyze import morris
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
    
    Mu = []
    Sigma = []
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
            Si = morris.analyze(problem,np.array(X_clim),np.array(Y_clim),conf_level=0.95,print_to_console=True,num_levels=4,grid_jump=2)
            
            mu_clim = Si['mu_star']
            sigma_clim = Si['sigma']
            name_clim = Si['names']
        
            Mu.append(mu_clim)
            Sigma.append(sigma_clim)
            Name.append(name_clim)
            Clim.append(x)
    
    return Clim,Name,Mu,Sigma
