import configparser
import numpy    as np
import os       as os
import os.path  as osp
from   pandas   import DataFrame, Series, read_sql_query

###############################################################################
#Non-Standard Import
###############################################################################
try:
    from . import model_handler    as mh
    from . import settings_checker as sc
except:
    import model_handler    as mh
    import settings_checker as sc
    
###############################################################################
#Globals
###############################################################################
SBase   = None
__dir__ = osp.dirname(osp.abspath(__file__))

table_sql = '''
CREATE TABLE "settings" (
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
);
'''

table_unique_sql='''
CREATE UNIQUE INDEX idx_positions_title ON settings ("system_type", "settings_name");
'''

###############################################################################
#Parameter Ensemble Constructor
###############################################################################    
def make_settings(system_type,    settings_name,       units,    
                  parameters,     init={},             tspan=[],           
                  priors={},      parameter_bounds={}, fixed_parameters=[], 
                  solver_args={}, init_orient='scenario'):
    '''
    Checks and standardizes formatting of data types.
    '''
    
    core_model = mh.quick_search(system_type)
    if type(parameters) == DataFrame:
        param_values = parameters
    else:
        try:
            param_values = DataFrame(parameters)
        except:
            param_values = DataFrame([parameters])
    
    init1        = sc.check_and_assign_init(core_model['states'], init, init_orient)
    tspan1       = sc.check_and_assign_tspan(tspan)
    priors1      = sc.check_and_assign_priors(param_values, priors)
    bounds1      = sc.check_and_assign_parameter_bounds(param_values, parameter_bounds)
    solver_args1 = sc.check_and_assign_solver_args(solver_args)

    if fixed_parameters:
        if not all([p in core_model['states'] for p in fixed_parameters]):
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
def add_settings_to_database(settings):
    global SBase
    
    core_model = mh.quick_search(settings['system_type'])

    try:
        params_dict = settings['parameters'].to_dict('list')
    except:
        params_dict = settings['parameters'] 
    
    row = {'system_type'   : ', '.join(core_model['system_type']),
           'settings_name' : str(settings['settings_name']),
           'units'         : str(settings['units']),
           'parameters'    : str(params_dict),
           }
    for key1 in ['init', 'priors', 'parameter_bounds']:
        row[key1] = str({key2: list(settings[key1][key2]) for key2 in settings[key1]})
    
    row['tspan']            = str([list(span) for span in settings['tspan']])
    row['fixed_parameters'] = str(settings['fixed_parameters'])
    row['solver_args']      = str(settings['solver_args'])
    
    with SBase:  
        add_row('settings', row, SBase)
        print('Added settings ' + row['settings_name'])
    return row['system_type'], row['settings_name']

def add_row(table, row, database=SBase):

    row_   = '(' + ', '.join([k for k in row.keys()]) + ')'
    values = tuple(row.values())
    
    sql = 'REPLACE INTO ' + table + str(row_) + ' VALUES(' + ','.join(['?']*len(values)) + ')'
    cur = database.cursor()
    cur.execute(sql, values)
    return cur.lastrowid

###############################################################################
#Search
###############################################################################    
def search_settings(system_type, settings_name='', skip_constructor=False):
    global SBase
    database     = SBase
    core_model   = mh.quick_search(system_type)
    system_type1 = ', '.join(core_model['system_type'])
    
    if settings_name:
        comm = 'SELECT * FROM settings WHERE system_type LIKE "%' + system_type1 + '%" AND settings_name LIKE "%' + settings_name + '%";'
    else:
        comm         = 'SELECT * FROM settings WHERE system_type LIKE "%' + system_type1 + '%";'
    
    cursor          = database.execute(comm)
    all_settings = cursor.fetchall()    
    

    # #Evaluate and get lists
    # all_settings = [[ [] if not pe[i] else pe[i] if '{' in pe[i] else pe[i].split(', ') for i in range(len(pe))] for pe in all_settings]
    
    columns = database.execute('PRAGMA table_info(settings);')
    columns = columns.fetchall()
    columns = [column[1] for column in columns]
    all_settings  = [dict(zip(columns, s)) for s in all_settings]
    
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
        return all_settings
    
    all_settings = [make_settings(**s) for s in all_settings]

    return all_settings 

