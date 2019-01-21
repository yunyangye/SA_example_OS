# -*- coding: utf-8 -*-
"""
Created on Sun Jun  3 22:45:50 2018

@author: yunyangye
"""
import os
import csv
import numpy as np

pathway = os.getcwd()
###############################################################################
# inputs' summary
## list all the inputs which need to be inserted
###############################################################################

# define the climate zones that need to be considered
climate = ['1A','2A','2B','3A','3B','3C','4A','4B','4C','5A','5B','6A','6B','7A','8A']# define the needed climate zones

# number of samples for training and testing meta-models
num_sample = 100#number of samples in each climate zone = num_sample * number of sensitive model inputs

# kernel of meta model (options: 'rbf','linear','poly','sigmoid')
kernel = 'linear'

# sensitivity analysis inputs
## Morris
mo_num_sample = 200# number of the samples for each parameter [final #samples: num*(#parameters+1)]
mo_num_levels_sample = 8# the number of grid levels
mo_grid_jump_sample = 4# the grid jump size

## FAST
fa_num_sample = 1000# Sample size N > 4M^2 is required. M=4 by default

## Sobol
so_num_sample = 1000# Sample size N > 4M^2 is required. M=4 by default

## Non-parametric analysis (CompModSA)
np_num_sample = 10000# LHS sample size

###############################################################################
# parameters' library
## list the entire sets of some inputs
###############################################################################
climate_lib = ['1A','2A','2B','3A','3B','3C','4A','4B','4C','5A','5B','6A','6B','7A','8A']

###############################################################################
# meta-models
## sampling
## run models
## train and test meta-models
###############################################################################

# sampling (lhs)
os.chdir(os.path.join(pathway,'Meta'))
import sampleMeta as samp
os.chdir(pathway)

for cz in climate:
    data_set,param_values = samp.sampleMeta(num_sample,cz)
    ## record the data in the folder './results/samples'
    ## store the information of data_set
    with open('./results/samples/data_set_'+str(cz)+'.csv', 'wb') as csvfile:
        for row in data_set:
            data = csv.writer(csvfile, delimiter=',')
            data.writerow(row)
    
    ## store the information of param_values
    with open('./results/samples/param_values_'+str(cz)+'.csv', 'wb') as csvfile:
        for row in param_values:
            data = csv.writer(csvfile, delimiter=',')
            data.writerow(row)

# run the models
os.chdir(os.path.join(pathway,'runModel'))
import parallelSimuMeta as ps
os.chdir(pathway)

model_results,run_time = ps.parallelSimu(climate,1)

print run_time

###############################################################################
# sensitivity analysis
## method description

#### 1-Morris:
###### sample: from SALib.sample import morris
###### analyze: from SALib.analyze import morris

#### 2-FAST:
###### sample: from SALib.sample import fast_sampler
###### analyze: from SALib.analyze import fast

#### 3-Sobol:
###### sample: from SALib.sample import saltelli
###### analyze: from SALib.analyze import sobol

#### 4-Non-parametric analysis (CompModSA):
###### sample: Latin Hypercube Sampling (LHS)
###### analyze: check the type of relationship:
###### LIN_REG: Linear Regression
###### RS_REG: Response Surface Regression
###### GAM: Generalized Additive Models
###### RP_REG: Recursive Partitioning Regression

###############################################################################

##########
# Morris #
##########
# sample (Morris)
os.chdir(os.path.join(pathway,'SensAnal'))
import sampleMORRIS as sm
os.chdir(pathway)

for cz in climate:
    mo_data_set,mo_problem,mo_param_values = sm.sampleMORRIS(mo_num_sample,mo_num_levels_sample,mo_grid_jump_sample,cz)
    ## record the data in the folder './results/sensitive'
    ## store the information of data_set
    with open('./results/sensitive/mo_data_set_'+str(cz)+'.csv', 'wb') as csvfile:
        for row in mo_data_set:
            mo_data = csv.writer(csvfile, delimiter=',')
            mo_data.writerow(row)

    ## store the information of param_values
    with open('./results/sensitive/mo_param_values_'+str(cz)+'.csv', 'wb') as csvfile:
        for row in mo_param_values:
            mo_data = csv.writer(csvfile, delimiter=',')
            mo_data.writerow(row)

