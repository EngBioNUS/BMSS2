import importlib
import os
import os.path    as osp
from   pathlib    import Path

bmh, bsh = None, None
    
###############################################################################
#Globals
###############################################################################
__dir__ = osp.dirname(osp.abspath(__file__))

###############################################################################
#Reset
###############################################################################
def reset_MBase(*other_files):
    '''
    Provides a safe way to reset MBase. Close all connections to BMSS first. 
    Restart the kernel if necessary.
    '''
    global bmh
    global bsh
    
    to_del = ['MBase.db', 'UBase.db'] + list(other_files)
    
    print(to_del)
    for filename in os.listdir():
        if filename in to_del:
            os.remove(filename)
            msg = 'Deleted {}'.format(filename)
            print(msg)
            
    for filename in os.listdir('model_functions'):
        if '__' not in filename:
            os.remove('model_functions/' + filename)
            msg = 'Removed {} from model_functions.'.format(filename)
            print(msg)
    
    bmh = importlib.import_module('model_handler')
    bsh = importlib.import_module('settings_handler')
    
    #For loading markup files in markup to MBase
    markup_directory = Path(os.getcwd()) /'BMSS_markup'
    for f in os.listdir(markup_directory):
        print('Reading', f)
        filename   = markup_directory/f
        core_model = bmh.from_config(filename)
        
        bmh.backend_add_to_database(core_model, database=bmh.MBase)
        bmh.model_to_code(core_model)
        bsh.backend_config_to_database(filename, bmh.MBase)
    
if __name__ == '__main__':
    '''
    RESTART THE KERNEL OR THIS WILL THROW AN ERROR!
    '''
    reset_MBase()