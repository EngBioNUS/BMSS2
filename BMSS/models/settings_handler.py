import configparser
import numpy    as np
import os       as os
import os.path  as osp
from   pandas   import concat, DataFrame, Series, read_sql_query

###############################################################################
#Non-Standard Import
###############################################################################
try:
    from . import model_handler as mh
    from . import settings_checker as sc
except:
    import model_handler as mh
    import settings_checker as sc
    
###############################################################################
#Globals
###############################################################################
_dir = osp.dirname(osp.abspath(__file__))

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
                  parameters,     init=None,           tspan=None,           
                  priors={},      parameter_bounds={}, fixed_parameters=[], 
                  solver_args={}, init_orient='scenario', 
                  user_core_model=None, 
                  **ignored):
    '''Checks and standardizes formatting of data types. Ignores irrelavant keyword arguments.
    Returns a settings data structure which is a dict.
    
    :param system_type: A string of keywords serving as a unique identifier for 
        the core_model separated by commas, will be formatted so there is one space
        after each comma, keywords should be in CamelCase
    :type system_type: str
    :param settings_name: A string, forms a unique identifier when paired with system_type
    :type settings_name: str
    :param units: A dict where the keys are parameter names and the values are the units in strings
    :type units: dict
    :param parameters: A pandas DataFrame of parameter values OR a dictionary, 
        column names/keys must match the parameter names of the corresponding core_model  
    :type parameters: pandas DataFrame or dict
    :param init: A dictionary where the keys correspond to a state in the core_model and 
        the values are the initial values for numerical integration OR where the keys
        correspond to different scenarios 
    :type init: dict
    :param tspan: A list of segments for piecewise numerical integration where each segments
        is a list of time points, defaults to values generated using numpy.linspace
    :type tspan: list, optional
    :param priors: A dictionary of Gaussian priors for parameter estimation where each key 
        is a parameter name and each value a tuple in the form (mean, standard_deviation)
    :type priors: dict, optional
    :param parameter_bounds: A dictionary of parameter bounds for parameter estimation 
        where each key is a parameter name and each value a tuple in the form (lower, upper)
    :type parameter_bounds: dict, optional
    :param fixed_parameters: A list of parameter names that will be fixed during parameter estimation.
    :type fixed_parameters: list, optional 
    :param solver_args: Additional keyword arguments for scipy.integrate.odeint, defaults to None
    :type solver_args: dict, optional
    :param init_orient: 'scenario' if the keys in init are scenario numbers, 'state' 
        if the keys are the state names, defaults to 'scenario'
    :type init_orient: str
    :param user_core_model: A core_model data structure for cross-checking. If None, 
        this function will search the database for the core_model.
    :type user_core_model: dict
    '''
    
    system_type1 = system_type if type(system_type) == str else ', '.join(system_type)
    if user_core_model:
        core_model   = user_core_model
        if core_model['system_type'] != system_type1:
            raise Exception('system_type does not match that of user_core_model.')
        print('Making settings using user_core_model')
    else:
        core_model = mh.quick_search(system_type1)
        
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
def add_to_database(settings, dialog=False):
    '''Accepts a settings data structure and adds it to UBase. dialog is currently ignored.
    '''
    
    if dialog:
        raise NotImplemented('Dialog option has not been implemented for this function.')
    
    if (settings['system_type'], settings['settings_name']) in list_settings(database=mh.MBase):
        raise Exception('Settings exists in MBase and cannot be modified. Please use a different settings_name.')

    return backend_add_to_database(settings, database=mh.UBase, dialog=dialog)

###############################################################################
#Supporting Functions
###############################################################################
def backend_add_to_database(settings, database, dialog=False):
    '''Supporting function for add_to_database. Do not run.
    
    :meta private:
    '''
    
    #Check core model exists
    core_model = mh.quick_search(settings['system_type'])
    
    #Prevent duplicates between MBase and UBase
    system_type_ensemble_name = (settings['system_type'], settings['settings_name'])
    
    if database == mh.MBase and system_type_ensemble_name in list_settings(database=mh.UBase):
        raise Exception(str(system_type_ensemble_name) + ' cannot be added to MBase as it is already in UBase.')
        
    if database == mh.UBase and system_type_ensemble_name in list_settings(database=mh.MBase):    
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
    
    mh.add_row('settings', row, database)
    print('Added settings ' + row['settings_name'])
    return row['system_type'], row['settings_name']

