import configparser
import importlib
import os
import os.path    as osp
import sqlite3    as sq
import warnings
import yaml       as ya
from   io         import StringIO
from   pandas     import concat, DataFrame, Series, read_sql_query, read_csv
from   sqlite3    import Error

###############################################################################
#Non-Standard Imports
###############################################################################
try:
    from .model_checker import check_model_terms
    from .model_coder   import model_to_code

except:
    from model_checker import check_model_terms
    from model_coder   import model_to_code
    
###############################################################################
#Globals
###############################################################################
MBase  = None
UBase  = None
_dir   = osp.dirname(osp.abspath(__file__))
userid = 'usr'

table_sql = '''
CREATE TABLE IF NOT EXISTS "models" (
    "id"           TEXT,
	"system_type"  TEXT,
	"states"	   TEXT,
    "parameters"   TEXT,
    "inputs"       TEXT,
    "equations"    TEXT,
    "ia"           TEXT,
    "descriptions" TEXT,
    "active"       INTEGER DEFAULT 1,
    UNIQUE(system_type)
);
'''

###############################################################################
#Database and Table Construction
###############################################################################
def create_connection(db_file):
    '''
    Creates database specified by db_file.
    '''
    db = sq.connect(db_file)
    return db

def create_table(db, *args):
    '''
    Creates table.
    Use args to add additional sql commands.
    '''
    try:
        c = db.cursor()

        for arg in args:
            c.execute(arg)
    except Error as e:
        raise e

###############################################################################
#Constructor
###############################################################################
def make_core_model(system_type, states, parameters, inputs, equations, descriptions=None, ia='', **kwargs):
    '''Returns a dictionary with the keys id, system_type, states, parameters, inputs, equations, ia.
    Otherwise referred to as a core_model in the BMSS2 documentation. Redundant
    states, parameters and inputs are disallowed.
    
    :param system_type: A string of keywords serving as a unique identifier for 
        the core_model separated by commas, will be formatted so there is one space
        after each comma, keywords should be in CamelCase
    :type system_type: str
    :param states: A list of strings corresponding to state names used in the core_model
    :type states: list
    :param parameters: A list of strings corresponding to parameter names used in the core_model
    :type parameters: list
    :param inputs: A list of strings corresponding to input names used in the core_model
    :type inputs: list
    :param equations: A list of strings corresponding to lines of equations used in the core_model
        where the lines form coherent Python code when joined by '\n'.join
    :type equations: list
    :param descriptions: A description of the model.
    :type descriptions: dict, optional
    :param ia: For IA results as a string that can be read into csv format. Avoid using this argument.
    :type ia: string, optional
    :kwargs: Will be ignored
    '''    
    if type(system_type) == str:
        system_type1 = ', '.join([s.strip() for s in system_type.split(',')])
    else:
        system_type1 = ', '.join(system_type)
        return make_core_model(system_type1, states, parameters, inputs, equations, descriptions, ia='')
    
    states1       = list(states)
    parameters1   = list(parameters)
    inputs1       = list(inputs)
    equations1    = list(equations)
    descriptions1 = descriptions if descriptions else {}

    core_model = {'id'           : '',
                  'system_type'  : system_type1,
                  'states'       : states1,
                  'parameters'   : parameters1,
                  'inputs'       : inputs1,
                  'equations'    : equations1, 
                  'ia'           : ia,
                  'descriptions' : descriptions1,
                  }
    
    for key in ['states', 'parameters', 'inputs', 'equations']:
        if not all([type(x)==str for x in core_model[key]]):
            raise Exception('Invalid name in ' + key + '. Only strings are allowed.')
    
    if type(core_model['ia']) != str:
        raise Exception('Invalid name in ia. Only strings are allowed.')
    
    is_valid, text = check_model_terms(core_model)
    if not is_valid:
        warnings.warn('Error in ' + str(system_type1) + ' when checking terms: ' + text)
        # raise Exception('Error in ' + str(system_type1) + ' when checking terms: ' + text)
    
    return core_model

