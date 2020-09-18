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
    
    '''
    If the model is in the database, the results can be added to the database 
    as well using this code.
    
    ir.dump_sg_results(sg_results, variables, config_data)
    '''
    