import configparser
import importlib
import numpy as np
import pandas as pd

###############################################################################
#Non-Standard Import
###############################################################################
try:
    from . import model_handler    as mh
    from . import settings_handler as sh
    from .utils_settings import *
except:
    import model_handler    as mh
    import settings_handler as sh
    from   utils_settings   import *

###############################################################################
#Interfacing with Configparser
###############################################################################    
def from_config(filename):
    '''Opens a config file and reads the fields/subfields required for setting up 
    the analysis while ignoring the irrelavant ones. Returns a dictionary of the 
    collected information.
    
    :param filename: Name of file to read.
    :type filename: str
    '''
    config             = configparser.RawConfigParser()
    config.optionxform = lambda option: option
    config_data               = {}
    with open(filename, 'r') as file:
        config.read_file(file)
    
    n = 1
    for section in config.sections():
        if not is_analysis_settings(config, section):
            continue
        
        init        = config[section]['init']
        params      = config[section]['parameter_values']
        tspan       = config[section]['tspan']
        solver_args = config[section].get('solver_args')
        
        init        = eval_init_string(init)
        tspan       = eval_tspan_string(tspan)
        params      = eval_params_string(params)
        solver_args = string_to_dict(solver_args) if solver_args else {}
            
        config_data[n] = {'system_type': section, 'init': init, 'params': params, 'tspan': tspan, 'solver_args': solver_args}
        
        n += 1
        
    return config_data

###############################################################################
#Main Set Up
###############################################################################    
def get_models_and_params(filename, user_core_models={}):
    '''Reads the config file and adds combines it with core_model data. If you are
    using a core model that is not in the database, you must provide the core_model
    using the core_models argument where the key is the system_type. Returns the 
    models, params and config_data.
    
    :param filename: Name of file to read.
    :type filename: str
    :param user_core_model: A dictionary of core_models indexed by their system_type.
        core_models already in the database do not need to be specified here.
    :type user_core_model: dict, optional
    '''

    config_data, core_models = setup_helper(filename, from_config, user_core_models)
    models, params           = compile_models(core_models, config_data)
    return models, params, config_data

def compile_models(core_models, config_data):
    models     = make_compiled_models_template(core_models)
    params     = {}
    
    for key in config_data:
        models[key]['init']                    = config_data[key].get('init',       {1: np.array([0]*len(models[key]['states'])) })
        models[key]['tspan']                   = config_data[key].get('tspan',      [np.linspace(0, 600, 31)])
        models[key]['int_args']['solver_args'] = config_data[key].get('solver_args', {})
        
        try:
            temp       = {param + '_' + str(key): config_data[key]['params'][param].values  for param in config_data[key]['params']}
        except:
            temp       = {param + '_' + str(key): config_data[key]['guess'][param].values  for param in config_data[key]['guess']}
            
        params = {**params, **temp}
    
    return models, pd.DataFrame(params)

def setup_helper(filename, reader, user_core_models={}):
    '''
    The first return value is the config_data which will be generated based on
    three possible scenarios:
    
        1. filename is a dictionary 
           The filename is already config_data. No processing needed.
           
        2. filename is a string
           filename is name of the settings file to be opened and parsed by reader. 
           
        3. filename is neither of the above
           filename is an iterable containing names of settings file. It will be
           iteratively parsed by reader and subsequently reindexed to give config_data.
    
    The second return value is a list of core_model data structures associated with 
    config_data. The list is arranged in the order given by config_data and the 
    core_models are retrieved based on two possible scenarios:
        
        1. The system_type in config_data[model_num]['system_type'] is in core_models
           The core_model indexed under core_models[system_type] will be used.
           
        2. The system_type in config_data[model_num]['system_type'] is not in core_models
           The function searches the BMSS database for the appropriate core_model
           using quick_search
    
    :meta: private
    '''
    if type(filename) == str:
        config_data = reader(filename)
    elif type(filename) == dict:#Assume user has already imported the data
        config_data = filename
    else:#Assume data is spread across multiple files
        config_data = [value for f in filename for value in reader(f).values()]
        config_data = dict(enumerate(config_data, start=1))
    
    core_models = [user_core_models[config_data[key]['system_type']] if config_data[key]['system_type'] in user_core_models else mh.quick_search(config_data[key]['system_type']) for key in config_data]
    core_models = [mh.copy_core_model(core_model) for core_model in core_models]
    
    return config_data, core_models