def copy_core_model(core_model):
    keys = ['id', 'system_type', 'states' , 'parameters', 'inputs', 'equations', 'ia', 'descriptions']
    
    new_core_model = {}
    for key in keys:
        try:
            value = core_model[key].copy()
        except:
            value = core_model[key]
    
        new_core_model[key] = value
    return new_core_model
        
###############################################################################
#Model Storage
###############################################################################
def add_to_database(core_model, dialog=True):
    '''Accepts a core_model and adds it to UBase.
    '''
    if 'BMSS' in core_model['system_type']:
        raise Exception('system_type cannot contain "BMSS" as keyword.')
    return backend_add_to_database(core_model, database=UBase, dialog=dialog)

###############################################################################
#Supporting Functions
###############################################################################
def backend_add_to_database(core_model, database, dialog=False):
    '''Supporting function for add_to_database. Do not run.
    
    :meta private:
    '''
    global MBase
    global UBase
    global userid
     
    system_type    = core_model['system_type']
    make_new_id    = True
    existing_model = quick_search(system_type, error_if_no_result=False, active_only=False)
    d              = 'Mbase' if database == MBase else 'UBase'
    if existing_model:
        if dialog:
            while True:
                x = input('Overwrite existing model? (y/n): ')
                if x.lower() == 'y':
                    break
                elif x.lower() == 'n':
                    return existing_model['id']
                else:
                    continue
                    
        if system_type == existing_model['system_type']:
            core_model['id'] = existing_model['id']
            make_new_id = False
                

    row    = string_dict_values(core_model)   
    row_id = add_row('models', row, database)

    #Update id based on row number if the model is new
    if make_new_id:
        model_id = 'bmss' + str(row_id) if database == MBase else userid + str(row_id)

        update_value_by_rowid(row_id, 'id', model_id, database)
    
    else:
        model_id = core_model['id']
    
    o = 'Added model ' if make_new_id else 'Modified model '
    n =  model_id      if make_new_id else core_model['id']
    print(o + n + ' to '+ d)
    
    model_to_code(core_model, local=False)
    return model_id

def string_dict_values(core_model):
    '''Converts core_model to string
    
    :meta private:
    '''
    model_dict = {key: str(core_model[key]) for key in core_model}
    
    return model_dict

def update_value_by_rowid(row_id, column_id, value, database):
    '''Supporting function for backend_add_to_database. Do not run.
    
    :meta private:
    '''
    with database as db:
        comm = "UPDATE models SET " + column_id + " = '" + str(value) + "' WHERE rowid = " + str(row_id) 
        cur  = db.cursor()
        cur.execute(comm)
    
def add_row(table, row, database):
    '''Supporting function for backend_add_to_database. Do not run.
    
    :meta private:
    '''
    row_   = '(' + ', '.join([k for k in row.keys()]) + ', active)'
    values = tuple(row.values()) + ('1',)
    
    with database as db:
        comm = 'REPLACE INTO ' + table + str(row_) + ' VALUES(' + ','.join(['?']*len(values))+ ')'
        cur  = db.cursor()
        cur.execute(comm, values)

    return cur.lastrowid

