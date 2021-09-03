import matplotlib.pyplot as plt

import setup_bmss                as lab
import BMSS.models.model_handler as mh
import BMSS.models.setup_sim     as sm
import BMSS.simulation           as sim

'''
Tutorial 8 Part 1: Introduction to simulation datastructures
- Introduction to the models and params data structure
- Learn how to use .ini files to manage sensitivity settings/arguments
'''

plt.style.use(lab.styles['dark_style'])
plt.close('all')

if __name__ == '__main__':
    '''
    
    '''
    
    '''
    1. Reading the Core Models
    '''
    
    user_core_models = 'MainModel', 'Submodel1', 'Submodel2'
    user_core_models = {i: mh.from_config(i+'.ini') for i in user_core_models}
    
    filename = 'settings_sim_1.ini'
    models, params, config_data = sm.get_models_and_params(filename, user_core_models)
    
    ym, _ = sim.integrate_models(models, params)
    
    plot_index  = {1: ['x0', 'x1'],
                    }
    titles      = {1: {'x0': 'x0', 'x1': 'x1'},
                    }
    labels      = {1: {1: 'Scenario 1'}
                    }
    
    figs, AX = sim.plot_model(plot_index, ym, titles=titles, labels=labels)
    