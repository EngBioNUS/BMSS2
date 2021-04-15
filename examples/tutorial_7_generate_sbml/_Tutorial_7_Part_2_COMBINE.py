# -*- coding: utf-8 -*-
"""
This tutorial shows the functions to generate COMBINE Omex files.

Features:
-to generate OMEX files from model database
-execute omex file from file location
"""

from pathlib import Path

import setup_bmss as lab
import BMSS.standardfiles_generators.combinegen as combinegen
import BMSS.models.model_handler as mh
import BMSS.models.settings_handler as sh
import tellurium as te
import matplotlib.pyplot as plt

plt.close('all')

if __name__ == '__main__':

    outputpath = (Path.cwd())
    #Where the COMBINE file will be outputed to, working directory by default
    print(outputpath)
    
    
    
    '''
    Use the following section to add model to database from config file.
    '''
    filename = "TestModel_Repressilator_OMEX_example.ini"
    
    #Add model to database and view all the models in the database
    system_type = mh.config_to_database(filename)
    lst = mh.list_models()
    print(lst)
    
    #Add settings to database and view all the settings in the database
    system_types_settings_names = sh.config_to_database(filename)
    lst_setting = sh.list_settings()
    print(lst_setting)
    
    
    
    
    '''
    Use database_to_combine to create a COMBINE archive from an existing model in database.
    '''
    model_name = "Test_Model, OMEX, Repressilator, Example" #Enter model name
    settings_name = "__default__" #usually "__default__" by default
    Plot_Variable = ["X", "Y", "Z"] #, "rmq"] #Assign which variables you would like to plot
    KISAO_algorithm = "0"
    #Define which KISAO algorithm to use for tspan, write "0" if to use default CVODE
    
    
    combinegen.database_to_combine(model_name, settings_name, Plot_Variable, outputpath, KISAO_algorithm)

    
    
    
    
    
    
    '''
    Use the following function to execute the COMBINE archive
    ''' 
    COMBINEfilelocation = str(Path.cwd()/'COMBINE_Test_Model_Repressilator_OMEX_Example.omex')
    #Autoexecute omex file from file location. Path set to where this python script is saved.
    
    #Use this to choose which COMBINE Archive to execute
    te.convertAndExecuteCombineArchive(COMBINEfilelocation) 
    
    
