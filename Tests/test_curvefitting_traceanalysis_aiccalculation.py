import add_BMSS_to_path
import pytest

import matplotlib.pyplot as plt
import numpy             as np
import os
import pandas            as pd
from   numba             import jit
from   pathlib           import Path

'''
Tests for curve-fitting
'''

import BMSS.models.model_handler    as mh
import BMSS.models.settings_handler as sh
import BMSS.models.setup_cf         as sc
import BMSS.curvefitting            as cf
import BMSS.traceanalysis           as ta
import BMSS.aicanalysis             as ac 

config_data      = None
user_core_models = None
model_files      = ['Monod_Constitutive_Single.ini', 'Monod_Constitutive_Double.ini']
settings_file_1  = 'settings_cf_sa_1.ini'
settings_file_2  = 'settings_cf_sa_1.ini' #Negative test case

config_data      = None
sampler_args     = None
data             = None
data_mu          = None
data_sd          = None
init             = None
state_sd         = None
tspan            = None
accepted         = None
traces           = {}
table            = None

def divide(df1, df2):
    result = df1/df2
    result[('Time', 'Trials')] = df1[('Time', 'Trials')]
    return result
def multiply(df1, df2):
    result = df1*df2
    result[('Time', 'Trials')] = df1[('Time', 'Trials')]
    return result
    
def df_to_dict_array(df):
    d = df.to_dict('list')
    return {key: np.array(d[key]) for key in d}
    
def import_data(all_data, data_by_model_num):
    '''
    BMSS curve-fitting accepts a nested dictionary of experimental data in the
    form data[model_num][state][scenario_num].
    
    Apart from the experimental data, we also need the initial values of the states,
    their stdev and the tspan.
    '''
    
    data     = {}
    data_mu  = {}
    data_sd  = {}
    init     = {}
    state_sd = {}
    tspan    = {}
    for model_num in data_by_model_num:
        #Let's first read the data from csv format
        raw_data = data_by_model_num[model_num]
        
        '''
        Each of these is a DataFrame where the first index represents the scenario
        and the second one the trial/replicate.
        '''
        
        '''
        Now we take the mean and standard deviation and subtract the blank.
        '''
        v        = {}
        mu       = {}
        sd       = {}
        mu_init  = {}
        sd_final = {}
        time     = []
        for state in raw_data:
            vals = raw_data[state].iloc[:,1:]
            t    = raw_data[state][('Time', 'Trials')].values.astype(np.float64)
            
            '''
            Subtract the blank. If your data does not require blank subtraction, remove this part.
            '''
            vals = vals[[c for c in vals.columns if 'Blank' not in c]].subtract(vals['Blank'], axis='rows', level=1)
            
            '''
            Calculate the mean and sd
            '''
            vals_sd = vals.std( axis=1, level=0)
            vals_mu = vals.mean(axis=1, level=0) 
            vals    = vals.stack().droplevel(level=1).reset_index(drop=True)
            
            '''
            BMSS curve-fitting algorithm currently only accepts dicts with positive integers
            for scenarios. We need to rename the DataFrames.
            '''
            scenarios     = list((vals.columns.get_level_values(0)))
            scenario_nums = list(range(1, len(scenarios)+1))
            
            vals_sd.columns = scenario_nums
            vals_mu.columns = scenario_nums
            vals.columns    = scenario_nums
            
            mu[state] = df_to_dict_array(vals_mu)
            sd[state] = df_to_dict_array(vals_sd)
            v[state]  = df_to_dict_array(vals)
            
            '''
            Time is indexed under key = 0
            '''
            mu[state][0] = t
            sd[state][0] = t
            v[state][0]  = t
            
            '''
            The algorithm ignores negative keys. We can store the scenario names under key = -1
            '''
            mu[state][-1] = scenarios
            sd[state][-1] = scenarios
            v[state][-1]  = scenarios
            
            '''
            Apart from the data, we also need the initial values for integration as well
            as the sd for each state for calculating the log-likelihood
            '''
            mu_init[state]  = vals_mu.iloc[0].to_dict()
            sd_final[state] = vals_sd.iloc[-1].mean()
            time.append(t)
    
        
        data_sd[model_num] = sd
        data_mu[model_num] = mu
        data[model_num]    = v
                
        init[model_num]     = mu_init
        state_sd[model_num] = sd_final
        tspan[model_num]    = np.unique(np.concatenate(time)) #includes sorting

    return data, data_mu, data_sd, init, state_sd, tspan


