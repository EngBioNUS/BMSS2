import importlib

import setup_bmss                   as lab
import BMSS.models.setup_sg         as ssg

'''
Tutorial 6 Part 3: Generating .py Files
- Create standalone .py files for running strike-goldd
'''

if __name__ == '__main__':
    '''
    Just as .py files for integration can be generated for core models, so can .py
    for running strike_goldd. Simply set the write_file argument in 
    get_strike_goldd_args to True. 
    '''
    
    filename    = 'settings_sg.ini' 
    
    sg_args, variables, config_data = ssg.get_strike_goldd_args(filename, write_file=True)
    
    '''
    The newly written .py files are have the prefix 'sg_' in front of them. Open 
    files and take a look inside!
    '''
    
    mod = importlib.import_module('sg_TestModel_Monod_Inducible')
    
    result = mod.run_strike_goldd()
    
    print('Result')
    print(result)