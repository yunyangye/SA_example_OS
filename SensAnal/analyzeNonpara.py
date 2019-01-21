# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 19:43:19 2017

@author: yunyangye
"""
import rpy2.robjects as rbj
import numpy as np
import os

def sensiAnal(result_file_name):
    rscript = '''
    #normalization 0~1
    normalit<-function(m){
      (m - min(m))/(max(m)-min(m))
    }
    
    main <- function(cz,method,result_file_name) {
      #install all the packages that are needed
      #install.packages('corpcor', repos='http://cran.rstudio.com/')
      #install.packages('fields', repos='http://cran.rstudio.com/')
      #install.packages('gam', repos='http://cran.rstudio.com/')
      #install.packages('gbm', repos='http://cran.rstudio.com/')
      #install.packages('locfit', repos='http://cran.rstudio.com/')
      #install.packages('maptree', repos='http://cran.rstudio.com/')
      #install.packages('mda', repos='http://cran.rstudio.com/')
      #install.packages('mlegp', repos='http://cran.rstudio.com/')
      #install.packages('polspline', repos='http://cran.rstudio.com/')
      #install.packages('quadprog', repos='http://cran.rstudio.com/')
      #install.packages('randomForest', repos='http://cran.rstudio.com/')
      #install.packages('spam', repos='http://cran.rstudio.com/')
      #install.packages('tgp', repos='http://cran.rstudio.com/')
      #install.packages('./CompModSA_1.2.tar.gz', repos = NULL, type = 'source')
      
      #load the package CompModSA and related packages
      library('CompModSA', lib.loc='~/R/x86_64-pc-linux-gnu-library/3.3')
      
      path_location <- getwd()
      data <- read.csv(paste(path_location,'/results/',result_file_name,'.csv',sep=""), header=FALSE, sep=",")
      
      #select data
      data1 <- data[data[,2]==cz,3:ncol(data)]
      
      #transfer all values in the matrix into float
      for (row in 1:nrow(data1)) {
        data1[order(as.numeric(row)),]
      }            
      
      #normalization 0~1
      ex.dat <- apply(data1,2,normalit)
      ex.dat[is.nan(ex.dat)] <- 1
      
      #prepare the input and output
      value_1 = ncol(data1)-2
      value_2 = value_1 + 2
      value_3 = ncol(data1)
      
      #select method
      if (method=='LIN_REG') {
        #LIN_REG
        col_data <- c()
        for (i in 1:(ncol(ex.dat)-2)) {
          if (max(ex.dat[,i]) == min(ex.dat[,i])) {
            col_data <- c(col_data, i)
          }
        }
        if (length(col_data)>0) {
          ex.dat1 <- ex.dat[,-col_data]
        } else {
          ex.dat1 <- ex.dat
        }
        value_1_1 = value_1-length(col_data)
        value_2_1 = value_2-length(col_data)
        value_3_1 = value_3-length(col_data)
        file_name <- paste(path_location,'/results/sensitive/SA_LIN_REG_',cz,'.txt',sep="")
        sink(file_name)
        ans.reg <- sensitivity(ex.dat1, x.pos=1:value_1_1, y.pos=value_2_1:value_3_1, surface='reg')
        print(ans.reg)
        sink()
      } else if (method=='RS_REG'){
        #RS_REG
        col_data <- c()
        for (i in 1:(ncol(ex.dat)-2)) {
          if (max(ex.dat[,i]) == min(ex.dat[,i])) {
            col_data <- c(col_data, i)
          }
        }
        if (length(col_data)>0) {
          ex.dat1 <- ex.dat[,-col_data]
        } else {
          ex.dat1 <- ex.dat
        }
        value_1_1 = value_1-length(col_data)
        value_2_1 = value_2-length(col_data)
        value_3_1 = value_3-length(col_data)
        file_name <- paste(path_location,'/results/sensitive/SA_RS_REG_',cz,'.txt',sep="")
        sink(file_name)
        ans.rsreg <- sensitivity(ex.dat, x.pos=1:value_1, y.pos=value_2:value_3, surface='rs.reg')
        print(ans.rsreg)
        sink()
      } else if (method=='GAM') {
        #GAM
        col_data <- c()
        for (i in 1:(ncol(ex.dat)-2)) {
          if (max(ex.dat[,i]) == min(ex.dat[,i])) {
            col_data <- c(col_data, i)
          }
        }
        if (length(col_data)>0) {
          ex.dat1 <- ex.dat[,-col_data]
        } else {
          ex.dat1 <- ex.dat
        }
        value_1_1 = value_1-length(col_data)
        value_2_1 = value_2-length(col_data)
        value_3_1 = value_3-length(col_data)
        file_name <- paste(path_location,'/results/sensitive/SA_GAM_',cz,'.txt',sep="")
        sink(file_name)
        ans.gam <- sensitivity(ex.dat1, x.pos=1:value_1_1, y.pos=value_2_1:value_3_1, surface='mars')
        print(ans.gam)
        sink()
      } else {
        #RP_REG
        col_data <- c()
        for (i in 1:(ncol(ex.dat)-2)) {
          if (max(ex.dat[,i]) == min(ex.dat[,i])) {
            col_data <- c(col_data, i)
          }
        }
        if (length(col_data)>0) {
          ex.dat1 <- ex.dat[,-col_data]
        } else {
          ex.dat1 <- ex.dat
        }
        value_1_1 = value_1-length(col_data)
        value_2_1 = value_2-length(col_data)
        value_3_1 = value_3-length(col_data)
        file_name <- paste(path_location,'/results/sensitive/SA_RP_REG_',cz,'.txt',sep="")
        sink(file_name)
        ans.rpreg <- sensitivity(ex.dat, x.pos=1:value_1, y.pos=value_2:value_3, surface='tree')
        print(ans.rpreg)
        sink()
      }
    }
    '''

    # open the table and check the considered climate zones
    data = np.genfromtxt('results/'+result_file_name+'.csv',
                         skip_header=1,
                         dtype=str,
                         delimiter=',')
    
    climate_req = []
    for row in data:
        if row[1] not in climate_req:
            climate_req.append(row[1])
    
    method_lin_r = "'"+'LIN_REG'+"'"
    method_rs_r = "'"+'RS_REG'+"'"
    method_gam_r = "'"+'GAM'+"'"
    method_rp_r = "'"+'RP_REG'+"'"
    file_name_r = "'"+result_file_name+"'"
    
    for x in climate_req:
        cz_r = "'"+x+"'"
        rscript1 = rscript + '''main(''' + cz_r + ''',''' + method_lin_r + ''',''' + file_name_r + ''')'''
        rscript2 = rscript + '''main(''' + cz_r + ''',''' + method_rs_r + ''',''' + file_name_r + ''')'''
        rscript3 = rscript + '''main(''' + cz_r + ''',''' + method_gam_r + ''',''' + file_name_r + ''')'''
        rscript4 = rscript + '''main(''' + cz_r + ''',''' + method_rp_r + ''',''' + file_name_r + ''')'''
    
        rbj.r(rscript1)
        rbj.r(rscript2)
        rbj.r(rscript3)
        rbj.r(rscript4)
