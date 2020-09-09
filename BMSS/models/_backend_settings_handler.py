import configparser
import numpy    as np
import os       as os
import os.path  as osp
from   pandas   import concat, DataFrame, Series, read_sql_query

###############################################################################
#Non-Standard Import
###############################################################################
try:
    from . import _backend_model_handler as bmh
    from . import settings_checker as sc
except:
    import _backend_model_handler as bmh
    import settings_checker as sc
    
###############################################################################
#Globals
###############################################################################
SBase   = None
__dir__ = osp.dirname(osp.abspath(__file__))

table_sql = '''
CREATE TABLE IF NOT EXISTS "settings" (
	"system_type"      TEXT,
    "settings_name"    TEXT,
    "units"            TEXT,
    "parameters"       TEXT,
    "init"             TEXT,
    "priors"           TEXT,
    "parameter_bounds" TEXT,
    "fixed_parameters" TEXT, 
    "tspan"            TEXT,
    "solver_args"      TEXT,
    "active"           INTEGER DEFAULT 1,
    UNIQUE(system_type, settings_name)
);
'''
###############################################################################
#Parameter Ensemble Constructor
###############################################################################    
def make_settings(system_type,    settings_name,       units,    
                  parameters,     init={},             tspan=[],           
                  priors={},      parameter_bounds={}, fixed_parameters=[], 
                  solver_args={}, init_orient='scenario', 
                  user_core_model={}, 
                  **ignored):
    '''
    Checks and standardizes formatting of data types.
    
    All irrelavant keyword arguments are ignored.
    '''
    
    if user_core_model:
        core_model = user_core_model
        if core_model['system_type'] != system_type:
            raise Exception('system_type does not match that of user_core_model.')
        print('Making settings using user_core_model')
    else:
        core_model = bmh.quick_search(system_type)
        
    param_values = sc.check_and_assign_param_values(core_model, parameters)
    init1        = sc.check_and_assign_init(core_model['states'], init, init_orient)
    tspan1       = sc.check_and_assign_tspan(tspan)
    priors1      = sc.check_and_assign_priors(param_values, priors)
    bounds1      = sc.check_and_assign_parameter_bounds(param_values, parameter_bounds)
    solver_args1 = sc.check_and_assign_solver_args(solver_args)

    if fixed_parameters:
        fixable_parameters = core_model['parameters'] + core_model['inputs']
        if not all([p in fixable_parameters for p in fixed_parameters]):
            raise Exception('Error in fixed parameters. Unexpected parameters found.')
    
    
    settings_name1 = '__default__' if settings_name == '_' else settings_name
    
    result       = {'system_type'      : core_model['system_type'],
                    'settings_name'    : settings_name1,
                    'units'            : units,
                    'parameters'       : param_values,
                    'init'             : init1,
                    'priors'           : priors1,
                    'parameter_bounds' : bounds1,
                    'tspan'            : tspan1,
                    'fixed_parameters' : fixed_parameters,
                    'solver_args'      : solver_args1,
                    }
    return result

###############################################################################
#Param Storage
###############################################################################
def add_to_database(settings, dialog=True):
    '''
    Accepts a settings data structure and adds it to UBase. dialog is currently ignored.
    '''
    
    if (settings['system_type'], settings['settings_name']) in list_settings(database=bmh.MBase):
        raise Exception('Settings exists in MBase and cannot be modified. Please use a different settings_name.')

    return backend_add_to_database(settings, database=bmh.UBase, dialog=dialog)

