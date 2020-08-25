import sys
from os.path import dirname, abspath

# Get base directory
__base_dir__ = dirname(dirname(dirname(abspath(__file__))))

# avoid duplicate path
if not __base_dir__ in sys.path:
    sys.path.insert(0, __base_dir__)
    
else:
    pass

#print(sys.path)