# run the model (Morris)
## generate meta model
os.chdir(os.path.join(pathway,'Meta'))
import calibrate as cali
os.chdir(pathway)

## get the inputs and outputs of samples
sample_results = []
with open('./results/energy_data_1.csv', 'rb') as csvfile:
    data = csv.reader(csvfile, delimiter=',')
    for row in data:
        sample_results.append(row)

## get the possible sensitive inputs
variables = []
with open('./variable.csv', 'rb') as csvfile:
    data = csv.reader(csvfile, delimiter=',')
    for ind,row in enumerate(data):
        if ind > 0:
            variables.append(row[0:2])

print 'complete to read the data'

for cz in climate:
    ## get the model results
    X_climate = []# model inputs
    y_climate = []# site EUI
    for row in sample_results:
        if row[1] == cz:
            temp = []
            for i in range(2,len(row)-2):
                temp.append(float(row[i]))
            X_climate.append(temp)
            y_climate.append(float(row[len(row)-1]))
    
    ## get the new sample set (inputs)
    param_values = []
    with open('./results/sensitive/mo_param_values_'+str(cz)+'.csv', 'rb') as csvfile:
        param_data = csv.reader(csvfile,delimiter=',')
        for row in param_data:
            temp = []
            for x in row:
                temp.append(float(x))
            param_values.append(temp)
    
    print cz
    print 'complete to get the new sample set'
    
    ## train the data by using meta models
    y_climate_SVR, mse_climate = cali.meta_svr(X_climate,y_climate,param_values,kernel)
    
    print 'MSE_'+cz
    print mse_climate
    print 'complete to get the meta model output'
    
    ## record mse
    with open('./results/mse.csv', 'a') as csvfile:
        mo_data = csv.writer(csvfile, delimiter=',')
        mo_data.writerow([cz,'MO',mse_climate])

    ## record the results
    mo_resu = []
    k = 1
    for ind in range(len(param_values)):
        temp = []
        temp.append(k)
        temp.append(cz)
        for x in param_values[ind]:
            temp.append(x)
        temp.append(0)
        temp.append(y_climate_SVR[ind])
        mo_resu.append(temp)
        k += 1
        
    with open('./results/energy_data_mo_1.csv', 'a') as csvfile:
        for row in mo_resu:
            mo_data = csv.writer(csvfile, delimiter=',')
            mo_data.writerow(row)

# analyze (Morris)
os.chdir(os.path.join(pathway,'SensAnal'))
import analyzeMORRIS as am
os.chdir(pathway)

## get information of energy_sa
mo_temp_energy = []
with open('./results/energy_data_mo_1.csv', 'rb') as csvfile:
    mo_data = csv.reader(csvfile, delimiter=',')
    for row in mo_data:
        mo_temp_energy.append(row)

mo_energy_sa = []
for row in mo_temp_energy:
    mo_temp = []
    mo_temp.append(row[1])
    for x in row[2:]:
        mo_temp.append(float(x))
    mo_energy_sa.append(mo_temp)

## get information of Problem
mo_data_set_temp = np.genfromtxt('./variable.csv',
                                 skip_header=1,
                                 dtype=str,
                                 delimiter=',')

mo_Problem = []
for cz in climate:
    ind = climate_lib.index(cz)
    mo_data_set = []
    k = 1
    for row in mo_data_set_temp:
        mo_temp = [str(k)]
        mo_temp.append(row[0])# the measure's name
        mo_temp.append(row[1])# the argument's name
        mo_temp.append(float(row[ind+2]))# the minimum value
        mo_temp.append(float(row[ind+19]))# the maximum value
        mo_data_set.append(mo_temp)
        k += 1
    
    mo_names = []
    mo_bounds = []
    for row in mo_data_set:
        mo_names.append(row[0])
        mo_temp = []
        mo_temp.append(row[3])
        mo_temp.append(row[4])
        mo_bounds.append(mo_temp)
        
    ## set the variables and ranges of variables
    mo_problem = {
        'num_vars': len(mo_data_set),
        'names': mo_names,
        'bounds': mo_bounds
    }
    
    mo_Problem.append([cz,mo_problem])

