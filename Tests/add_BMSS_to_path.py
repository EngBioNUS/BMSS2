import sys
from os       import getcwd, listdir
from os.path  import abspath, dirname, join

#Add BMSS path
_dir = dirname(dirname(__file__))
sys.path.insert(0, _dir)
