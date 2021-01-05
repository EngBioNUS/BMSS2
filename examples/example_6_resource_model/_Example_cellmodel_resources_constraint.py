
import matplotlib.pyplot as plt

import setup_bmss                as lab
import BMSS.models.model_handler as mh
import BMSS.models.setup_sim     as sm
import BMSS.simulation           as sim

plt.style.use(lab.styles['bmss_notebook_style'])

#Reset Plots
plt.close('all')

def modify_params(init_values, params, model_num, scenario_num, segment):
    #Always use a copy and not the original
    new_params = params.copy()
    
    #Change value of inducer based on scenario_num
    if segment == 1:
        new_params[-2] = 1
        new_params[-1] = 1
    else:
        new_params[-2] = 0
        new_params[-1] = 0
        
    return new_params


if __name__ == '__main__':
    
    #Set up core models and sampler arguments
    filename = 'CellModel_CellularResources_ProteomeAllocation_RibosomeLimitation.ini' 
    
    core_model = mh.from_config(filename)
    user_core_models = {core_model['system_type']: core_model}
    
    print('core_model:\n', core_model)
    
    #Get argument for simulation
    models, params, config_data = sm.get_models_and_params(filename, user_core_models=user_core_models)
    print('\nModels:\n', models)
    print('\nparams:\n', params)
    
    models[1]['int_args']['modify_params'] = modify_params
    print('\nUpdated params:\n', params)
    
    #Integrate the models numerically
    ym, em = sim.integrate_models(models, params)
    print('\nym:\n', ym[1][1][0].info())
    
    #Define plot settings
    plot_index  = {1: ['N', 's0', 'r', 'a'],
                   }
    titles      = {1: {'N': 'N - Cell Number', 's0':'s0 - Extracellular nutrient',
                       'r': 'r - Ribosome', 'a': 'a - Energy'},
                   }

    #Only plot the last 600 mins ignoring the first 1e5 mins of steady-state run
    #which is required to form the initial conditions for this resource model
    ymedit = ym.copy()
    ymedit[1][1][0] = ym[1][1][0].iloc[1000001:] #state dataframe
    ymedit[1][0] = ym[1][0][-60000:-1] #Time array
    print('\nymedit:\n', ymedit[1][1][0].info())
    
    figs, AX = sim.plot_model(plot_index, ymedit, titles=titles)

    
    