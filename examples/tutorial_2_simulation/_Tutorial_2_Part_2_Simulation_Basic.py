import matplotlib.pyplot as plt
import os
from   numba             import jit
from   pathlib           import Path

import setup_bmss            as lab
import BMSS.models.setup_sim as sm
import BMSS.simulation       as sim

'''
Tutorial 2 Part 2: Basic Simulation of Models
- Integrate models
- Plot the results
- Calculate additional non-state variables
- Control the layout of the plots
'''

plt.style.use(lab.styles['dark_style'])
plt.close('all')

if __name__ == '__main__':
    #Set up the arguments
    #See Part 1 of this tutorial for explanations
    filename = 'settings_sim_1.ini'
    
    models, params, config_data = sm.get_models_and_params(filename)
    
    ym, _ = sim.integrate_models(models, params, multiply=True)
    
    '''
    The results of the integration are stored in ym as a nested dictionary in the
    form of ym[model_num][scenario_num][row] where row is a row index in params.
    Thus, suppose we only have one model. ym will then have one key.
    '''
    print('Keys in ym:', ym.keys())
    
    '''
    If that model has 2 scenarios, ym[1] will have 2 keys not including 0.
    Meanwhile, ym[model_num][0] contains the time array for the model.
    '''
    print('Keys in ym[1]', ym[1].keys())
    
    '''
    The multiply argument of integrate_models is set to True, the parameters and 
    scenarios are simulated combinatorially. Since there are two scenarios and two 
    rows of parameters, ym[1][1] and ym[1][2] will have two keys each.
    '''
    
    print('Keys in ym[1][1]', ym[1][1].keys())
    
    '''
    If the multiply argument is set to False, the parameters are "zipped" with 
    the scenarios and ym[1][1] and ym[1][2] will have one key each.
    '''
    
    ##Plot Settings
    '''
    The following arguments follow a similar format to models where the first key corresponds to the model being integrated.
    The definition of the values indexed by those keys are as follows:
    plot_index : A list of state variables to plot as well as extra functions for plotting.
    titles     : A list of title names corresponding the states in plot_index. This argument is optional.
    labels     : A dict of scenario: name pairs that will be used in the legend. This argument is optional.                            
    '''
    plot_index  = {1: ['m', 'p'],
                    }
    titles      = {1: {'m': 'Model 1 mRNA', 'p': 'Model 1 Protein'},
                    }
    labels      = {1: {1: 'Scenario 1', 2: 'Scenario 2'}
                    }
    
    figs, AX = sim.plot_model(plot_index, ym, titles=titles, labels=labels)
    
    #Plotting extra variables
    '''
    Sometimes, we might want to examine quantities that are not time series of the state variables.
    In this case, we can come up with our own functions to evaluate extra variables.
    This extra function takes of the form of func(y, t, params).
    The arrays in ym and their corresponding rows in params are fed into this function.
    The return values are:
        1. The y axis values
        2. The x axis values
        3. The marker used for plotting (Refer to matplotlib)
    '''
    
    @jit(nopython=True)
    def synthesis_p(y, t, params):
        '''
        filler
        x: Time
        y: synthesis_rate
        filler
        '''
        m = y[:,0]
        
        synp = params[3]
        
        synthesis_rate = synp*m
        
        return synthesis_rate, t, '-'
        
    ym, em = sim.integrate_models(models, params, synthesis_p)
    
    '''
    em is a nested dictinary in the form em[function][model_num][scenario_num][row]
    '''
    
    #Modify the plot settings accordingly
    plot_index  = {1: ['p', synthesis_p],
                    }
    titles      = {1: {'p': 'Model 1 Protein', synthesis_p: 'Rate of Protein Synthesis'},
                    }
    labels      = {1: {1: 'Scenario 1', 2: 'Scenario 2'}
                    }
    
    figs, AX = sim.plot_model(plot_index, ym, e=em, titles=titles, labels=labels) 
    
    '''
    We can control the layouts by using our own Figure and Axes objects and passing them 
    into plot_model.
    '''
    
    figs = [plt.figure()]
    AX_  = [figs[0].add_subplot(2, 1, i+1) for i in range(2)]
    AX   = {1:{'p'         : AX_[0],
                synthesis_p : AX_[1],
                },
            }
    figs, AX = sim.plot_model(plot_index, ym, e=em, titles=titles, labels=labels, figs=figs, AX=AX) 
    
    '''
    We can export the data for our external analysis in csv format.
    '''
    #Prefix at the front of the filenames
    prefix = ''
    
    #A new folder will be created using this directory. The files will be stored here.
    directory = Path(os.getcwd()) / 'simulation_results'
    
    sim.export_simulation_results(ym, em, prefix=prefix, directory=directory)
    