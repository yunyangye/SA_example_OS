# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 15:00:04 2018

@author: yunyangye
"""
from SALib.sample import fast_sampler
import numpy as np

#################################################
#this package aims to sample the models to serve for the SA
##Morris
#################################################

#num is the number of the samples
#cz is climate zone
def sampleFAST(num,cz):
    #read the variable table, "variable"
    data_set_temp = np.genfromtxt('./variable.csv',
                                  skip_header=1,
                                  dtype=str,
                                  delimiter=',')

    #generate the data set under cz
    climate = ['1A','2A','2B','3A','3B','3C','4A','4B','4C','5A','5B','6A','6B','7A','8A']
    ind = climate.index(cz)
    data_set = []
    k = 1
    for row in data_set_temp:
        temp = [str(k)]
        temp.append(row[0])#the measure's name
        temp.append(row[1])#the argument's name
        temp.append(float(row[ind+2]))#the minimum value
        temp.append(float(row[ind+19]))#the maximum value
        data_set.append(temp)
        k += 1

    names = []
    bounds = []
    for row in data_set:
        names.append(row[0])
        temp = []
        temp.append(row[3])
        temp.append(row[4])
        bounds.append(temp)
    
    #set the variables and ranges of variables
    problem = {
        'num_vars': len(data_set),
        'names': names,
        'bounds': bounds
    }

    #select the samples
    param_values = fast_sampler.sample(problem, num)
    
    return data_set,problem,param_values