def update_sampler_args(data, data_mu, data_sd, init, state_sd, tspan, sampler_args, states):
    
    for model_num in states:
        #Add data_mu or data to sampler_args
        sampler_args['data'] = data_mu
        
        #Change the name of states to match the names used in data
        sampler_args['models'][model_num]['states'] = states[model_num] 
        
        #Change the initial values to the models
        temp         = pd.DataFrame(sampler_args['models'][model_num]['init']).T
        temp.columns = states[model_num]
        for state in init[model_num]:
            temp[state] = init[model_num][state].values()
        
        print('Printing init. vals. for model ' + str(model_num) + ' in update_sampler_args (df form)')
        print(temp)
        sampler_args['models'][model_num]['init'] = df_to_dict_array(temp.T)
        
        #Add the sd of the state
        sampler_args['models'][model_num]['sd'] = state_sd[model_num]
        
        #Change the tspan of the model
        #In this case, we only have one segment so no further manipulation is required.
        sampler_args['models'][model_num]['tspan'] = [tspan[model_num]]
        
        #Add modify_init to model 2
        sampler_args['models'][model_num]['int_args']['modify_init'] = modify_init
        
    return sampler_args


def modify_init(init_values, params, model_num, scenario_num, segment):
    '''
    Return a new np.array of initial values. For safety, DO NOT MODIFY IN PLACE.
    '''
    new_init = init_values.copy()
    if model_num == 2:
        #Initial concentration of mRNA should be steady-state concentration
        #dm = synm -m*degm
        #At steady-state: m = synm/degm
        synm, degm  = params[3], params[4]
        new_init[2] = synm/degm
    return new_init

def modify_params(init_values, params, model_num, scenario_num, segment):
    '''
    Not used in this example. You can use this as a template.
    Return a new np.array of initial values. For safety, DO NOT MODIFY IN PLACE.
    '''
    new_params = params.copy()
    return new_params

class TestSetupCF:
    def test_from_config(self):
        global config_data
        global user_core_models
        global settings_file_1
        
        user_core_models = [mh.from_config(filename) for filename in model_files]
        user_core_models = {core_model['system_type']: core_model for core_model in user_core_models}
        
        #Read settings
        filename    = settings_file_1
        config_data = sc.from_config(filename)
        
        assert type(config_data) == dict
    
    @pytest.mark.xfail
    def test_from_config_fail_1(self):
        global config_data
        global user_core_models
        global settings_file_2
        
        user_core_models = [mh.from_config(filename) for filename in model_files]
        user_core_models = {core_model['system_type']: core_model for core_model in user_core_models}
        
        #Read settings
        filename    = settings_file_2
        config_data = sc.from_config(filename)
        
        assert type(config_data) == dict
    
    def test_get_sampler_args(self):
        global user_core_models
        global settings_file_1
        global sampler_args
        global config_data
    
        filename    = settings_file_1
        
        #Get arguments for simulation
        result = sc.get_sampler_args(filename, user_core_models=user_core_models)
        
        #Expect models, params, config_data = result
        assert len(result) == 2
        
        try:
           sampler_args, config_data = result
        except:
            sampler_args, config_data = result.values()   

