import matplotlib.pyplot as plt
import numpy             as np
import pandas            as pd

import setup_bmss                as lab
import BMSS.models.model_handler as mh
import BMSS.models.setup_cf      as sc
import BMSS.aicanalysis          as ac
import BMSS.curvefitting         as cf
import BMSS.traceanalysis        as ta
from   read_data                 import read_data

'''
Example 2 Part 2: Model selection via AIC
'''

plt.style.use(lab.styles['bmss_notebook_style'])

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

#Plot settings   
if __name__ == '__main__':
    '''
    We have collected data from our characterization experiments of the NOT gate 
    system. We now want to fit the models and select the best one based on the 
    AIC criterion.
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
    #Details in Tutorial 5 Part 2
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
    
    #Run sampler
    traces    = {}    
    result    = cf.simulated_annealing(**sampler_args)
    accepted  = result['a']
    traces[1] = accepted
    
    #Plot results
    plot_index  = {1: ['Fluor/OD'],
                   2: ['Fluor/OD', 'm1', 'm2'],
                   3: ['Fluor/OD', 'm1', 'm2',]
                   }
    titles      = {1: {'Fluor/OD': 'Pep Model 1'},
                   2: {'Fluor/OD': 'Pep Model 2', 'm1': 'mRNA 1 Model 2', 'm2': 'mRNA 2 Model 2'},
                   3: {'Fluor/OD': 'Pep Model 3', 'm1': 'mRNA 1 Model 3', 'm2': 'mRNA 2 Model 3'}
                   }
    labels      = {1: {1: 'Input=0', 2: 'Input=1'},
                   2: {1: 'Input=0', 2: 'Input=1'},
                   3: {1: 'Input=0', 2: 'Input=1'}
                   }
    legend_args = {'loc': 'upper left'}
    
    figs, AX  = cf.plot(posterior   = accepted.iloc[-40::2], 
                        models      = sampler_args['models'],  
                        data        = data_mu,
                        data_sd     = data_sd,
                        plot_index  = plot_index,
                        labels      = labels,
                        titles      = titles,
                        legend_args = legend_args,
                        figs        = None,
                        AX          = None
                        )
    
    trace_params = [p for p in accepted.columns if p not in sampler_args['fixed_parameters']]
    n_figs       = round(len(trace_params)/10 + 0.5)
    trace_figs   = [plt.figure() for i in range(n_figs)]
    trace_AX_    = [trace_figs[i].add_subplot(5, 2, ii+1) for i in range(len(trace_figs)) for ii in range(10)]
    trace_AX     = dict(zip(trace_params, trace_AX_))
    
    trace_figs, trace_AX = ta.plot_steps(traces, 
                                         skip        = sampler_args['fixed_parameters'], 
                                         legend_args = legend_args,
                                         figs        = trace_figs,
                                         AX          = trace_AX
                                         )
    # #Rank models 
    # #Details in Tutorial 6 Part 1
    # table = ac.calculate_aic(data   = sampler_args['data'], 
    #                          models = sampler_args['models'], 
    #                          priors = sampler_args['priors'],
    #                          params = accepted.iloc[-10:]
    #                          )
    
    # ranked_table  = ac.rank_aic(table, inplace=False)
    
    # print('Ranked AIC table')
    # print(ranked_table.head())
    
    