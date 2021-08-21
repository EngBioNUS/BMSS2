import matplotlib.pyplot as plt
import numpy             as np
import pandas            as pd
from   numba             import jit

import setup_bmss              as lab
import BMSS.models.setup_cf    as sc
import BMSS.traceanalysis      as ta
import BMSS.curvefitting       as cf
import preprocessing           as pp

plt.style.use(lab.styles['dark_style'])

#Reset Plots
plt.close('all')

'''
Tutorial 4 Part 2: Fitting data with simulated annealing
- Import and preprocess data
- Combine data with sampler arguments
- Call curve-fitting function
- Plot results of curve-fitting
'''

if __name__ == '__main__':

    '''
    First we import the data and do preprocessing. The steps for preprocessing 
    have been packaged into functions for brevity. You can use the functions as templates
    for your future work!
    '''
    all_data = {'OD600': pd.read_excel('data/data.xlsx', header=[0, 1], index_col=0, sheet_name='OD600'),
                'Fluor': pd.read_excel('data/data.xlsx', header=[0, 1], index_col=0, sheet_name='Fluor')
                }
    
    #Normalize Fluorescence by OD and convert to Molar
    all_data['Fluor'] = all_data['Fluor'].divide(all_data['OD600'])
    all_data['Fluor'] = all_data['Fluor']* 1e-6/(18.814*30)
    
    data_by_model_num = {1: {'OD600': all_data['OD600'],
                             'Fluor': all_data['Fluor']
                              },
                          2: {'OD600': all_data['OD600'],
                              'Fluor': all_data['Fluor']
                              }
                          }
    #Extract the necessary information
    #Note that subtraction of the blank has been included in this function!!!
    data_mu, data_sd, init, state_sd, tspan = pp.import_data(all_data, data_by_model_num)
    
    '''
    Next we import the sampler arguments and update them.
    '''
    filename = 'settings_sa.ini'
    sampler  = 'sa'
    
    sampler_args, config_data = sc.get_sampler_args(filename, sampler)
    
    states = {1: ['OD600', 'Glu', 'Fluor'],
              2: ['OD600', 'Glu', 'mh', 'Fluor'],
              }
    
    sampler_args = pp.update_sampler_args(data_mu, data_sd, init, state_sd, tspan, sampler_args, states)
    
    result = cf.simulated_annealing(**sampler_args)
    
    '''
    The return value is a dictionary with the following values.
    'a': The accepted samples as a DataFrame
    'r': The rejected samples as a DataFrame
    '''
    accepted = result['a']
    
    print('Accepted results (last 5 rows)')
    print(accepted.tail())
    
    plot_index = {1: ['OD600', 'Fluor'],
                  2: ['OD600', 'Fluor', 'mh']
                  }
    

    titles     = {1: dict(zip(plot_index[1], plot_index[1])),
                  2: dict(zip(plot_index[2], plot_index[2]))
                  }
    
    cf.plot(posterior  = accepted.tail(10), 
            models     = sampler_args['models'],
            guess      = sampler_args['guess'],
            data       = data_mu,
            plot_index = plot_index,
            titles     = titles
            )
    
    #Plot the trace
    traces = {1: accepted} #Add as many traces as you want using a dictionary
    ta.plot_steps(traces, skip=sampler_args['fixed_parameters'])