import configparser
###############################################################################
#Non-Standard Imports
###############################################################################
from ._backend_setup_sim import compile_models, string_to_dict, string_to_dict_array, string_to_list_string, eval_init_string, eval_params_string, eval_tspan_string

try:
    from .                   import model_handler as mh 
    from ._backend_setup_sim import compile_models, string_to_dict, string_to_dict_array, string_to_list_string, eval_init_string, eval_params_string, eval_tspan_string

except:
    import model_handler    as     mh
    from _backend_setup_sim import compile_models, string_to_dict, string_to_dict_array, string_to_list_string, eval_init_string, eval_params_string, eval_tspan_string

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
        init             = config[section]['init']
        params           = config[section]['parameter_values']
        tspan            = config[section]['tspan']
        solver_args      = config[section].get('solver_args')
        fixed_parameters = config[section].get('fixed_parameters')
        parameter_bounds = config[section].get('parameter_bounds')
        
        init             = eval_init_string(init)
        tspan            = eval_tspan_string(tspan)
        params           = eval_params_string(params)
        solver_args      = string_to_dict(solver_args)            if solver_args      else {}
        fixed_parameters = string_to_list_string(fixed_parameters)       if fixed_parameters else []
        parameter_bounds = string_to_dict_array(parameter_bounds) if parameter_bounds else {}
            
        config_data[n] = {'system_type'      : section,     'init'             : init,      
                          'params'           : params,      'tspan'            : tspan,            
                          'solver_args'      : solver_args, 'fixed_parameters' : fixed_parameters, 
                          'parameter_bounds' : parameter_bounds
                          }
        
        n += 1
        
    return config_data

###############################################################################
#Main Set Up
###############################################################################    
def get_sensitivity_args(filename):
    config_data    = from_config(filename) if type(filename) == str else filename
    core_models    = [mh.quick_search(config_data[key]['system_type']) for key in config_data]
    
    models, params = compile_models(core_models, config_data)
    
    bounds           = {}
    fixed_parameters = []
    
    for key in config_data:
        models[key]['init']                    = config_data[key]['init']
        models[key]['tspan']                   = config_data[key]['tspan']
        models[key]['int_args']['solver_args'] = config_data[key]['solver_args']
        
        temp      = {param + '_' + str(key): config_data[key]['parameter_bounds'][param] for param in config_data[key]['parameter_bounds']}
        bounds    = {**bounds, **temp} 
        
        fixed_parameters   += [param + '_' + str(key) for param in config_data[key]['fixed_parameters']]
    
    return {'models'           : models, 
            'params'           : params, 
            'parameter_bounds' : bounds,
            'fixed_parameters' : fixed_parameters,
            'analysis_type'    : 'sobol',
            'N'                : 1000 
            }