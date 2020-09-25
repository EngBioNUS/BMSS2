
import os
import numpy             as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import pandas            as pd
from   pathlib           import Path

import setup_bmss                as lab
import BMSS.models.model_handler as mh
import BMSS.models.setup_cf      as sc
import BMSS.aicanalysis          as ac
import BMSS.curvefitting         as cf
import BMSS.traceanalysis        as ta
import BMSS.models.setup_sim     as sm
import BMSS.simulation           as sim
import BMSS.models.setup_sen     as ss
import BMSS.sensitivityanalysis  as sn
import BMSS.models.setup_sg         as ssg
import BMSS.models.ia_results       as ir
import BMSS.strike_goldd_simplified as sg

plt.style.use(lab.styles['bmss_notebook_style'])

#Reset Plots
plt.close('all')

# Default settings for figure
#plt.rcdefaults()
plt.rcParams['font.size'] = 2
#plt.rcParams['axes.labelsize'] = 18


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
        elif 'Time' in column:
            scenarios = [column] + scenarios
        else:
            scenarios.append(column)
    
    print(len(scenarios))
          
    #Set up data_mu, data_sd, init, tspan
    for model_num in range(1, 12):
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
                data_mu[model_num][state][i] = df[scenario].values *1e-6/(18.814*30)
                data_sd[model_num][state][i] = df[scenario + 'std'].values *1e-6/(18.814*30)
                
                #Specific to the model in question
                init_val           = data_mu[model_num][state][i][0]              
                init[model_num][i] = {state:init_val}
    
    #Set up state_sd
    df_sd           = df[[scenario + 'std' for scenario in scenarios if 'Time' not in scenario]]
    state_sd[state] = df_sd.mean().mean()*1e-6/(18.814*30)
    
    #Add scenarios for reference    
    data_mu[1]['Fluor/OD'][-1] = scenarios
    data_sd[1]['Fluor/OD'][-1] = scenarios
    
    return data_mu, data_sd, init, state_sd, tspan


def modify_init(init_values, params, model_num, scenario_num, segment):
    #Always use a copy and not the original
    new_init = init_values.copy()
    
    if model_num in [1,2,3,4,5,6]:
        new_init[0] = 1
        new_init[2] = 1
    elif model_num in [7,8,9,10]:
        new_init[0] = 1
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


def modify_params_sa(init_values, params, model_num, scenario_num, segment):
    #Always use a copy and not the original
    new_params = params.copy()
    
    #Change value of inducer based on scenario_num
    if scenario_num == 1:
        new_params[-2] = 0.1
        new_params[-1] = 0.1
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


def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    '''Truncate the colormap so that we remove the extreme colors
    such as black and white.
    '''
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap
    

