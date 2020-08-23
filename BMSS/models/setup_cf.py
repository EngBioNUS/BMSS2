import configparser
###############################################################################
#Non-Standard Imports
###############################################################################
try:
    from .                   import model_handler    as mh 
    from .                   import settings_handler as sh
    from ._backend_setup_sim import (compile_models, split_at_top_level, 
                                     string_to_dict, string_to_dict_array, 
                                     string_to_list_string, eval_init_string, 
                                     eval_params_string, eval_tspan_string, 
                                     dict_template, list_template)

except:
    import model_handler    as     mh
    import settings_handler as     sh
    from _backend_setup_sim import (compile_models, split_at_top_level, 
                                     string_to_dict, string_to_dict_array, 
                                     string_to_list_string, eval_init_string, 
                                     eval_params_string, eval_tspan_string, 
                                     dict_template, list_template)
    
###############################################################################
#Interfacing with Configparser
###############################################################################
def from_config(filename, sampler='sa'):
    config             = configparser.RawConfigParser()
    config.optionxform = lambda option: option
    config_data               = {}
    with open(filename, 'r') as file:
        config.read_file(file)
    
    n = 1
    for section in config.sections():
        solver_args      = config[section].get('solver_args')
        fixed_parameters = config[section].get('fixed_parameters')
        parameter_bounds = config[section].get('parameter_bounds')
        priors           = config[section].get('priors')
        step_size        = config[section].get('step_size')
        sa_args          = config[section].get('sa_args')
        de_args          = config[section].get('de_args')
        bh_args          = config[section].get('bh_args')
        da_args          = config[section].get('da_args')
        guess            = config[section].get('guess')
        units            = config[section].get('units')
        
        solver_args      = string_to_dict(solver_args)             if solver_args      else {}
        fixed_parameters = string_to_list_string(fixed_parameters) if fixed_parameters else []
        parameter_bounds = string_to_dict_array(parameter_bounds)  if parameter_bounds else {}
        priors           = string_to_dict(priors)                  if priors           else {}
        step_size        = string_to_dict(step_size)               if step_size        else {}
        sa_args          = string_to_dict(sa_args)                 if sa_args else {}
        de_args          = string_to_dict(de_args)                 if de_args else {}
        bh_args          = string_to_dict(bh_args)                 if bh_args else {}
        da_args          = string_to_dict(da_args)                 if da_args else {}
        guess            = eval_params_string(guess)               if guess   else {}
        units            = string_to_dict(units)                   if units   else {}
        
        if sampler == 'sa':
            trials = sa_args.get('trials', 5000)
            blocks = sa_args.get('blocks', [])
            if blocks:
                blocks = [block.strip() for block in split_at_top_level(blocks, ',')]
                blocks = [[b.strip() for b in block[1:len(block)-1].split(',')] for block in blocks]
                
            config_data[n] = {'system_type' : section,     'guess'  : guess,  'priors'           : priors, 
                              'solver_args' : solver_args, 'trials' : trials, 'parameter_bounds' : parameter_bounds,
                              'step_size'   : step_size,   'blocks' : blocks, 'fixed_parameters' : fixed_parameters,   
                              'units'       : units
                              }
        
        elif sampler == 'de':
            config_data[n] = {'system_type' : section,     'guess'  : guess,  'priors' : priors, 
                              'solver_args' : solver_args, 'parameter_bounds' : parameter_bounds,  
                              'de_args'     : de_args,     'fixed_parameters' : fixed_parameters,
                              'units'  : units
                              }
            
        elif sampler == 'bh':
            config_data[n] = {'system_type' : section,     'guess'  : guess,  'priors' : priors, 
                              'solver_args' : solver_args, 'parameter_bounds' : parameter_bounds,  
                              'step_size'   : step_size,   'fixed_parameters' : fixed_parameters,   
                              'bh_args'     : bh_args,     'units'  : units
                              }
        elif sampler == 'da':
            config_data[n] = {'system_type' : section,     'guess'  : guess,  'priors' : priors, 
                              'solver_args' : solver_args, 'parameter_bounds' : parameter_bounds,   
                              'da_args'     : da_args,     'fixed_parameters' : fixed_parameters, 
                              'units'  : units
                              }
        n += 1
        
    return config_data

