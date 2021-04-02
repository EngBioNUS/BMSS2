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
<<<<<<< Updated upstream
    filename = "TestModel_CellModel_CellularResources_ProteomeAllocation_RibosomeLimitation_omex.ini"
=======
    filename = "TestModel_Repressilator_OMEX_example.ini"
>>>>>>> Stashed changes
    
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
<<<<<<< Updated upstream
    model_name = "TestModel, CellModel, CellularResources, ProteomeAllocation, RibosomeLimitation, omex" #Enter model name
    settings_name = "__default__" #usually "__default__" by default
    Plot_Variable = ["r", "a", "p"] #, "rmq"] #Assign which variables you would like to plot
    KISAO_algorithm = "kisao.0000433"
=======
    model_name = "Test_Model, Repressilator, OMEX, Example" #Enter model name
    settings_name = "__default__" #usually "__default__" by default
    Plot_Variable = ["X", "Y", "Z"] #, "rmq"] #Assign which variables you would like to plot
    KISAO_algorithm = "0"
>>>>>>> Stashed changes
    #Define which KISAO algorithm to use for tspan, write "0" if to use default CVODE
    
    
    combinegen.database_to_combine(model_name, settings_name, Plot_Variable, outputpath, KISAO_algorithm)

    
    
    
    
    
    
    '''
    Use the following function to execute the COMBINE archive
    ''' 
<<<<<<< Updated upstream
    COMBINEfilelocation = str(Path.cwd()/'COMBINE_TestModel_CellModel_CellularResources_ProteomeAllocation_RibosomeLimitation.omex')
=======
    COMBINEfilelocation = str(Path.cwd()/'COMBINE_Test_Model_Repressilator_OMEX_Example.omex')
>>>>>>> Stashed changes
    #Autoexecute omex file from file location. Path set to where this python script is saved.
    
    #Use this to choose which COMBINE Archive to execute
    te.convertAndExecuteCombineArchive(COMBINEfilelocation) 
    
    
