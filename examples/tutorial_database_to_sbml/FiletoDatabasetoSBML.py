# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 10:48:32 2020

@author: Wilbert
"""
import simplesbml
import BMSS.models.model_handler as mh
import BMSS.models.settings_handler as sh
import glob
  
def BMSSmodeltoSBML(path):
    #Look up folder with .ini files
    
    
    files = []

    files = [f for f in glob.glob(path + "**/*.ini", recursive=True)]
    
    for f in files:
        print('\n')
        print(f)
    
    new_files = files
    
    sbmlfilelist=[]
    number_scenario = 0
       
    for l in range(len(files)):    #Add ini files to database
        tempfilestart = files[l].index("ConfigSBML")
        tempfileend = files[l].index(".ini")                          
        new_files[l] = files[l][tempfilestart+11:]
        filename = new_files[l]
        system_type = mh.config_to_database(filename)
        system_types_settings_names = sh.config_to_database(filename)
        system_type, settings_name = system_types_settings_names[0]
        search_result_model = mh.quick_search(system_type)
        search_result_settings = sh.quick_search(system_type=system_type, settings_name=settings_name)
        core_model    = search_result_model
        settings = search_result_settings
        unit_model = settings['units']
        equations = core_model['equations']
        addparam =  settings['parameters']
        number_init = len(settings['init'])
        number_parameters = len(settings['parameters'])
        
        for w in unit_model: #Unit Look-up/conversion
            unit_model[w] = unit_model[w].replace('1/', 'per_') 
            unit_model[w] = unit_model[w].replace('M/', 'molper') 
            unit_model[w] = unit_model[w].replace('NONE', 'Dimension_less') 
            unit_model[w] = unit_model[w].replace('dimensionless', 'Dimension_less')
            unit_model[w] = unit_model[w].replace('% Arabinose', 'mol') 
            unit_model[w] = unit_model[w].replace('/l', 'L') 
            unit_model[w] = unit_model[w].replace('sec', 'second')
            unit_model[w] = unit_model[w].replace('secondonds', 'seconds')
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
                
                
                for i in range(len(core_model['states'])):
                    
                    if equations[i][0] == 'd': #if equation is for deritive with time
                        variable_start = equations[i].index("d")
                        variable_end = equations[i].index("=")
                        equations[i] = equations[i].replace('**', '^')  
                        variable_name = equations[i][variable_start+1:variable_end-1]
                        model_sbml.addRateRule(variable_name, equations[i][variable_end+2:])
                        
                    else: #if equation is for variable directly
                        variable_end = equations[i].index("=")
                        assignment_name = equations[i][:variable_end-1]
                        equations[i] = equations[i].replace('**', '^') 
                        model_sbml.addAssignmentRule(assignment_name, equations[i][variable_end+2:])
                        #model_sbml.addRateRuleRule(assignment_name, '0') #Will get missing differential if not included

                
                number_scenario = number_scenario + 1
                convertion = model_sbml.toSBML()
                tempfileend = files[l].index(".ini")
                placeholder = files[l][:tempfileend]
                sbmlfilename = 'DatabasetoSBML_' + placeholder +'.xml'
                f = open(sbmlfilename, 'w') #creates SBML file in same folder as python script
                f.write(convertion)
                f.close()
                del model_sbml
                sbmlfilelist.append(sbmlfilename)
        
    
    print()
    print('Number of Files Printed =', number_scenario)
    print('SBML files outputed: ', sbmlfilelist)
#Change according to where ini files are located. Include the "\\"


path = 'd:\\Git\\BMSS2\\examples\\tutorial_2_simulation\\ConfigSBML\\' 


BMSSmodeltoSBML(path)