###############################################################################
#Main Set Up
###############################################################################    
def get_sampler_args(filename, sampler='sa'):
    if sampler == 'sa':
        return get_sampler_args_sa(filename)
    elif sampler == 'de':
        return get_sampler_args(filename)
    elif sampler == 'bh':
        return get_sampler_args(filename)
    elif sampler == 'da':
        return get_sampler_args(filename)
    else:
        raise Exception('sampler must be sa, de, bh or da. sampler given was ' + str(sampler))
    

def get_sampler_args_sa(filename):
    '''
    Shortcut for setting up simulated annealing for one model
    '''

    config_data    = from_config(filename, 'sa') if type(filename) == str else filename
    core_models    = [mh.quick_search(config_data[key]['system_type']) for key in config_data]
    models, params = compile_models(core_models, config_data)
    
    guess            = {}
    bounds           = {}
    priors           = {}
    step_size        = {}
    blocks           = []
    fixed_parameters = []
    trials           = []
    for key in config_data:
        models[key]['int_args']['solver_args'] = config_data[key]['solver_args']
        
        temp      = {param + '_' + str(key): config_data[key]['guess'][param] for param in config_data[key]['guess']}
        guess     = {**guess, **temp}
        
        temp      = {param + '_' + str(key): config_data[key]['parameter_bounds'][param] for param in config_data[key]['parameter_bounds']}
        bounds    = {**bounds, **temp} 
        
        temp      = {param + '_' + str(key): config_data[key]['priors'][param] for param in config_data[key]['priors']}
        priors    = {**priors, **temp}
    
        temp      = {param + '_' + str(key): config_data[key]['step_size'][param] for param in config_data[key]['step_size']}
        step_size = {**step_size, **temp}
        
        blocks += [[param + '_' + str(key) for param in block] for block in config_data[key]['blocks']]
        
        fixed_parameters   += [param + '_' + str(key) for param in config_data[key]['fixed_parameters']]
        
        if config_data[key]['trials']:
            trials.append(config_data[key]['trials'])
        
    sampler_args = {'data'     : {},
                    'guess'    : guess,
                    'models'   : models, 
                    'fixed_parameters'     : fixed_parameters,
                    'priors'   : priors,
                    'bounds'   : bounds,
                    'blocks'   : blocks,
                    'step_size': step_size,
                    'trials'   : max(trials) if trials else 3000,
                    }
        
    return sampler_args, config_data

def get_sampler_args_de(filename):
    '''
    Shortcut for setting up differential evolution for one model
    '''

    config_data    = from_config(filename, 'sa') if type(filename) == str else filename
    core_models    = [mh.quick_search(config_data[key]['system_type']) for key in config_data]
    models, params = compile_models(core_models, config_data)
    
    guess            = {}
    bounds           = {}
    priors           = {}
    fixed_parameters = []
    scipy_args       = {}
    for key in config_data:
        models[key]['int_args']['solver_args'] = config_data[key]['solver_args']
        
        temp      = {param + '_' + str(key): config_data[key]['guess'][param] for param in config_data[key]['guess']}
        guess     = {**guess, **temp}
        
        temp      = {param + '_' + str(key): config_data[key]['parameter_bounds'][param] for param in config_data[key]['parameter_bounds']}
        bounds    = {**bounds, **temp} 
        
        temp      = {param + '_' + str(key): config_data[key]['priors'][param] for param in config_data[key]['priors']}
        priors    = {**priors, **temp}
    
        fixed_parameters   += [param + '_' + str(key) for param in config_data[key]['fixed_parameters']]
        
        scipy_args = config_data[key]['de_args'] if 'de_args' in config_data[key] else scipy_args
        
    sampler_args = {'data'       : {},
                    'guess'      : guess,
                    'models'     : models, 
                    'fixed_parameters'       : fixed_parameters,
                    'priors'     : priors,
                    'bounds'     : bounds,
                    'scipy_args' : scipy_args
                    }
        
    return sampler_args, config_data

