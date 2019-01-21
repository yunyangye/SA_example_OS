# -*- coding: utf-8 -*-
"""
Created on Tue Sep  5 16:51:07 2017

@author: yunyangye
"""
import os

######################################################
#read the source and site energy uses from reports
######################################################
def readEnergyUse(num_model):
    if os.path.isfile('./'+str(num_model)+'/reports/eplustbl.html'):
        #'./reports/eplustbl.html' is the result file
        with open(r'./'+str(num_model)+'/reports/eplustbl.html', "r") as f:
            page = f.read()
    
######################################################
#Site energy
######################################################
        #get the id of total site energy
        for index,x in enumerate(page):
            if page[index:index+22] == "Total Site Energy</td>":
                id_site_energy = index + 22
                break
    
        #read the data of total site energy
        for i in range(0,1000):
            if page[id_site_energy+i:id_site_energy+i+3] == "/td":
                last_value_site = id_site_energy+i-2
                break
    
        total_site = float(str(page[last_value_site]))*0.01
        total_site += float(str(page[last_value_site-1]))*0.1
        
        for i in range(0,8):
            if page[last_value_site-3-i] != " ":
                total_site += float(str(page[last_value_site-3-i]))*10**i

######################################################
#Source energy
######################################################
        #get the id of total source energy
        for index,x in enumerate(page):
            if page[index:index+24] == "Total Source Energy</td>":
                id_source_energy = index + 24
                break
    
        #read the data of total site energy
        for i in range(0,1000):
            if page[id_source_energy+i:id_source_energy+i+3] == "/td":
                last_value_source = id_source_energy+i-2
                break
    
        total_source = float(str(page[last_value_source]))*0.01
        total_source += float(str(page[last_value_source-1]))*0.1
        
        for i in range(0,8):
            if page[last_value_source-3-i] != " ":
                total_source += float(str(page[last_value_source-3-i]))*10**i

######################################################
#Total building area
######################################################    
        #get the id of total building area
        for index,x in enumerate(page):
            if page[index:index+24] == "Total Building Area</td>":
                id_total_area = index + 24
                break
        
        #read the data of total building area
        for i in range(0,1000):
            if page[id_total_area+i:id_total_area+i+3] == "/td":
                last_value_area = id_total_area+i-2
                break
    
        total_area = float(str(page[last_value_area]))*0.01
        total_area += float(str(page[last_value_area-1]))*0.1
        
        for i in range(0,8):
            if page[last_value_area-3-i] != " ":
                total_area += float(str(page[last_value_area-3-i]))*10**i
    
        #unit of end_use_data is GJ
        #unit of total_area is m2
        return total_site, total_source, total_area

    else:
        return -1, -1, -1
