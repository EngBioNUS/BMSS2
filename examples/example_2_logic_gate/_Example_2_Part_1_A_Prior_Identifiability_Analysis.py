import setup_bmss                   as lab
import BMSS.models.model_handler    as mh
import BMSS.models.setup_sg         as ssg
import BMSS.strike_goldd_simplified as sg
'''
Tutorial 7 Part 2: A priori Identifiability Analysis with Strike-Goldd
- Call the function required to run the strike_goldd algorithm.
'''

if __name__ == '__main__':
    #Set up core models and sampler arguments
    #Details in Tutorial 7 Part 1 
    model_files = ['LogicGate_Not_Single.ini',
                   'LogicGate_Not_Double.ini',
                   'LogicGate_Not_Double_MaturationSecond.ini',
                   ]
    
    user_core_models = [mh.from_config(filename) for filename in model_files]
    user_core_models = {core_model['system_type']: core_model for core_model in user_core_models}
    
    sg_args, variables, config_data = ssg.get_strike_goldd_args(model_files, user_core_models=user_core_models)
    
    '''
    The optional argument dst allows you to supply your own dictionary to which the
    results will be added after each iteration. This allows you to thread and/or
    save the results before all the iterations have been completed.
    '''
    #Run strike-goldd algorithm
    #Details in Tutorial 7 Part 2
    dst              = {}
    iterative_result = sg.analyze_sg_args(sg_args, dst=dst)
    
    for key in iterative_result:
        print('Model ' + str(key))
        print(iterative_result[key])
        print()
    