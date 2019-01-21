# -*- coding: utf-8 -*-
"""
Created on Sun Jun 10 17:34:23 2018

@author: yunyangye
"""
import pyDOE as doe
import numpy as np

#################################################
#this def aims to sample the models to serve for the SA
##Latin Hypercube Sampling
#################################################

#num is the number of the samples
#cz is climate zone
def sampleMeta(num,cz):
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
    num_sens = 0
    for row in data_set_temp:
        temp = [str(k)]
        temp.append(row[0])#the measure's name
        temp.append(row[1])#the argument's name
        temp.append(float(row[ind+2]))#the minimum value
        temp.append(float(row[ind+19]))#the maximum value
        data_set.append(temp)
        num_sens += 1
        k += 1

    #select the samples
    sample_temp = doe.lhs(num_sens, samples=num*num_sens)
    
    param_values = []
    for row1 in sample_temp:
        temp = []
        num_doe = 0
        for row in data_set:
            temp.append((row[4]-row[3])*row1[num_doe]+row[3])
            num_doe += 1
                
        param_values.append(temp)
    
    return data_set,param_values
