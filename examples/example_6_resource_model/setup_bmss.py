'''
THIS FILE IS NOT MEANT TO BE USED OUTSIDE OF THE EXAMPLES FOLDER!!!
Adds base directory to path so LabAnalysis and LabRecords can be imported. 
'''

import sys
from os       import getcwd, listdir
from os.path  import abspath, dirname, join

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
