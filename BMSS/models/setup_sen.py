import configparser
###############################################################################
#Non-Standard Imports
###############################################################################
try:
    from .                   import model_handler    as mh 
    from .                   import settings_handler as sh
    from .setup_sim          import (compile_models, setup_helper,
                                     string_to_dict, string_to_dict_array, 
                                     string_to_list_string, eval_init_string, 
                                     eval_params_string, eval_tspan_string, 
                                     dict_template, list_template, t_template,
                                     is_analysis_settings)

except:
    import model_handler    as     mh
    import settings_handler as     sh
    from   setup_sim        import (compile_models, setup_helper,
                                    string_to_dict, string_to_dict_array, 
                                    string_to_list_string, eval_init_string, 
                                    eval_params_string, eval_tspan_string, 
                                    dict_template, list_template,
                                    is_analysis_settings)
    
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
        
        init             = config[section]['init']
        params           = config[section]['parameter_values']
        tspan            = config[section]['tspan']
        solver_args      = config[section].get('solver_args')
        fixed_parameters = config[section].get('fixed_parameters')
        parameter_bounds = config[section].get('parameter_bounds')
        units            = config[section].get('units')
        
        init             = eval_init_string(init)
        tspan            = eval_tspan_string(tspan)
        params           = eval_params_string(params)
        solver_args      = string_to_dict(solver_args)             if solver_args      else {}
        fixed_parameters = string_to_list_string(fixed_parameters) if fixed_parameters else []
        parameter_bounds = string_to_dict_array(parameter_bounds)  if parameter_bounds else {}
        units            = string_to_dict(units)                   if units            else {}
        
        config_data[n] = {'system_type'      : section,     'init'             : init,      
                          'params'           : params,      'tspan'            : tspan,            
                          'solver_args'      : solver_args, 'fixed_parameters' : fixed_parameters, 
                          'parameter_bounds' : parameter_bounds,
                          'units'            : units
                          }
        
        n += 1
        
    return config_data

###############################################################################
#Main Set Up
###############################################################################    
def get_sensitivity_args(filename, user_core_models={}):
    '''Reads the config file and adds combines it with core_model data. If you are
    using a core model that is not in the database, you must provide the core_model
    using the core_models argument where the key is the system_type. Returns a 
    dictionary of keyword arguments and the config_data.
    
    :param filename: The name of the file to read
    :type filename: str
    :param user_core_model: A dictionary of core_models indexed by their system_type.
        core_models already in the database do not need to be specified here.
    :type user_core_model: dict, optional
    '''
    config_data, core_models = setup_helper(filename, from_config, user_core_models)
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
    
    sensitivity_args =  {'models'           : models, 
                         'params'           : params, 
                         'parameter_bounds' : bounds,
                         'fixed_parameters' : fixed_parameters,
                         'analysis_type'    : 'sobol',
                         'N'                : 1000 
                         }
    
    return sensitivity_args, config_data

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
        
        longest          = len(max(parameters,               key=len))    
        longest_         = len(max(settings['solver_args'],  key=len))  
        solver_args      = settings['solver_args'].keys()
        init_values      = dict_template('init',             states,     longest, settings['init'])
        param_values     = dict_template('parameter_values', parameters, longest, settings['parameters'])
        parameter_bounds = dict_template('parameter_bounds', parameters, longest, settings['parameters'])
        units_values     = dict_template('units',            parameters, longest, settings['units'], default='')
        tspan            = ['[' + ', '.join(['{:.2f}'.format(x) for x in segment]) + ']' for segment in settings['tspan']]
        tspan            = t_template('tspan',            '[' + ', '.join(tspan) + ']')
        fixed_parameters = list_template('fixed_parameters', settings['fixed_parameters'])
        solver_args      = dict_template('solver_args',      solver_args, longest_, settings['solver_args'])
        
        
        model_id         = '#id = ' + str(core_model['id'])
        model_equations  = '#equations = \n' + '\n'.join(['#\t' + line for line in core_model['equations'] ])
        section_header   = '\n'.join([section_header, model_id, model_equations, ''])
        
        result += '\n\n'.join([section_header, init_values, param_values, units_values, tspan, parameter_bounds, fixed_parameters, solver_args])
        
    if filename:
        with open(filename, 'w') as file:
            file.write(result)
    return result


