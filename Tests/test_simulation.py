import add_BMSS_to_path
import pytest

import matplotlib.pyplot as plt
import numpy             as np
import os
import pandas            as pd
from   numba             import jit
from   pathlib           import Path

'''
Tests for simulation
'''

import BMSS.models.model_handler    as mh
import BMSS.models.settings_handler as sh
import BMSS.models.setup_sim        as sm
import BMSS.simulation              as sim

config_data      = None
user_core_models = None
model_files      = ['testmodel.ini']
settings_file_1  = 'settings_sim_1.ini'
settings_file_2  = 'settings_sim_2.ini' #Negative test case

models      = None 
params      = None 
config_data = None

ym = None
em = None 

@jit(nopython=True)
def synthesis_p(y, t, params):
    '''
    filler
    x: Time
    y: synthesis_rate
    filler
    '''
    m = y[:,0]
    
    synp = params[3]
    
    synthesis_rate = synp*m
    
    return synthesis_rate, t, '-'
        
class TestSetupSim:
    def test_from_config(self):
        global config_data
        global user_core_models
        global model_files
        global settings_file_1
        
        user_core_models = [mh.from_config(filename) for filename in model_files]
        user_core_models = {core_model['system_type']: core_model for core_model in user_core_models}
        
        #Read settings
        filename    = settings_file_1
        config_data = sm.from_config(filename)
        
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
        #Must raise Exception here
        filename    = settings_file_2
        config_data = sm.from_config(filename)
        
    def test_get_models_and_params(self):
        global user_core_models
        global settings_file_1
        global models
        global params
        global config_data
        
        filename    = settings_file_1
        
        #Get arguments for simulation
        result = sm.get_models_and_params(filename, user_core_models=user_core_models)
        
        #Expect models, params, config_data = result
        assert len(result) == 3
        
        try:
            models, params, config_data = result
        except:
            models, params, config_data = result.values()   

class TestSimulation:
    def test_integrate_models_1(self):
        global models
        global params
        global ym
        
        ym, _ = sim.integrate_models(models, params)
        
        try:
            ym[1][1]
        except Exception as e:
            raise e
        
        assert not _
    
    def test_plot_model_1(self):
        global ym
        
        plot_index  = {1: ['m', 'p'],
                   }
        titles      = {1: {'m': 'Model 1 mRNA', 'p': 'Model 1 Protein'},
                       }
        labels      = {1: {1: 'Scenario 1', 2: 'Scenario 2'}
                       }
        
        figs, AX = sim.plot_model(plot_index, ym, titles=titles, labels=labels)
        
        assert len(figs)
    
    def test_integrate_models_2(self):
        global models
        global params
        global ym
        global em
        global synthesis_p
            
        ym, em = sim.integrate_models(models, params, synthesis_p)
        
        assert em
    
    def test_plot_model_2(self):
        global ym
        global em
        global synthesis_p
        
        #Modify the plot settings accordingly
        plot_index  = {1: ['p', synthesis_p],
                       }
        titles      = {1: {'p': 'Model 1 Protein', synthesis_p: 'Rate of Protein Synthesis'},
                       }
        labels      = {1: {1: 'Scenario 1', 2: 'Scenario 2'}
                       }
        
        figs, AX = sim.plot_model(plot_index, ym, e=em, titles=titles, labels=labels) 

        assert len(figs)
        
    def test_plot_model_3(self):
        global ym
        global em
        global synthesis_p
        
        #Modify the plot settings accordingly
        plot_index  = {1: ['p', synthesis_p],
                       }
        titles      = {1: {'p': 'Model 1 Protein', synthesis_p: 'Rate of Protein Synthesis'},
                       }
        labels      = {1: {1: 'Scenario 1', 2: 'Scenario 2'}
                       }
        
        figs = [plt.figure()]
        AX_  = [figs[0].add_subplot(1, 2, i+1) for i in range(2)]
        AX   = {1: {'p': AX_[0], synthesis_p: AX_[1]}
                }
        
        figs, AX = sim.plot_model(plot_index, ym, e=em, titles=titles, labels=labels, figs=figs, AX=AX) 

        assert len(figs) == 1
    
    def test_export_simulation_results(self):
        #Prefix at the front of the filenames
        prefix = ''
        
        #A new folder will be created using this directory. The files will be stored here.
        directory = Path(os.getcwd()) / 'simulation_results'
        
        sim.export_simulation_results(ym, em, prefix=prefix, directory=directory)
        
        assert 'simulation_results' in os.listdir()

if __name__ == '__main__':
    t = TestSetupSim()
    t.test_from_config()
    t.test_from_config_fail_1()
    t.test_get_models_and_params()
        
        