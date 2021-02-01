import setup_bmss                   as lab
import BMSS.models.model_handler    as mh
import BMSS.models.settings_handler as sh
import BMSS.models.setup_sim        as sm

'''
Example 1 Part 2: Creating Settings Templates
'''

if __name__ == '__main__':
    
    '''
    Creating the settings file in the previous example can be tedious. BMSS 
    helps you avoid unecessary errors by providing functions for generating 
    settings templates.
    '''
    #Read model
    #Details in Tutorial 1 Part 1
    core_model       = mh.from_config('testmodel.ini')
    user_core_models = {core_model['system_type']: core_model}
    
    '''
    First we need a filename
    '''
    settings_template_filename = 'settings_template_1.ini'
    
    '''
    Next we need to specify which system_type and which settings_name we want
    using tuples. In this example, our model is not in the database and neither 
    have any settings. Thus, we leave settings_name as None.
    '''
    system_types_settings_names = [('TestModel, Dummy', None)
                                   ]
    
    sm.make_settings_template(system_types_settings_names, 
                              filename         = settings_template_filename,
                              user_core_models = user_core_models)
    
    '''
    Open the file and check its contents.
    '''
    
    '''
    For a model which has been saved in the database, user_core_models is not
    needed.
    '''
    settings_template_filename  = 'settings_template_2.ini'
    system_types_settings_names = [('TestModel, Monod, Inducible, Bioconversion, ProductInhibition', '__default__')
                                   ]
    
    sm.make_settings_template(system_types_settings_names, 
                              filename         = settings_template_filename,
                              user_core_models = user_core_models)
    
    
    '''
    Open the file and check its contents. Note that unlike the previous case, some
    of the values have already in filled in. This is because the database also contains
    a combination of settings saved under "__default__". For detailed explanations
    on how to create and save settings, you can refer to Tutorial 1.
    '''
    
    '''
    Finally, you can combine settings for multiple models into a single file if you
    find it useful for organization.
    '''
    settings_template_filename  = 'settings_template_3.ini'
    system_types_settings_names = [('TestModel, Dummy', None),
                                   ('TestModel, Monod, Inducible, Bioconversion, ProductInhibition', '__default__')
                                   ]
    
    sm.make_settings_template(system_types_settings_names, 
                              filename         = settings_template_filename,
                              user_core_models = user_core_models)
    
    
    
    
    
    
    