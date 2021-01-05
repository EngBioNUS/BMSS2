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


'''To generate SBML files from model database.'''
sbmlgen.database_to_sbml()


'''To generate SBML files from a list of configuration files.'''
files = ['bmss42.ini', 'CellModel_CellularResources_ProteomeAllocation_RibosomeLimitation.ini']
sbmlgen.config_to_sbml(files)


'''To autogenerate SBML files for all .ini files stored inside the ConfigSBML folder.'''
inputpath = (Path.cwd()/'ConfigSBML')
print(inputpath)
sbmlgen.autogenerate_sbml_from_folder(inputpath)