print mo_energy_sa
print mo_Problem
mo_Clim,mo_Name,mo_Mu,mo_Sigma = am.sensiAnal(mo_energy_sa,mo_Problem)

## record the results into sensitivity_mo.csv
mo_arg_name = np.genfromtxt('./variable.csv',
                            skip_header=1,
                            dtype=str,
                            delimiter=',',
                            usecols=(0,1))
print mo_arg_name
mo_sensitivity = []
for ind,row in enumerate(mo_Name):
    for ind1,x in enumerate(row):
        mo_temp = []
        mo_temp.append(mo_Clim[ind])
        mo_temp.append(mo_arg_name[int(x)-1][0])
        mo_temp.append(mo_arg_name[int(x)-1][1])
        mo_temp.append(mo_Mu[ind][ind1])
        mo_temp.append(mo_Sigma[ind][ind1])
        mo_sensitivity.append(mo_temp)

with open('./results/sensitive/sensitivity_mo.csv', 'wb') as csvfile:
    for row in mo_sensitivity:
        
        mo_data = csv.writer(csvfile, delimiter=',')
        mo_data.writerow(row)

########
# FAST #
########

# sample (FAST)
os.chdir(os.path.join(pathway,'SensAnal'))
import sampleFAST as sf
os.chdir(pathway)

for cz in climate:
    fa_data_set,fa_problem,fa_param_values = sf.sampleFAST(fa_num_sample,cz)
    ## record the data in the folder './results/sensitive'
    ## store the information of data_set
    with open('./results/sensitive/fa_data_set_'+str(cz)+'.csv', 'wb') as csvfile:
        for row in fa_data_set:
            fa_data = csv.writer(csvfile, delimiter=',')
            fa_data.writerow(row)

    ## store the information of param_values
    with open('./results/sensitive/fa_param_values_'+str(cz)+'.csv', 'wb') as csvfile:
        for row in fa_param_values:
            fa_data = csv.writer(csvfile, delimiter=',')
            fa_data.writerow(row)

# run the models (FAST)
## generate meta model
os.chdir(os.path.join(pathway,'Meta'))
import calibrate as cali
os.chdir(pathway)

## get the inputs and outputs of samples
sample_results = []
with open('./results/energy_data_1.csv', 'rb') as csvfile:
    data = csv.reader(csvfile, delimiter=',')
    for row in data:
        sample_results.append(row)

## get the possible sensitive inputs
variables = []
with open('./variable.csv', 'rb') as csvfile:
    data = csv.reader(csvfile, delimiter=',')
    for ind,row in enumerate(data):
        if ind > 0:
            variables.append(row[0:2])

print 'complete to read the data'

for cz in climate:
    ## get the model results
    X_climate = []# model inputs
    y_climate = []# site EUI
    for row in sample_results:
        if row[1] == cz:
            temp = []
            for i in range(2,len(row)-2):
                temp.append(float(row[i]))
            X_climate.append(temp)
            y_climate.append(float(row[len(row)-1]))
    
    ## get the new sample set (inputs)
    param_values = []
    with open('./results/sensitive/fa_param_values_'+str(cz)+'.csv', 'rb') as csvfile:
        param_data = csv.reader(csvfile,delimiter=',')
        for row in param_data:
            temp = []
            for x in row:
                temp.append(float(x))
            param_values.append(temp)
    
    print cz
    print 'complete to get the new sample set'
    
    ## train the data by using meta models
    y_climate_SVR, mse_climate = cali.meta_svr(X_climate,y_climate,param_values,kernel)
    
    print 'MSE_'+cz
    print mse_climate
    print 'complete to get the meta model output'
    
    ## record mse
    with open('./results/mse.csv', 'a') as csvfile:
        fa_data = csv.writer(csvfile, delimiter=',')
        fa_data.writerow([cz,'FA',mse_climate])

    ## record the results
    fa_resu = []
    k = 1
    for ind in range(len(param_values)):
        temp = []
        temp.append(k)
        temp.append(cz)
        for x in param_values[ind]:
            temp.append(x)
        temp.append(0)
        temp.append(y_climate_SVR[ind])
        fa_resu.append(temp)
        k += 1
        
    with open('./results/energy_data_fa_1.csv', 'a') as csvfile:
        for row in fa_resu:
            fa_data = csv.writer(csvfile, delimiter=',')
            fa_data.writerow(row)