###############################################################################
#Search
###############################################################################
def search_database(keyword, search_type='system_type', database=None, active_only=True):
    '''Searches database for core_model data structure based on a keyword and a 
    key(field) in the core_model. Returns a list of core_model dictionaries.
    
    :param keyword: A string that will be matched against entries in the database
    :type keyword: str
    :param search_type: A string corresponding to any key in the core_model, will 
        be used for matching
    :type search_type: str
    :param database: Can be either MBase or UBase, if None, this function will search
        both databases, defaults to None
    :type database: SQL Connection, optional 
    :param active_only: A boolean for backend use, if True, this limits the search 
        to rows where the value of active is True, defaults to True
    :type active_only: bool, optional
    '''
    global MBase
    global UBase
    
    keyword1  = keyword if type(keyword) == str else ', '.join(keyword)
    comm      = 'SELECT id, system_type, states, parameters, inputs, equations, ia, descriptions FROM models WHERE ' + search_type + ' LIKE "%' + keyword1 
    result    = []
    if active_only:
        comm      += '%" AND active = 1;'
    else:
        comm += '%";'

    databases = [database] if database else [MBase, UBase]
    for database in databases:
        with database as db:
            cursor    = db.execute(comm)
            models    = cursor.fetchall()    
        
        columns = database.execute('PRAGMA table_info(models);')
        columns = columns.fetchall()
        columns = [column[1] for column in columns if column[1]!='active']
        models  = [dict(zip(columns, model)) for model in models]
        models = [process_model(model) for model in models]
        result += models
    
    return result

def process_model(model):
    '''
    :meta private:
    '''
    
    result = {}
    for key, value in model.items():
        if key in ['id', 'system_type', 'ia']:
            result[key] = value
        else:
            try:
                result[key] = eval(value)
            except Exception as e:
                system_type = model['system_type']
                msg         = 'An error occurred when calling eval on {} for {}'.format(key, system_type)
                raise Exception(msg, *e.args)
    return result

def quick_search(system_type, error_if_no_result=True, **kwargs):
    '''Searches both system_type/id and returns an exact match in system_type/id.
    Raises an error when no matches are found if error_if_no_result is set to True.
    '''
    core_models = search_database(system_type, search_type='system_type', **kwargs)
    for core_model in core_models:
        if core_model['system_type'] == system_type:
            return core_model
    if error_if_no_result:
        raise Exception('Could not retrieve model with system_type ' + str(system_type))
        
    else:
        return

def list_models(database=None):
    '''Returns a list of system_types
    '''
    global MBase
    global UBase
        
    if database:
        with database as db:
            comm      = 'SELECT system_type FROM models WHERE active = 1;'
            cursor    = db.execute(comm)
            models    = [m[0] for m in cursor.fetchall()]
        
        return models
    else:
        return list_models(MBase) + list_models(UBase)

def get_model_function(system_type, local=False):
    '''Supporting function for get_model_function. Do not run.
    
    :meta private:
    '''
    model_name     = system_type.replace(', ', '_')
    if local:
        module = importlib.import_module(model_name)
    else:
        module = importlib.import_module('.model_functions.' + model_name, 'BMSS.models')
    model_function = getattr(module, 'model_'+  model_name )
    
    return model_function

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
        with database as db:
            df = read_sql_query("SELECT * from models", db)
        return df
    else:
        global MBase
        global UBase
        df = to_df(MBase), to_df(UBase)
        df = concat(df, ignore_index=True)
        return df

def backend_from_df(df, database):
    '''For backend maintenance only.
    
    :meta private:
    '''
    with database as db:
        return df.to_sql('models', db, if_exists='replace', index=False)

###############################################################################
#Interfacing with Configparser
###############################################################################
def from_config(filename):
    '''Reads a file and returns a core_model data structure.
    
    :param filename: The name of the file to read.
    :type filename: str
    '''
    config = configparser.ConfigParser()
    config.optionxform  = lambda option: option
    model  = {'system_type'  : [],
              'states'       : [], 
              'parameters'   : [],
              'inputs'       : [],
              'equations'    : [],
              'ia'           : '',
              'descriptions' : {}
              }
    with open(filename, 'r') as file:
        config.read_file(file)
        
    for key in config.sections():
        if key not in model:
            continue
        if key == 'ia':
            line = config[key][key].strip()
        elif key == 'equations':
            line = config[key][key].replace('\n', ',').split(',')
            line = [s.strip() if s else '' for s in line]
            line = line if line[0] else line[1:]
        elif key == 'descriptions':
            temp = config[key]
            line = {k: temp[k] for k in temp}
        else:
            line = config[key][key].replace('\n', ',').split(',')
            line = [s.strip() for s in line if s]
        
        model[key] = line
    
    return make_core_model(**model)

