import setup_bmss                   as lab
import BMSS.models.setup_sg         as ssg
import BMSS.strike_goldd_simplified as sg
import BMSS.models.ia_result_to_csv as ic
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
    save the results before all the iterations have been completed.
    '''
    dst        = {}
    sg_results = sg.analyze_sg_args(sg_args, dst=dst)
    
    print('Result from strike_goldd')
    print(sg_results[1])
    print()

    new_rows = ic.export_sg_results(sg_results, variables, config_data, user_core_models={}, local=True)
    
    print('Returned rows after calling export_results', '{')
    for key in new_rows[1]:
        print(key, ':', new_rows[1][key])
    print('}')
    
    '''
    If you want to run the strike-goldd algorithm on a single model, you can call
    the underlying strike_goldd algorithm directly.
        
    sg_result = sg.strike_goldd(**sg_args[1])
    
    core_model = mh.quick_search('BMSS, Monod, Inducible')
    
    new_row = ic.write_new_row_to_file(sg_results[1], 
                                       model_variables = variables[1],
                                       core_model      = core_model,
                                       local           = True,
                                       **config_data[1]
                                       )
    
    If you code your own config_data, make sure you have these keys and their relevant values:
    'system_type', 'init', 'input_conditions', 'fixed_parameters', 'measured_states'
    '''
    