import matplotlib.pyplot as plt
import numpy             as np
import pandas            as pd

import setup_bmss                   as lab
import BMSS.models.model_handler    as mh
import BMSS.models.settings_handler as sh
import BMSS.models.setup_cf         as sc
import BMSS.icanalysis              as ac
import BMSS.curvefitting            as cf
import BMSS.traceanalysis           as ta
from   read_data                    import read_data

'''
Example 3 Part 2: IPTG/pLAC promoter
'''

plt.style.use(lab.styles['dark_style'])

#Reset Plots
plt.close('all')

def modify_params(init_values, params, model_num, scenario_num, segment):
    #Always use a copy and not the original
    new_params   = params.copy()
    inducer_conc = [0, 1.56, 3.1, 6.125, 12.5, 25, 50, 100, 500]
    
    if model_num == 1 or model_num == 2:
        #Change inducer conc based on scenario
        new_params[-1] = inducer_conc[scenario_num-1]
    
    #Change x_max (maximum OD) based on scenario
    if scenario_num < 7:
        new_params[1] = 0.96
    else:
        new_params[1] = 1.12
    
    return new_params

#Plot settings   
if __name__ == '__main__':
    
    inducer_conc = [0, 1.56, 3.1, 6.125, 12.5, 25, 50, 100, 500]
    inducer_conc = {i+1: inducer_conc[i] for i in range(len(inducer_conc)) }
    
    #Set up core models and sampler arguments
    #Details in Tutorial 5 Parts 1 and 2
    model_files = ['Inducible_Single_LogisticGrowth.ini',
                   'Inducible_Double_LogisticGrowth.ini',
                   'Inducible_Double_DegradingInducer_LogisticGrowth.ini',
                   'Inducible_Double_Uptake_LogisticGrowth.ini'
                   ]
    
    settings_files = model_files
    
    user_core_models = [mh.from_config(filename) for filename in model_files]
    user_core_models = {core_model['system_type']: core_model for core_model in user_core_models}
    
    sampler_args, config_data = sc.get_sampler_args(settings_files, user_core_models=user_core_models)
    
    #Import data
    #Details in Tutorial 4 Part 2
    #Function for importing the data is different from the one the tutorial
    #as the blanks and means have already been accounted for.
    #Data structures are still the same
    data_files = {'Fluor/OD' : 'data/plac_promoter_rfp.csv',
                  'OD'       : 'data/plac_promoter_od.csv'
                  }
    data_mu, data_sd, init, state_sd, tspan = read_data(data_files, n_models=len(config_data))
    
    #Update sampler_args with the information from the data
    for scenario in init[3]:
        init[3][scenario]['ind'] = inducer_conc[scenario]
    for scenario in init[4]:
        init[4][scenario]['inde'] = inducer_conc[scenario]
   
    sampler_args['models'][1]['states'] = ['OD', 'Fluor/OD']
    sampler_args['models'][2]['states'] = ['OD', 'm', 'Fluor/OD']
    sampler_args['models'][3]['states'] = ['OD', 'ind', 'm', 'Fluor/OD']
    sampler_args['models'][4]['states'] = ['OD', 'inde', 'indi', 'm', 'Fluor/OD']
    sampler_args['data']                = data_mu
    
    for model_num in sampler_args['models']:
        sampler_args['models'][model_num]['tspan'] = [tspan]
        sampler_args['models'][model_num]['sd']    = state_sd
        
        model_init = {scenario: [init[model_num][scenario].get(state, 0) for state in sampler_args['models'][model_num]['states']] for scenario in init[model_num]}
        
        sampler_args['models'][model_num]['init']                      = model_init
        sampler_args['models'][model_num]['int_args']['modify_params'] = modify_params
    
    traces    = {}    
    result    = cf.simulated_annealing(**sampler_args)
    accepted  = result['a']
    posterior = accepted.iloc[-40::4]
    traces[1] = accepted
    
    '''
    In order to calculate the AIC, we need the data, models, priors and
    parameters for evaluation. 
    '''
    table = ac.calculate_ic(data   = sampler_args['data'], 
                            models = sampler_args['models'], 
                            priors = sampler_args['priors'],
                            params = posterior
                            )
    
    '''
    rank_aic accepts a DataFrame containing AIC values. It then sorts the DataFrame 
    and adds columns for the normalized AIC and the evidence for that model. The 
    original columns in the input DataFrame remain untouched.
    
    As can be seen from the result, rank_aic isn't picky about what indices and 
    columns you use as long as your DataFrame has its AIC values indexed under aic_column_name.
    '''
    
    ranked_table = ac.rank_ic(table, inplace=False)
    
    '''
    After choosing the best model and its fitted parameters, we can convert it into 
    a settings data structure so we can reuse it as a template in the future.
    '''
    
    best             = ranked_table.iloc[0]
    best_row_index   = best['row']
    best_model_num   = best['model_num']
    best_system_type = config_data[best_model_num]['system_type']
    
    new_settings                  = config_data[best_model_num]
    new_settings['settings_name'] = 'Example_3_pLac'
    new_settings['parameters']    = cf.get_params_for_model(models    = sampler_args['models'], 
                                                            trace     = accepted, 
                                                            model_num = best_model_num,
                                                            row_index = best_row_index
                                                            )
    
    '''
    We now call the constructor for the settings data structure. Once the new settings
    have been created, we can add it to the database if we wish.
    
    Note that information such as sa_args cannot be stored as settings and will
    be ignored.
    '''
    new_settings = sh.make_settings(**new_settings, 
                                    user_core_model=user_core_models[best_system_type])
    
    inducer_conc_str = {key: str(inducer_conc[key]) for key in inducer_conc}
    
    plot_index  = {1: ['OD', 'Fluor/OD'],
                   2: ['OD', 'Fluor/OD', 'm'],
                   3: ['OD', 'Fluor/OD', 'm', 'ind'],
                   4: ['OD', 'Fluor/OD', 'm', 'indi']
                   }
    titles      = {1: {'OD':'OD', 'Fluor/OD': 'Pep'},
                   2: {'OD':'OD','Fluor/OD': 'Pep', 'm': 'mRNA'},
                   3: {'OD':'OD','Fluor/OD': 'Pep', 'm': 'mRNA', 'ind': 'Inducer'},
                   4: {'OD':'OD','Fluor/OD': 'Pep', 'm': 'mRNA', 'indi': 'Inducer(Internal)'}
                   }
    labels      = {1: inducer_conc_str,
                   2: inducer_conc_str,
                   3: inducer_conc_str,
                   4: inducer_conc_str
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
    
    for model_num in sampler_args['models']:
        params   = sampler_args['models'][model_num]['params'] 
        traces_  = {key: traces[key][params] for key in traces}
        figs, AX = ta.plot_steps(traces_, 
                                  skip=sampler_args['fixed_parameters'], 
                                  legend_args=legend_args
                                  )
