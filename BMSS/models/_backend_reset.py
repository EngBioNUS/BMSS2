import importlib
import os
import os.path    as osp
from   pathlib    import Path

try:
    from . import _backend_model_handler    as bmh
    from . import _backend_settings_handler as bsh
except:
    import _backend_model_handler    as bmh
    import _backend_settings_handler as bsh
    
###############################################################################
#Globals
###############################################################################
__dir__ = osp.dirname(osp.abspath(__file__))

###############################################################################
#Reset
###############################################################################
def reset_MBase():
    '''
    Provides a safe way to reset MBase. Close all connections to BMSS first.
    '''
    global bmh
    global bsh
    
    importlib.reload(bmh)
    importlib.reload(bsh)
    
    bmh.MBase.close()
    db_file     = osp.join(__dir__, 'MBase.db')
    os.remove(db_file)
    
    importlib.reload(bmh)
    importlib.reload(bsh)
    
    database    = bmh.create_connection(db_file)
    bmh.MBase   = database
    bmh.create_table(database, bmh.table_sql)
    bmh.create_table(database, bsh.table_sql)
    
    #For loading markup files in markup to MBase
    markup_directory = Path(os.getcwd()) /'markup'
    for f in os.listdir(markup_directory):
        print(f)
        filename   = markup_directory/f
        core_model = bmh.from_config(filename)
        
        bmh.backend_add_to_database(core_model, database=bmh.MBase)
        bmh.model_to_code(core_model)
        bsh.backend_config_to_database(filename, bmh.MBase)
        
    
if __name__ == '__main__':
    reset_MBase()