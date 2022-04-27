import setup_bmss                   as lab
import BMSS.models.model_handler    as mh
import BMSS.models.setup_sg         as ssg
import BMSS.models.ia_results       as ir
import BMSS.strike_goldd_simplified as sg

'''
Example 2 Part 1: A priori Identifiability Analysis with Strike-Goldd
'''

if __name__ == '__main__':
    '''
    In this example, we want to characterize a NOT gate system. We want to know 
    if our candidate models will be fully identifiable based on the states 
    measured. This can achieved using the strike-GOLDD algorithm.
    '''
    #Set up core models and sampler arguments
    #Details in Tutorial 7 Part 1 
    model_files = ['LogicGate_Not_Single.ini',
                   'LogicGate_Not_Double.ini',
                   'LogicGate_Not_Double_MaturationSecond.ini',
                   ]
    
    user_core_models = [mh.from_config(filename) for filename in model_files]
    user_core_models = {core_model['system_type']: core_model for core_model in user_core_models}
    
    sg_args, config_data, variables = ssg.get_strike_goldd_args(model_files, user_core_models=user_core_models)
    
    
    #Run strike-goldd algorithm
    #Details in Tutorial 7 Part 2
    sg_results = sg.analyze_sg_args(sg_args)
    outfile   = 'sg_results.yaml'
    yaml_dict = ir.export_sg_results(sg_results, variables, config_data, user_core_models=user_core_models, filename=outfile)
    
    print('Printing yaml_dict[1]', '{')
    for key in yaml_dict[1]:
        print(key, ':', yaml_dict[1][key])
    print('}')
    
    