###############################################################################
#Supporting Functions
###############################################################################
def backend_add_to_database(settings, database, dialog=False):
    '''
    Supporting function for add_to_database. Do not run.
    '''
    
    #Check core model exists
    core_model = bmh.quick_search(settings['system_type'])
    
    #Prevent duplicates between MBase and UBase
    system_type_ensemble_name = (settings['system_type'], settings['settings_name'])
    
    if database == bmh.MBase and system_type_ensemble_name in list_settings(database=bmh.UBase):
        raise Exception(str(system_type_ensemble_name) + ' cannot be added to MBase as it is already in UBase.')
        
    if database == bmh.UBase and system_type_ensemble_name in list_settings(database=bmh.MBase):    
        raise Exception(str(system_type_ensemble_name) + ' cannot be added to UBase as it is already in MBase.')
    
    params_dict = settings['parameters'].to_dict('list')
    params_dict = {key: params_dict[key] for key in settings['parameters'].to_dict('list')}
    
    row = {'system_type'   : settings['system_type'],
           'settings_name' : settings['settings_name'],
           'units'         : str(settings['units']),
           'parameters'    : str(params_dict),
           }
    
    for key1 in ['init', 'priors', 'parameter_bounds']:
        row[key1] = str({key2: list(settings[key1][key2]) for key2 in settings[key1]})
    
    row['tspan']            = str([list(span) for span in settings['tspan']])
    row['fixed_parameters'] = str(settings['fixed_parameters'])
    row['solver_args']      = str(settings['solver_args'])
    
    bmh.add_row('settings', row, database)
    print('Added settings ' + row['settings_name'])
    return row['system_type'], row['settings_name']

###############################################################################
#Search
###############################################################################    
def search_database(system_type, settings_name='', database=None, skip_constructor=False, active_only=True):
    
    #Can only add a settings for active models
    core_model = bmh.quick_search(system_type, active_only=True)
    result     = []
    
    if settings_name:
        comm = 'SELECT * FROM settings WHERE system_type LIKE "%' + system_type + '%" AND settings_name LIKE "%' + settings_name
    else:
        comm         = 'SELECT * FROM settings WHERE system_type LIKE "%' + system_type  
    
    if active_only:
        comm += '%" AND active = 1;'
    else:
        comm += '%";'
        
    databases = [database] if database else [bmh.MBase, bmh.UBase]
    
    for database in databases:
        with database as db:
            cursor       = db.execute(comm)
            all_settings = cursor.fetchall()    
         
        columns = database.execute('PRAGMA table_info(settings);')
        columns = columns.fetchall()
        columns = [column[1] for column in columns if column[1]!='active']
        all_settings  = [dict(zip(columns, s[:-1])) for s in all_settings]
        
        for s in all_settings:
            s['units']            = eval(s['units'])
            s['parameters']       = eval(s['parameters'])
            s['init']             = eval(s['init'])
            s['priors']           = eval(s['priors'])
            s['parameter_bounds'] = eval(s['parameter_bounds'])
            s['tspan']            = eval(s['tspan'])
            s['fixed_parameters'] = eval(s['fixed_parameters'])
            s['solver_args']      = eval(s['solver_args'])
        
        if skip_constructor:
            result += all_settings
        else:
            result += [make_settings(**s) for s in all_settings]

    return result

def quick_search(system_type, settings_name='', error_if_no_result=True, **kwargs):
    if settings_name:
        result = search_database(system_type, settings_name=settings_name, **kwargs)
        if result:
            result
            return result[0]
        else:
            raise Exception('Could not find parameters for system_type '  + str(system_type))
    else:
        result = search_database(system_type, settings_name='__default__', **kwargs)
        if result:
            return result[0]
        else:
            try:
                result = search_database(system_type, settings_name='')
                return result[0]
            except:
                if error_if_no_result:
                    raise Exception('Could not find default parameters for system_type '  + str(system_type))
    return {}
    
def list_settings(database=None):
    if database:
        if database == bmh.UBase:
            print('Listing core models in UBase.')
        else:
            print('Listing core models in MBase.')
        comm         = 'SELECT system_type, settings_name FROM settings'
        cursor       = database.execute(comm)
        all_settings = [s for s in cursor.fetchall()]
        return all_settings
    else:
        return list_settings(bmh.MBase) + list_settings(bmh.UBase)
    