if __name__ == '__main__':
    
    #Import data
    data_file = Path.cwd() /'data'/'LogicGate_ORAraAtcTop10d37M9.csv'
    data_mu, data_sd, init, state_sd, tspan = read_data(data_file)
    print('\ninit:\n', init)
    
    #Set up core models and sampler arguments
    model_files = ['LogicGate_OR_Double_Delay_Degrade_ResCompete.ini',
                   'LogicGate_OR_Double_Delay_Delay_ResCompete.ini',
                   'LogicGate_OR_Double_Degrade_Delay_ResCompete.ini',
                   'LogicGate_OR_Double_Delay_Degrade.ini',
                   'LogicGate_OR_Double_Delay_Delay.ini',
                   'LogicGate_OR_Double_Degrade_Delay.ini',
                   'LogicGate_OR_Double_Delay.ini',
                   'LogicGate_OR_Double_DelayInput2.ini',
                   'LogicGate_OR_Double_Degrade.ini',
                   'LogicGate_OR_Double_DegradeInput2.ini',
                   'LogicGate_OR_Double.ini',
                   ]
    
    #List of model dicts
    core_models_list = [mh.from_config(filename) for filename in model_files]
    print(core_models_list)
    
    #Nested dict with system_type as first key to store the model dict
    user_core_models = {core_model['system_type']: core_model for core_model in core_models_list}
    print('\n\n', user_core_models)
    
    
    '''Run simulation using the same configuration file (run only the first model).
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
    
    #Integrate the models numerically
    ym, em = sim.integrate_models(models, params)
    
    #Define plot settings
    plot_index  = {1: ['Pep3'],
                   }
    titles      = {1: {'Pep3': 'Model 1 Protein'},
                   }
    labels      = {1: {1: 'Input=00', 2: 'Input=01', 3: 'Input=10', 4: 'Input=11'}
                   }
    
    figs, AX = sim.plot_model(plot_index, ym, titles=titles, labels=labels)
    
    #Export simulation results
    prefix = ''
    
    #A new folder will be created inside the output_folder using this directory.
    directory = output_folder / 'simulation_results'
    
    sim.export_simulation_results(ym, em, prefix=prefix, directory=directory)
    
    
    '''Run curvefitting and model selection using the same configuration file.
    The steps are as follows:
        1. prepare configuration .ini file (aside from core model information)
            - guess, priors, parameter_bounds, fixed_parameters,
        2. get_sampler_args
        3. update sampler_args with information from experimental data file
        4. run curve fitting algorithm
        5. plot results: can include simulation from guess (optional)
        6. plot traces to check for convergence
        7. calculate and rank aic
    '''
    
    sampler_args, config_data = sc.get_sampler_args(model_files, user_core_models=user_core_models)
    print('\nsampler_args:\n', sampler_args)
    
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
    
    #Run sampler
    traces    = {}    
    result    = cf.simulated_annealing(**sampler_args)
    accepted  = result['a']
    traces[1] = accepted

    #Export accepted dataframe into csv file
    accepted.to_csv(output_folder / 'accepted.csv')
    
    #Plot results
    plot_index = {}
    titles = {}
    labels = {}
    for model_num in sampler_args['models']:
        plot_index[model_num]  = ['Fluor/OD']
        titles[model_num]      = {'Fluor/OD': 'Pep Model '+ str(model_num)}
        labels[model_num]      = {1: 'Input=00', 2: 'Input=01', 3: 'Input=10', 4: 'Input=11'}
                     
    legend_args = {'loc': 'upper left'}
    
    #Plot the results into two figures for better visualization
    fig1 = plt.figure()
    fig2 = plt.figure()
    AX1 = [fig1.add_subplot(2, 4, i+1) for i in range(8)]
    AX2 = [fig2.add_subplot(1, 3, i+1) for i in range(3)]
    AX = {}
    for i in range(8):
        AX[i+1] = {'Fluor/OD': AX1[i]}
        
    for i in range(3):
        AX[i+9] = {'Fluor/OD': AX2[i]}
    
    figs, AX  = cf.plot(posterior   = accepted.iloc[-40::2], 
                        models      = sampler_args['models'], 
                        guess       = sampler_args['guess'],
                        data        = data_mu,
                        data_sd     = data_sd,
                        plot_index  = plot_index,
                        labels      = labels,
                        titles      = titles,
                        legend_args = legend_args,
                        figs        = [fig1, fig2],
                        AX          = AX
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
    print('\ntrace_params:\n', trace_params)
    print('\ntrace_AX:\n', trace_AX)
    print('\ntraces:\n', traces)
    
    #export the traces for all parameters into csv for ease of visualization
    traces[1].to_csv(output_folder / 'Traces_dataframe.csv')
    
    trace_figs, trace_AX = ta.plot_steps(traces, 
                                         skip        = sampler_args['fixed_parameters'], 
                                         legend_args = legend_args,
                                         figs        = trace_figs,
                                         AX          = trace_AX
                                         )
    print('\ntrace_AX\n', trace_AX)
    #modify the figure setting else all the labels overlapped.
    for tax in trace_AX.values():
        tax.set_xticks(tax.get_xticks()[::2])
        tax.set_yticks(tax.get_yticks()[::2])
        tax.tick_params(axis ='both', labelsize = 16)
        tax.xaxis.label.set_size(fontsize = 16)
        tax.yaxis.label.set_size(fontsize = 16)
    
    plt.tight_layout(pad = 1.0) # set spacing between figures
    
    #Rank models
    table = ac.calculate_aic(data   = sampler_args['data'], 
                             models = sampler_args['models'], 
                             priors = sampler_args['priors'],
                             params = accepted.iloc[-10:]
                             )
    
    ranked_table  = ac.rank_aic(table, inplace=False)
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
    
    
    '''Run A posteriori identifiability analysis.
    The steps are as follows:
        1. generate multiple seeds from the guess and bounds
        2. run curvefitting multiple times based on the generated seeds
        3. plot the trace figure for all the fitted parameters
        4. use pairplot based on the traces to identify the correlation between parameters
    '''
    
    #Run sampler multiple times
    seeder = seed(sampler_args['guess'], sampler_args['fixed_parameters'], sampler_args['bounds'])
    traces = {}    
    for i in range(2):
        print('Run ' + str(i+1))
        sampler_args['guess'] = seeder()
        result                = cf.simulated_annealing(**sampler_args)
        accepted              = result['a']
        traces[i+1]           = accepted.iloc[::5]#Thin the trace
    
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
    
    pairs = [['syn_mRNA1_1', 'syn_mRNA2_1'],
             ['syn_mRNA2_1', 'syn_mRNA3_1']
             ]
    
    pairplot_figs, pairplot_AX = ta.pairplot_steps(traces, pairs)
    
    
    '''Run a priori identifiability analysis (Strike-Goldd).
    The steps are as follows:
        1. prepare configuration file (aside from core model):
            init, input_conditions, fixed_parameters, measured_states
        2. read config data (nested dict with first key being the model num
            with the subdict contains information similar to those required
            for simulation)
        3. get sensitivity args from config_data and user_core_models
        4. update sensiitvity args in particular the key 'objective' by
            specifying the output response for SA
        5. use analyze wrapper function to run SA
        6. plot the results in heatmaps: first-order and second-order analysis results.
    '''
    
    #List of model dicts
    core_models_list = [mh.from_config(filename) for filename in model_files]
    print(core_models_list)
    
    #to ensure that user_core_models is the default one without any modification
    user_core_models = {core_model['system_type']: core_model for core_model in core_models_list}
    print('\n\n', user_core_models)
    
    config_data = {}
    config_data_ = mh.from_config(model_files[0])
    config_data[1] = config_data_
    print('\nconfig_data:\n', config_data)
    
    print('\nuser_core_models:\n', user_core_models)
    new_user_core_models = {config_data[model_num]['system_type']: user_core_models[config_data[model_num]['system_type']] for model_num in config_data}
    print('\nnew_user_core_models:\n', new_user_core_models)
    
    sg_args, config_data, variables = ssg.get_strike_goldd_args(model_files[0], user_core_models=new_user_core_models)
    print('\nsg_args:\n', sg_args)
    print('\nvariables:\n', variables)
    
    
    dst        = {}
    sg_results = sg.analyze_sg_args(sg_args, dst=dst)
    outfile   = 'sg_results.yaml'
    yaml_dict = ir.export_sg_results(sg_results, variables, config_data, user_core_models=new_user_core_models, filename=outfile)
    
    
    '''Run sensitivity analysis (SA) on the selected model (best model).
    The steps are as follows:
        1. prepare configuration file (aside from core model):
            tspan, parameter_bounds, fixed_parameters
        2. read config data (nested dict with first key being the model num
            with the subdict contains information similar to those required
            for simulation)
        3. get sensitivity args from config_data and user_core_models
        4. update sensiitvity args in particular the key 'objective' by
            specifying the output response for SA
        5. use analyze wrapper function to run SA
        6. plot the results in heatmaps: first-order and second-order analysis results.
        
    '''
    
    config_data = ss.from_config(model_files[0])
    print('\nconfig_data:\n', config_data)
    
    new_user_core_models = {config_data[model_num]['system_type']: user_core_models[config_data[model_num]['system_type']] for model_num in config_data}
    print('\nuser_core_models:\n', new_user_core_models)
    
    sensitivity_args = ss.get_sensitivity_args(config_data, user_core_models=new_user_core_models)
    print('\nsensitivity_args:\n', sensitivity_args)
    print('\nsensitivity_args keys:\n', sensitivity_args.keys())
    
    def Pep3_yield(y, t, params):
        final_Pep3 = y[-1, -1]
        
        return final_Pep3
    
    sensitivity_args['models'][1]['int_args']['modify_init'] = modify_init
    sensitivity_args['models'][1]['int_args']['modify_params'] = modify_params_sa
    sensitivity_args['N'] = 500
    sensitivity_args['objective'] = {1: [Pep3_yield]}
    
#    for key in sensitivity_args['fixed_parameters']:
#        sensitivity_args['parameter_bounds'].pop(key, None)
    
    #To debug, there will be an error regarding the len of params, so have to turn this off first   
    sensitivity_args['parameter_bounds'] = {}
        
    print('\nparameter_bounds:\n', len(sensitivity_args['parameter_bounds']))
    print('\nparams:\n', sensitivity_args['params'])
    
    analysis_result, em, samples, problems = sn.analyze(**sensitivity_args)
    print('\nanalysis_result\n', analysis_result)
    
    #Plot settings
    titles = {1: {Pep3_yield: 'Pep output'}
              }
    cmap = plt.get_cmap('rocket')
    new_cmap = truncate_colormap(cmap, 0.1, 0.9)
    sn.plot_first_order(analysis_result, problems=problems, titles=titles,\
                        analysis_type=sensitivity_args['analysis_type'],\
                        figs=None, AX=None, cmap = new_cmap)

    sn.plot_second_order(analysis_result, problems=problems, titles=titles,\
                         analysis_type=sensitivity_args['analysis_type'],\
                         figs=None, AX=None)
    
    
    