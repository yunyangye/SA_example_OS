   # -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 10:50:32 2017

@author: yunyangye
"""
import shutil as st
import os
import multiprocessing as mp
import time
import information as inf
import readEnergyUse as rene
import replace as rp
import delete as dt
import math
import csv

######################################################
#run models and get the results in parallel
######################################################

######################################################
#run models
######################################################
#climate is the climate zone; weather file name is [climate].epw and baseline model file name is CZ[climate].osm
#param_values is the name of measures, name of arguments and values are used in each case (two-dimension list)
#num_model is the NO. of the model
#round_num is the number of the round times
def runModel(climate,param_values,num_model,round_num,output):    
    #copy source folder and rename the new name
    st.copytree('./sourceFolder','./'+str(num_model))

    #change the weather_file and seed_file in compact.osw
    weather_file = climate + '.epw'
    seed_file = 'CZ' + climate + '.osm'
    
    with open('./'+str(num_model)+'/compact.osw', "r") as f:
        page = f.read()
    
    old_weather = inf.getValue1('weather_file',page)
    rp.replace1('./'+str(num_model)+'/compact.osw',old_weather,weather_file)

    old_seed = inf.getValue1('seed_file',page)
    rp.replace1('./'+str(num_model)+'/compact.osw',old_seed,seed_file)

    #delete the measures' information that is not used in the work
    name_meas = []
    for row in param_values:
        if row[0] not in name_meas:
            name_meas.append(row[0])
    dt.delete('./'+str(num_model)+'/compact.osw',name_meas)
    
    #change the values in the existing sebi.osw based on measure
    for row in param_values:
        value = inf.getValue2(row[0],row[1],page)
        rp.replace2('./'+str(num_model)+'/compact.osw',str(value),str(row[2]),row[0],row[1])
    
    #run the models
    #'/usr/bin/openstudio': path of the software
    os.system("'/usr/bin/openstudio' run -w './"+str(num_model)+"/compact.osw'")

    #get the results
    #output data
    output_data = [num_model,climate]
    for row in param_values:
        output_data.append(row[2])

    #source eui and site eui
    total_site, total_source, total_area = rene.readEnergyUse(num_model)
    output_data.append(total_source/total_area*1000.0/11.35653)
    output_data.append(total_site/total_area*1000.0/11.35653)
    #Unit: MJ/m2
    #[record_model,source_EUI,site_EUI]
    
    #record the data in the './results/energy_data.csv'
    with open('./results/energy_data_'+str(round_num)+'.csv', 'a') as csvfile:
        energy_data = csv.writer(csvfile, delimiter=',')
        energy_data.writerow(output_data)

    #record the error in the './results/error.csv'
    if total_area < 0:
        with open('./results/error.csv', 'a') as csvfile:
            error = csv.writer(csvfile, delimiter=',')
            error.writerow(output_data)

    output.put(output_data)
    
    #delete the folder
    st.rmtree('./'+str(num_model))

######################################################
#run models in parallel for sensitivity analysis
######################################################
#Climate is the list of climate zone; weather file name is [climate].epw and baseline model file name is CZ[climate].osm
#round_num is the number of the round times
def parallelSimu(Climate,round_num):
    #record the start time
    start = time.time()
    
    #select the measures
    Measure = []
    Baseline = []
    for x in Climate:       
        measure_name = []
        measure_val = []
        #read the information of measures and samples' values
        with open('./results/samples/data_set_'+str(x)+'.csv', 'rb') as csvfile:
            data1 = csv.reader(csvfile, delimiter=',')
            for row in data1:
                temp = [row[1],row[2]]
                measure_name.append(temp)

        with open('./results/samples/param_values_'+str(x)+'.csv', 'rb') as csvfile:
            data2 = csv.reader(csvfile, delimiter=',')
            for row in data2:
                measure_val.append(row)
        
        #all the measure values are num here
        for row in measure_val:
            measure = []
            for ind,val in enumerate(row):
                temp = []
                temp.append(measure_name[ind][0])
                temp.append(measure_name[ind][1])
                temp.append(float(val))
                measure.append(temp)
            Measure.append(measure)
            Baseline.append(x)
            
    #multi-processing
    output = mp.Queue()
    processes = [mp.Process(target=runModel,args=(Baseline[i],Measure[i],i+1,round_num,output)) for i in range(len(Baseline))]

    #count the number of cpu
    cpu = mp.cpu_count()#record the results including inputs and outputs
    print cpu
    
    model_results = []
    
    run_times = math.floor(len(processes)/cpu)
    if run_times > 0:
        for i in range(int(run_times)):
            for p in processes[i*int(cpu):(i+1)*int(cpu)]:
                p.start()
            
            for p in processes[i*int(cpu):(i+1)*int(cpu)]:
                p.join()
    
            #get the outputs
            temp = [output.get() for p in processes[i*int(cpu):(i+1)*int(cpu)]]
            
            for x in temp:
                model_results.append(x)
    
    for p in processes[int(run_times)*int(cpu):len(processes)]:
        p.start()
            
    for p in processes[int(run_times)*int(cpu):len(processes)]:
        p.join()    
        
    #get the outputs
    temp = [output.get() for p in processes[int(run_times)*int(cpu):len(processes)]]
    for x in temp:
        model_results.append(x)
            
    #record the end time
    end = time.time()
    
    return model_results,end-start

