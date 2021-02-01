from os       import getcwd, listdir
from os.path  import abspath, dirname, join

__all__ = ['models',
           'aicanalysis',
           'curvefitting',
           'sensitivityanalysis',
           'simulation',
           'strike_goldd_simplified',
           'traceanalysis'
           ]

#Add styles
library = join(dirname(__file__), 'stylelib')
styles  = {file.split('.')[0]: abspath(join(library,file)) for file in listdir(library)}