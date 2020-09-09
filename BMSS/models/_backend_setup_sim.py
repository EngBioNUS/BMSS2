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
except:
    import model_handler    as mh
    import settings_handler as sh

###############################################################################
#Interfacing with Configparser
###############################################################################    
def from_config(filename):
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
#Check if Analysis Settings
###############################################################################    
def is_analysis_settings(config, section):
    if section in ['id', 'system_type', 'states', 'parameters', 'inputs', 'equations', 'ia']:
        return False
    if 'system_type' in config[section]:
        return False
    
    return True

###############################################################################
#Supporting Functions for Reading Strings into Python
###############################################################################    
def eval_init_string(string):
    try:
        result = string_to_array(string)
        result = {i+1: result[i] for i in range(len(result))}
    except:
        result        = string_to_dataframe(string)
        result.index += 1
        result        = result.T.to_dict('list')

    for key in result:
        if any([type(x) == str for x in result[key]]) == str:
            raise Exception('Error in reading initial values. There is likely a missing comma(s).')
        try:
            result[key] = np.array(result[key])
        except:
            raise Exception('Error in reading initial values. Ensure you input is list-like.')
    return result

def eval_tspan_string(string):
    if string:
        try:
            return string_to_linspace(string)
        except:
            return np.array(eval(string.replace('\n', '')))
    else:
        return [np.linspace(0, 600, 31)]

def eval_params_string(string):
    return string_to_dataframe(string)

def string_to_linspace(string):
    '''
    Use this when you expect arguments for numpy.linspace
    '''
    try:
        return [np.linspace(*segment) for segment in eval('[' + string +']')]
    except:
        try:
            return [np.linspace(*segment) for segment in eval(string)]
        except:
            return np.array(eval(string))

def string_to_list(string):
    '''
    Use this when you expect a list of numbers
    '''
    string1 = string.replace('\n', ',')
    lst     = [s.strip() for s in string1.split(',')]
    lst     = [s for s in lst if s]
    string1 = ', '.join(lst)

    try:
        return eval('[' + string1 +']')
    except:
        return eval(string1)

def string_to_list_string(string):
    '''
    Use this when you expect a list of strings
    '''
    string1 = string.replace('[', '').replace(']', '').replace('\n', ',')
    lst     = [s.strip() for s in string1.split(',')]
    lst     = [s for s in lst if s]

    return lst
    
def string_to_array(string):
    '''
    Use this when you expect a list that can be converted into a numpy array.
    '''
    return np.array(string_to_list(string))
        
def string_to_dict(string):
    '''
    Use this when you expect a dictionary
    '''
    result = [s.strip() for s in split_at_top_level(string)]
    result = [line.split('=') for line in result ]
    result = [[lst[0].strip(), '='.join(lst[1:]).strip()] for lst in result]
    
    result = {pair[0]: try_eval(pair[1]) for pair in result}    
    
    return result

def string_to_dict_array(string):
    '''
    Use this when you expect a dictionary and expect the values to be numpy arrays
    '''
    temp = string_to_dict(string)
    try:
        iter(temp[next(iter(temp))])
        return {key: np.array(temp[key])  for key in temp}
    except:
        return {key: np.array([temp[key]])  for key in temp}
    
def string_to_dataframe(string):
    '''
    Use this when you expect a dictionary and want to convert it into a DataFrame
    '''
    return pd.DataFrame(string_to_dict_array(string))
    
def split_at_top_level(string, delimiter=','):
    '''
    Use this for nested lists.
    This is also a helper function for string_to_dict.
    '''
    nested = []
    buffer = ''
    result = []
    matching_bracket = {'(':')', '[':']', '{':'}'}
    
    for char in string:
        if char in ['[', '(', '{']:
            nested.append(char)
            buffer += char
        
        elif char in [']', ')', '}']:
            if char == matching_bracket.get(nested[-1]):
                nested = nested[:-1]
                buffer += char
            else:
                raise Exception('Mismatched brackets.' )
        elif char == delimiter and not nested:
            if buffer:
                result.append(buffer)
                buffer = ''
        else:
            buffer += char
    if buffer:
        result.append(buffer)
    return result

def try_eval(x):
    '''
    Attempts to convert string to numbers.
    '''
    try:
        return eval(x)
    except:
        return x

###############################################################################
#Main Set Up
###############################################################################    
def get_models_and_params(filename, user_core_models={}):
    '''
    Reads the config file and adds combines it with core model data. If you are
    using a core model that is not in the database, you must provide the core model
    using the core_models argument where the key is the system_type.
    '''

    # config_data    = from_config(filename) if type(filename) == str else filename
    # core_models    = [mh.quick_search(config_data[key]['system_type']) for key in config_data]
    
    config_data, core_models = setup_helper(filename, from_config, user_core_models)
    
    models, params = compile_models(core_models, config_data)
    return models, params, config_data

def compile_models(core_models, config_data):
    models         = make_compiled_models_template(core_models)
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

def setup_helper(filename, reader, core_models={}):
    config_data    = reader(filename) if type(filename) == str else filename
    core_models    = [core_models[config_data[key]['system_type']] if config_data[key]['system_type'] in core_models else mh.quick_search(config_data[key]['system_type']) for key in config_data]
    
    return config_data, core_models

def make_compiled_models_template(core_models):
    '''
    Constructs a compiled models dict using a list/tuple of core models
    '''
    models = {}
    
    for i in range(len(core_models)):
        core_model  = core_models[i]
        
        try:
            model_function = mh.get_model_function(core_model['system_type'])
        except:
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
def make_settings_template(system_types_settings_names, filename=''):
    '''
    Accepts pairs of tuples containing (system_type, settings_name)
    '''
    result = ''
    
    system_types_settings_names1 = [system_types_settings_names] if type(system_types_settings_names) == str else system_types_settings_names
    
    for pair in system_types_settings_names1:
        try:
            system_type, settings_name = pair
        except:
            system_type, settings_name = pair, '__default__'

        core_model     = mh.quick_search(system_type)
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
        tspan         = list_template('tspan',            '[' + ', '.join(tspan) + ']')
        solver_args   = dict_template('solver_args',      solver_args, longest_, settings['solver_args'])
        
        model_id         = '#id = ' + str(core_model['id'])
        model_equations  = '#equations = \n' + '\n'.join(['#\t' + line for line in core_model['equations'] ])
        section_header   = '\n'.join([section_header, model_id, model_equations])
        
        result += '\n\n'.join([section_header, init_values, param_values, units_values, tspan, solver_args])
        
    if filename:
        with open(filename, 'w') as file:
            file.write(result)
    return result

def dict_template(sub_section, keys, longest, data={}, default='[]'):
    result  = sub_section + ' = \n' + ',\n'.join(['\t'  + key + ' '*(longest - len(key)) + ' = ' + str(data.get(key, default)) for key in keys])
    
    return result

def list_template(sub_section, values):
    return sub_section + ' = \n' + '\n\t'+ str(values)
                       
if __name__ == '__main__':
    pass