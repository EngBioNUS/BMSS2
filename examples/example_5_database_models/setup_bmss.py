
'''
Adds base directory to path so BMSS can be imported. You can just use import BMSS 
if you have successfully installed it using pip.
'''

import sys
from os       import getcwd, listdir
from os.path  import abspath, dirname, join

try:
    import BMSS
except:
    #Get base directory
    __base_dir__ = dirname(dirname(dirname(__file__)))
    
    #Append to path
    sys.path.insert(0, __base_dir__)
    
#Add Styles
try:
    __src_dir__  = join(__base_dir__, 'BMSS')
    library      = join(__src_dir__, 'stylelib')
    styles       = {file.split('.')[0]: abspath(join(library,file)) for file in listdir(library)}
except:
    styles = {}

