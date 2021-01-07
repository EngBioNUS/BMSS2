# -*- coding: utf-8 -*-
"""
This tutorial shows the functions to generate SBML standard files.

Features:
-to generate SBML files from model database
-to generate SBML .xml files from a list of configuration files
-to autogenerate SBML .xml files for all configuration files contained inside a folder path  
"""

from pathlib import Path

import setup_bmss as lab
import BMSS.standardfiles_generators.sbmlgen as sbmlgen

'''
Use database_to_sbml to generate SBML files from model database.
Running only the function will bring up 2 prompts. The first prompt indicates 
which model you would like to generate the SBML file. If there are model settings 
available, the second prompt indicates which setting you would like to use to 
generate the SBML file.
'''
sbmlgen.database_to_sbml()


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



