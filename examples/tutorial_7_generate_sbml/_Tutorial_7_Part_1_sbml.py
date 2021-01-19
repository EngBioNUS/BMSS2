# -*- coding: utf-8 -*-
"""
This tutorial shows the functions to generate SBML standard files.

Features:
-to generate SBML files from model database
-to generate SBML .xml files from a list of configuration files
-to autogenerate SBML .xml files for all configuration files contained inside a folder path  
"""

from pathlib import Path

##import setup_bmss as lab
import BMSS.standardfiles_generators.sbmlgen as sbmlgen
import BMSS.models.model_handler as mh
import BMSS.models.settings_handler as sh

if __name__ == '__main__':
    '''
    Use database_to_sbml to generate SBML file from model database.
    You can view the current models and settings in the database with lst and lst_settings.
    Then, input the model name into the variable; ensure that it is correct word-for-word
    And input the settings name.
    Run sbmlgen.database_to_sbml function
    Use this if you want to only convert from the existing database.
    '''
    
    #Views all the models and settings in the database
    lst = mh.list_models()
    lst_setting = sh.list_settings()
    
    model_name = "TestModel, BMSS, LogicGate, gate, DelayActivationInput2" #Enter model name
    settings_name = "__default__" #usually "__default__" by default
    sbmlgen.database_to_sbml(model_name, settings_name)
    
    
    
    '''
    Use config_to_sbml to generate SBML files from a list of configuration files.
    Running only this function will generate SBML files from single/multiple .ini 
    files. Use this if you want to only convert selected files from the whole folder.
    '''
    
    files = ['TestModel_LogicGate_ORgate_DelayActivation_DelayActivation.ini', 
             'TestModel_CellModel_CellularResources_ProteomeAllocation_RibosomeLimitation.ini']
    sbmlgen.config_to_sbml(files)
    
    
    
    '''
    To autogenerate SBML files for all .ini files stored inside the ConfigSBML folder.
    Running this function will generate the corresponding SBML files for all .ini 
    files stored in ConfigSBML folder. Ensure that all .ini files are in correct 
    format or the function will terminate with error.
    '''
    inputpath = (Path.cwd()/'ConfigSBML')
    print(inputpath)
    sbmlgen.autogenerate_sbml_from_folder(inputpath)
    
    
    
