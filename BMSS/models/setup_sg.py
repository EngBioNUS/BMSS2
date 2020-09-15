import configparser
from   sympy    import Matrix, Float, Symbol
from   textwrap import dedent

###############################################################################
#Non-Standard Imports
###############################################################################


try:
    from .                   import model_handler    as mh 
    from .                   import settings_handler as sh
    from .                   import ia_model_import  as im
    from .ia_result_to_csv   import write_new_row_to_file
    from ._backend_setup_sim import (compile_models, setup_helper, 
                                     string_to_dict, string_to_dict_array, 
                                     string_to_list_string, eval_init_string, 
                                     eval_params_string, eval_tspan_string, 
                                     dict_template, list_template,
                                     split_at_top_level,
                                     is_analysis_settings)

except:
    import model_handler    as     mh
    import settings_handler as     sh
    import ia_model_import  as     im
    from ia_result_to_csv   import write_new_row_to_file
    from _backend_setup_sim import (compile_models, setup_helper, 
                                     string_to_dict, string_to_dict_array, 
                                     string_to_list_string, eval_init_string, 
                                     eval_params_string, eval_tspan_string, 
                                     dict_template, list_template,
                                     split_at_top_level,
                                     is_analysis_settings)

###############################################################################
#Interfacing with ConfigParser
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
        
        parameter_values = config[section].get('parameter_values')
        fixed_parameters = config[section].get('fixed_parameters')
        measured_states  = config[section].get('measured_states')
        input_conditions = config[section].get('input_conditions')
        decomposition    = config[section].get('decomposition')
        init             = config[section].get('init')
        units            = config[section].get('units')
        
        fixed_parameters = string_to_list_string(fixed_parameters) if fixed_parameters else []
        measured_states  = string_to_list_string(measured_states)  if measured_states  else []
        input_conditions = string_to_dict(input_conditions)        if input_conditions else {}
        parameter_values = string_to_dict(parameter_values)        if parameter_values else {} 
        units            = string_to_dict(units)                   if units            else {}
        init             = eval_init_string(init)                  if init             else {}
        
        if decomposition:
            temp = ''.join([s for s in decomposition if s in ['[', ']']])
            if '[[' in temp:
                decomposition = decomposition.strip()
                decomposition = decomposition[1: len(decomposition)-1]
        else:
            decomposition = []
            
        decomposition    = [s.strip() for s in split_at_top_level(decomposition)]
        decomposition    = [[v.strip() for v in s.replace(']', '').replace('[', '').split(',')] for s in decomposition]
        
        for key in init:
            try: 
                next(iter(init[key]))
                if len(init[key]) != 1:
                    raise Exception('Error in init. Only one value allowed.')
            except:
                pass
            
        config_data[n] = {'system_type'      : section, 
                          'parameter_values' : parameter_values,
                          'init'             : init,
                          'input_conditions' : input_conditions,
                          'fixed_parameters' : fixed_parameters,
                          'measured_states'  : measured_states, 
                          'decomposition'    : decomposition,
                          'units'            : units
                          }
        n += 1
        
    return config_data

