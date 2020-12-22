import matplotlib.pyplot as plt
import numpy             as np
import pandas            as pd

import setup_bmss                   as lab
import BMSS.models.ia_results       as ir
import BMSS.models.model_handler    as mh
import BMSS.models.settings_handler as sh
import BMSS.models.setup_cf         as sc
import BMSS.models.setup_sg         as ssg
import BMSS.aicanalysis             as ac
import BMSS.curvefitting            as cf
import BMSS.strike_goldd_simplified as sg
import BMSS.traceanalysis           as ta
from   read_data                    import read_data

'''
This file shows you all the steps required for curve-fitting and assumes you
have either gone through Example 1 or Tutorial 2.

In this example, we want to characterize the pTet promoter given a set of 
experimental data. We have three models we want to consider:
    1. A model provided by BMSS in the database
    2. A model provided by the user that has previously been added to the database
    3. A model provided by the user that has not been added to the database


'''

#Global variables
inducer_conc = [25, 12.5, 6.25, 3.125, 1.56, 0]
inducer_conc = {i+1: inducer_conc[i] for i in range(len(inducer_conc)) }

def modify_params(init_values, params, model_num, scenario_num, segment):
    global inducer_conc
    #Always use a copy and not the original
    new_params   = params.copy()
    
    #Change inducer conc based on scenario_num
    if model_num == 1:
        new_params[-1] = inducer_conc[scenario_num]
    
    #Change x_max (maximum OD) based on scenario
    if scenario_num == 1:
        new_params[1] = 0.91
    else:
        new_params[1] = 1.0
        
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
    '''
    0. Setting Up This Example
    '''
    
    '''
    This step adds the second model in the file to the database so that this 
    example can run smoothly.
    
    '''
    
    try:
        mh.quick_search('Inducible, Double, DegradingInducer, LogisticGrowth')
    except:
        mh.config_to_database('Inducible_Double_DegradingInducer_LogisticGrowth.ini')
    
    '''
    1. Create a Custom Model
    '''
    model_files = ['Inducible_Double_Uptake_LogisticGrowth.ini']
    
    user_core_models = [mh.from_config(filename) for filename in model_files]
    user_core_models = {core_model['system_type']: core_model for core_model in user_core_models}
    
    '''
    user_core_models is a dictionary containing core_model data structures.
    Use the following code below to see what's inside.
    
    for key in user_core_models:
        print(key)
        print(user_core_models[key])
        print()
    '''
    
    '''
    2. Create Settings Files for Analysis
    '''
    
    '''
    Each of type of analysis in BMSS can make use of a settings file that allows
    you to set up the relevant arguments required by the BMSS's functions. This
    file(s) is in .ini format and contains information relevant to the arguments
    required by BMSS's functions.
    
    There is nothing to stop you from coding the arguments yourself. However,
    making use of settings files provides the following advantages:
        1. Cleans your code by having your script separate from the input arguments 
        2. Reduces the amount of typing and potential errors when setting up
        3. Allows easy sharing of the inputs
        4. Prevents accidental modification to your script when changing the inputs
        
    
    The settings file(s) itself can be generated automatically by calling the 
    appropriate version of the function make_settings_template which is shown below.
    '''
    
    system_types_settings_names = [('BMSS, Logistic, Inducible', 'pTet'),
                                   ('Inducible, Double, DegradingInducer, LogisticGrowth', None),
                                   ('Inducible, Double, Uptake, LogisticGrowth', None)
                                   ]
    
    sc.make_settings_template(system_types_settings_names, 
                              filename         = 'settings_template_cf.ini',
                              user_core_models = user_core_models
                              )
    
    '''
    system_types_settings_names is a list of pairs where the first element is the
    system_type being used in the analysis and the second element is the name 
    of a set of settings that has previously been saved in the database (if any).
    
    If no settings for that system_type have previously been saved or you do not 
    want to use any of the saved settings available, set the second element to
    None.
    
    Open the file settings_template.ini and check its contents. A set of settings
    for the first model indexed under 'pTet' has been used to fill up the values.
    However, no values have been provided for the other two models. You have to 
    fill them up yourself.
    '''
    
    '''
    2. Reading Analysis Settings
    '''
    
    '''
    The function below combines the information in the settings files with 
    information from the core_model data structure to generate the arguments.
    If a system_type specified in the settings file is not in user_core_models,
    BMSS will search the database for that system_type and then extract the 
    relevant information.
    
    Since the first two models are already in the database, only the third model
    needs to be provided via user_core_models. In addition, a .py file containing
    a function for numerical integration of the third model will be generated
    in the current directory.
    
    Note that the settings can be spread over multiple files in which case, 
    settings_files should be a list(or tuple) of filenames.
    '''
    
    #The actual settings file for this case study
    settings_files = 'settings.ini'
    
    sampler_args, config_data = sc.get_sampler_args(settings_files, user_core_models=user_core_models)
    
    '''
    config_data is a dictionary corresponding to the settings that were extracted
    from the settings file. Use the code below to see what's inside.
    
    print('Printing contents of config_data[1]')
    for key in config_data[1]:
        print(key)
        print(config_data[1][key])
        print()
        
    sampler_args is a dictionary that can be directly fed into the simulated
    annealing algorithm in BMSS
    
    '''
    
    '''
    3. Reading Experimental Data
    '''
    
    data_files = {'Pep' : 'data/pTet_promoter_rfp.csv',
                  'OD'  : 'data/pTet_promoter_od.csv'
                  }
    data_mu, data_sd, init, state_sd, tspan = read_data(data_files, n_models=len(config_data))
    
    '''
    sampler_args is only half-complete as curve-fitting requires experimental 
    data. We will now read the csv files containing this data. In this example,
    the data in the csv has already undergone preprocessing including subtraction 
    of blank samples and calculation of the means and standard deviation for 
    each time point. The function read_data reads this in and extracts other 
    information such the initial values of each state, their sd and the time points.
    
    Note however that BMSS does not enforce a particular format for storing 
    raw experimental data. If you want a function that performs preprocessing,
    you can refer to Tutorial 5 Part 2.
    '''
    
    '''
    4. Updating Function Arguments
    '''
    
    '''
    The models data structure is a dictionary containing all information required
    for numerical integration of a particular model. It has been indexed under 
    "models". You can see what's  inside using this code.
    
    print('Printing the first model')
    for key in sampler_args['models'][1]:
        print(key)
        print(sampler_args['models'][1][key])
        print()
    
    During curve-fitting, our algorithm will calculate the SSE by comparing the 
    results of integrating models[model_num] with those of the data[model_num]. 
    
    However, the states in the model may have been differently named from the 
    ones in the data.In addition, some models have states that were not measured 
    during the experiment.
    
    How do we ensure BMSS performs the comparison correctly?
    '''
    
    sampler_args['models'][1]['states'] = ['OD', 'Pep']
    sampler_args['models'][2]['states'] = ['OD', 'ind', 'm', 'Pep']
    sampler_args['models'][3]['states'] = ['OD', 'inde', 'indi', 'm', 'Pep']
    
    '''
    The first thing we do is to update the names of the states in each model to 
    match the states specified in data.
    
    For example, the default states in the first model are x and h which represent
    biomass and protein respectively. These correspond to OD and Pep in the data.
    We thus change the states in the models data structure to reflect this. States
    that were not measured and are not in the experimental data can be left unchanged.
    '''
    
    #The inducer concentration is a state for the second and third models
    #We need to incorporate them into the initial values.
    for scenario in inducer_conc:
        init[2][scenario]['ind'] = inducer_conc[scenario]
        init[3][scenario]['ind'] = inducer_conc[scenario]
    
    for model_num in sampler_args['models']:
        sampler_args['models'][model_num]['tspan'] = [tspan]
        sampler_args['models'][model_num]['sd']    = state_sd
        
        model_init = {scenario: [init[model_num][scenario].get(state, 0) for state in sampler_args['models'][model_num]['states']] for scenario in init[model_num]}
        
        sampler_args['models'][model_num]['init']                      = model_init
        sampler_args['models'][model_num]['int_args']['modify_params'] = modify_params
    
    '''
    We then update the other arguments in the models accordingly.
    '''
    
    sampler_args['data'] = data_mu
    
    '''
    Finally we add the data to sampler_args
    '''
    
    '''
    5. Running the Sampler
    '''
    traces    = {}    
    result    = cf.simulated_annealing(**sampler_args)
    accepted  = result['a']
    posterior = accepted.iloc[-40::4]
    traces[1] = accepted.iloc[::5]#Thin the trace
    
    '''
    accepted is a pandas DataFrame containing the parameter sets sampled that 
    were accepted.

    For simplicity, we take the posterior by sampling from the last 40 steps.
    '''
    
    inducer_conc_str = {key: str(inducer_conc[key]) for key in inducer_conc}
    
    plot_index  = {1: ['OD', 'Pep'],
                    2: ['OD', 'Pep', 'm', 'ind'],
                    3: ['OD', 'Pep', 'm', 'inde'],
                    }
    titles      = {1: {'OD':'OD Model 1', 'Pep': 'Pep Model 1'},
                    2: {'OD':'OD Model 2', 'Pep': 'Pep Model 2', 'm': 'mRNA Model 2', 'ind' : 'Inducer Model 2'},
                    3: {'OD':'OD Model 2', 'Pep': 'Pep Model 2', 'm': 'mRNA Model 2', 'inde': 'Inducer Model 2'}
                    }
    labels      = {1: inducer_conc_str,
                    2: inducer_conc_str,
                    3: inducer_conc_str
                    }
    legend_args = {'loc': 'upper left'}
    
    figs, AX  = cf.plot(posterior  = posterior, 
                        models     = sampler_args['models'],  
                        data       = data_mu,
                        data_sd    = data_sd,
                        plot_index = plot_index,
                        labels     = labels,
                        titles     = titles,
                        legend_args= legend_args,
                        figs       = None,
                        AX         = None
                        )
    
    '''
    6. Model Ranking with AIC Calculation
    '''
    
    table = ac.calculate_aic(data   = sampler_args['data'], 
                             models = sampler_args['models'], 
                             priors = sampler_args['priors'],
                             params = posterior
                             )
    
    ranked_table = ac.rank_aic(table, aic_column_name='AIC Value', inplace=False)
    
    '''
    rank_aic accepts a DataFrame containing AIC values indexed under 
    aic_column_name. It then sorts the DataFrame and adds columns for the normalized
    AIC and the evidence for that model. The original columns in the input
    DataFrame remain untouched.
    
    rank_aic isn't picky about what indices and columns you use as long as your 
    DataFrame has its AIC values indexed under the argument aic_column_name.
    '''
    
    '''
    7. Saving the Results
    '''
    
    '''
    Saving the models and settings allows us to reuse them without having to
    specify them each time. The steps below 
    
    1. Add the best model to the database (if it is not already inside) 
    2. Create a settings data structure based on the best settings
    3. Add the settings to the database
    '''
    
    best             = ranked_table.iloc[0]
    best_row_index   = best['row']
    best_model_num   = best['model_num']
    best_system_type = config_data[best_model_num]['system_type']
    
    #1. Add the best model to the database (if it is not already inside) 
    if best_system_type in user_core_models:
        best_core_model = user_core_models[best_system_type]
        mh.add_to_database(best_core_model)
    
    #2. Create a settings data structure based on the best settings
    new_settings                  = config_data[best_model_num]
    new_settings['settings_name'] = 'Example_5_pTet'
    new_settings['parameters']    = cf.get_params_for_model(models    = sampler_args['models'], 
                                                            trace     = accepted, 
                                                            model_num = best_model_num,
                                                            row_index = best_row_index
                                                            )
    
    new_settings = sh.make_settings(**new_settings)
    
    #3. Add the settings to the database
    sh.add_to_database(new_settings)
    
    #4. View the settings database
    
    
    '''
    8. A Posteriori Identifiability Analysis
    '''
    
    '''
    BMSS's trace plotting functions are built for multi-trace operations. This
    allows you to easily check if your simulations converge to same region.
    '''
    
    seeder = seed(sampler_args['guess'], sampler_args['fixed_parameters'], sampler_args['bounds'])
    
    for i in range(10):
        print('Run ' + str(i+1))
        sampler_args['guess'] = seeder()
        result                = cf.simulated_annealing(**sampler_args)
        accepted              = result['a']
        traces[i+1]           = accepted.iloc[::5]#Thin the trace
    
    for model_num in sampler_args['models']:
        params       = sampler_args['models'][model_num]['params'] 
        traces_      = {key: traces[key][params] for key in traces}
        t_figs, t_AX = ta.plot_steps(traces_, 
                                      skip        = sampler_args['fixed_parameters'], 
                                      legend_args = legend_args
                                      )
        
        k_figs, k_AX = ta.plot_steps(traces_, 
                                     skip        = sampler_args['fixed_parameters'], 
                                     legend_args = legend_args
                                     )
        h_figs, h_AX = ta.plot_steps(traces_, 
                                     skip        = sampler_args['fixed_parameters'], 
                                     legend_args = legend_args
                                     )
        
    '''
    To save time, we recommend you thin the trace at your discretion!
    '''
    
    '''
    9. A Priori Identifiability Analysis
    '''
        
    '''
    BMSS allows you perform algebraic identifiability analysi using the STRIKE-GOLDD
    algorithm developed by Villaverde et al. which makes use of symbolic algebra
    and Lie derivatives to assess parameter identifiability.
    '''
    
    ssg.make_settings_template(system_types_settings_names, 
                                filename         = 'settings_template_sg.ini', 
                                user_core_models = user_core_models)
    
    '''
    Once again, template files for the settings can be generated.
    '''
    
    sg_args, config_data, variables = ssg.get_strike_goldd_args('settings_sg.ini', 
                                                                user_core_models = user_core_models,
                                                                write_file       = True
                                                                )
    
    '''
    The optional argument dst allows you to supply your own dictionary to which the
    results will be added after each iteration. This allows you to thread and/or
    save the results before all the iterations have been completed. Just use an
    empty dictionary for dst.
    '''
    #Run strike-goldd algorithm
    #Details in Tutorial 7 Part 2
    dst        = {}
    sg_results = sg.analyze_sg_args(sg_args, dst=dst)
    outfile    = 'sg_results.yaml'
    yaml_dict  = ir.export_sg_results(sg_results, variables, config_data, user_core_models=user_core_models, filename=outfile)
    
    '''
    print('Printing yaml_dict[1]', '{')
    for key in yaml_dict[1]:
        print(key, ':', yaml_dict[1][key])
    print('}')
    '''
    
    
    
    
    
    
    
    