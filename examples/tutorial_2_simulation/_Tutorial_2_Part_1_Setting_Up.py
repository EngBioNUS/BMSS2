import setup_bmss                   as lab
import BMSS.models.model_handler    as mh
import BMSS.models.setup_sim        as sm


'''
Tutorial 2 Part 1: Introduction to simulation datastructures
- Introduction to the models data structure
- Creating templates for simulation
'''

if __name__ == '__main__':
    '''
    Note: This file is meant to be run after you have added the model from Tutorial 1.
    If you have not done so, run the following function.
    mh.config_to_database('testmodel.ini')
    '''
    
    '''
    A .ini file can be used to specify simulation settings.
    This allows you to write fewer lines of code and lets you focus on the settings.
    The function performed three things:
        1. Read the .ini files (returned as config_data)
        2. Created a data structure for the models specified in the .ini file (returned as models)
        3. Created a DataFrame for the parameter values specified in the .ini file
    '''
    filename = 'settings_sim_1.ini'
    
    models, params, config_data = sm.get_models_and_params(filename)
    

    '''
    Models should be in the form {model_num: compiled model}.
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
    Parameters should be supplied either as a dict or a DataFrame. 
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
    If you are using a core model that has not been added to the database, 
    you will need to prepare the data structures in two steps instead.
    '''
    core_model             = mh.from_config('testmodel.ini')
    config_data_new        = sm.from_config(filename)
    models_new, params_new = sm.compile_models([core_model], config_data_new)
    
    #Create simulation settings templates using saved settings
    sm.make_settings_template([('TestModel, Dummy', '__default__')], 'settings_sim_template.ini')
    