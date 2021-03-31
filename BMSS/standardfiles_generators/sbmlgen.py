# -*- coding: utf-8 -*-
"""
This module contains functions to generate SBML standard files.

Features:
-to generate SBML .xml files from a list of configuration files
-to generate SBML files from model database
-to autogenerate SBML .xml files for all configuration files contained inside a folder path  
"""

import os
import glob

import BMSS.standardfiles_generators.simplesbml as simplesbml
import BMSS.models.model_handler    as mh
import BMSS.models.settings_handler as sh

def unitlookup(settings):
    '''Reads in the list of units listed in the database and converts them to 
    units defined in simplesbml
    :param settings:  settings database of model
    :return: cleaned units of parameters in list format
    
    :meta private:
    '''
    
    unit_model = settings['units']
    
    #--Checker--
    assert len(unit_model) == len(settings['parameters'].columns), 'Not all Parameters have units declared'
    
    for w in unit_model: #Unit Look-up/conversion
        unit_model[w] = unit_model[w].replace('aa', 'items') 
        unit_model[w] = unit_model[w].replace('mol-1', 'permol')
        unit_model[w] = unit_model[w].replace('molmin-1', 'molpermin')
        unit_model[w] = unit_model[w].replace('1/', 'per_') 
        unit_model[w] = unit_model[w].replace('M/', 'molper') 
        unit_model[w] = unit_model[w].replace('NONE', 'Dimension_less') 
        unit_model[w] = unit_model[w].replace('dimensionless', 'Dimension_less')
        unit_model[w] = unit_model[w].replace('/l', 'L') 
        unit_model[w] = unit_model[w].replace('sec', 'second')
        unit_model[w] = unit_model[w].replace('molL-1min-1', 'molperLmin') 
        unit_model[w] = unit_model[w].replace('min-1', 'per_min')
        unit_model[w] = unit_model[w].replace('molL-1', 'molperL')   
        
    return unit_model

def SBMLcreation(core_model, settings, unit_model, addparam, init_scenario, param_scenario):
    '''Reads in the core model, settings, parameters and which scenario of 
    init and parameters values and outputs SBML format in sbmlstr
    :param core_model:  core model of model in nested dictionary format
    :param settings:  settings database of model
    :param unit_model:  units for parameters in list format
    :param addparam:  parameters of model in dataframe
    :param init_scenario:  init value scenario in int format
    :param param_scenario:  parameter value scenario in int format
    :return: SBML string in XML format
    :meta private:
    '''
    
    #--Checker--
    assert core_model['system_type'] == settings['system_type'], 'System_type not the same between the core_model and settings'
    if 'inputs' in core_model.keys():
        assert (len(core_model['parameters'])+len(core_model['inputs'])) == len(addparam.columns), 'settings have missing parameters'
    else:
        assert len(core_model['parameters']) == len(addparam.columns), 'settings have missing parameters'
    
        
    
    
    model_sbml = simplesbml.SbmlModel()      
    for i in range(len(core_model['states'])):
        model_sbml.addSpecies(core_model['states'][i], settings['init'][init_scenario+1][i])    
    
    for i in range(len(addparam.columns)):
        name = addparam.columns[i]
        model_sbml.addParameter(name, addparam.values[param_scenario,i], units = unit_model[name])
    
    for eqn in core_model['equations']:
        if eqn is not '':
            if eqn[0] == 'd': #if equation is for deritive with time
                variable_start = eqn.index("d")
                variable_end = eqn.index("=")
                eqn = eqn.replace('**', '^')  
                variable_name = eqn[variable_start+1:variable_end-1]
                model_sbml.addRateRule(variable_name, eqn[variable_end+2:])
                
            else: #if equation is for variable directly
                variable_end = eqn.index("=")
                assignment_name = eqn[:variable_end-1]
                eqn = eqn.replace('**', '^') 
                model_sbml.addAssignmentRule(assignment_name, eqn[variable_end+2:])
                
    sbmlstr = model_sbml.toSBML()
    return sbmlstr

  
