import setup_bmss                as lab
import BMSS.models.model_handler as mh
import BMSS.models.setup_sim     as sm


'''
Tutorial 2 Part 1: Introduction to simulation datastructures
- Introduction to the models and params data structure
- Learn how to use .ini files to manage sensitivity settings/arguments
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
    1. Reading the Arguments File
    '''
    
    filename    = 'settings_sim_1.ini'
    config_data = sm.from_config(filename)
    
    '''
    2. Compiling Arguments
    '''
    
    core_model       = mh.from_config('testmodel.ini')
    user_core_models = {core_model['system_type']: core_model}
    
    models, params, config_data = sm.get_models_and_params(filename, user_core_models=user_core_models)
    
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
    function call. In this situation, we do not need testmodel.ini as BMSS will extract 
    from the database.
    '''
    
    new_models, new_params, new_config_data = sm.get_models_and_params(filename)
    
    '''
    4. Template Generation
    
    For models already in the database, templates can be generated. Open the output
    file and check its contents.
    '''
    system_types_settings_names = [('TestModel, Dummy', '__default__')
                                   ]
    
    sm.make_settings_template(system_types_settings_names, 'settings_sim_template.ini')
    