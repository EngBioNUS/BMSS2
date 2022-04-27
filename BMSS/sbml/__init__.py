from .OnlinetoConfig import (get_online_biomodel, 
                             gen_settingstemplate,
                             gen_config,
                            )
from .sbmlgen        import (database_to_sbml, 
                             autogenerate_sbml_from_folder, 
                            )
from .combinegen     import *
# from .               import OnlinetoConfig
# from .               import sbmlgen 
from .sbml_converter import *
# sbml_to_config = lambda *args, **kwargs: OnlinetoConfig.sbmltoconfig(*args, **kwargs)[0]

# def sbml_to_config(sbmlfile, system_type, output_path='', tspan=None, is_path=True):
#     '''Converts SBML file to config file(s).
    
#     :param sbmlfile: Path-like or SBML string.
#     :param system_type: The system_type for naming the model.
#     :param output_paths: The location for creating the config files. No files will be created if the string is empty.
#     :param tspan: A list/array of time points.
#     :param is_path: True if sbmlfile is a path, False if sbmlfile is an SBML string.
#     :return result: Config string.
    
#     '''
#     if is_path:
        
#         with open(sbmlfile, 'r') as file:
#             sbmlstr = file.read()
#     else:
#         sbmlstr = sbmlfile
        
#     result  = OnlinetoConfig.sbmltoconfig(sbmlstr, system_type, output_path, tspan)
#     return result

# def config_to_sbml(inifile, output_path=''):
#     '''Converts config file(s) to SBML.
    
#     :param inifile: Path-like or ini string.
#     :param output_paths: The location for creating the config files. No files will be created if the string is empty.
#     :return result: List of output files.
    
#     '''
#     return sbmlgen.config_to_sbml([inifile], output_path)