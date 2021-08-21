import numpy  as np
import pandas as pd

import setup_bmss           as lab
import BMSS.models.setup_cf as sc
import BMSS.curvefitting    as cf

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
        
        mu       = {}
        sd       = {}
        mu_init  = {}
        sd_final = {}
        time     = []
        for state in raw_data:
            vals = raw_data[state]
            t    = np.array(raw_data[state].index, dtype=np.float64)
            
            #Get the mean and sd
            vals_sd = vals.groupby(axis=1, level=0).std()
            vals_mu = vals.groupby(axis=1, level=0).mean()

            '''
            Convert the DataFrames.
            '''
            mu[state] = df_to_dict_array(vals_mu)
            sd[state] = df_to_dict_array(vals_sd)
            
            '''
            Time is indexed under key = 0
            '''
            mu[state]['time'] = t
            sd[state]['time'] = t
            
            '''
            Apart from the data, we also need the initial values for integration as well
            as the sd for each state for calculating the log-likelihood
            '''
            mu_init[state]  = vals_mu.iloc[0].to_dict()
            sd_final[state] = vals_sd.iloc[-1].mean()
            time.append(t)
        
        data_sd[model_num] = sd
        data_mu[model_num] = mu
                
        init[model_num]     = mu_init
        state_sd[model_num] = sd_final
        tspan[model_num]    = np.unique(np.concatenate(time)) #includes sorting

    return data_mu, data_sd, init, state_sd, tspan


def update_sampler_args(data_mu, data_sd, init, state_sd, tspan, sampler_args, states):
    
    for model_num in states:
        #Add data_mu or data to sampler_args
        sampler_args['data'] = data_mu
        
        #Change the name of states to match the names used in data
        sampler_args['models'][model_num]['states'] = states[model_num] 
        
        #Change the initial values to the models
        temp         = pd.DataFrame(sampler_args['models'][model_num]['init']).T
        temp.columns = states[model_num]
        scenarios    = init[model_num][next(iter(init[model_num]))].keys()
        temp.index   = scenarios
        for state in init[model_num]:
            temp[state] = init[model_num][state].values()

        sampler_args['models'][model_num]['init'] = df_to_dict_array(temp.T)
        
        #Add the sd of the state
        sampler_args['models'][model_num]['sd'] = state_sd[model_num]
        
        #Change the tspan of the model
        #In this case, we only have one segment so no further manipulation is required.
        sampler_args['models'][model_num]['tspan'] = [tspan[model_num]]
        
        #Add modify_init to model 2
        if model_num == 2:
            sampler_args['models'][model_num]['int_args']['modify_init'] = modify_init
        
    
    return sampler_args


def modify_init(init_values, params, model_num, scenario_num, segment):
    '''
    Return a new np.array of initial values. For safety, DO NOT MODIFY IN PLACE.
    '''
    new_init = init_values.copy()
    if model_num == 2:
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