class TestCurveFitting:
    
    def test_simulated_annealing(self):
        global data
        global data_mu
        global data_sd
        global init
        global state_sd
        global tspan
        global sampler_args
        global accepted
        global traces
        
        all_data = {'OD600': pd.read_csv('data/OD600_Data.csv', header=[0, 1]),
                    'Fluor': pd.read_csv('data/GFP_Data.csv', header=[0, 1])
                    }
    
        #Normalize Fluorescence by OD and convert to Molar
        all_data['Fluor'] = divide(all_data['Fluor'], all_data['OD600'])
        all_data['Fluor'] = multiply(all_data['Fluor'], 1e-6/(18.814*30))
        
        data_by_model_num = {1: {'OD600': all_data['OD600'],
                                  'Fluor': all_data['Fluor']
                                  },
                              2: {'OD600': all_data['OD600'],
                                  'Fluor': all_data['Fluor']
                                  }
                              }
        #Extract the necessary information
        #Note that subtraction of the blank has been included in this function!!!
        data, data_mu, data_sd, init, state_sd, tspan = import_data(all_data, data_by_model_num)
    
        states = {1: ['OD600', 'Glu', 'Fluor'],
                  2: ['OD600', 'Glu', 'mh', 'Fluor'],
                  }
        
        sampler_args = update_sampler_args(data, data_mu, data_sd, init, state_sd, tspan, sampler_args, states)

        result = cf.simulated_annealing(**sampler_args)
        
        '''
        The return value is a dictionary with the following values.
        'a': The accepted samples as a DataFrame
        'r': The rejected samples as a DataFrame
        '''
        accepted = result['a']
        
        traces[1] = accepted
        
        assert len(accepted)
    
    def test_scipy(self):
        global data
        global data_mu
        global data_sd
        global init
        global state_sd
        global tspan
        global sampler_args
        
        
        all_data = {'OD600': pd.read_csv('data/OD600_Data.csv', header=[0, 1]),
                    'Fluor': pd.read_csv('data/GFP_Data.csv', header=[0, 1])
                    }
        
        #Normalize Fluorescence by OD and convert to Molar
        all_data['Fluor'] = divide(all_data['Fluor'], all_data['OD600'])
        all_data['Fluor'] = multiply(all_data['Fluor'], 1e-6/(18.814*30))
        
        data_by_model_num = {1: {'OD600': all_data['OD600'],
                                 'Fluor': all_data['Fluor']
                                 }
                              }
        #Extract the necessary information
        #Note that subtraction of the blank has been included in this function!!!
        data, data_mu, data_sd, init, state_sd, tspan = import_data(all_data, data_by_model_num)
        
        '''
        Iterate across each type of sampler
        '''
        filename_samplers = [('settings_cf_de_1.ini', 'de', cf.scipy_differential_evolution),
                             ('settings_cf_bh_1.ini', 'bh', cf.scipy_basinhopping),
                             ('settings_cf_da_1.ini', 'da', cf.scipy_dual_annealing)
                             ]
        
        for filename, sampler, sampler_function in filename_samplers:
            sampler_args, config_data = sc.get_sampler_args(filename, sampler)
            
            states = {1: ['OD600', 'Glu', 'Fluor'],
                      }
            
            sampler_args = update_sampler_args(data, data_mu, data_sd, init, state_sd, tspan, sampler_args, states)
            
            result = sampler_function(**sampler_args)
        
            assert type(result) == dict
    
class TestTraceAnalysis:
    
    def test_plot_steps(self):
        figs, AX = ta.plot_steps(traces, 
                                  skip=[], 
                                  palette={}, 
                                  legend_args={}, 
                                  plot_args={'marker': '+', 'linewidth':0}
                                  )
        assert figs
        assert AX
        
    def test_plot_kde(self):
        figs, AX = ta.plot_steps(traces, 
                                  skip=[], 
                                  palette={}, 
                                  legend_args={}, 
                                  plot_args={'marker': '+', 'linewidth':0}
                                  )
        
        assert figs
        assert AX

class TestAICAnalysis:
    def test_calculate_aic(self):
        global table
        
        table = ac.calculate_aic(data   = sampler_args['data'], 
                                 models = sampler_args['models'], 
                                 priors = sampler_args['priors'],
                                 params = accepted.iloc[-10:]
                                 )
        assert len(table)
    
    def test_rank_aic(self):
        global table
        
        ranked_table  = ac.rank_aic(table, aic_column_name='AIC Value', inplace=False)
        
        table = ranked_table
        
        assert len(table)
        
if __name__ == '__main__':
    t = TestSetupCF()
    t.test_from_config()
    t.test_get_sampler_args()
    
    t = TestCurveFitting()
    t.test_simulated_annealing()
    # t.test_scipy()
    
    # t = TestTraceAnalysis()
    # t.test_plot_steps()
    
    t = TestAICAnalysis()
    t.test_calculate_aic()
    t.test_rank_aic()
    
        
        