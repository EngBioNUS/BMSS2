import setup_bmss                as lab
import BMSS.models.model_handler as mh
import BMSS.models.setup_sen     as ss

'''
Tutorial 3 Part 1: Setting Up
- Learn how to use .ini files to manage sensitivity settings/arguments
'''

if __name__ == '__main__':
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
    
    filename    = 'settings_sen.ini'
    config_data = ss.from_config(filename)
    
    '''
    2. Compiling Arguments
    '''
    
    core_model                    = mh.from_config('Monod_Constitutive_Single_ProductInhibition.ini')
    user_core_models              = {core_model['system_type']: core_model}
    sensitivity_args, config_data = ss.get_sensitivity_args(config_data, user_core_models=user_core_models)
    
    print('Keys in sensitivity_args: ')
    print(sensitivity_args.keys())
        
    '''
    3. Wrapping for Models in Database
    
    For models already in the database, we can combine the above steps into a single 
    function call.
    '''
    
    new_sensitivity_args, new_config_data = ss.get_sensitivity_args(filename)
    
    '''
    4. Template Generation
    
    For models already in the database, templates can be generated. Open the output
    file and check its contents.
    '''
    system_types_settings_names = [('BMSS, Monod, Constitutive, Single, ProductInhibition', None),
                                    ]
    
    ss.make_settings_template(system_types_settings_names, filename='settings_sen_template.ini')
    
    
    