# analyze (FAST)
os.chdir(os.path.join(pathway,'SensAnal'))
import analyzeFAST as af
os.chdir(pathway)

## get information of energy_sa
fa_temp_energy = []
with open('./results/energy_data_fa_1.csv', 'rb') as csvfile:
    fa_data = csv.reader(csvfile, delimiter=',')
    for row in fa_data:
        fa_temp_energy.append(row)

fa_energy_sa = []
for row in fa_temp_energy:
    fa_temp = []
    fa_temp.append(row[1])
    for x in row[2:]:
        fa_temp.append(float(x))
    fa_energy_sa.append(fa_temp)

## get information of Problem
fa_data_set_temp = np.genfromtxt('./variable.csv',
                                 skip_header=1,
                                 dtype=str,
                                 delimiter=',')

fa_Problem = []
for cz in climate:
    ind = climate_lib.index(cz)
    fa_data_set = []
    k = 1
    for row in fa_data_set_temp:
        fa_temp = [str(k)]
        fa_temp.append(row[0])# the measure's name
        fa_temp.append(row[1])# the argument's name
        fa_temp.append(float(row[ind+2]))# the minimum value
        fa_temp.append(float(row[ind+19]))# the maximum value
        fa_data_set.append(fa_temp)
        k += 1
    
    fa_names = []
    fa_bounds = []
    for row in fa_data_set:
        fa_names.append(row[0])
        fa_temp = []
        fa_temp.append(row[3])
        fa_temp.append(row[4])
        fa_bounds.append(fa_temp)
        
    ## set the variables and ranges of variables
    fa_problem = {
        'num_vars': len(fa_data_set),
        'names': fa_names,
        'bounds': fa_bounds
    }
    
    fa_Problem.append([cz,fa_problem])

print fa_energy_sa
print fa_Problem
fa_Clim,fa_Name,fa_S1,fa_ST = af.sensiAnal(fa_energy_sa,fa_Problem)

fa_S1_list = list(fa_S1)
fa_ST_list = list(fa_ST)

## record the results into sensitivity_fa.csv
fa_arg_name = np.genfromtxt('./variable.csv',
                            skip_header=1,
                            dtype=str,
                            delimiter=',',
                            usecols=(0,1))
print fa_arg_name
fa_sensitivity = []
for ind,row in enumerate(fa_Name):
    for ind1,x in enumerate(row):
        fa_temp = []
        fa_temp.append(fa_Clim[ind])
        fa_temp.append(fa_arg_name[int(x)-1][0])
        fa_temp.append(fa_arg_name[int(x)-1][1])
        fa_temp.append(fa_S1_list[ind][ind1])
        fa_temp.append(fa_ST_list[ind][ind1])
        fa_sensitivity.append(fa_temp)

with open('./results/sensitive/sensitivity_fa.csv', 'wb') as csvfile:
    for row in fa_sensitivity:
        fa_data = csv.writer(csvfile, delimiter=',')
        fa_data.writerow(row)

#########
# Sobol #
#########

# sample (Sobol)
os.chdir(os.path.join(pathway,'SensAnal'))
import sampleSobol as ss
os.chdir(pathway)

for cz in climate:
    so_data_set,so_problem,so_param_values = ss.sampleSobol(so_num_sample,cz)
    ## record the data in the folder './results/sensitive'
    ## store the information of data_set
    with open('./results/sensitive/so_data_set_'+str(cz)+'.csv', 'wb') as csvfile:
        for row in so_data_set:
            so_data = csv.writer(csvfile, delimiter=',')
            so_data.writerow(row)

    ## store the information of param_values
    with open('./results/sensitive/so_param_values_'+str(cz)+'.csv', 'wb') as csvfile:
        for row in so_param_values:
            so_data = csv.writer(csvfile, delimiter=',')
            so_data.writerow(row)

# run the model (Sobol)
## generate meta model
os.chdir(os.path.join(pathway,'Meta'))
import calibrate as cali
os.chdir(pathway)

## get the inputs and outputs of samples
sample_results = []
with open('./results/energy_data_1.csv', 'rb') as csvfile:
    data = csv.reader(csvfile, delimiter=',')
    for row in data:
        sample_results.append(row)

