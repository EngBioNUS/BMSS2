import matplotlib.pyplot as plt
import numpy             as np
import pandas            as pd
import setup_bmss        as lab

#BMSS import statements
import BMSS.models.model_handler as mh
import BMSS.models.setup_sim     as sm
import BMSS.simulation           as sim

plt.close('all')

#Set up core models and sampler arguments
model_files = ['LogicGate_OR_Double_Degrade_Delay.ini',
               ]

#List of model dicts
user_core_models = {}

for filename in model_files:
    core_model                    = mh.from_config(filename)
    system_type                   = core_model['system_type']
    user_core_models[system_type] = core_model

print('User core models', list(user_core_models.keys()))

#Get arguments for simulation
models, params, config_data = sm.get_models_and_params('sim_settings.ini', user_core_models=user_core_models)

def modify_Double_Degrade_Delay(init_values, params, model_num, scenario_num, segment):
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

models[1]['int_args']['modify_params'] = modify_Double_Degrade_Delay

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
    