###############################################################################
#Search
###############################################################################    
def search_database(system_type='', settings_name='', database=None, skip_constructor=False, active_only=True):
    '''Searches database for settings data structure based on system_type and settings
    name. Returns a list of settings dictionaries.
    
    :param system_type: A string that will be matched against entries in the database
    :type system_type: str
    :param settings_name: A string corresponding to any key in the core_model, will 
        be used for matching
    :type settings_name: str
    :param database: Can be either MBase or UBase, if None, this function will search
        both databases, defaults to None
    :type database: SQL Connection, optional
    :param skip_constructor: For backend use, defaults to False
    :type skip_constructor: bool, optional
    :param active_only: A boolean for backend use, if True, this limits the search 
        to rows where the value of active is True, defaults to True
    :type active_only: bool, optional
    '''
    #Can only add a settings for active models
    core_model = mh.quick_search(system_type, active_only=True)
    result     = []
    
    if settings_name and system_type:
        comm = 'SELECT * FROM settings WHERE system_type LIKE "%' + system_type + '%" AND settings_name LIKE "%' + settings_name
    elif settings_name:
        comm = 'SELECT * FROM settings WHERE settings_name LIKE "%' + settings_name
    else:
        comm = 'SELECT * FROM settings WHERE system_type LIKE "%' + system_type  
    
    if active_only:
        comm += '%" AND active = 1;'
    else:
        comm += '%";'
        
    databases = [database] if database else [mh.MBase, mh.UBase]
    
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

def quick_search(system_type='', settings_name='', error_if_no_result=True, **kwargs):
    '''Searches database and returns first search result. If no settings name is 
    given, will attempt to search for the settings indexed under "__default__".
    '''
    
    try:
        settings_name1 = settings_name if settings_name else '__default__'
        settings = search_database(system_type, settings_name1, **kwargs)[0]
    except:
        if error_if_no_result:
            raise Exception('Could not find default parameters for system_type '  + str(system_type))
        else:
            return
        
    if settings['system_type'] != system_type or settings['settings_name'] != settings_name:
        if error_if_no_result:
            raise Exception('Could not find default parameters for system_type '  + str(system_type))
        else:
            return
        
    return settings
    
def list_settings(database=None):
    '''Returns a list of tuples in the form (system_type, settings_name) from 
    database.
    '''
    if database:
        comm         = 'SELECT system_type, settings_name FROM settings where active = 1'
        cursor       = database.execute(comm)
        all_settings = [s for s in cursor.fetchall()]
        return all_settings
    else:
        return list_settings(mh.MBase) + list_settings(mh.UBase)
    

###############################################################################
#Interfacing with Pandas
###############################################################################
def to_df(database=None):
    '''Returns a copy of the databases as a pandas DataFrame.
    
    :param database: The database to be read, if None, both databases will be read,
        defaults to None
    :type database: SQL Connection
    '''
    if database:
        df = read_sql_query("SELECT * from settings", database)
        return df
    else:

        df = to_df(mh.MBase), to_df(mh.UBase)
        df = concat(df, ignore_index=True)
        return df

def from_df_replace(df, database):
    '''
    For backend maintenance only. Do not run unless you know what you are doing.
    
    :meta private:
    '''
    return df.to_sql('settings', database, if_exists='replace', index=False)

