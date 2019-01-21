# -*- coding: utf-8 -*-
"""
Created on Sat Apr 21 12:21:16 2018

@author: yunyangye
"""
import numpy as np
from tempfile import mkstemp
from shutil import move
from os import remove, close

######################################################
#delete the contents
######################################################

######################################################
#delete the contents of measures
######################################################
#file_path: the file path
#name_meas: the names of the measures that are selected
def delete(file_path,name_meas):
    #read the data from the measureName.csv
    data = np.genfromtxt('./runModel/measureName.csv',
                         skip_header=1,
                         dtype=str,
                         delimiter=',',
                         usecols = (0))
   
    #check the measures that are not included
    del_meas = []
    for x in data:
       if x not in name_meas:
           del_meas.append(x)

    #delete the measure
    for ind,x in enumerate(del_meas):
        #create temp file
        fh, abs_path = mkstemp()
    
        #identify the lines of the measure
        with open(file_path) as old_file:
            k = 0
            meas_begin = 0
            brac_chec = 1
            for line in old_file:
                if x in line:
                    meas_begin = k

                if meas_begin > 0:
                    if '{' in line:
                        brac_chec += 1
                    if '}' in line:
                        brac_chec -= 1
                    if brac_chec == 0:
                        meas_end = k
                        break
                k += 1

        with open(file_path) as old_file:
            length = 0
            for line in old_file:
                length += 1
        
        #delete the measures that are not included
        with open(abs_path, 'w') as new_file:
            with open(file_path) as old_file:
                #change the values of the measure
                n = 0
                for line in old_file:
                    #copy the information from old file into new one
                    #change old information into new one
                    if meas_end == length-3:
                        if n < meas_begin-2 or n > meas_end:
                            new_file.write(line)
                        elif n == meas_begin-2:
                            new_file.write(line.replace('},', '}'))
                    else:   
                        if n < meas_begin-1 or n > meas_end:
                            new_file.write(line)
                    n += 1 
    
        close(fh)
        #remove original file from the file path
        remove(file_path)
        #move new file into the file path
        move(abs_path,file_path)
