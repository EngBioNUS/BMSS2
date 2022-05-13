
import os
import numpy             as np
import matplotlib.pyplot as plt
import pandas            as pd
from   pathlib           import Path

import setup_bmss                as lab
import BMSS.models.model_handler as mh
import BMSS.models.setup_cf      as sc
import BMSS.curvefitting         as cf
import BMSS.traceanalysis        as ta
import BMSS.models.setup_sim     as sm
import BMSS.simulation           as sim


'''
Example 4: This example demonstrates how we use the optimized Model 4 from 
iteration 2 to generate 3 synthetic data sets. The optimized Model 4 has all 
parameters fully converged after two parameters associated with the two inducers
were set as fixed parameters during model fitting.
'''

#Reset Plots
plt.close('all')

plt.rcdefaults()
plt.rcParams['font.family'] = 'Calibri' 
plt.rcParams['font.weight'] = 'normal' 
plt.rcParams['font.size'] = 18
plt.rcParams['axes.labelsize'] = 18
plt.rcParams['axes.labelweight'] = 'normal' 
plt.rcParams['axes.linewidth'] = 2
plt.rcParams['legend.frameon'] = False
plt.rcParams["legend.handletextpad"] = 0.3
plt.rcParams["legend.columnspacing"] = 0.5
plt.rcParams["legend.borderaxespad"] = 0
plt.rcParams.update({'axes.spines.top': False, 'axes.spines.right': False}) 

output_folder = (Path.cwd() / 'Output_files')
output_folder.mkdir(exist_ok=True)


def read_data(filename):
    '''Read experimental data and process the data into proper format (customized).
    Return: mean and standard deviation data in dict
    '''
    state     = 'Fluor/OD'
    data_mu   = {}
    data_sd   = {}
    state_sd  = {}
    tspan     = None
    df        = pd.read_csv(filename)
    scenarios = []
    
    init      = {}
    
    for column in df.columns:
        if 'std' in column:
            continue
        else:
            scenarios.append(column)
    
    print(len(scenarios))
          
    #Set up data_mu, data_sd, init, tspan
    for model_num in range(1,2):
        data_mu[model_num] = {state:{}}
        data_sd[model_num] = {state:{}}
        init[model_num]    = {}
        
        for i in range(len(scenarios)):
            scenario = scenarios[i]
            
            if i == 0:
                data_mu[model_num][state][i] = df[scenario].values
                data_sd[model_num][state][i] = df[scenario].values
                tspan                        = df[scenario].values 
            else:
                print(scenario + 'std')
                data_mu[model_num][state][i] = df[scenario].values #*1e-6/(18.814*30)
                data_sd[model_num][state][i] = df[scenario + 'std'].values #*1e-6/(18.814*30)
                
                #Specific to the model in question
                init_val           = data_mu[model_num][state][i][0]              
                init[model_num][i] = {state:init_val}
    
    #Set up state_sd
    df_sd           = df[[scenario + 'std' for scenario in scenarios if 'Time' not in scenario]]
    state_sd[state] = df_sd.mean().mean() #*1e-6/(18.814*30)
    
    #Add scenarios for reference    
    data_mu[1]['Fluor/OD'][-1] = scenarios
    data_sd[1]['Fluor/OD'][-1] = scenarios
    
    return data_mu, data_sd, init, state_sd, tspan


def modify_init(init_values, params, model_num, scenario_num, segment):
    #Always use a copy and not the original
    new_init = init_values.copy()
    
    if model_num in [1]: 
        new_init[0] = 1
        new_init[2] = 1
    else:
        pass
        
    return new_init


def modify_params(init_values, params, model_num, scenario_num, segment):
    #Always use a copy and not the original
    new_params = params.copy()
    
    #Change value of inducer based on scenario_num
    if scenario_num == 1:
        new_params[-2] = 0
        new_params[-1] = 0
    elif scenario_num == 2:
        new_params[-2] = 0
        new_params[-1] = 1
    elif scenario_num == 3:
        new_params[-2] = 1
        new_params[-1] = 0
    else:
        new_params[-2] = 1
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


