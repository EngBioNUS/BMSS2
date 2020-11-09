import add_BMSS_to_path
import pytest

import matplotlib.pyplot as plt
import numpy             as np
import os
import pandas            as pd
from   numba             import jit
from   pathlib           import Path

'''
Tests for sensitivity analysis
'''

import BMSS.models.model_handler    as mh
import BMSS.models.settings_handler as sh
import BMSS.models.setup_sen        as ss
import BMSS.sensitivityanalysis     as sn

config_data      = None
user_core_models = None
model_files      = ['Monod_Constitutive_Single_ProductInhibition.ini']
settings_file_1  = 'settings_sen_1.ini'
settings_file_2  = 'settings_sen_2.ini' #Negative test case

sensitivity_args = None
problems         = None
samples          = None
analysis_result  = None

em = None 

def h_yield(y, t, params):
    final_x = y[-1, 0]
    final_h = y[-1, 2]

    return final_x*final_h
    

class TestSetupSen:
    def test_from_config(self):
        global config_data
        global user_core_models
        global model_files
        global settings_file_1
        
        user_core_models = [mh.from_config(filename) for filename in model_files]
        user_core_models = {core_model['system_type']: core_model for core_model in user_core_models}
        
        #Read settings
        filename    = settings_file_1
        config_data = ss.from_config(filename)
        
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
        config_data = ss.from_config(filename)
        
        assert type(config_data) == dict
    
    def test_get_sensitivity_args(self):
        global user_core_models
        global settings_file_1
        global sensitivity_args
        global config_data
    
        filename    = settings_file_1
        
        #Get arguments for simulation
        result = ss.get_sensitivity_args(filename, user_core_models=user_core_models)
        
        #Expect models, params, config_data = result
        assert len(result) == 2
        
        try:
           sensitivity_args, config_data = result
        except:
            sensitivity_args, config_data = result.values()   

class TestSensitivityAnalysis:
    
    def test_make_samples(self):
        global analysis_result
        global em
        global samples
        global problems
        
        sensitivity_args['params'].index = ['Strain 1', 'Strain 2']
        
        #For speed, reduce the number of samples.
        sensitivity_args['N'] = 500
        
        sensitivity_args['objective'] = {1: [h_yield]}
        
        analysis_result, em, samples, problems = sn.analyze(**sensitivity_args)
        
        assert samples
        assert problems
        assert em
    
    def test_plot_first_order(self):
        #Plot settings
        titles = {1: {1: {0: {h_yield: 'h Yield'
                             }
                          }
                      }
                  }
        #Shorthand version. Comment it out later to see the difference.
        titles = {1: {h_yield: 'h Yield'}
                  }
        figs, AX = sn.plot_first_order(analysis_result, problems=problems, titles=titles, analysis_type=sensitivity_args['analysis_type'], figs=None, AX=None)
        
        assert figs
        assert AX
        
if __name__ == '__main__':
    t = TestSetupSen()
    t.test_from_config()
            
            
            
            