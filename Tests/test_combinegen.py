#!pytest test_combinegen.py -W ignore::DeprecationWarning

import add_BMSS_to_path
import pytest
import tellurium as te, os
import BMSS.standardfiles_generators.combinegen as combinegen
from pathlib import Path
import glob

import BMSS.standardfiles_generators.simplesbml as simplesbml
import BMSS.models.model_handler    as mh
import BMSS.models.settings_handler as sh
import phrasedml


class TestCombinecreator:
    def test_genOMEX(self):
        global model_name
        global KISAO_algorithm
        global Plot_Variable
        global core_model
        outputpath = (Path.cwd())
        model_name = "TestModel, CellModel, CellularResources, ProteomeAllocation, RibosomeLimitation" #Enter model name
        settings_name = "__default__" #usually "__default__" by default
        Plot_Variable = ["r", "a", "p"] #, "rmq"] #Assign which variables you would like to plot
        KISAO_algorithm = "kisao.0000071"
        #Define which KISAO algorithm to use for tspan, write "0" if to use default CVODE
        
        search_result_settings = sh.search_database(model_name, settings_name)
        search_result_model = mh.quick_search(model_name)
        core_model = search_result_model
        settings = search_result_settings[0]
        
        
        combinegen.database_to_combine(model_name, settings_name, Plot_Variable, outputpath, KISAO_algorithm)
        return
    
    
    def test_KISAOalgorithmchecker(self):
        #Test if KISAO algorithm declared is accepted by tellurium
        #Checker is called in beginning of database_to_combine 
        global KISAO_algorithm
        combinegen.KISAOchecker(KISAO_algorithm)
        
    def test_KISAOalgorithmchecker_fail(self):
        #Test if KISAO algorithm declared is accepted by tellurium
        #Checker is called in beginning of database_to_combine 
        KISAO_algorithm_fail = "kisao.0000000"
        
        combinegen.KISAOchecker(KISAO_algorithm_fail)
        
    
    def test_outputOMEX(self):
        #Test if OMEX was output correctly
        global model_name
        filename = model_name.replace(", ", "_")
        filename = 'COMBINE_' + filename + '.omex'
        if os.path.exists(filename) == False:
            raise IOError("File did not output properly")
        return
    
    def test_outputOMEX_fail(self):
        #OMEX file does not exist
        global model_name
        filename = model_name.replace(", ", "_")
        filename = 'COMBINE_fail_' + filename + '.omex'
        if os.path.exists(filename) == False:
            raise IOError("File did not output properly")
        return
    
    def test_plotvariablechecker(self):
        #Test if plot variable declared is in the species
        #Checker is called in beginning of database_to_combine
        global core_model
        Plot_Variable = ["r", "a", "p"]
        combinegen.plotvariablechecker(Plot_Variable, core_model)
        return
    
    def test_plotvariablechecker_fail_1(self):
        #Test if plot variable declared is in the species
        #None of the variables exist in the model
        #Checker is called in beginning of database_to_combine
        global core_model
        Plot_Variable = ["z", "y", "x"]
        combinegen.plotvariablechecker(Plot_Variable, core_model)
        return
    
    def test_plotvariablechecker_fail_2(self):
        #No Plot Variable was declared
        #Checker is called in beginning of database_to_combine
        global core_model
        Plot_Variable = []
        combinegen.plotvariablechecker(Plot_Variable, core_model)
        return
            
if __name__ == '__main__':
    t = TestCombinecreator()
    #Run if model not yet added to database
    filename = "TestModel_CellModel_CellularResources_ProteomeAllocation_RibosomeLimitation_2.ini"
    system_type = mh.config_to_database(filename)
    system_types_settings_names = sh.config_to_database(filename)
    search_result_settings = sh.search_database(system_type, "__default__")
    search_result_model = mh.quick_search(system_type)
    core_model = search_result_model
    settings = search_result_settings[0]
    t.test_genOMEX()