## get the possible sensitive inputs
variables = []
with open('./variable.csv', 'rb') as csvfile:
    data = csv.reader(csvfile, delimiter=',')
    for ind,row in enumerate(data):
        if ind > 0:
            variables.append(row[0:2])

print 'complete to read the data'

for cz in climate:
    ## get the model results
    X_climate = []# model inputs
    y_climate = []# site EUI
    for row in sample_results:
        if row[1] == cz:
            temp = []
            for i in range(2,len(row)-2):
                temp.append(float(row[i]))
            X_climate.append(temp)
            y_climate.append(float(row[len(row)-1]))
    
    ## get the new sample set (inputs)
    param_values = []
    with open('./results/sensitive/so_param_values_'+str(cz)+'.csv', 'rb') as csvfile:
        param_data = csv.reader(csvfile,delimiter=',')
        for row in param_data:
            temp = []
            for x in row:
                temp.append(float(x))
            param_values.append(temp)
    
    print cz
    print 'complete to get the new sample set'
    
    ## train the data by using meta models
    y_climate_SVR, mse_climate = cali.meta_svr(X_climate,y_climate,param_values,kernel)
    
    print 'MSE_'+cz
    print mse_climate
    print 'complete to get the meta model output'
    
    ## record mse
    with open('./results/mse.csv', 'a') as csvfile:
        so_data = csv.writer(csvfile, delimiter=',')
        so_data.writerow([cz,'SO',mse_climate])

    ## record the results
    so_resu = []
    k = 1
    for ind in range(len(param_values)):
        temp = []
        temp.append(k)
        temp.append(cz)
        for x in param_values[ind]:
            temp.append(x)
        temp.append(0)
        temp.append(y_climate_SVR[ind])
        so_resu.append(temp)
        k += 1
        
    with open('./results/energy_data_so_1.csv', 'a') as csvfile:
        for row in so_resu:
            so_data = csv.writer(csvfile, delimiter=',')
            so_data.writerow(row)

# analyze (Sobol)
os.chdir(os.path.join(pathway,'SensAnal'))
import analyzeSobol as aso
os.chdir(pathway)

## get information of energy_sa
so_temp_energy = []
with open('./results/energy_data_so_1.csv', 'rb') as csvfile:
    so_data = csv.reader(csvfile, delimiter=',')
    for row in so_data:
        so_temp_energy.append(row)

so_energy_sa = []
for row in so_temp_energy:
    so_temp = []
    so_temp.append(row[1])
    for x in row[2:]:
        so_temp.append(float(x))
    so_energy_sa.append(so_temp)

## get information of Problem
so_data_set_temp = np.genfromtxt('./variable.csv',
                                 skip_header=1,
                                 dtype=str,
                                 delimiter=',')

so_Problem = []
for cz in climate:
    so_ind = climate_lib.index(cz)
    so_data_set = []
    k = 1
    for row in so_data_set_temp:
        so_temp = [str(k)]
        so_temp.append(row[0])# the measure's name
        so_temp.append(row[1])# the argument's name
        so_temp.append(float(row[so_ind+2]))# the minimum value
        so_temp.append(float(row[so_ind+19]))# the maximum value
        so_data_set.append(so_temp)
        k += 1
    
    so_names = []
    so_bounds = []
    for row in so_data_set:
        so_names.append(row[0])
        so_temp = []
        so_temp.append(row[3])
        so_temp.append(row[4])
        so_bounds.append(so_temp)
        
    ## set the variables and ranges of variables
    so_problem = {
        'num_vars': len(so_data_set),
        'names': so_names,
        'bounds': so_bounds
    }
    
    so_Problem.append([cz,so_problem])

print so_energy_sa
print so_Problem
so_Clim,so_Name,so_S1,so_S1_conf,so_ST,so_ST_conf = aso.sensiAnal(so_energy_sa,so_Problem)

so_S1_list = list(so_S1)
so_S1_conf_list = list(so_S1_conf)
so_ST_list = list(so_ST)
so_ST_conf_list = list(so_ST_conf)

## record the results into sensitivity.csv
so_arg_name = np.genfromtxt('./variable.csv',
                            skip_header=1,
                            dtype=str,
                            delimiter=',',
                            usecols=(0,1))