def config_to_sbml(inifileslist):
    '''Read in list of configuration files and generate the corresponding SBML
    files.
    
    :param inifileslist: a list of input configuration files in strings.
    :type inifileslist: list
    '''
    
    sbmlfilelist=[]
    number_scenario = 0
    
    for f in inifileslist:
        print('\n', f)
    
       
    for f in inifileslist:    #Add ini files to database
        print('filename', f)
        system_type = mh.config_to_database(f)
        system_types_settings_names = sh.config_to_database(f)
        system_type, settings_name = system_types_settings_names[0]
        search_result_model = mh.quick_search(system_type)
        search_result_settings = sh.quick_search(system_type=system_type, settings_name=settings_name)
        core_model    = search_result_model
        settings = search_result_settings
        addparam =  settings['parameters']
        number_init = len(settings['init'])
        number_parameters = len(settings['parameters'])
        unit_model = unitlookup(settings)
    
        for j in range(number_init): #Cycle through number of init values
            for k in range(number_parameters): #Cycle through number of parameters
                sbmlstr = SBMLcreation(core_model, settings, unit_model, addparam, j, k)
                #Function that creates SBML file and returns the number of files outputed and the file list.
                number_scenario = number_scenario + 1
                placeholder = os.path.splitext(f)[0]
                sbmlfilename = 'DatabasetoSBML_' + placeholder +'.xml'
                f = open(sbmlfilename, 'w') #creates SBML file in same folder as python script
                f.write(sbmlstr)
                f.close()
                del sbmlstr
                sbmlfilelist.append(sbmlfilename)
    
    print()
    print('Number of Files Printed =', number_scenario)
    print('SBML files outputed: ', sbmlfilelist)

                            



def autogenerate_sbml_from_folder(folderpath):
    '''To automatically generate the corresponding SBML files from the given
    folder containing all the configuration files.
    
    :param folderpath: the path to the folder containing all the configuration files.
    :type folderpath: str
    '''
        
    files = [f for f in glob.glob(os.path.join(folderpath,"**/*.ini"), recursive=True)]
    
    for f in files:
        print('\n', f)

    sbmlfilelist=[]
    number_scenario = 0
       
    for f in files:    #Add ini files to database
        system_type = mh.config_to_database(f)
        system_types_settings_names = sh.config_to_database(f)
        system_type, settings_name = system_types_settings_names[0]
        search_result_model = mh.quick_search(system_type)
        search_result_settings = sh.quick_search(system_type=system_type, settings_name=settings_name)
        core_model    = search_result_model
        settings = search_result_settings
        addparam =  settings['parameters']
        number_init = len(settings['init'])
        number_parameters = len(settings['parameters'])
        unit_model = unitlookup(settings)
       
        for j in range(number_init): #Cycle through number of init values
            for k in range(number_parameters): #Cycle through number of parameters
                sbmlstr = SBMLcreation(core_model, settings, unit_model, addparam, j, k)
                number_scenario = number_scenario + 1
                placeholder = os.path.splitext(os.path.basename(f))[0]
                sbmlfilename = os.path.join(folderpath, 'DatabasetoSBML_' + placeholder +'.xml')
                f = open(sbmlfilename, 'w') #creates SBML file in same folder as python script
                f.write(sbmlstr)
                f.close()
                del sbmlstr
                sbmlfilelist.append(sbmlfilename)
        
        #Function that creates SBML file and returns the number of files outputed and the file list.
        
    
    print()
    print('Number of Files Printed =', number_scenario)
    print('SBML files outputed: ', sbmlfilelist)


def database_to_sbml(system_type, settings_name):
    '''Select model stored in database and generate the SBML file. 
    :param system_type:  system_type of model to search in database in string format
    :param settings_name:  settings_name of model to search in database in string format
    '''
    sbmlfilelist    = []
    number_scenario = 0

    
    search_result_settings = sh.search_database(system_type, settings_name)
    search_result_model    = mh.quick_search(system_type)
    core_model             = search_result_model
    settings               = search_result_settings[0]
    addparam               = settings['parameters']
    number_init            = len(settings['init'])
    number_parameters      = len(settings['parameters'])
    
    unit_model = unitlookup(settings)
    
    for j in range(number_init): #Cycle through number of init
        for k in range(number_parameters): #Cycle through number of parameters
            sbmlstr = SBMLcreation(core_model, settings, unit_model, addparam, j, k)           
            number_scenario = number_scenario + 1
            sbmlfilename = 'DatabasetoSBML_' + str(number_scenario)+'.xml'
            f = open(sbmlfilename, 'w')
            f.write(sbmlstr)
            f.close()
            del sbmlstr
            sbmlfilelist.append(sbmlfilename)
    #Function that creates SBML file and returns the number of files outputed and the file list.
        
    print()
    print('Number of Scenarios in Model =', number_scenario)
    print('SBML files outputed: ', sbmlfilelist)
