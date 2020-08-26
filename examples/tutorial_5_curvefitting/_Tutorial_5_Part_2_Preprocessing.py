import matplotlib.pyplot as plt
import pandas            as pd
import numpy             as np
from   numba             import jit

import setup_bmss              as lab
import BMSS.models.setup_cf    as sc
import BMSS.timeseries         as ts
import BMSS.traceanalysis      as ta
import BMSS.curvefitting       as cf

plt.style.use(lab.styles['bmss_notebook_style'])

#Reset Plots
plt.close('all')

'''
Tutorial 5 Part 2: Preprocessing Experimental Data
- Introduction to TimeSeries class
'''

def df_to_dict_array(df):
    d = df.to_dict('list')
    return {key: np.array(d[key]) for key in d}
    
if __name__ == '__main__':
    
    '''
    It is likely your raw data contains readings for multiple scenarios and trials.
    '''
    
    #Let's first read the data from csv format
    raw_data = {'OD600': pd.read_csv('data/OD600_Data.csv', header=[0, 1]),
                'Fluor': pd.read_csv('data/GFP_Data.csv', header=[0, 1])
                }
    
    '''
    Each of these is a DataFrame where the first index represents the scenario
    and the second one the trial/replicate.
    '''
    print('Raw OD data')
    print(raw_data['OD600'].head())
    
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
        
        #Convert AU to Molar for fluorescence
        if state == 'Fluor':
            vals = vals *1e-6/(18.814*30)
            vals = vals/raw_data['OD600'].iloc[:,1:]
        
        #Subtract the blank
        vals = vals[[c for c in vals.columns if 'Blank' not in c]].subtract(vals['Blank'], axis='rows', level=1)
        
        #Get the mean and sd
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
    
    '''
    BMSS curve-fitting accepts a nested dictionary of experimental data in the
    form data[model_num][state][scenario_num]
    '''
    
    data     = {}
    data_mu  = {}
    data_sd  = {}
    init     = {}
    state_sd = {}
    tspan    = {}
    
    data_sd[1] = sd
    data_mu[1] = mu
    data[1]    = v
    
    init[1]         = mu_init
    state_sd[1]     = sd_final
    tspan[1]        = np.unique(np.concatenate(time))
    
    '''
    We now incorporate the data into the sampler arguments
    '''
    filename = 'settings_sa.ini'
    sampler  = 'sa'
    
    sampler_args, config_data = sc.get_sampler_args(filename, sampler)
    
    #Add data_mu or data to sampler_args
    sampler_args['data'] = data_mu
    
    #Change the name of states to match the names used in data
    sampler_args['models'][1]['states'] = ['OD600', 'Glu', 'Fluor'] 
    
    #Change the initial values to the models
    temp         = pd.DataFrame(sampler_args['models'][1]['init']).T
    temp.columns = states[1]
    for state in init[1]:
        temp[state] = init[1][state].values()
    
    print('Printing init. vals. for model 1 in update_sampler_args (df form)')
    print(temp)
    sampler_args['models'][1]['init'] = df_to_dict_array(temp.T)
    
    
    #Add the sd of the state
    sampler_args['models'][1]['sd'] = state_sd[1]
    
    #Change the tspan of the model
    #In this case, we only have one segment so no further manipulation is required.
    sampler_args['models'][1]['tspan'] = [tspan[1]]
    
    print('Data in first model')
    for key in sampler_args['models'][1]:
        print(key)
        print(sampler_args['models'][1][key])
        print()
    
        