def quick_search(system_type, settings_name='', error_if_no_result=True, **kwargs):

    if settings_name:
        result = search_settings(system_type, settings_name=settings_name, **kwargs)
        if result:
            result
            return result[0]
        else:
            raise Exception('Could not find parameters for system_type '  + str(system_type))
    else:
        result = search_settings(system_type, settings_name='__default__', **kwargs)
        if result:
            return result[0]
        else:
            try:
                result = search_settings(system_type, settings_name='')
                return result[0]
            except:
                if error_if_no_result:
                    raise Exception('Could not find default parameters for system_type '  + str(system_type))
    return {}
    
def list_settings():
    database  = SBase
    comm      = 'SELECT system_type, settings_name FROM settings'
    
    cursor       = database.execute(comm)
    all_settings = [s for s in cursor.fetchall()]
    
    return all_settings

###############################################################################
#Interfacing with Pandas
###############################################################################
def to_df():
    global SBase
    database  = SBase
    df        = read_sql_query("SELECT * from settings", database)
    return df

def from_df_replace(df):
    '''
    For backend maintenance only. Do not run unless you know what you are doing.
    '''
    global SBase
    database = SBase
    return df.to_sql('settings', database, if_exists='replace', index=False)

###############################################################################
#Interfacing with Configparser
###############################################################################    
def from_config(filename):
    '''
    Returns a dict for constructing a parameter ensemble
    '''
    
    config              = configparser.RawConfigParser()
    config.optionxform  = lambda option: option
    parameter_ensembles = []
    with open(filename, 'r') as file:
        config.read_file(file)
    
    for section in config.sections():
        if section in ['id', 'system_type', 'states', 'parameters', 'inputs', 'equations', 'ia']:
            continue
        
        system_type   = config[section]['system_type']
        params        = config[section]['parameter_values']
        units         = config[section]['units']
        init          = config[section].get('init', {})
        priors        = config[section].get('priors', {})
        bounds        = config[section].get('parameter_bounds', {})
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

        params = string_to_dict(params)
        units  = string_to_dict(units)
        priors = string_to_dict(priors) if priors else {}
        bounds = string_to_dict(bounds) if bounds else {}
        
        parameter_ensemble = {'system_type'     : system_type, 
                              'settings_name'   : settings_name,
                              'parameters'      : params,
                              'units'           : units,
                              'init'            : init,  
                              'priors'          : priors, 
                              'parameter_bounds': bounds
                              }
        parameter_ensembles.append(make_settings(**parameter_ensemble))
        
    return parameter_ensembles

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
def make_settings_template(system_types_settings_names, filename='', blank_template=False):
    result = ''
    
    system_types_settings_names1 = [system_types_settings_names] if type(system_types_settings_names) == str else system_types_settings_names
    
    for pair in system_types_settings_names1:
        try:
            system_type, settings_name = pair
        except:
            system_type, settings_name = pair, '__default__'
        
        core_model     = mh.quick_search(system_type)
        parameters     = core_model['parameters'] + core_model['inputs']
        longest        = len(max(parameters, key=len))
        section_header = '[]\nsystem_type = ' + ', '.join(core_model['system_type'])
        
        param_ensemble = {'system_type'     : system_type, 
                          'settings_name'   : settings_name,
                          'parameters'      : [],
                          'units'           : {},
                          'init'            : {},  
                          'priors'          : {}, 
                          'parameter_bounds': {}
                          }
        if not blank_template:
            try:
                param_ensemble = quick_search(system_type, settings_name, skip_constructor=True)
            except:
                pass
            
        init_values   = dict_template('init', core_model['states'], longest, param_ensemble['init'])
        param_values  = dict_template('parameter_values', parameters, longest, param_ensemble['parameters'])
        prior_values  = dict_template('priors', parameters, longest, param_ensemble['priors'])
        bounds_values = dict_template('parameter_bounds', parameters, longest, param_ensemble['parameter_bounds'])
        units_values  = dict_template('units', parameters, longest, param_ensemble['units'])
        
        model_id         = '#id = ' + str(core_model['id'])
        model_equations  = '#equations = \n' + '\n'.join(['#\t' + line for line in core_model['equations'] ])
        section_header   = '\n'.join([section_header, model_id, model_equations])
        
        result += '\n\n'.join([section_header, init_values, param_values, prior_values, bounds_values, units_values])
        
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
    global SBase

    all_settings = from_config(filename)
    
    result = list(map(add_settings_to_database, all_settings))
    
    return result