def make_compiled_models_template(core_models):
    '''Constructs a compiled models dict using a list/tuple of core models
    
    :meta private:
    '''
    models = {}
    
    for i in range(len(core_models)):
        core_model  = core_models[i]
        
        try:
            model_function = mh.get_model_function(core_model['system_type'])
            print('Extracted function for ' + str(core_model['system_type']) + 'from database.')
        except:
            print('Writing function for ' + str(core_model['system_type']))
            mh.model_to_code(core_model, local=True)
            model_function = mh.get_model_function(core_model['system_type'], local=True)
        
        temp = {'function' : model_function,
                'init'     : {},
                'states'   : core_model['states'],
                'params'   : [param+'_'+str(i+1) for param in core_model['parameters'] + core_model['inputs']],
                'tspan'    : [],
                'int_args' : {'modify_init'   : None,
                              'modify_params' : None,
                              'solver_args'   : {},
                              }
                }
        
        models[i+1] = temp
    
    return models

###############################################################################
#Template Generation
###############################################################################
def make_settings_template(system_types_settings_names, filename='', user_core_models={}):
    '''Writes settings to a config file. If you are using a core_model that is 
    not in the database, you must provide the core_model using the core_models 
    argument where the key is the system_type.Returns the code as a string.
    
    :param system_types_settings_names: Pairs of tuples containing (system_type, settings_name)
    :type system_types_settings_names: list or tuple
    :param filename: The name of the file to write to
    :type filename: str, optional
    :param user_core_model: A dictionary of core_models indexed by their system_type.
        core_models already in the database do not need to be specified here.
    :type user_core_model: dict, optional
    '''
    result = ''
    
    system_types_settings_names1 = [system_types_settings_names] if type(system_types_settings_names) == str else system_types_settings_names
    
    for pair in system_types_settings_names1:
        try:
            system_type, settings_name = pair
        except:
            system_type, settings_name = pair, '__default__'

        core_model     = user_core_models[system_type] if system_type in user_core_models else mh.quick_search(system_type)
        parameters     = core_model['parameters'] + core_model['inputs']
        states         = core_model['states']
        section_header = '[' + core_model['system_type'] + ']'
        
        settings = {'system_type'     : system_type, 
                    'settings_name'   : settings_name,
                    'parameters'      : {},
                    'units'           : {},
                    'init'            : {},  
                    'priors'          : {}, 
                    'parameter_bounds': {},
                    'tspan'            : [],
                    'fixed_parameters' : [],
                    'solver_args'      : {'rtol'   : 1.49012e-8,
                                          'atol'   : 1.49012e-8,
                                          'tcrit'  : [],
                                          'h0'     : 0.0,
                                          'hmax'   : 0.0,
                                          'hmin'   : 0.0,
                                          'mxstep' : 0
                                          },
                    }
        
        if settings_name:
            settings = sh.quick_search(system_type, settings_name, skip_constructor=True)
        
        longest       = len(max(parameters,               key=len))    
        longest_      = len(max(settings['solver_args'],  key=len))  
        solver_args   = settings['solver_args'].keys()
        init_values   = dict_template('init',             states,     longest, settings['init'])
        param_values  = dict_template('parameter_values', parameters, longest, settings['parameters'])
        units_values  = dict_template('units',            parameters, longest, settings['units'], default='')
        tspan         = ['[' + ', '.join(['{:.2f}'.format(x) for x in segment]) + ']' for segment in settings['tspan']]
        tspan         = t_template('tspan',            '[' + ', '.join(tspan) + ']')
        solver_args   = dict_template('solver_args',      solver_args, longest_, settings['solver_args'])
        
        model_id         = '#id = ' + str(core_model['id'])
        model_equations  = '#equations = \n' + '\n'.join(['#\t' + line for line in core_model['equations'] ])
        section_header   = '\n'.join([section_header, model_id, model_equations])
        
        result += '\n\n'.join([section_header, init_values, param_values, units_values, tspan, solver_args, '']) 
        
    if filename:
        with open(filename, 'w') as file:
            file.write(result)
    return result

def dict_template(sub_section, keys, longest, data={}, default='[]'):
    '''
    :meta private:
    '''
    result  = sub_section + ' = \n' + ',\n'.join(['\t'  + key + ' '*(longest - len(key)) + ' = ' + str(data.get(key, default)) for key in keys])
    
    return result

def t_template(sub_section, values):
    '''
    :meta private:
    '''
    
    result = sub_section + ' = \n' + '\n\t' + values
    return result
    
def list_template(sub_section, values):
    '''
    :meta private:
    '''

    result = sub_section + ' = \n' + '\n\t' + '[' +', '.join([str(value) for value in values]) + ']'

    return result
                       
if __name__ == '__main__':
    pass