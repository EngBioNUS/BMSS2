import configparser
import importlib
import os
import os.path    as osp
import sqlite3    as sq
from   pandas     import concat, DataFrame, Series, read_sql_query
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
MBase   = None
UBase   = None
__dir__ = osp.dirname(osp.abspath(__file__))


table_sql = '''
CREATE TABLE "models" (
    "id"           TEXT,
	"system_type"  TEXT,
	"states"	   TEXT,
    "parameters"   TEXT,
    "inputs"       TEXT,
    "equations"    TEXT,
    "ia"           TEXT 
);
'''

table_unique_sql='''
CREATE UNIQUE INDEX idx_positions_title ON models (system_type);
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
#Model Storage
###############################################################################
def add_model_to_database(model):
    '''
    Accepts a model in dict form and adds it to UBase.
    '''
    if 'BMSS' in model['system_type']:
        raise Exception('system_type cannot contain "BMSS" as keyword.')
    return backend_add_model_to_database(model, database=UBase)

###############################################################################
#Supporting Functions
###############################################################################
def backend_add_model_to_database(model, database):
    '''
    Supporting function for add_model_to_database. Do not run.
    '''
    global MBase
    global UBase
    
    if type(model) == dict:
        model1 = model
    elif type(model) == str:
        #Assume .ini file
        model1 = from_config(model)
    elif type(model) == Series:
        model1 = model.to_dict()
    else:
        raise TypeError('Model is neither a filename, a dict nor a Series.')
     
    with database:
        system_type = ', '.join(model1['system_type'])
        other       = MBase   if database == UBase else UBase
        d           = 'MBase' if database == MBase else 'UBase'
        
        #Ban addition if system_type exists in other database
        if system_type in list_models(database=other):
            raise Exception('system_type ' + system_type + ' already in ' + d + '. Please choose a different system_type.')
            
        try:
            #Check if model is in database
            existing_model = search_models(system_type, search_type ='system_type', database=database)[0]
            if existing_model['id']:
                #Existing model is being modified. Reuse id.
                model1['id']   = existing_model['id'] 
                make_new_id    = False
            else:
                #This should not happen.
                Warning('system_type ' + system_type + 'is already in ' + d +' but does not have an id. BMSS will add an id now.')
                make_new_id = True
        except:
            #Make new id if model is not in DBase
            make_new_id = True

        row    = string_dict_values(model1)    
        row_id = add_row('models', row, database)

        #Update id based on row number if the model is new
        if make_new_id:
            if database == MBase:
                model_id = 'bmss' + str(row_id) 
            else:
                model_id = 'usr' + str(row_id)
            update_value_by_rowid(row_id, 'id', model_id, database)
        
        o = 'Added model ' if make_new_id else 'Modified model '
        n =  model_id      if make_new_id else model1['id']
        print(o + n + ' to '+ d)
    return row_id

def string_dict_values(model):

    model_dict = {key: model[key] if type(model[key]) == str else ', '.join(model[key]) for key in model}

    return model_dict

def update_value_by_rowid(row_id, column_id, value, database):
    
    sql = "UPDATE models SET " + column_id + " = '" + str(value) + "' WHERE rowid = " + str(row_id) 
    cur = database.cursor()
    cur.execute(sql)
    
def add_row(table, row, database):
    
    row_   = '(' + ', '.join([k for k in row.keys()]) + ')'
    values = tuple(row.values())
    
    sql = 'REPLACE INTO '+table+str(row_)+' VALUES(' + ','.join(['?']*len(values))+ ')'
    cur = database.cursor()
    cur.execute(sql, values)

    return cur.lastrowid

###############################################################################
#Search
###############################################################################
def search_models(keyword, search_type='system_type', database=None):
    global MBase
    global UBase
    
    keyword1  = keyword if type(keyword) == str else ', '.join(keyword)
    comm      = 'SELECT * FROM models WHERE ' + search_type + ' LIKE "%' + keyword1 + '%";'
    result    = []
    
    databases = [database] if database else [MBase, UBase]
    for database in databases:
        cursor    = database.execute(comm)
        models    = cursor.fetchall()    
        
        #Evaluate and get lists
        models = [[model[i].split(', ') if model[i] else [] for i in range(len(model))] for model in models]
                
        columns = database.execute('PRAGMA table_info(models);')
        columns = columns.fetchall()
        columns = [column[1] for column in columns]
        models  = [dict(zip(columns, model)) for model in models]
        for model in models:
            model['id'] = model['id'][0]
            model['ia'] = model['ia'][0] if model['ia'] else ''
        
        result += models
    return result
    
def quick_search(system_type, error_if_no_result=True):
    '''
    Searches both system_type and id and returns the first result.
    Meant to be used when you know the exact system_type/id.
    Raises an error when no matches are found if error_if_no_result is set to True.
    '''
    try:
        core_model = search_models(system_type, search_type='system_type') + search_models(system_type, search_type='id')
        core_model = core_model[0]
    except:
        if error_if_no_result:
            raise Exception('Could not retrieve model with system_type ' + str(system_type))
    return core_model

def list_models(database=None):
    if database:
        comm      = 'SELECT system_type FROM models'
        cursor    = database.execute(comm)
        models    = [m[0] for m in cursor.fetchall()]
        
        return models
    else:
        global MBase
        global UBase
        return list_models(MBase) + list_models(UBase)

def get_model_function(keyword, search_type='system_type'):
    '''
    Returns model function. Assumes .py file is already stored in model_functions folder.
    '''
    core_model     = search_models(keyword, search_type=search_type)[0] 
    model_function = get_model_function_from_core_model(core_model)
    return model_function 

def get_model_function_from_core_model(core_model):
    '''
    Supporting function for get_model_function. Do not run.
    '''
    model_name     = '_'.join(core_model['system_type'])
    module         = importlib.import_module('.model_functions.' + model_name, 'BMSS.models')
    model_function = getattr(module, 'model_'+  model_name )
    
    return model_function

###############################################################################
#Interfacing with Pandas
###############################################################################
def to_df(database=None):
    if database:
        df = read_sql_query("SELECT * from models", database)
        return df
    else:
        global MBase
        global UBase
        df = to_df(MBase), to_df(UBase)
        df = concat(df, ignore_index=True)
        return df

def backend_from_df(df, database=None):
    '''
    For backend maintenance. Do not run unless you know what you are doing.
    '''
    return df.to_sql('models', database, if_exists='replace', index=False)

###############################################################################
#Interfacing with Configparser
###############################################################################
def from_config(filename):
    config = configparser.ConfigParser()
    model  = {'id'          : '',
              'system_type' : [],
              'states'      : [], 
              'parameters'  : [],
              'inputs'      : [],
              'equations'   : [],
              'ia'          : ''
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
        else:
            line = config[key][key].replace('\n', ',').split(',')
            line = [s.strip() for s in line if s]
        
        model[key] = line
    
    is_valid, text = check_model_terms(model)
    if not is_valid:
        raise Exception('Error in ' + str(model['system_type']) + ': ' + text)
    return model

def to_config(model, filename):
    config = configparser.ConfigParser()
    
    for key in model:
        if not model[key]:
            continue
        if type(model[key]) == str:
            line = model[key]
        elif key == 'equations':
            line = '\n' + '\n'.join(model[key])
        else:
            line = ', '.join(model[key])
        config[key] = {key:line}
        
    with open(filename, 'w') as configfile:
        config.write(configfile)
    
    return config

###############################################################################
#Direct Config to Database
###############################################################################
def config_to_database(filename):
    global UBase
    return backend_config_to_database(filename, database=UBase)

def backend_config_to_database(filename, database):
    '''
    For backend maintenance. Do not run.
    '''
    model     = from_config(filename)
    backend_add_model_to_database(model, database)
    return model['system_type']

###############################################################################
#Deletion
###############################################################################
def delete(system_type):
    try:
        model        = quick_search(system_type)
        system_type1 = model['system_type']
    except:
        print('system_type or id ' +str(system_type) + 'not found')
        return
    
    system_type1 = ', '.join(system_type1)
    if system_type1 in list_models(UBase):
        sql = 'DELETE FROM models WHERE system_type="'+ system_type1 + '";'    
        res = UBase.execute(sql)
        print('Removed [' + system_type1 + ']')
    else:
        print('Cannot remove model from MBase')
    
###############################################################################
#Function for Setup
###############################################################################
def setup():
    global UBase
    global MBase
    for filename in ['MBase.db', 'UBase.db']:
        db_file     = osp.join(__dir__, filename)#osp.join(osp.realpath(osp.split(__file__)[0]), filename)
        database    = create_connection(db_file)
        res         = database.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_names = [table[0] for table in res]
        if 'models' not in table_names:
            create_table(database, table_sql, table_unique_sql)
        
        if filename == 'MBase.db':
            MBase = database
        else:
            UBase = database
    
    print('Connected to MBase_models, UBase_models')
    return database

###############################################################################
#Reset
###############################################################################
def reset_MBase_models():
    '''
    Deletes all models in MBase and loads models in BMSS/models/markup.
    '''
    global MBase
    global __dir__
    print('Resetting MBase')
    MBase.close()
    db_file = osp.join(__dir__, 'MBase.db')
    os.remove(db_file)
    MBase   = create_connection(db_file)
    create_table(MBase, table_sql, table_unique_sql)
    
    directory = osp.join(__dir__, 'markup')
    
    filenames = os.listdir(directory)    

    for filename in filenames:
        filename1 = osp.join(directory, filename)
        backend_config_to_database(filename1, database=MBase)
    
def reset_UBase_models():
    '''
    Deletes all models in UBase.
    '''
    global UBase
    global __dir__
    print('Resetting MBase')
    UBase.close()
    db_file = osp.join(__dir__, 'UBase.db')
    os.remove(db_file)
    UBase   = create_connection(db_file)
    create_table(UBase, table_sql, table_unique_sql)

###############################################################################
#Initialization
###############################################################################
setup()

if __name__ == '__main__':
    from os.path import dirname, join
    from os import getcwd

    __model__ = {'id'          : 'bmss01001',
                 'system_type' : ['DUMMY', 'DUMMY'],
                 'states'      : ['mRNA', 'Pep'], 
                 'parameters'  : ['syn_mRNA', 'deg_mRNA', 'syn_Pep', 'deg_Pep', 'Ki'],
                 'inputs'      : ['Ind'],
                 'equations'   : ['dmRNA = syn_mRNA*Ind/(Ind + Ki) - deg_mRNA*mRNA',
                                  'dPep  = syn_Pep*mRNA - deg_Pep'
                                  ],
                 'ia'          : 'ia_result_bmss01001.csv'
                 
                 }
    
#    backend_add_model_to_database(__model__, MBase)
    add_model_to_database(__model__)
    
    print(to_df()['system_type'])
    delete('DUMMY, DUMMY')
    print('..............')
    print(to_df()['system_type'])
#    
#    df = to_df()

    
#    filename = join(dirname(getcwd()), 'examples', 'Monod_Constitutive_Single.ini')
#    
#    d = from_config(filename)
#    print(d)
#    
#    to_config(d, 'template.ini')
#    
#    model_to_code(d, local=True)

#    search_result = search_models('Inducible, ConstInd')
#    print(search_result)
#    print(list_models())