###############################################################################
#Interfacing with Configparser
###############################################################################    
def from_config(filename, user_core_models={}):
    '''Returns a settings data structure.
    
    :param filename: Name of file to read.
    :type filename: str
    :param user_core_models: A dictionary of core_models required for calling make_settings,
        to be ignored if the core_model is already in the database.
    :type user_core_models: dict, optional
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
        
        core_model    = mh.quick_search(system_type)
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

        params           = string_to_dict(params)
        units            = string_to_dict(units)
        priors           = string_to_dict(priors) if priors else {}
        bounds           = string_to_dict(bounds) if bounds else {}
        fixed_parameters = string_to_list_string(fixed_parameters)
        tspan            = eval_tspan_string(tspan)
        
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
        
        user_core_model = user_core_models.get(settings['system_type'], {})
        all_settings.append(make_settings(**settings, user_core_model=user_core_model))
        
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
    '''Writes settings to a config file. Returns the code as a string.
    
    :param system_types_settings_names: Pairs of tuples containing (system_type, settings_name)
    :type system_types_settings_names: list or tuple
    :param filename: The name of the file to write to
    :type filename: str, optional
    '''
    result = ''
    
    system_types_settings_names1 = [system_types_settings_names] if type(system_types_settings_names) == str else system_types_settings_names
    
    for pair in system_types_settings_names1:
        try:
            system_type, settings_name = pair
        except:
            system_type, settings_name = pair, '__default__'
        
        if type(system_type) == str:
            core_model     = mh.quick_search(system_type)
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
        
        settings['init'] = DataFrame.from_dict(settings['init'], orient='index', columns=states).to_dict('list')
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
    '''Adds settings in file to the database. Returns a list of tuples of 
    system_type, settings_name pairs.
    '''

    all_settings = from_config(filename)
    
    result = list(map(add_to_database, all_settings))
    
    return result

def backend_config_to_database(filename, database):
    '''
    For backend maintenance. Do not run.
    
    :meta private:
    '''
    all_settings = from_config(filename)
    
    
    result = [backend_add_to_database(settings, database) for settings in all_settings]
    
    return result

###############################################################################
#Modification
###############################################################################
def _backend_modify_database(system_type, settings_name, data):
    '''
    Updates the row containing system_type with data.
    Automatically determines if the system_type is part of MBase or UBase.
    Not meant to be used on unsanitized data.
    '''
            
    if 'BMSS' in system_type:
        database = mh.MBase
    else:
        database = mh.UBase
    
    with database as db:
        for column, value in data.items():
            comm = "UPDATE settings SET " + str(column) + " = '" + str(value) + "' WHERE system_type = '" + str(system_type) + "' AND settings_name = '" + str(settings_name) + "'"
            cur  = db.cursor()
            cur.execute(comm)
            print('Changes to ' + str(system_type) + ' saved to database.')
        
    return

###############################################################################
#Deletion
###############################################################################
def delete(system_type, settings_name):
    '''Sets the value of the active column of the core_model in the .db file to 0.
    Can be restored using the restore function.
    '''
    database = mh.UBase
    with database as db:
        comm = 'UPDATE settings SET active = 0 WHERE system_type = "' + system_type + '" AND settings_name = "' + settings_name + '";'
        cur  = db.cursor()
        cur.execute(comm)
        
def restore(system_type, settings_name):
    '''Sets the value of the active column of the core_model in the .db file to 1.
    '''
    database = mh.UBase
    with database as db:
        comm = 'UPDATE settings SET active = 1 WHERE system_type = "' + system_type + '" AND settings_name = "' + settings_name + '";'
        cur  = db.cursor()
        cur.execute(comm)
    
def true_delete(system_type, settings_name, database):
    if not quick_search(system_type, settings_name, active_only=False, error_if_no_result=False, database=database):
        print(str(system_type) + '/' + str(settings_name) + ' could not be deleted as it was not found.')
    
    with database as db:
        comm = 'DELETE FROM settings WHERE system_type="'+ system_type + '" AND settings_name="' + settings_name +'";'    
        db.execute(comm)
        print('Removed ' + str(system_type) + '/' + str(settings_name))
    
###############################################################################
#Function for Setup
###############################################################################
def setup():
    for database in [mh.MBase, mh.UBase]:
        res         = database.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_names = [table[0] for table in res]
        if 'settings' not in table_names:
            mh.create_table(database, table_sql)
    
    print('Connected to MBase_settings, UBase_settings')
    return database

###############################################################################
#Initialization
###############################################################################
setup()

if __name__ == '__main__':
    from pathlib import Path
    
    filename = Path(os.getcwd()) / 'BMSS_markup' / 'Monod_Inducible_Bioconversion_ProductInhibitedGrowth.ini'
    
    core_model = mh.from_config(filename)
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
    
    # core_model = mh.make_core_model(**__model__)
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
    
    
