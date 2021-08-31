import matplotlib.pyplot as plt
import numpy             as np
import pandas            as pd

import setup_bmss                as lab
import BMSS.models.model_handler as mh
import BMSS.models.setup_cf      as sc
import BMSS.icanalysis           as ac
import BMSS.curvefitting         as cf
import BMSS.traceanalysis        as ta
from   read_data                 import read_data

'''
Example 2 Part 3: A posteriori Identifiability Analysis
'''

plt.style.use(lab.styles['dark_style'])

#Reset Plots
plt.close('all')

def modify_init(init_values, params, model_num, scenario_num, segment):
    #Always use a copy and not the original
    new_init = init_values.copy()
    
    if model_num == 1:
        pass
    
    elif model_num == 2:
       synm1, synm2, degm, kp1, rep, synp1, synp2, degp, u1 = params
       
       new_init[1] = synm2/degm
       
        
    else:
        synm1, synm2, degm, kp1, rep, synp1, synp2, matp2, degp, u1 = params
        m1, m2, p1, p2n, p2 = init_values
        
        new_init[1] = synm2/degm
        new_init[3] = synp2*m2/matp2
        
    return new_init

def modify_params(init_values, params, model_num, scenario_num, segment):
    #Always use a copy and not the original
    new_params = params.copy()
    
    #Change value of inducer based on scenario_num
    if scenario_num == 1:
        new_params[-1] = 0
    else:
        new_params[-1] = 1

    return new_params

def seed(guess, fixed_parameters, parameter_bounds):
    def vary(key):#Generate new value for parameter
        value = guess[key]
        delta = (np.random.rand() - 0.5)
        
        new_value            = value*16**delta#4 fold variation
        min_value, max_value = parameter_bounds.get(key, [None, None])

        if min_value is not None: #Make sure new value does not exceed bounds
            return max(min_value, min(max_value, new_value))
        else:
            return new_value
    
    def helper(return_original=False):
        if return_original:#Have a way to retrieve original guess
            return guess
        else:
            return {key: guess[key] if key in fixed_parameters else vary(key) for key in guess }
    return helper

#Plot settings   
if __name__ == '__main__':
    '''
    We want to check if our parameters have been properly identified by 
    examining convergence. BMSS's traceanalysis submodule allows us to 
    visualize the trace plot.
    '''
    #Set up core models and sampler arguments
    #Details in Tutorial 5 Parts 1 and 2
    model_files = ['LogicGate_Not_Single.ini',
                   'LogicGate_Not_Double.ini',
                   'LogicGate_Not_Double_MaturationSecond.ini',
                   ]
    
    user_core_models = [mh.from_config(filename) for filename in model_files]
    user_core_models = {core_model['system_type']: core_model for core_model in user_core_models}
    
    sampler_args, config_data = sc.get_sampler_args(model_files, user_core_models=user_core_models)
    
    #Import data
    #Details in Tutorial 4 Part 2
    #Function for importing the data is different from the one the tutorial
    #as the blanks and means have already been accounted for.
    #Data structures are still the same
    data_files = {'Fluor/OD' : 'data/not_gate.csv',
                  }
    data_mu, data_sd, init, state_sd, tspan = read_data(data_files, n_models=len(config_data))
    
    #Update sampler_args with the information from the data
    sampler_args['models'][1]['states'] = ['p1', 'Fluor/OD']
    sampler_args['models'][2]['states'] = ['m1', 'm2', 'p1', 'Fluor/OD']
    sampler_args['models'][3]['states'] = ['m1', 'm2', 'p1', 'p2n', 'Fluor/OD']
    sampler_args['data']                = data_mu
    
    for model_num in sampler_args['models']:
        sampler_args['models'][model_num]['tspan'] = [tspan]
        sampler_args['models'][model_num]['sd']    = state_sd
        
        model_init = {scenario: [init[model_num][scenario].get(state, 0) for state in sampler_args['models'][model_num]['states']] for scenario in init[model_num]}
        sampler_args['models'][model_num]['init']                      = model_init
        sampler_args['models'][model_num]['int_args']['modify_params'] = modify_params
        sampler_args['models'][model_num]['int_args']['modify_init']   = modify_init
    
    #Run sampler multiple times from multiple times
    seeder = seed(sampler_args['guess'], sampler_args['fixed_parameters'], sampler_args['bounds'])
    traces = {}    
    for i in range(20):
        print('Run ' + str(i+1))
        sampler_args['guess'] = seeder()
        result                = cf.simulated_annealing(**sampler_args)
        accepted              = result['a']
        traces[i+1]           = accepted.iloc[::10]#Thin the trace
    
    
    trace_params = [p for p in accepted.columns if p not in sampler_args['fixed_parameters']]
    n_figs       = round(len(trace_params)/8 + 0.5)
    trace_figs   = [plt.figure() for i in range(n_figs)]
    trace_AX_    = [trace_figs[i].add_subplot(4, 2, ii+1) for i in range(len(trace_figs)) for ii in range(8)]
    trace_AX     = dict(zip(trace_params, trace_AX_))
    
    #Check if chains converge to same region
    trace_figs, trace_AX = ta.plot_steps(traces, 
                                         skip        = sampler_args['fixed_parameters'], 
                                         figs        = trace_figs,
                                         AX          = trace_AX, 
                                         legend_args = {}
                                         )
    
    pairs = [['synp1_1', 'synp2_1'],
             ['synp1_1', 'kp1_1']
             ]
    
    pairplot_figs, pairplot_AX = ta.pairplot_steps(traces, pairs)
    '''
    The correlation for synp1 and synp2 is weak. This can be seen by the 
    the way synp1 can vary to a large extent for a given value of synp2. Meanwhile, 
    the correlation for kp1 and synp1 is somewhat stronger as can be seen from 
    the reciprocal trend of the trace plot.
    '''
    