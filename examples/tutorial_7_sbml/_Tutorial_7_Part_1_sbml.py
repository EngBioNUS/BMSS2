# -*- coding: utf-8 -*-
"""
This tutorial shows the functions to generate SBML standard files.

Features:
-to generate SBML files from model database
-to generate SBML .xml files from a list of configuration files
-to autogenerate SBML .xml files for all configuration files contained inside a folder path  
"""

from pathlib import Path

import setup_bmss                   as lab
import BMSS.sbml                    as sb
import BMSS.models.model_handler    as mh
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
    
    system_type   = "TestModel, BMSS, LogicGate, gate, DelayActivationInput2" #Enter model name
    settings_name = "__default__" #usually "__default__" by default
    output_path   = Path.cwd()
    sbmlfilelist  = sb.database_to_sbml(system_type, settings_name, output_path)
    
    #Read the sbml back in
    sbmlfile    = sbmlfilelist[0]
    output_path = Path.cwd()
    
    sb.sbml_to_config(sbmlfile, system_type, output_path)
    
    
    
    
