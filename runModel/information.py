# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 18:02:14 2017

@author: yunyangye
"""
######################################################
#get the information from existing .osw file
######################################################

######################################################
#be used to get the names of baseline model and weather file
######################################################
#text is the name of item
#page is content of file
def getValue1(text,page):
    n = len(text)
    #find text
    k = 0
    for index,x in enumerate(page):
        if page[index:index+n] == text:
            k = index+n
        
        #get the first char's index of information
        first_char = 0
        for i in range(k+1, k+1000):
            if page[i] == '"':
                first_char = i+1
                break
        
        #get the last char's index of information
        last_char = 0
        for i in range(first_char, first_char+1000):
            if page[i] == '"':
                last_char = i-1
                break

    #get the existing value of text
    return page[first_char:last_char+1]

######################################################
#be used to get the values of measures
######################################################
#text_meas is the name of measure
#text_argu is the name of argument
#page is content of file
def getValue2(text_meas,text_argu,page):
    #identify the beginning of the measure
    l_mes = len(text_meas)#length of measure
    j = 0#beginning of the measure
    for index,x in enumerate(page):
        if page[index:index+l_mes] == text_meas:
            j = index+l_mes
                
    #identify the last char's index of item
    n = len(text_argu)#length of argument name
    k = 0#the end of the argument name
    for index,x in enumerate(page):
        if index > j:
            if page[index:index+n] == text_argu:
                k = index+n
                break
        
    #get the first char's index of information
    first_char = 0
    for i in range(k+1, k+1000):
        if page[i] == ':':
            first_char = i+2
            break
        
    #get the last char's index of information
    last_char = 0
    for i in range(first_char, first_char+1000):
        if page[i] == '}' or page[i] == '\t' or page[i] == '\n' or page[i] == ',':
            last_char = i-1
            break
  
    #get the information    
    return page[first_char:last_char+1]
