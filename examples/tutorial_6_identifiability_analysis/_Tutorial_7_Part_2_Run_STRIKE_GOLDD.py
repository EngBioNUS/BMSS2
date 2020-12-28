import setup_bmss                   as lab
import BMSS.models.setup_sg         as ssg
import BMSS.strike_goldd_simplified as sg
import BMSS.models.ia_results       as ir
import BMSS.models.model_handler    as mh

'''
Tutorial 7 Part 2: A priori Identifiability Analysis with Strike-Goldd
- Call the function required to run the strike_goldd algorithm.
'''

if __name__ == '__main__':
    filename    = 'settings_sg.ini' 
    
    sg_args, config_data, variables = ssg.get_strike_goldd_args(filename)
    
    '''
    We can now run the strike-goldd algorithm. This returns a dictionary where 
    the result for each model is indexed under model_num.
    
    The optional argument dst allows you to supply your own dictionary to which the
    results will be added after each iteration. This allows you to thread and/or
    save the results before all the iterations have been completed. Just use an
    empty dictionary.
    '''
    dst        = {}
    sg_results = sg.analyze_sg_args(sg_args, dst=dst)
    
    print('Result from strike_goldd')
    print(sg_results[1])
    print()
    
    '''
    The results can be exported as a human-readable report as a .yaml file
    
    If you code your own config_data, make sure you have these keys and their relevant values:
    'system_type', 'init', 'input_conditions', 'fixed_parameters', 'measured_states'
    '''
    outfile   = 'sg_results.yaml'
    yaml_dict = ir.export_sg_results(sg_results, variables, config_data, user_core_models={}, filename=outfile)
    
    print('Printing yaml_dict[1]', '{')
    for key in yaml_dict[1]:
        print(key, ':', yaml_dict[1][key])
    print('}')
    print()
    

    '''
    The core_model data structure can be updated as follows.
    
    ir.dump_sg_results(sg_results, variables, config_data, user_core_models={}, save=True)
    
    For models in the database, the results for that model will be added to the 
    database if save is set to True. If the model is not in the database or 
    has been supplied using user_core_models, the results for that model will 
    not be saved in the database regardless of the value of save.
    '''
    
    #This will not be saved into the database
    system_type = config_data[1]['system_type']
    core_model1 = mh.quick_search(system_type)
    
    print('Printing core_model1["ia"] before update')
    print(core_model1['ia'])
    print()
    
    user_core_models = {system_type: core_model1}
    
    ir.dump_sg_results(sg_results, variables, config_data, user_core_models=user_core_models, save=False)
    
    print('Printing core_model1["ia"] after update')
    print(core_model1['ia'])
    print()
    
    #Search for core_model again and check if the changes have been saved.
    core_model2 = mh.quick_search(system_type)
    print('Printing core_model2["ia"] update')
    print(core_model2['ia'])
    print()
    
    '''
    The results have not been saved as the core_models supplied via
    user_core_models are never saved to the database.
    '''
    
    #This will not be saved into the database either
    ir.dump_sg_results(sg_results, variables, config_data, save=False)
    
    #Search for core_model again and check if the changes have been saved.
    core_model3 = mh.quick_search(system_type)
    print('Printing core_model3["ia"] update')
    print(core_model3['ia'])
    print()
    
    '''
    The results have not been saved as save was set to False.
    '''
    
    #This will be saved.
    ir.dump_sg_results(sg_results, variables, config_data, save=True)
    
    core_model4 = mh.quick_search(system_type)
    print('Printing core_model4["ia"] update')
    print(core_model4['ia'])
    print()
    
    #Reset the ia for core_model
    mh.reset_ia(system_type)
    