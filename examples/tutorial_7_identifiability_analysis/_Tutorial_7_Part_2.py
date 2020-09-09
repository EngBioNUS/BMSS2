import setup_bmss                   as lab
import BMSS.models.setup_sg         as ssg
import BMSS.strike_goldd_simplified as sg
'''
Tutorial 7 Part 2: A priori Identifiability Analysis with Strike-Goldd
- Call the function required to run the strike_goldd algorithm.
'''

if __name__ == '__main__':
    filename    = 'settings_sg.ini' 
    
    sg_args, variables, config_data = ssg.get_strike_goldd_args(filename)
    
    '''
    We can now run the strike-goldd algorithm.
    '''
    
    sg_result = sg.strike_goldd(**sg_args[1])
    
    print('Result from strike_goldd')
    print(sg_result)
    
    '''
    If we have multiple models, we can call analyze_sg_args to iteratively analyze
    the models in a single function call. This returns a dictionary where the result
    for each model is indexed under model_num.
    
    The optional argument dst allows you to supply your own dictionary to which the
    results will be added after each iteration. This allows you to thread and/or
    save the results before all the iterations have been completed.
    '''
    dst              = {}
    iterative_result = sg.analyze_sg_args(sg_args, dst=dst)
    
    