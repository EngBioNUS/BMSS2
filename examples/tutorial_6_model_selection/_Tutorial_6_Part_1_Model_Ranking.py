import matplotlib.pyplot as plt
import numpy             as np
import pandas            as pd
from   numba             import jit

import setup_bmss                   as lab
import BMSS.models.settings_handler as sh
import BMSS.models.setup_cf         as sc
import BMSS.aicanalysis             as ac
import BMSS.curvefitting            as cf

plt.style.use(lab.styles['bmss_notebook_style'])

#Reset Plots
plt.close('all')

'''
Tutorial 6 Part 2: Advanced options for curve-fitting
- Use scipy's optimizers
- Plot extra variables
'''

from _preprocessing import (data, data_mu, data_sd, init, state_sd, tspan, 
                            sampler_args, config_data
                            )

if __name__ == '__main__':

    '''
    The steps for preprocessing are the same as in Tutorial 5 Part 2 and have been
    moved to _preprocessing.py. 
    '''
    
    result = cf.simulated_annealing(**sampler_args)
    
    '''
    The return value is a dictionary with the following values.
    'a': The accepted samples as a DataFrame
    'r': The rejected samples as a DataFrame if applicable
    's': The scipy return value if applicable
    'f': The full trace including calls to local optimizers if applicable
    '''
    accepted = result['a']
    
    '''
    In order to calculate the AIC, we need the data, models, priors and
    parameters for evaluation. 
    '''
    
    aic = ac.calculate_aic(data   = sampler_args['data'], 
                           models = sampler_args['models'], 
                           priors = sampler_args['priors'],
                           params = accepted.iloc[-10:])
    
    print('AIC of each row of params for each model.')
    print(aic)
    print()
    
    '''
    rank_aic accepts a DataFrame containing AIC values indexed under 
    aic_column_name. It then sorts the DataFrame and adds columns for the normalized
    AIC and the evidence for that model. The original columns in the input
    DataFrame remain untouched.
    
    As can be seen from the result, rank_aic isn't picky about what indices and 
    columns you use as long as your DataFrame has its AIC values indexed under aic_column_name.
    '''
    
    table         = pd.DataFrame(aic.stack().reset_index())
    table.columns = ['row', 'model_num', 'AIC Value']
    ranked_table  = ac.rank_aic(table, aic_column_name='AIC Value', inplace=False)
    
    '''
    Plots
    '''
    plot_index = {1: ['OD600', 'Glu', 'Fluor']
                  }
    
    titles     = {1: dict(zip(plot_index[1], plot_index[1]))
                  }
    
    #Create our own Figure and Axes objects for cutom layouts
    fig = plt.figure()
    AX_ = [fig.add_subplot(3, 1, i+1) for i in range(3)]
    AX  = {1: {'OD600'  : AX_[0],
                'Fluor' : AX_[1],
                'Glu'   : AX_[2]
                }
            }
    cf.plot(posterior  = accepted.tail(10), 
            models     = sampler_args['models'],
            guess      = sampler_args['guess'],
            data       = data_mu,
            plot_index = plot_index,
            titles     = titles,
            figs       = [fig],
            AX         = AX
            )
    
    '''
    After choosing the best model and its fitted parameters, we can convert it into 
    a settings data structure so we can reuse it as a template in the future.
    '''
    
    best             = ranked_table.iloc[0]
    best_model_num   = best['model_num']
    best_row         = accepted.iloc[best['row']]
    best_param_names = sampler_args['models'][best_model_num]['params']
    
    
    new_settings = config_data[best_model_num]
    new_settings['settings_name'] = 'Tutorial_6_GFP'
    new_settings['parameters']    = best_row[best_param_names]
    
    '''
    We now call the constructor for the settings data structure. Once the new settings
    have been created, we can add it to the database if we wish.
    
    Note that information such as sa_args cannot be stored as settings and will
    be ignored.
    '''
    new_settings = sh.make_settings(**new_settings)
    sh.add_to_database(new_settings)
    