if __name__ == '__main__':
    
    #Import data
    data_file = Path.cwd() /'data'/'LogicGate_ORAraAtcTop10d37M9_Molar.csv'
    data_mu, data_sd, init, state_sd, tspan = read_data(data_file)
    print('\ninit:\n', init)
    
    #Set up core models and sampler arguments (optimized Model 4 from iteration 2
    #after setting two parameters as fixed parameters)
    model_files = ['LogicGate_OR_Single_Delay_Degrade_ResCompete_NomRNA_Nosynpep3_Nopepmax_Optimized.ini']
    
    
    #List of model dicts
    core_models_list = [mh.from_config(filename) for filename in model_files]
    print(core_models_list)
    
    #Nested dict with system_type as first key to store the model dict
    user_core_models = {core_model['system_type']: core_model for core_model in core_models_list}
    print('\n\n', user_core_models)
    
    
    '''Run simulation using the same configuration file (can be used to test
    any model with their initial guesses before performing model selection).
    The steps are as follows:
        1. prepare configuration .ini file (aside from core model information)
            - init, parameter_values, tspan 
        2. get_models_and_params
        3. update models argument with modify_params or/and modify_init if any
        4. integrate models
        5. plot model
        6. export simulation results (optional)
    '''
    
    #Get arguments for simulation
    models, params, config_data = sm.get_models_and_params(model_files[0], user_core_models=user_core_models)
    
    models[1]['int_args']['modify_params'] = modify_params
    models[1]['int_args']['modify_init'] = modify_init
    print(models)
    print(params)
    
    '''Integrate the models numerically to generate synthetic data for Inde and Ind'''
    ym, em = sim.integrate_models(models, params, multiply=True)
    
    plot_index  = {1: ['Pep3', 'Ind', 'Inde', 'Indi'],
                    }
    titles      = {1: {'Pep3': 'Protein', 'Ind': 'Ind', 'Inde': 'Inde', 'Indi': 'Indi'},
                    }
    labels      = {1: {1: 'Input=00', 2: 'Input=01', 3: 'Input=10', 4: 'Input=11'}
                    }
    
    figs, AX = sim.plot_model(plot_index, ym, titles=titles, labels=labels)
    
    '''generate synthetic protein data when increasing deg_Pep by 1.5x''' 
    params.iloc[0, 2] = params.iloc[0, 2]*1.5 # 0.358*2
    ym, em = sim.integrate_models(models, params, multiply=True)
    
    plot_index  = {1: ['Pep3'],
                    }
    titles      = {1: {'Pep3': 'Protein'},
                    }
    labels      = {1: {1: 'Input=00', 2: 'Input=01', 3: 'Input=10', 4: 'Input=11'}
                    }
    
    figs, AX = sim.plot_model(plot_index, ym, titles=titles, labels=labels)
    
    
    #Export simulation results
    prefix = ''
    
    #A new folder will be created inside the output_folder using this directory.
    directory = output_folder / 'simulation_results'
    
    sim.export_simulation_results(ym, em, prefix=prefix, directory=directory)
    
    
    '''Set sampler arguments for running curvefitting and Trace analysis
    The steps are as follows:
        1. prepare configuration .ini file (aside from core model information)
            - guess, priors, parameter_bounds, fixed_parameters,
        2. get_sampler_args
        3. update sampler_args with information from experimental data file
    '''
    
    sampler_args, config_data = sc.get_sampler_args(model_files, user_core_models=user_core_models)
    
    sampler_args['data'] = data_mu
    
    for model_num in sampler_args['models']:
        sampler_args['models'][model_num]['tspan'] = [tspan]
        sampler_args['models'][model_num]['sd']    = state_sd
        sampler_args['models'][model_num]['states'][-1] = 'Fluor/OD'
        model_init = {scenario: [init[model_num][scenario].get(state, 0) for state in sampler_args['models'][model_num]['states']] for scenario in init[model_num]}
        print(model_init)
        sampler_args['models'][model_num]['init']                      = model_init
        sampler_args['models'][model_num]['int_args']['modify_params'] = modify_params
        sampler_args['models'][model_num]['int_args']['modify_init']   = modify_init
    
    
    '''Run A posteriori identifiability analysis.
    The steps are as follows:
        1. generate multiple seeds from the guess and bounds
        2. run curvefitting multiple times based on the generated seeds
        3. plot the trace figure for all the fitted parameters
        4. plot the fitting results againsts the data for the individual traces
    '''
    
    '''Set the trials to ensure proper convergence'''
    sampler_args['trials'] = 7000
    
    #Run sampler multiple times
    seeder = seed(sampler_args['guess'], sampler_args['fixed_parameters'], sampler_args['bounds'])
    traces = {}    
    for i in range(5):
        print('Run ' + str(i+1))
        sampler_args['guess'] = seeder()
        result                = cf.simulated_annealing(**sampler_args)
        accepted              = result['a']
        traces[i+1]           = accepted.iloc[::5]#Thin the trace
    
        #Plot results
        plot_index = {}
        titles = {}
        labels = {}
        for model_num in sampler_args['models']:
            plot_index[model_num]  = ['Fluor/OD']
            titles[model_num]      = {'Fluor/OD': 'Pep Model '+ str(model_num)}
            labels[model_num]      = {1: 'Input=00', 2: 'Input=01', 3: 'Input=10', 4: 'Input=11'}
                         
        legend_args = {'loc': 'upper left'}
        
        figs, AX  = cf.plot(posterior   = accepted.iloc[-40::2], 
                            models      = sampler_args['models'], 
                            guess       = {}, #sampler_args['guess'],
                            data        = data_mu,
                            data_sd     = data_sd,
                            plot_index  = plot_index,
                            labels      = labels,
                            titles      = titles,
                            legend_args = legend_args,
                            )
        
        print('\nAX\n', AX)
        for ax in AX.values():
            ax1 = ax['Fluor/OD']
            ax1.set_xticks(ax1.get_xticks()[::2]) #thin the ticklabels
            ax1.set_yticks(ax1.get_yticks()[::2])
    
    trace_params = [p for p in accepted.columns if p not in sampler_args['fixed_parameters']]
    n_figs       = round(len(trace_params)/10 + 0.5)
    trace_figs   = [plt.figure() for i in range(n_figs)]
    trace_AX_    = [trace_figs[i].add_subplot(5, 2, ii+1) for i in range(len(trace_figs)) for ii in range(10)]
    trace_AX     = dict(zip(trace_params, trace_AX_))
    
    legend_args = {'loc': 'upper left'}
    
    #Check if chains converge to same region
    trace_figs, trace_AX = ta.plot_steps(traces, 
                                          skip        = sampler_args['fixed_parameters'], 
                                          figs        = trace_figs,
                                          AX          = trace_AX
                                          )
    