###############################################################################
#Main Set Up
###############################################################################    
def get_strike_goldd_args(filename, user_core_models={}, write_file=False):
    config_data, core_models = setup_helper(filename, from_config, user_core_models)
    
    all_variables = {}
    sg_args       = {}
    
    for model_num, core_model in zip(config_data, core_models):
        var     = [core_model[key] for key in ['states', 'parameters', 'inputs']]
        eq      = core_model['equations']
        h       = config_data[model_num].get('measured_states')
        x       = core_model['states']
        p       = [v for v in core_model['parameters'] if v not in config_data[model_num].get('fixed_parameters', [])]
        u       = config_data[model_num].get('input_conditions', {})
        ics     = config_data[model_num].get('init')
        ics     = dict(zip(x, ics[next(iter(ics))]))
        decomp  = config_data[model_num].get('decomposition')
        values  = config_data[model_num].get('parameter_values', {})

        if write_file: 
            outfile = 'sg_' + core_model['system_type'].replace(', ', '_') + '.py'
        else:
            outfile = ''

        mapping = [v for key in ['states', 'parameters', 'inputs'] for v in core_model[key]]
        mapping = {Symbol(v) : Symbol(v + '_' + str(model_num)) for v in mapping}
        code    = im.write_to_file(var, eq, h, x, p, u, ics, decomp, values, outfile)
        data    = {}
        temp    = []

        save_variables = '''
        data["h"]      = measured_states
        data["x"]      = states
        data["p"]      = unknown_parameters
        data["f"]      = diff
        data["u"]      = input_conditions
        data["ics"]    = init_conditions
        data["decomp"] = decomposition
        
        temp.append(variables)
        '''
        exec(code)
        exec(dedent(save_variables))

        items = mapping.items()
        for key in data :
            if key in ['h', 'x', 'p', 'f']:
                data[key] = data[key].subs(items)
            elif key in ['u', 'ics']:
                data[key] = {k.subs(items): data[key][k] for k in data[key]}
            else:
                data[key] = [[v.subs(items) for v in group] for group in data[key]]
        
        temp = {key: temp[0][key].subs(items) for key in temp[0]}
        
        sg_args[model_num]       = data
        all_variables[model_num] = temp
            
    return sg_args, config_data, all_variables

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
        parameters     = core_model['parameters']
        inputs         = core_model['inputs']
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
        
        longest            = len(max(parameters,               key=len))    
        longest_           = len(max(inputs,                   key=len))  if inputs else None
        init_values        = dict_template('init',             states,     longest,  settings['init'])
        param_values       = dict_template('parameter_values', parameters, longest,  settings['parameters'])
        input_conditions   = dict_template('input_conditions', inputs,     longest_, inputs) if inputs else ''
        fixed_parameters   = list_template('fixed_parameters', settings['fixed_parameters'])
        measured_states    = list_template('measured_states', states)
        unknown_parameters = list_template('unknown_parameters', [p for p in parameters if p not in settings['fixed_parameters']])
        
        model_id         = '#id = ' + str(core_model['id'])
        model_equations  = '#equations = \n' + '\n'.join(['#\t' + line for line in core_model['equations'] ])
        section_header   = '\n'.join([section_header, model_id, model_equations])
        
        result += '\n\n'.join([section_header, param_values, init_values, fixed_parameters, measured_states, unknown_parameters, input_conditions])
        
    if filename:
        with open(filename, 'w') as file:
            file.write(result)
    return result
    
# if __name__ == '__main__':
#     __model__ = {'id'          : 'bmss01001',
#                  'system_type' : ['Inducible', 'ConstInd'],
#                  'states'      : ['mRNA', 'Pep'], 
#                  'parameters'  : ['syn_mRNA', 'deg_mRNA', 'syn_Pep', 'deg_Pep', 'Ki'],
#                  'inputs'      : ['Ind'],
#                  'equations'   : ['dmRNA = syn_mRNA*Ind/(Ind + Ki) - deg_mRNA*mRNA',
#                                   'dPep  = syn_Pep*mRNA - deg_Pep'
#                                   ],
#                  'ia'          : 'ia_result_bmss01001.csv'
                 
#                  }
    
#     keyword    = 'ConstInd'
#     core_model = mh.search_models(keyword)[0]
    
#     info = {'known_params'    : {'deg_mRNA':[0.13, 'min-1'],
#                                  },
#             'inputs'          : {'Ind': 1,
#                                  },
#             'outputs'         : ['mRNA', 'Pep'],
#             'decomp'          : [['Pep'], ['mRNA', 'Pep']],
#             }
            
#     info = from_config('instance_information.ini')
    
#     ia_model = instantiate_ia_model(core_model, **info)
    

#     im.write_to_file(ia_model, 'dummy.py')
    

# #    make_ia_model_markup(ia_model, filename='mymodel.txt')

# #    print(from_config('instance_information.ini'))
# #    cf_model = instantiate_model_from_config('instance_information.ini')
# #    for key in cf_model:
# #        print(key)
# #        print(cf_model[key])
# #        print()
        