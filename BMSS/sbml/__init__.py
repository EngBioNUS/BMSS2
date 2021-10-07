from .OnlinetoConfig import (get_online_biomodel, 
                             gen_settingstemplate,
                             gen_config,
                            )
from .sbmlgen        import (database_to_sbml, 
                             autogenerate_sbml_from_folder, 
                            )
from .combinegen     import *
from .               import OnlinetoConfig
from .               import sbmlgen 

sbml_to_config = lambda *args, **kwargs: OnlinetoConfig.sbmltoconfig(*args, **kwargs)[0]

def sbml_to_config(sbmlfile, system_type, output_path='', tspan=None, is_path=True):
    if is_path:
        
        with open(sbmlfile, 'r') as file:
            sbmlstr = file.read()
    else:
        sbmlstr = sbmlfile
        
    result  = OnlinetoConfig.sbmltoconfig(sbmlstr, system_type, output_path, tspan)
    return result

def config_to_sbml(inifile, output_path=''):
    return sbmlgen.config_to_sbml([inifile], output_path)