def to_config(core_model, filename):
    '''Exports a core_model data structure to a config file.
    
    :param core_model: The core_model to be exported
    :type core_model: dict
    :param filename: The name of the file to write to
    :type filename: str 
    '''
    config = configparser.ConfigParser()
    
    for key in core_model:
        if not core_model[key]:
            continue
        if type(core_model[key]) == str:
            line = core_model[key]
        elif type(core_model[key]) == dict:
            config[key] = core_model[key]
            continue
        elif key == 'equations':
            line = '\n' + '\n'.join(core_model[key])
        else:
            line = ', '.join(core_model[key])
        config[key] = {key:line}
        
    with open(filename, 'w') as configfile:
        config.write(configfile)
    
    return config

###############################################################################
#Direct Config to Database
###############################################################################
def config_to_database(filename, dialog=True):
    '''Reads a config file containing information for a core_model data structure 
    and adds the core_model to the database.
    
    :param filename: Name of the file to be read
    :type filename: str
    :param dialog: For backend use, defaults to True
    :type dialog: bool, optional
    '''
    global UBase
    return backend_config_to_database(filename, database=UBase, dialog=dialog)

def backend_config_to_database(filename, database, dialog=False):
    '''For backend maintenance. Do not run.
    
    :meta private:
    '''
    core_model = from_config(filename)
    backend_add_to_database(core_model, database, dialog=dialog)
    return core_model['system_type']

###############################################################################
#Updateing IA
###############################################################################
def update_ia(core_model, new_row, save=True):
    '''
    Appends new_row to the core_model['ia'] where new_row can be a dict or Series.
    
    If save is True and the core_model is in the database, the changes will be 
    applied to database.
    '''
    global MBase
    global UBase
    
    s  = new_row if type(new_row) in [Series, DataFrame] else Series(new_row) 
        
    if core_model['ia']:
        df = read_ia(core_model)
        
        try:
            s = s[df.columns]
        except:
            raise Exception('Mismatch in column names. \nExpected: ' +  
                            str(df.columns) + '\nReceived: ' + str(s.index))
            
        #Check if inputs are duplicated
        try:
            row_num          = df['input'][s['input'] == df['input']].index[0]
            df.iloc[row_num] = s
            print('Updated row ' + str(row_num) + ' in ' + str(core_model['system_type']))
        except:
            df = df.append(s, ignore_index=True)
            print('Added row to ' + str(core_model['system_type']))
    
    else:
        df = DataFrame(s).T
    
    ia_string        = df.to_csv(index=False)
    core_model['ia'] = ia_string
    
    if save:
        system_type = core_model['system_type']
        
        if quick_search(system_type, error_if_no_result=False):
            _backend_modify_database(system_type, {'ia': ia_string})
        else:
            print('Changes to ' + str(system_type) + ' not saved to database.')
    else:
        print('Changes to ' + str(core_model['system_type']) + ' not saved to database.')
    return ia_string

def read_ia(core_model, mode='df', filename=''):
    '''
    Reads the string in core_model['ia'] and converts into a DataFrame.
    
    If mode is df, the DataFrame is returned.
    
    If mode is csv, the string is written to a csv file.
    
    If mode is yaml, the method to_dict("record") is called and the resulting
    dict is converted to .yaml.
    '''
    df = read_csv(StringIO(core_model['ia']), header=[0, 1])    
    
    if mode == 'csv':
        return df.to_csv(filename, index=False)
    elif mode == 'yaml':
        d = df.to_dict('record')
        return ya.dump(d, filename=filename)
    else:
        return df

def reset_ia(system_type):
    if quick_search(system_type, error_if_no_result=False):
        _backend_modify_database(system_type, {'ia': ''})
 
