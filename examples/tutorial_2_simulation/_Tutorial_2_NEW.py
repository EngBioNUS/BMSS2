import matplotlib.pyplot as plt
import os
from   numba             import jit
from   pathlib           import Path

import setup_bmss                as lab
import BMSS.models.model_handler as mh
import BMSS.models.setup_sim     as sm
import BMSS.simulation           as sim


'''

'''

if __name__ == '__main__':
    '''
    Note: This file is meant to be run after you have added the model and settings
    from Tutorial 1 Parts 2 and 3.
    
    If you have not done so, run the following function.
    mh.config_to_database('testmodel.ini')
    '''
    
    '''
    Separating the settings/arguments for your analysis from your main code improves
    readability and convenience during reuse and modification. In addition, it also 
    prevents accidental modifications to your code when tweaking the settings/arguments.
    
    All BMSS analysis modules have an associated "setup"  module that can allows
    you to manage your settings/arguments via a .ini file. In each case, these 
    functionalities are available.
    
    1. Reading the .ini file into a dictionary.
    2. Compiling the arguments from the dictionary for use in BMSS analysis modules.
    3. Wrapping steps 1 and 2 into a single function when working with models in the database.
    4. Generation of a .ini template for use as a settings file.
    
    The steps automatically convert the information in the .ini files into arguments
    that can be fed directly into BMSS functions. The settings files for different types
    of analysis are all very similar. This allows you to copy and paste sections as 
    appropriate.
    '''
    
    '''
    1. Reading the Settings File
    '''
    
    filename    = 'settings_sim_1.ini'
    config_data = sm.from_config(filename)
    
    '''
    2. Compiling Arguments
    '''
    
    core_model     = mh.from_config('testmodel.ini')
    models, params = sm.compile_models([core_model], config_data)
    
    '''
    Models is a dictionary in the form {model_num: compiled model}.
    A compiled model is a dict containing the model function to be integrated 
    as well as other information required for integration, analysis and plotting.
    The keys are as follows:
    'function' : The model function.
    'init'     : A dict of initial values for each scenario you wish to simulate.
    'states'   : A list of names of the state variables in order. Required for plotting.
    'params'   : A list of names of the parameters that will be looked up from params 
                  that we defined earlier.
    'tspan'    : A list of arrays corresponding to time segments in order. 
                  For example, if you are doing piecewise-integration from 0~10 and then 10~20, 
                  use [np.linspace(0, 10, 11), np.linspace(10, 20, 11)]
                  If you are just integrating smoothly from 0~20, use [np.linspace(0, 20, 21)]
    'int_args' : A dict containing optional arguments for integration. 
                  The first two keys 'modify_init' and 'modify_params' index functions 
                  for piecewise integration. During piecewise integration, the functions (if any) 
                  will modify the initial values and parameters for each segment of integration.
                  For example, if the value of 'Ind' is 0 from 0~10 and 1 from 11~20, write a function 
                  that modifies the value of Ind params based on the segment of integration and 
                  index it under 'modify_params'. 
                  The function will be called at just before integration at the start of
                  each segment. An example will be shown later!
                  The third key is 'solver_args' and contains arguments that will be passed 
                  into the ode solver.
                  Use this only if you know what you are doing!
    The following steps demonstrate how we set up the models data structure.
    '''
    model = models[1]
    for key in model:
        print(key)
        print(model[key])
        print()
    
    '''
    Parameters is a DataFrame where each row contains the parameters for all the models. 
    During integration, the models are integrated using each row of parameter values. 
    The values to be used within each row for a model are given by models[model_num]['params']
    '''
    print('Params data structure')
    print(params)
    
    '''
    Note that an underscore followed by the model_num has been automatically added to each parameter. 
    This helps to prevent errors which can occur when different models share certain parameter names.
    '''
    
    '''
    3. Wrapping for Models in Database
    
    For models already in the database, we can combine the above steps into a single 
    function call.
    '''
    
    new_models, new_params, new_config_data = sm.get_models_and_params(filename)
    
    ym, _ = sim.integrate_models(models, params)
    
    '''
    The results of the integration are stored in ym as a nested dictionary in the
    form of ym[model_num][scenario_num][row] where row is a row index in params.
    Meanwhile, ym[model_num][0] contains the time array for the model.
    Thus, suppose we only have one model. ym will then have one key.
    If that model has 2 scenarios, ym[1] will have 2 keys not including 0.
    Finally, if there are two rows of parameters, ym[1][1] and ym[1][2] will have two keys each.
    '''
    print('Keys in ym:', ym.keys())
    print('Keys in ym[1]', ym[1].keys())
    print('Keys in ym[1][1]', ym[1][1].keys())
    
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
    We can export the data for our external analysis in csv format.
    '''
    #Prefix at the front of the filenames
    prefix = ''
    
    #A new folder will be created using this directory. The files will be stored here.
    directory = Path(os.getcwd()) / 'simulation_results'
    
    sim.export_simulation_results(ym, em, prefix=prefix, directory=directory)