def get_sampler_args_bh(filename):
    '''
    Shortcut for setting up differential evolution for one model
    '''

    config_data    = from_config(filename, 'sa') if type(filename) == str else filename
    core_models    = [mh.quick_search(config_data[key]['system_type']) for key in config_data]
    models, params = compile_models(core_models, config_data)
    
    guess            = {}
    bounds           = {}
    priors           = {}
    fixed_parameters = []
    step_size        = {}
    scipy_args       = {}
    for key in config_data:
        models[key]['int_args']['solver_args'] = config_data[key]['solver_args']
        
        temp      = {param + '_' + str(key): config_data[key]['guess'][param] for param in config_data[key]['guess']}
        guess     = {**guess, **temp}
        
        temp      = {param + '_' + str(key): config_data[key]['parameter_bounds'][param] for param in config_data[key]['parameter_bounds']}
        bounds    = {**bounds, **temp} 
        
        temp      = {param + '_' + str(key): config_data[key]['priors'][param] for param in config_data[key]['priors']}
        priors    = {**priors, **temp}
        
        temp      = {param + '_' + str(key): config_data[key]['step_size'][param] for param in config_data[key]['step_size']}
        step_size = {**step_size, **temp}
        
        fixed_parameters   += [param + '_' + str(key) for param in config_data[key]['fixed_parameters']]
        
        scipy_args = config_data[key]['bh_args'] if 'bh_args' in config_data[key] else scipy_args
        
    sampler_args = {'data'               : {},
                    'guess'              : guess,
                    'models'             : models, 
                    'fixed_parameters'               : fixed_parameters,
                    'priors'             : priors,
                    'bounds'             : bounds,
                    'step_size'          : step_size,
                    'scipy_args'         : scipy_args,
                    'step_size_is_ratio' : False
                    }
        
    return sampler_args, config_data

def get_sampler_args_da(filename):
    '''
    Shortcut for setting up differential evolution for one model
    '''

    config_data    = from_config(filename, 'sa') if type(filename) == str else filename
    core_models    = [mh.quick_search(config_data[key]['system_type']) for key in config_data]
    models, params = compile_models(core_models, config_data)
    
    guess            = {}
    bounds           = {}
    priors           = {}
    fixed_parameters = []
    scipy_args       = {}

    for key in config_data:
        models[key]['int_args']['solver_args'] = config_data[key]['solver_args']
        
        temp      = {param + '_' + str(key): config_data[key]['guess'][param] for param in config_data[key]['guess']}
        guess     = {**guess, **temp}
        
        temp      = {param + '_' + str(key): config_data[key]['parameter_bounds'][param] for param in config_data[key]['parameter_bounds']}
        bounds    = {**bounds, **temp} 
        
        temp      = {param + '_' + str(key): config_data[key]['priors'][param] for param in config_data[key]['priors']}
        priors    = {**priors, **temp}
        
        fixed_parameters   += [param + '_' + str(key) for param in config_data[key]['fixed_parameters']]
        
        scipy_args = config_data[key]['da_args'] if 'da_args' in config_data[key] else scipy_args
        
    sampler_args = {'data'               : {},
                    'guess'              : guess,
                    'models'             : models, 
                    'fixed_parameters'               : fixed_parameters,
                    'priors'             : priors,
                    'bounds'             : bounds,
                    'scipy_args'         : scipy_args,
                    }
        
    return sampler_args, config_data

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
        
        longest          = len(max(parameters,               key=len))    
        longest_         = len(max(settings['solver_args'],  key=len))  
        solver_args      = settings['solver_args'].keys()
        param_values     = dict_template('parameter_values', parameters, longest, settings['parameters'])
        parameter_bounds = dict_template('parameter_bounds', parameters, longest, settings['parameters'])
        priors           = dict_template('priors',           parameters, longest, settings['parameters'])
        units_values     = dict_template('units',            parameters, longest, settings['units'], default='')
        fixed_parameters = list_template('fixed_parameters', settings['fixed_parameters'])
        solver_args      = dict_template('solver_args',      solver_args, longest_, settings['solver_args'])
   
        model_id         = '#id = ' + str(core_model['id'])
        model_equations  = '#equations = \n' + '\n'.join(['#\t' + line for line in core_model['equations'] ])
        section_header   = '\n'.join([section_header, model_id, model_equations])
        
        result += '\n\n'.join([section_header, param_values, units_values, parameter_bounds, priors, fixed_parameters, solver_args])
        
    if filename:
        with open(filename, 'w') as file:
            file.write(result)
    return result



