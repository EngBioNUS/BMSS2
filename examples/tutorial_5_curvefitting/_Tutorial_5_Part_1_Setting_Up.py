import setup_bmss                as lab
import BMSS.models.model_handler as mh
import BMSS.models.setup_cf      as sc

'''
Tutorial 5 Part 1: Setting Up
- Learn how to use .ini files to manage curve-fitting settings/arguments
'''

if __name__ == '__main__':
    
    '''
    In this example, we want to perform curve-fitting for constitutive GFP expression 
    in E. coli. We start by importing the settings required for the sampler arguments.
    
    Just like in Tutorials 2 and 3, you can store settings in .ini files.
    The function get_sampler_args extracts the information and compiles it into 
    the arguments for BMSS curve-fitting functions.
    '''
    filename = 'settings_sa.ini'
    sampler  = 'sa'
    
    sampler_args, config_data = sc.get_sampler_args(filename, sampler)
    
    '''
    If you are coding the arguments yourself or using a model not in the database, 
    you can use the following steps.
    
    core_model_1     = mh.from_config('prototype_model.ini')
    user_core_models = {prototype['system_type'] : core_model_1}
    
    sampler_args, config_data = sc.get_sampler_args(filename, sampler, user_core_models=user_core_models)
    
    '''
    
    '''
    If you want only the information from the .ini file without compiling it into
    '''
    config_data = sc.from_config(filename, sampler)
    
    #Create simulation settings templates using saved settings
    system_types_settings_names = [('BMSS, Monod, Constitutive, Single', ''),
                                   ]
    sc.make_settings_template(system_types_settings_names, filename='settings_cf_template.ini')
    
    '''
    Note: This file is meant to be run after you have added the model from Tutorial 1.
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
    
    filename    = 'settings_sa.ini'
    config_data = sc.from_config(filename, sampler='sa')
    
    '''
    2. Compiling Arguments
    '''
    
    core_model                = mh.from_config('Monod_Constitutive_Single.ini')
    user_core_models          = {core_model['system_type']: core_model}
    sampler_args, config_data = sc.get_sampler_args(config_data, sampler='sa', user_core_models=user_core_models)
    
    print('Keys in sampler_args: ')
    print(sampler_args.keys())
        
    '''
    3. Wrapping for Models in Database
    
    For models already in the database, we can combine the above steps into a single 
    function call.
    '''
    
    new_sampler_args, new_config_data = sc.get_sampler_args(filename)
    
    '''
    4. Template Generation
    
    For models already in the database, templates can be generated. Open the output
    file and check its contents.
    '''
    system_types_settings_names = [('BMSS, Monod, Constitutive, Single', None),
                                    ]
    
    sc.make_settings_template(system_types_settings_names, filename='settings_sa_template.ini')
    