###############################################################################
#Interfacing with Pandas
###############################################################################
def to_df(database=None):
    if database:
        df = read_sql_query("SELECT * from settings", database)
        return df
    else:

        df = to_df(bmh.MBase), to_df(bmh.UBase)
        df = concat(df, ignore_index=True)
        return df

def from_df_replace(df, database):
    '''
    For backend maintenance only. Do not run unless you know what you are doing.
    '''
    return df.to_sql('settings', database, if_exists='replace', index=False)

###############################################################################
#Interfacing with Configparser
###############################################################################    
def from_config(filename):
    '''
    Returns a settings data structure
    '''
    
    config              = configparser.RawConfigParser()
    config.optionxform  = lambda option: option
    all_settings        = []
    with open(filename, 'r') as file:
        config.read_file(file)
    
    for section in config.sections():
        if section in ['id', 'system_type', 'states', 'parameters', 'inputs', 'equations', 'ia']:
            continue
        if 'system_type' not in config[section]:
            continue
        
        system_type   = config[section]['system_type']
        params        = config[section]['parameter_values']
        units         = config[section]['units']
        init          = config[section].get('init', {})
        priors        = config[section].get('priors', {})
        bounds        = config[section].get('parameter_bounds', {})
        tspan         = config[section].get('tspan', '[[0, 600, 31]]')
        fixed_parameters = config[section].get('fixed_parameters', '[]')
        settings_name = str(section)
        
        core_model    = bmh.quick_search(system_type)
        system_type   = core_model['system_type']
        states        = core_model['states']
        if not settings_name:
            raise Exception('Ensemble name not valid!')
        settings_name = '__default__' if settings_name == '_' else settings_name
        
        if init:
            if '=' in init:
                init = string_to_dict(init)
                try: 
                    init        = DataFrame(init)
                    init.index += 1
                    init        = init.T.to_dict('list')
                except:
                    init  = {1: list(init.values())}

                for key in init:
                    if len(init[key]) != len(states):
                        raise Exception('Length of init must match number of states. system_type given: ' + str(system_type))
            else:
                init = eval(init)
                if len(init) != len(states):
                    raise Exception('Length of init must match number of states. system_type given: ' + str(system_type))
                init = {1: init}

        params = string_to_dict(params)
        units  = string_to_dict(units)
        priors = string_to_dict(priors) if priors else {}
        bounds           = string_to_dict(bounds) if bounds else {}
        fixed_parameters = string_to_list_string(fixed_parameters)
        tspan  = eval_tspan_string(tspan)
        
        settings = {'system_type'      : system_type, 
                    'settings_name'    : settings_name,
                    'parameters'       : params,
                    'units'            : units,
                    'init'             : init,  
                    'priors'           : priors, 
                    'parameter_bounds' : bounds,
                    'tspan'            : tspan,
                    'fixed_parameters' : fixed_parameters
                    }
        
        all_settings.append(make_settings(**settings))
        
    return all_settings

def eval_tspan_string(string):
    try:
        return string_to_linspace(string)
    except:
        return np.array(eval(string.replace('\n', '')))

def string_to_linspace(string):
    try:
        return [np.linspace(*segment) for segment in eval('[' + string +']')]
    except:
        return [np.linspace(*segment) for segment in eval(string)]

def string_to_list_string(string):
    temp = string.strip().replace('[', '').replace(']', '')
    temp = [s.strip() for s in temp.split(',')]
    
    return [s for s in temp if s]
    
def string_to_dict(string):
    result = [s.strip() for s in split_at_top_level(string)]
    result = [line.split('=') for line in result ]
    result = [[lst[0].strip(), '='.join(lst[1:]).strip()] for lst in result]
    
    result = {pair[0]: try_eval(pair[1]) for pair in result}    
    
    return result

