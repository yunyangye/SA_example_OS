# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 12:38:27 2017

@author: yunyangye
"""
from tempfile import mkstemp
from shutil import move
from os import remove, close

######################################################
#replace the contents of a file from pattern to subst
#used to modify workflow file
######################################################

######################################################
#replace the name of baseline model file and weather file
######################################################
#file_path: the file path
#pattern: the old information needs to be changed
#subst: the new information needs to be added
def replace1(file_path, pattern, subst):
    #create temp file
    fh, abs_path = mkstemp()

    #change weather file name or seed file name
    with open(abs_path, 'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))    

    close(fh)
    #remove original file from the file path
    remove(file_path)
    #move new file into the file path
    move(abs_path,file_path)

######################################################
#replace the value of a measure's argument
######################################################
#file_path: the file path
#pattern: the old information needs to be changed (str)
#subst: the new information needs to be added (str)
#meas: the name of the measure
#argu: the name of argument
def replace2(file_path, pattern, subst, meas, argu):
    #create temp file
    fh, abs_path = mkstemp()
    
    #change the values of measures
    #include the input name in the old and new information 
    pattern = '"'+argu+'": '+pattern
    subst = '"'+argu+'": '+subst

    #identify the beginning of the measure
    with open(file_path) as old_file:                
        k = 0
        record_begin = 0
        for line in old_file:
            if meas in line:
                record_begin = k
            k += 1

    #identify the total number of line of the file
    with open(file_path) as old_file:
        m = 0
        record_end = 0
        num_line = 0
        for line in old_file:
            num_line += 1
        
    #identify the end of the measure
    with open(file_path) as old_file:
        for line in old_file:
            #if the measure is not the last one
            if m > record_begin and 'measure_dir_name' in line:
                record_end = m
                break
            m += 1
            #if the measure is the last one
            if m == num_line:
                record_end = num_line
        
    with open(abs_path, 'w') as new_file:
        with open(file_path) as old_file:
            #change the values of the measure
            n = 0
            for line in old_file:
                #copy the information from old file into new one
                #change old information into new one
                if n < record_begin or n > record_end:
                    new_file.write(line)
                else:
                    new_file.write(line.replace(pattern, subst))
                n += 1

    close(fh)
    #remove original file from the file path
    remove(file_path)
    #move new file into the file path
    move(abs_path,file_path)
