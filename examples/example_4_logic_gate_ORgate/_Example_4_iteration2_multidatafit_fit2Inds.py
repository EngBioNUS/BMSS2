
import os
import numpy             as np
import matplotlib.pyplot as plt
import pandas            as pd
from   pathlib           import Path

import setup_bmss                as lab
import BMSS.models.model_handler as mh
import BMSS.models.setup_cf      as sc
import BMSS.icanalysis           as ac
import BMSS.curvefitting         as cf
import BMSS.traceanalysis        as ta
import BMSS.models.setup_sim     as sm
import BMSS.simulation           as sim


'''
Example 4: This is to verify the insights from IA by providing 2 additional
synthetic data representing the dynamics of inducers to be used for model fitting
and check the predictive performance
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


def read_data(states_and_filenames, n_models=1):
    data_mu   = {}
    data_sd   = {}
    state_sd  = {}
    tspan     = []
    init      = {}
    
    time = {}
    state_sd1 = {}
    
    for state, filename in states_and_filenames.items():
        df         = pd.read_csv(filename)
        scenarios  = []
        
        for column in df.columns:
            if 'std' in column:
                continue
            elif 'Time' in column:
                scenarios.append(column)
                tspan.append(df[column].values)
            else:
                scenarios.append(column)
              
        #Set up data_mu, data_sd, init, tspan
        for model_num in range(1, n_models+1):
            data_mu.setdefault(model_num, {})[state] = {}
            data_sd.setdefault(model_num, {})[state] = {}
            init.setdefault(model_num, {})
            
            state_sd1.setdefault(model_num, {})[state] = {}
            
            tspan1 = np.unique(np.concatenate(tspan))
            time[model_num] = tspan1

            for i, scenario in enumerate(scenarios):
                #Add experimental data and time to data_mu
                data_mu[model_num][state][i] = df[scenario].values    
                
                if 'Time' in scenario:
                    #Add time to data_sd
                    data_sd[model_num][state][i] = df[scenario].values
                    
                else:
                    #Add sd of experimental data to data_sd
                    data_sd[model_num][state][i] = df[scenario + 'std'].values         
                    
                    #Set up initial values for integration
                    #Take first value of experimental data and add to init
                    init_val           = data_mu[model_num][state][i][0]              

                    if i in init[model_num]:
                        init[model_num][i].update({state:init_val})
                    else:
                        init[model_num].update({i:{}})
                        init[model_num][i].update({state:init_val})
                        
            #Set up state_sd
            df_sd           = df[[scenario + 'std' for scenario in scenarios if 'Time' not in scenario]]
            state_sd[state] = df_sd.mean().mean()
            
            state_sd1[model_num][state] = state_sd[state]
        
            #Add scenarios for reference    
            data_mu[model_num][state][-1] = scenarios
            data_sd[model_num][state][-1] = scenarios
        
    return data_mu, data_sd, init, state_sd1, time


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
    
    #Set up core models and sampler arguments
    model_files = ['LogicGate_OR_Single_Delay_Degrade_ResCompete_NomRNA_Nosynpep3_Nopepmax.ini']
    
    #Import data (experimental data and synthetic data)
    data_file = {'Fluor/OD': Path.cwd() /'data'/'LogicGate_ORAraAtcTop10d37M9_Molar.csv',
                 'Ind2': Path.cwd() /'data'/'Ind_synthetic_data.csv',
                 'Ind1e': Path.cwd() /'data'/'Inde_synthetic_data.csv'} 
    
    data_mu, data_sd, init, state_sd, tspan = read_data(data_file, n_models=len(model_files))
    print('\ninit:\n', init)
    
    #List of model dicts
    core_models_list = [mh.from_config(filename) for filename in model_files]
    print(core_models_list)
    
    #Nested dict with system_type as first key to store the model dict
    user_core_models = {core_model['system_type']: core_model for core_model in core_models_list}
    print('\n\n', user_core_models)
    
    #Get arguments to be used for model simulation/prediction
    models, params, config_data = sm.get_models_and_params(model_files[0], user_core_models=user_core_models)
    
    models[1]['int_args']['modify_params'] = modify_params
    models[1]['int_args']['modify_init'] = modify_init
    print(models)
    print(params)
    
  
    '''Set sampler arguments for running curvefitting and Trace analysis
    The steps are as follows:
        1. prepare configuration .ini file (aside from core model information)
            - guess, priors, parameter_bounds, fixed_parameters,
        2. get_sampler_args
        3. update sampler_args with information from experimental data file
    '''
    
    sampler_args, config_data = sc.get_sampler_args(model_files, user_core_models=user_core_models)
    #Uncomment this to see what's inside sampler args
    #print('\nsampler_args:\n', sampler_args)
    
    sampler_args['data'] = data_mu
    
    # update the states to proper link data to model state variables
    states = {k: v['states'] for k, v in sampler_args['models'].items()}
    states[1][-1] = list(data_file.keys())[0] # Pep3
    states[1][2] = list(data_file.keys())[1] # Ind
    states[1][0] = list(data_file.keys())[2] # Inde
    
    for model_num in sampler_args['models']:
        sampler_args['models'][model_num]['tspan'] = [tspan[model_num]]
        sampler_args['models'][model_num]['sd']    = state_sd[model_num]
        sampler_args['models'][model_num]['states'] = states[model_num]
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
        4. use pairplot based on the traces to identify the correlation between parameters
    '''
    
    # import synthetic data (protein profiles when deg_Pep decreased by 1.5x)
    test_data_file = Path.cwd() /'data'/'Predict_deg_Pep_1_5x.csv'
    test_data_Pep3 = pd.read_csv(test_data_file).to_numpy()
    
    '''Set the trials to ensure proper convergence'''
    sampler_args['trials'] = 7000
    
    ## Run sampler multiple times
    seeder = seed(sampler_args['guess'], sampler_args['fixed_parameters'], sampler_args['bounds'])
    traces = {}  
    X_error = [] 
    num_trace = 5
    for i in range(num_trace):
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
            plot_index[model_num]  = ['Fluor/OD', 'Ind2', 'Ind1e']
            titles[model_num]      = {'Fluor/OD': 'Pep Model '+ str(model_num), 
                                      'Ind2': 'Ind Model '+ str(model_num),
                                      'Ind1e': 'Inde Model '+ str(model_num)}
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
        
        #Rank models
        table = ac.calculate_ic(data   = sampler_args['data'], 
                                  models = sampler_args['models'], 
                                  priors = sampler_args['priors'],
                                  params = accepted.iloc[-10:]
                                  )
        
        ranked_table  = ac.rank_ic(table, inplace=False)
        print('\nRanked AIC table:\n', ranked_table.head())
        
        #export the ranked table into csv file inside the output folder
        ranked_table.to_csv(output_folder / 'ranked_table.csv') 
        
        best           = ranked_table.iloc[0]
        best_row_index = best['row']
        best_model_num = best['model_num']
        
        new_settings                  = config_data[best_model_num]
        new_settings['settings_name'] = 'LogicGate_OR_bestfitted'
        new_settings['parameters']    = cf.get_params_for_model(models    = sampler_args['models'], 
                                                                trace     = accepted, 
                                                                model_num = best_model_num,
                                                                row_index = best_row_index
                                                                )
        print('\nBest fitted parameters:\n', new_settings['parameters'])
        
        #Integrate the models numerically
        best_param = new_settings['parameters'].to_frame().T# .reindex([0])
        
        print(best_param)
        
        '''predict protein profiles when increasing deg_Pep''' 
        best_param.iloc[0, 2] = best_param.iloc[0, 2]*1.5
        ym, em = sim.integrate_models(models, best_param, multiply=True)
        
        plot_index  = {1: ['Pep3'],
                        }
        titles      = {1: {'Pep3': 'Protein'},
                        }
        labels      = {1: {1: 'Input=00', 2: 'Input=01', 3: 'Input=10', 4: 'Input=11'}
                        }
        
        figs, AX = sim.plot_model(plot_index, ym, titles=titles, labels=labels)
        
        AX[1]['Pep3'].plot(test_data_Pep3[:,0], test_data_Pep3[:,1:5], 'x', markersize = 6,label='Test Data')
        AX[1]['Pep3'].legend(loc='upper left', fontsize=14)
        
        # compute the SSE for the predictions against the synthetic data
        X = sum([np.sum((ym[1][i][best_row_index].iloc[:,-1] - test_data_Pep3[:,i])**2) for i in range(1,5)])
        X_error.append(X)
        
        
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
    
    print(X_error)
    
   