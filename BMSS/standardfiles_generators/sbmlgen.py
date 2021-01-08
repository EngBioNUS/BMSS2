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

import setup_bmss as lab
import BMSS.standardfiles_generators.simplesbml as simplesbml
import BMSS.models.model_handler as mh
import BMSS.models.settings_handler as sh

def SBMLcreation(core_model, settings, tut7_1, f, folderpath, sbmlfilelist, number_scenario):
    unit_model = settings['units']
    addparam =  settings['parameters']
    number_init = len(settings['init'])
    number_parameters = len(settings['parameters'])
    
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
        
    for j in range(number_init): #Cycle through number of init values
        for k in range(number_parameters): #Cycle through number of parameters
            
            model_sbml = simplesbml.SbmlModel()
                
            for i in range(len(core_model['states'])):
                model_sbml.addSpecies(core_model['states'][i], settings['init'][j+1][i])    
            
            for i in range(len(addparam.columns)):
                name = addparam.columns[i]
                model_sbml.addParameter(name, addparam.values[k,i], units = unit_model[name])
            
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
                        
            number_scenario = number_scenario + 1
            sbmlstr = model_sbml.toSBML()
            if (tut7_1 == "1"): #config_to_sbml
                placeholder = os.path.splitext(f)[0]
                sbmlfilename = 'DatabasetoSBML_' + placeholder +'.xml'
            if (tut7_1 == "2"): #autogenerate_sbml_from_folder
                placeholder = os.path.splitext(os.path.basename(f))[0]
                sbmlfilename = os.path.join(folderpath, 'DatabasetoSBML_' + placeholder +'.xml')
            if (tut7_1 == "3"): #database_to_sbml
                sbmlfilename = 'DatabasetoSBML_' + str(number_scenario)+'.xml'
            f = open(sbmlfilename, 'w') #creates SBML file in same folder as python script
            f.write(sbmlstr)
            f.close()
            del model_sbml
            sbmlfilelist.append(sbmlfilename)
                        
    return number_scenario, sbmlfilelist
    
    
  
def config_to_sbml(inifileslist):
    '''Read in list of configuration files and generate the corresponding SBML
    files.
    
    :param inifileslist: a list of input configuration files in strings.
    :type inifileslist: list
    '''
    tut7_1 = "1" #for conversion function to know which if statement to use
    folderpath = 0 #for conversion function as folderpath needed for autogenerate_sbml_from_folder
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
       
        number_scenario, sbmlfilelist = SBMLcreation(core_model, settings, tut7_1, f, folderpath, sbmlfilelist, number_scenario) 
        #Function that creates SBML file and returns the number of files outputed and the file list.
        
    
    print()
    print('Number of Files Printed =', number_scenario)
    print('SBML files outputed: ', sbmlfilelist)

                            



def autogenerate_sbml_from_folder(folderpath):
    '''To automatically generate the corresponding SBML files from the given
    folder containing all the configuration files.
    
    :param folderpath: the path to the folder containing all the configuration files.
    :type folderpath: str
    '''
    tut7_1 = "2" #for conversion function to know which if statement to use
    
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

        number_scenario, sbmlfilelist = SBMLcreation(core_model, settings, tut7_1, f, folderpath, sbmlfilelist, number_scenario) 
        #Function that creates SBML file and returns the number of files outputed and the file list.
        
    
    print()
    print('Number of Files Printed =', number_scenario)
    print('SBML files outputed: ', sbmlfilelist)


def database_to_sbml(system_type, settings_name):
    '''Select model stored in database and generate the SBML file. 
    '''
    tut7_1 = "3" #for conversion function to know which if statement to use
    folderpath = 0 #for conversion function as folderpath needed for autogenerate_sbml_from_folder
    f = 0 #for conversion function as f needed for autogenerate_sbml_from_folder and config_to_sbml
    sbmlfilelist=[]
    number_scenario = 0

    
    search_result_settings = sh.search_database(system_type, settings_name)
    search_result_model = mh.quick_search(system_type)
    core_model    = search_result_model
    settings = search_result_settings[0]
    
    number_scenario, sbmlfilelist = SBMLcreation(core_model, settings, tut7_1, f, folderpath, sbmlfilelist, number_scenario) 
    #Function that creates SBML file and returns the number of files outputed and the file list.
        
    print()
    print('Number of Scenarios in Model =', number_scenario)
    print('SBML files outputed: ', sbmlfilelist)