###############################################################################
#Deletion
###############################################################################
def delete(system_type, settings_name):
    try:
        param_ensemble  = quick_search(system_type, settings_name)
        system_type1   = param_ensemble['system_type']
        settings_name1 = param_ensemble['settings_name']
    except:
        print('param ensemble or id ' + str(system_type) + '/' + str(settings_name) + 'not found')
        return
    
    system_type1 = ', '.join(system_type1)

    comm = 'DELETE FROM settings WHERE system_type="'+ system_type1 + '" AND settings_name="' + settings_name1 +'";'    
    SBase.execute(comm)
    print('Removed [' + str(system_type1) + ']/' + str(settings_name1))
    
###############################################################################
#Reset
###############################################################################
def reset_SBase():
    '''
    Deletes all ensembles in SBase.
    '''
    global SBase
    global __dir__
    print('Resetting SBase')
    SBase.close()
    db_file = osp.join(__dir__, 'SBase.db')
    os.remove(db_file)
    SBase   = mh.create_connection(db_file)
    mh.create_table(SBase, table_sql, table_unique_sql)
    
###############################################################################
#Function for Setup
###############################################################################
# def setup():
#     global SBase
    
#     db_file     = osp.join(osp.realpath(osp.split(__file__)[0]), 'SBase.db')
#     database    = mh.create_connection(db_file)
#     res         = database.execute("SELECT name FROM sqlite_master WHERE type='table';")
#     table_names = [table[0] for table in res]
#     if 'settings' not in table_names:
#         mh.create_table(database, table_sql, table_unique_sql)
#     SBase = database
#     print('Connected to SBase')
#     return database

def setup():
    
    for database in [mh.MBase, mh.UBase]:
        res         = database.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_names = [table[0] for table in res]
        if 'settings' not in table_names:
            mh.create_table(database, table_sql, table_unique_sql)
    
    print('Connected to MBase_settings, UBase_settings')
    return database

###############################################################################
#Initialization
###############################################################################
setup()

if __name__ == '__main__':
    __settings__ = {'system_type'      : ['Monod', 'Constitutive', 'Single'],
                    'settings_name'    : '__default__',
                    'units'            : {'mu_max' : '1/min', 
                                          'Ks'     : '% Glu', 
                                          'Y'      : 'OD/% Glu', 
                                          'synh'   : 'M/min'
                                          },
                    'parameters'       : DataFrame({'mu_max' : np.array([0.02]), 
                                                    'Ks'     : np.array([0.15]), 
                                                    'Y'      : np.array([4]), 
                                                    'synh'   : np.array([1e-06])
                                                    }),
                    'init'             : {'x' : [0],
                                          's' : [0],
                                          'h' : [0]
                                          },
                    'parameter_bounds' : {'mu_max' : [0.001, 0.03], 
                                          'Ks'     : [0.01, 0.5], 
                                          'Y'      : [0, 10], 
                                          'synh'   : [1e-7, 5e-5]
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
    

    __settings__['init'] = {1: [0, 0, 0]
                            }
    __settings__['parameter_bounds'] = {}
    # __settings__['init'] =[[0, 0, 0], [0, 0, 0]]
    # __settings__['init'] =[0, 0, 0]
    
    settings = make_settings(**__settings__)
    
    