def split_at_top_level(string, delimiter=','):
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
    try:
        return eval(x)
    except:
        return x

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
        
        if type(system_type) == str:
            core_model     = bmh.quick_search(system_type)
        else:
            core_model  = system_type
            system_type = core_model['system_type']
            
        parameters     = core_model['parameters'] + core_model['inputs']
        states         = core_model['states']
        section_header = '[]\nsystem_type = ' + core_model['system_type']
        
        if settings_name:
            settings = quick_search(system_type, settings_name, skip_constructor=True)
        else:            
            settings = {'system_type'      : system_type, 
                        'settings_name'    : settings_name,
                        'parameters'       : {},
                        'units'            : {},
                        'init'             : {},  
                        'priors'           : {}, 
                        'parameter_bounds' : {},
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
        
        longest          = len(max(parameters,               key=len))
        longest_         = len(max(settings['solver_args'],  key=len))  
        solver_args      = settings['solver_args'].keys()
        init_values      = dict_template('init',             states,     longest, settings['init'])
        param_values     = dict_template('parameter_values', parameters, longest, settings['parameters'])
        prior_values     = dict_template('priors',           parameters, longest, settings['priors'])
        bounds_values    = dict_template('parameter_bounds', parameters, longest, settings['parameter_bounds'])
        units_values     = dict_template('units',            parameters, longest, settings['units'], default='')
        tspan            = list_template('tspan',            [list(segment) for segment in settings['tspan']])
        fixed_parameters = list_template('fixed_parameters', settings['fixed_parameters'])
        solver_args      = dict_template('solver_args',      solver_args, longest_, settings['solver_args'])
        
        model_id         = '#id = ' + str(core_model['id'])
        model_equations  = '#equations = \n' + '\n'.join(['#\t' + line for line in core_model['equations'] ])
        section_header   = '\n'.join([section_header, model_id, model_equations])
        
        result += '\n\n'.join([section_header, init_values, param_values, prior_values, bounds_values, units_values, tspan, fixed_parameters, solver_args])
        
    if filename:
        with open(filename, 'w') as file:
            file.write(result)
    return result

def dict_template(sub_section, keys, longest, data={}, default='[]'):
    result  = sub_section + ' = \n' + ',\n'.join(['\t'  + key + ' '*(longest - len(key)) + ' = ' + str(data.get(key, default)) for key in keys])
    
    return result

def list_template(sub_section, values):
    return sub_section + ' = \n' + '\n\t'+ str(values)

###############################################################################
#Direct Config to Database
###############################################################################
def config_to_database(filename):
    '''
    Returns a list of tuples of system_type, settings_name pairs.
    '''

    all_settings = from_config(filename)
    
    result = list(map(add_to_database, all_settings))
    
    return result

def backend_config_to_database(filename, database):
    '''
    For backend maintenance. Do not run.
    '''
    all_settings = from_config(filename)
    
    
    result = [backend_add_to_database(settings, database) for settings in all_settings]
    
    return result

###############################################################################
#Deletion
###############################################################################
def delete(system_type, settings_name):
    database = bmh.UBase
    with database as db:
        comm = 'UPDATE settings SET active = 0 WHERE system_type = "' + system_type + '" AND settings_name = "' + settings_name + '";'
        cur  = db.cursor()
        cur.execute(comm)
        
def restore(system_type, settings_name):
    database = bmh.UBase
    with database as db:
        comm = 'UPDATE settings SET active = 1 WHERE system_type = "' + system_type + '" AND settings_name = "' + settings_name + '";'
        cur  = db.cursor()
        cur.execute(comm)
    
def true_delete(system_type, settings_name, database):
    try:
        settings = quick_search(system_type, settings_name, database)
    except:
        print(str(system_type) + '/' + str(settings_name) + 'not found')
        return
    with database as db:
        comm = 'DELETE FROM settings WHERE system_type="'+ system_type + '" AND settings_name="' + settings_name +'";'    
        db.execute(comm)
        print('Removed ' + str(system_type) + '/' + str(settings_name))
    
###############################################################################
#Function for Setup
###############################################################################
def setup():
    for database in [bmh.MBase, bmh.UBase]:
        res         = database.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_names = [table[0] for table in res]
        if 'settings' not in table_names:
            bmh.create_table(database, table_sql)
    
    print('Connected to MBase_settings, UBase_settings')
    return database

###############################################################################
#Initialization
###############################################################################
setup()

if __name__ == '__main__':
    from pathlib import Path
    
    filename = Path(os.getcwd()) / 'BMSS_markup' / 'Monod_Inducible_Bioconversion_ProductInhibitedGrowth.ini'
    
    core_model = bmh.from_config(filename)
    settings   = from_config(filename)
    
    
    
    __model__ = {'system_type' : ['DUMMY', 'DUMMY'],
                 'states'      : ['m', 'p'], 
                 'parameters'  : ['synm', 'degm', 'synp', 'degp'],
                 'inputs'      : ['Ind'],
                 'equations'   : ['dm = synm*Ind - degm*m',
                                 'dp  = synp*m - degp'
                                 ],
                 'ia'          : 'ia_result_bmss01001.csv'
                 }
    
    __settings__ = {'system_type'      : ['DUMMY, DUMMY'],
                    'settings_name'    : '__default__',
                    'units'            : {'synm' : 'M/min', 
                                          'degm' : '1/min',
                                          'synp' : '1/min',
                                          'degp' : '1/min',
                                          'Ind'  : 'M'
                                          },
                    'parameters'       : {'synm' : np.array([0.02]), 
                                          'degm' : np.array([0.15]),
                                          'synp' : np.array([0.02]),
                                          'degp' : np.array([0.012]) ,
                                          'Ind'  : np.array([1.0]) 
                                          },
                    'init'             : {1: [0, 0]},
                    'parameter_bounds' : {'degm' : [0.001, 0.03], 
                                          'degp' : [0.01, 0.5], 
                                          },
                    'solver_args'      : {'rtol'   : 1.49012e-8,
                                          'atol'   : 1.49012e-8,
                                          'tcrit'  : [],
                                          'h0'     : 0.0,
                                          'hmax'   : 0.0,
                                          'hmin'   : 0.0,
                                          'mxstep' : 0
                                          },
                }
    
    # core_model = bmh.make_core_model(**__model__)
    # settings   = make_settings(**__settings__, user_core_model=core_model)
    
    ###############################################################################
    #Testing Parameter Formats
    ###############################################################################
    # __settings__['parameters'] = {key+'_1' : __settings__['parameters'][key] for key in __settings__['parameters']}
    # settings = make_settings(**__settings__, user_core_model=core_model)
    
    # __settings__['parameters'] = Series(__settings__['parameters'], name=500)
    # settings = make_settings(**__settings__, user_core_model=core_model)
    
    ###############################################################################
    #Testing Initial Value Formats
    ###############################################################################
    # __settings__['init'] = {'m' : [0],
    #                         'p' : [0],
    #                         }
    # settings = make_settings(**__settings__, init_orient='states', user_core_model=core_model)
    
    # __settings__['init'] = [[0, 0], [0, 0]]
    # settings = make_settings(**__settings__, init_orient='states', user_core_model=core_model)
    
    # __settings__['init'] = Series([0, 0], index=['m', 'p'])
    # settings = make_settings(**__settings__, init_orient='states', user_core_model=core_model)
    
    # __settings__['init'] = DataFrame([[0, 0]], columns=['m', 'p'], index=[1])
    # settings = make_settings(**__settings__, init_orient='states', user_core_model=core_model)
    
    ###############################################################################
    #Testing Parameter Bound Formats
    ###############################################################################
    # __settings__['parameter_bounds'] = {}
    # settings = make_settings(**__settings__, user_core_model=core_model)
    
    
    # add_to_database(settings)
    
    
