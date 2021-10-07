import os
import numpy             as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
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
import BMSS.models.setup_sen     as ss
import BMSS.sensitivityanalysis  as sn
import BMSS.models.setup_sg         as ssg
import BMSS.models.ia_results       as ir
import BMSS.strike_goldd_simplified as sg

plt.close('all')
plt.style.use(lab.styles['dark_style'])

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
      
    #Set up data_mu, data_sd, init, tspan
    for model_num in range(1, 4):
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

#Set up core models and sampler arguments
model_files = ['LogicGate_OR_Double_Degrade_Delay.ini',
               'LogicGate_OR_Double.ini',
               'LogicGate_OR_Double_Delay_Degrade_ResCompete.ini'
               ]

#List of model dicts
user_core_models = {}

for filename in model_files:
    core_model                    = mh.from_config(filename)
    system_type                   = core_model['system_type']
    user_core_models[system_type] = core_model

print('User core models', list(user_core_models.keys()))

data_file = Path.cwd()/'data'/'LogicGate_ORAraAtcTop10d37M9.csv'
data_mu, data_sd, init, state_sd, tspan = read_data(data_file)

sampler_args, config_data = sc.get_sampler_args('cf_settings.ini', user_core_models=user_core_models)

sampler_args['data'] = data_mu

for model_num in sampler_args['models']:
    sampler_args['models'][model_num]['tspan'] = [tspan]
    sampler_args['models'][model_num]['sd']    = state_sd
    sampler_args['models'][model_num]['states'][-1] = 'Fluor/OD'
    sampler_args['models'][model_num]['int_args']['modify_params'] = modify_params

#Run sampler
traces    = {}    
result    = cf.simulated_annealing(**sampler_args)
accepted  = result['a']
traces[1] = accepted

#Export accepted dataframe into csv file
accepted.to_csv('Output_files/accepted.csv')

#Plot results
plot_index  = {1: ['Fluor/OD'], 
               2: ['Fluor/OD'], 
               3: ['Fluor/OD']
               }
titles      = {1: {'Fluor/OD': 'Pep Model 1'}, 
               2: {'Fluor/OD': 'Pep Model 2'}, 
               3: {'Fluor/OD': 'Pep Model 3'}
               }
labels      = {1: {1: 'Input=00', 2: 'Input=01', 3: 'Input=10', 4: 'Input=11'},
               2: {1: 'Input=00', 2: 'Input=01', 3: 'Input=10', 4: 'Input=11'},
               3: {1: 'Input=00', 2: 'Input=01', 3: 'Input=10', 4: 'Input=11'}
               }
legend_args = {'loc': 'upper left'}

#Plot the results into two figures for better visualization
fig1, AX1 = plt.subplots(1, 3)
# fig2, AX2 = plt.subplots(1, 3)
AX        = {1: {'Fluor/OD' : AX1[0]},
             2: {'Fluor/OD' : AX1[1]},
             3: {'Fluor/OD' : AX1[2]},
             }

figs, AX  = cf.plot(posterior   = accepted.iloc[-20::2], 
                    models      = sampler_args['models'], 
                    guess       = sampler_args['guess'],
                    data        = data_mu,
                    data_sd     = data_sd,
                    plot_index  = plot_index,
                    labels      = labels,
                    titles      = titles,
                    legend_args = legend_args,
                    AX          = AX
                    )

#Rank models
table = ac.calculate_ic(data   = sampler_args['data'], 
                        models = sampler_args['models'], 
                        priors = sampler_args['priors'],
                        params = accepted
                        )

ranked_table  = ac.rank_ic(table, inplace=False)
print('\nRanked AIC table:\n', ranked_table.head())

#Export the ranked table into csv file inside the output folder
ranked_table.to_csv('ranked_table.csv') 

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


