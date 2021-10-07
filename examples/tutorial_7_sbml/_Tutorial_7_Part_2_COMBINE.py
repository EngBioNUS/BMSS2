# -*- coding: utf-8 -*-
"""
This tutorial shows the functions to generate COMBINE Omex files.

Features:
-to generate OMEX files from model database
-execute omex file from file location
"""
import setup_bmss as lab
import BMSS.sbml  as sb

if __name__ == '__main__':
    
    '''
    Use database_to_combine to create a COMBINE archive from an existing model in database.
    '''
    system_type     = "BMSS, ConstantInduction, Inducible" #Enter model name
    settings_name   = "__default__" #usually "__default__" by default
    Plot_Variable   = ["m", "p"] #, "rmq"] #Assign which variables you would like to plot
    #Define which KISAO algorithm to use for tspan, write "0" if to use default CVODE
    
    combinefilelist = sb.database_to_combine(system_type, settings_name, Plot_Variable, KISAO_algorithm='0')
    
    
    #This part may not work depending your version of Python
    combinefile     = combinefilelist[0]
    
    
    
