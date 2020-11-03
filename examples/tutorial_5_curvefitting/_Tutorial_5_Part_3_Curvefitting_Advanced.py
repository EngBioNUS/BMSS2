import matplotlib.pyplot as plt
import numpy             as np
import pandas            as pd
from   numba             import jit

import setup_bmss              as lab
import BMSS.models.setup_cf    as sc
import BMSS.traceanalysis      as ta
import BMSS.curvefitting       as cf

plt.style.use(lab.styles['bmss_notebook_style'])

#Reset Plots
plt.close('all')

'''
Tutorial 5 Part 3: Advanced options for curve-fitting
- Use scipy's optimizers
- Plot extra variables
'''

#Reuse functions from Part 2
from _Tutorial_5_Part_2_Curvefitting_Basic import *

def specific_growth(y, t, params):
    '''
    This follows the same format as in Tutorial 2
    '''
    
    t1 = t[::2] 
    x = y[::2,0]

    mu = (x[1:] - x[:-1])/x[1:]
    
    #Return value, y_val, x_val, marker
    
    return mu, t1[1:], '-'

if __name__ == '__main__':

    '''
    First we import the data and do preprocessing. The steps for preprocessing 
    have been packaged into functions for brevity. You can use the functions as templates
    for your future work!
    '''
    all_data = {'OD600': pd.read_csv('data/OD600_Data.csv', header=[0, 1]),
                'Fluor': pd.read_csv('data/GFP_Data.csv', header=[0, 1])
                }
    
    #Normalize Fluorescence by OD and convert to Molar
    all_data['Fluor'] = divide(all_data['Fluor'], all_data['OD600'])
    all_data['Fluor'] = multiply(all_data['Fluor'], 1e-6/(18.814*30))
    
    data_by_model_num = {1: {'OD600': all_data['OD600'],
                             'Fluor': all_data['Fluor']
                              }
                          }
    #Extract the necessary information
    #Note that subtraction of the blank has been included in this function!!!
    data, data_mu, data_sd, init, state_sd, tspan = import_data(all_data, data_by_model_num)
    
    '''
    Iterate across each type of sampler
    '''
    filename_samplers = [('settings_de.ini', 'de', cf.scipy_differential_evolution),
                         ('settings_bh.ini', 'bh', cf.scipy_basinhopping),
                         ('settings_da.ini', 'da', cf.scipy_dual_annealing)
                         ]
    
    for filename, sampler, sampler_function in filename_samplers:
        sampler_args, config_data = sc.get_sampler_args(filename, sampler)
        
        states = {1: ['OD600', 'Glu', 'Fluor'],
                  }
        
        sampler_args = update_sampler_args(data, data_mu, data_sd, init, state_sd, tspan, sampler_args, states)
        
        result = sampler_function(**sampler_args)
        
        '''
        The return value is a dictionary with the following values.
        'a': The accepted samples as a DataFrame
        'r': The rejected samples as a DataFrame if applicable
        's': The scipy return value if applicable
        'f': The full trace including calls to local optimizers if applicable
        '''
        accepted = result['a']
        
        plot_index = {1: ['OD600', 'Glu', 'Fluor', specific_growth]
                      }
        

        titles     = {1: dict(zip(plot_index[1], plot_index[1]))
                      }
        
        #Create our own Figure and Axes objects for cutom layouts
        fig = plt.figure()
        AX_ = [fig.add_subplot(2, 2, i+1) for i in range(4)]
        AX  = {1: {'OD600'         : AX_[0],
                   'Fluor'         : AX_[1],
                   'Glu'           : AX_[2],
                   specific_growth : AX_[3]
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
        
        ta.plot_steps({1: accepted}, skip=sampler_args['fixed_parameters'])