import add_BMSS_to_path
import pytest

import matplotlib.pyplot as plt
import numpy             as np
import os
import pandas            as pd
from   numba             import jit
from   pathlib           import Path

'''
Tests for strike-goldd simplified
'''

import BMSS.models.model_handler    as mh
import BMSS.models.settings_handler as sh
import BMSS.models.setup_sg         as ssg
import BMSS.strike_goldd_simplified as sg
import BMSS.models.ia_results       as ir

config_data      = None
user_core_models = None
model_files      = ['Monod_Constitutive_Single.ini']
settings_file_1  = 'settings_sg_1.ini'
settings_file_2  = 'settings_sg_2.ini' #Negative test case

sg_args    = None
variables  = None
sg_results = None

class TestSetupSG:
    def test_from_config(self):
        global config_data
        global user_core_models
        global model_files
        global settings_file_1
        
        user_core_models = [mh.from_config(filename) for filename in model_files]
        user_core_models = {core_model['system_type']: core_model for core_model in user_core_models}
        
        #Read settings
        filename    = settings_file_1
        config_data = ssg.from_config(filename)
        
        assert type(config_data) == dict
    
    @pytest.mark.xfail
    def test_from_config_fail_1(self):
        global config_data
        global user_core_models
        global model_files
        global settings_file_2
        
        user_core_models = [mh.from_config(filename) for filename in model_files]
        user_core_models = {core_model['system_type']: core_model for core_model in user_core_models}
        
        #Read settings
        filename    = settings_file_2
        config_data = ssg.from_config(filename)
        
        assert type(config_data) == dict
    
    def test_get_sensitivity_args(self):
        global user_core_models
        global settings_file_1
        global sg_args
        global variables
        global config_data
    
        filename    = settings_file_1
        
        #Get arguments for simulation
        result = ssg.get_strike_goldd_args(filename, user_core_models=user_core_models)
        
        #Expect models, params, config_data = result
        assert len(result) == 3
        
        try:
           sg_args, config_data, variables = result
        except:
            sg_args, config_data, variables = result.values()   

class TestStrikeGolddSimplified:
    def test_make_samples(self):
        global sg_results
        
        sg_results = sg.analyze_sg_args(sg_args)
        
        assert sg_results
    
    @pytest.fixture(scope='session')
    def test_update_core_model(self):
        global sg_results
        global variables
        global config_data
        global user_core_models
        
        ir.dump_sg_results(sg_results, variables, config_data, user_core_models=user_core_models, save=False)
        
if __name__ == '__main__':
    t = TestSetupSG()
    
    