print so_arg_name
so_sensitivity = []
for ind,row in enumerate(so_Name):
    for ind1,x in enumerate(row):
        so_temp = []
        so_temp.append(so_Clim[ind])
        so_temp.append(so_arg_name[int(x)-1][0])
        so_temp.append(so_arg_name[int(x)-1][1])
        so_temp.append(so_S1_list[ind][ind1])
        so_temp.append(so_S1_conf_list[ind][ind1])
        so_temp.append(so_ST_list[ind][ind1])
        so_temp.append(so_ST_conf_list[ind][ind1])
        so_sensitivity.append(so_temp)

with open('./results/sensitive/sensitivity_so.csv', 'wb') as csvfile:
    for row in so_sensitivity:
        so_data = csv.writer(csvfile, delimiter=',')
        so_data.writerow(row)

#############################
# Non-parametric regression #
#############################

# sample (Non-parametric)
os.chdir(os.path.join(pathway,'SensAnal'))
import sampleNonpara as sn
os.chdir(pathway)

for cz in climate:
    np_data_set,np_problem,np_param_values = sn.sampleNonpara(np_num_sample,cz)
    ## record the data in the folder './results/sensitive'
    ## store the information of data_set
    with open('./results/sensitive/np_data_set_'+str(cz)+'.csv', 'wb') as csvfile:
        for row in np_data_set:
            np_data = csv.writer(csvfile, delimiter=',')
            np_data.writerow(row)

    ## store the information of param_values
    with open('./results/sensitive/np_param_values_'+str(cz)+'.csv', 'wb') as csvfile:
        for row in np_param_values:
            np_data = csv.writer(csvfile, delimiter=',')
            np_data.writerow(row)

# run the models (Non-parametric)
## generate meta model
os.chdir(os.path.join(pathway,'Meta'))
import calibrate as cali
os.chdir(pathway)

## get the inputs and outputs of samples
sample_results = []
with open('./results/energy_data_1.csv', 'rb') as csvfile:
    data = csv.reader(csvfile, delimiter=',')
    for row in data:
        sample_results.append(row)

## get the possible sensitive inputs
variables = []
with open('./variable.csv', 'rb') as csvfile:
    data = csv.reader(csvfile, delimiter=',')
    for ind,row in enumerate(data):
        if ind > 0:
            variables.append(row[0:2])

print 'complete to read the data'

for cz in climate:
    ## get the model results
    X_climate = []# model inputs
    y_climate = []# site EUI
    for row in sample_results:
        if row[1] == cz:
            temp = []
            for i in range(2,len(row)-2):
                temp.append(float(row[i]))
            X_climate.append(temp)
            y_climate.append(float(row[len(row)-1]))
    
    ## get the new sample set (inputs)
    param_values = []
    with open('./results/sensitive/np_param_values_'+str(cz)+'.csv', 'rb') as csvfile:
        param_data = csv.reader(csvfile,delimiter=',')
        for row in param_data:
            temp = []
            for x in row:
                temp.append(float(x))
            param_values.append(temp)
    
    print cz
    print 'complete to get the new sample set'
    
    ## train the data by using meta models
    y_climate_SVR, mse_climate = cali.meta_svr(X_climate,y_climate,param_values,kernel)
    
    print 'MSE_'+cz
    print mse_climate
    print 'complete to get the meta model output'
    
    ## record mse
    with open('./results/mse.csv', 'a') as csvfile:
        np_data = csv.writer(csvfile, delimiter=',')
        np_data.writerow([cz,'NP',mse_climate])

    ## record the results
    np_resu = []
    k = 1
    for ind in range(len(param_values)):
        temp = []
        temp.append(k)
        temp.append(cz)
        for x in param_values[ind]:
            temp.append(x)
        temp.append(0)
        temp.append(y_climate_SVR[ind])
        np_resu.append(temp)
        k += 1
        
    with open('./results/energy_data_np_1.csv', 'a') as csvfile:
        for row in np_resu:
            np_data = csv.writer(csvfile, delimiter=',')
            np_data.writerow(row)

# analyze (Non-parametric)
os.chdir(os.path.join(pathway,'SensAnal'))
import analyzeNonpara as an
os.chdir(pathway)

an.sensiAnal('energy_data_np_1')
