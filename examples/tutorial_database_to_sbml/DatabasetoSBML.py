# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 10:48:32 2020

@author: Wilbert
"""
import simplesbml
import setup_bmss                as lab
import BMSS.models.model_handler as mh
import BMSS.models.settings_handler as sh


def BMSSdatabasetoSBML():
    lst_setting = sh.list_settings()
    lst = mh.list_models()
    sbmlfilelist=[]
    print('\n' * 3)
    
    print('List of Models:')
    for count, key in enumerate(lst):
        print('[',count, ']', key)
        print()
    
    model_number = int(input("Enter only the number in the list of the model you would like to convert to SBML: ")) 
    model_chosen = lst[model_number]
    
    print('List of Settings')
    for count, key in enumerate(lst_setting):
        print('[',count, ']', key)
        print()
        
    setting_number = int(input("Enter only the number in the list of the setting you would like to convert to SBML: ")) 
    setting_number_zero = lst_setting[setting_number][0]
    setting_number_one = lst_setting[setting_number][1]

    
    search_result_settings = sh.search_database(setting_number_zero, setting_number_one)
    search_result_model = mh.quick_search(model_chosen)
    core_model    = search_result_model
    settings = search_result_settings[0]
    unit_model = settings['units']
    equations = core_model['equations']
    addparam =  settings['parameters']
    number_init = len(settings['init'])
    number_parameters = len(settings['parameters'])
    number_scenario = 0
    
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
        
    for j in range(number_init): #Cycle through number of init
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
            sbmlfilename = 'DatabasetoSBML_' + str(number_scenario)+'.xml'
            f = open(sbmlfilename, 'w')
            f.write(convertion)
            f.close()
            del model_sbml
            sbmlfilelist.append(sbmlfilename)
        
    
    print()
    print('Number of Scenarios in Model =', number_scenario)
    print('SBML files outputed: ', sbmlfilelist)

#Converts an existing model in Database to SBML. Run to start
BMSSdatabasetoSBML()        
    