###############################################################################
#Modification
###############################################################################
def _backend_modify_database(system_type, data):
    '''
    Updates the row containing system_type with data.
    Automatically determines if the system_type is part of MBase or UBase.
    Not meant to be used on unsanitized data.
    '''
            
    if 'BMSS' in system_type:
        database = MBase
    else:
        database = UBase
    
    with database as db:
        for column, value in data.items():
            comm = "UPDATE models SET " + str(column) + " = '" + str(value) + "' WHERE system_type = '" + str(system_type) + "'"
            cur  = db.cursor()
            cur.execute(comm)
            print('Changes to ' + str(system_type) + ' saved to database.')
        
    return

###############################################################################
#Deletion
###############################################################################
def delete(system_type):
    '''Sets the value of the active column of the core_model in the .db file to 0.
    Can be restored using the restore function.
    '''
    database = UBase
    
    with database as db:
        comm = 'UPDATE models SET active = 0 WHERE system_type = "' + system_type + '";'
        cur  = db.cursor()
        cur.execute(comm)

def restore(system_type):
    '''Sets the value of the active column of the core_model in the .db file to 1.
    '''
    database = UBase

    with database as db:
        comm = 'UPDATE models SET active = 1 WHERE system_type = "' + system_type + '";'
        cur  = db.cursor()
        cur.execute(comm)

def true_delete(system_type, database):
    if not quick_search(system_type, active_only=False, error_if_no_result=False, database=database):
        print(str(system_type) + ' could not be deleted as it was not found.')

    with database as db:
        comm = 'DELETE FROM models WHERE system_type="'+ system_type + '";'    
        db.execute(comm)
        print('Removed ' + system_type)

###############################################################################
#Function for Setup
###############################################################################
def setup():
    global UBase
    global MBase
    global userid
    global _dir
    
    #Database settings
    config = configparser.ConfigParser()
    with open(osp.join(_dir, 'database_settings.ini'), 'r') as file:
        config.read_file(file)
    
    userid = config['userid']['userid']
    
    #Connect to dabatases
    for filename in ['MBase.db', 'UBase.db']:
        db_file     = osp.join(_dir, filename)#osp.join(osp.realpath(osp.split(__file__)[0]), filename)
        database    = create_connection(db_file)
        cursor      = database.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_names = [table[0] for table in cursor]
        if 'models' not in table_names:
            create_table(database, table_sql)
        
        if filename == 'MBase.db':
            MBase = database
        else:
            UBase = database
    
    #Check required folders are present
    lst = os.listdir(_dir)
    for folder in ['model_functions', 'ia_results', 'BMSS_markup']:
        if folder not in lst:
            os.mkdir(osp.join(_dir, folder))
    print('Connected to MBase_models, UBase_models')
    
    return database

def change_userid(new_userid):
    global userid
    
###############################################################################
#Initialization
###############################################################################
setup()

if __name__ == '__main__':
    from   pathlib import Path
    import os
    
    # #For loading markup files in markup to MBase
    # markup_directory = Path(os.getcwd()) /'markup'
    # for f in os.listdir(markup_directory):
    #     filename = markup_directory/f
    #     backend_config_to_database(filename, MBase)
    
    __model__ = {'system_type' : ['DUMMY', 'DUMMY'],
                  'states'      : ['mRNA', 'Pep'], 
                  'parameters'  : ['syn_mRNA', 'deg_mRNA', 'syn_Pep', 'deg_Pep', 'Ki'],
                  'inputs'      : ['Ind'],
                  'equations'   : ['dmRNA = syn_mRNA*Ind/(Ind + Ki) - deg_mRNA*mRNA',
                                  'dPep  = syn_Pep*mRNA - deg_Pep'
                                  ],
                  'ia'          : ''
                 
                  }
    
    # core_model = make_core_model(**__model__)
    # add_to_database(core_model)
    # search_result = quick_search('DUMMY, DUMMY')
    # print(search_result)
    
    # filename = 'dummy.ini'
    # core_model = from_config(filename)
    # to_config(core_model, 'writeout.ini')
    