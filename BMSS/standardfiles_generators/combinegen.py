# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 16:28:02 2021

@author: Wilbert
"""

import tellurium as te, os
from pathlib import Path
import glob

import BMSS.standardfiles_generators.simplesbml as simplesbml
import BMSS.standardfiles_generators.sbmlgen as sbmlgen
import BMSS.models.model_handler    as mh
import BMSS.models.settings_handler as sh
import phrasedml


#--- Main Body ---
def database_to_combine(system_type, settings_name, Plot_Variable, outputpath, KISAO_algorithm):
    '''Select model stored in database and generate the SBML file. 
    :param system_type: system type of model in string format
    :param settings_name: settings name of model in string format
    :param Plot_Variable: Variables to be plotted in list format
    :param outputpath:  filepath to output OMEX file in OS path format
    :param KISAO_algorithm:  Kinetic Simulation Algorithm Ontology number in string format   
    '''
    
    KISAOchecker(KISAO_algorithm)
    combinefilelist=[]
    number_scenario = 0

    
    search_result_settings = sh.search_database(system_type, settings_name)
    search_result_model = mh.quick_search(system_type)
    core_model    = search_result_model
    settings = search_result_settings[0]
    
    combinefilename, number_scenario = Combinecreator(core_model, settings, Plot_Variable, outputpath, KISAO_algorithm)
    combinefilelist.append(combinefilename)
   
    
        
    print()
    print('Number of Scenarios in COMBINE File=', number_scenario)
    print('COMBINE files outputed: ', combinefilelist)    

#--- COMBINE Generator and Exporter ---
def Combinecreator(core_model, settings, Plot_Variable, outputpath, KISAO_algorithm):
    '''
    Generates and outputs COMBINE OMEX file.
    :param core_model: core model database of model
    :param settings: settings database of model
    :param Plot_Variable: Variables to be plotted in list format
    :param outputpath:  filepath to output OMEX file in OS path format
    :param KISAO_algorithm:  Kinetic Simulation Algorithm Ontology number in string format 
    :return combine_filename : OMEX file name in string format
    :return total_scenarios : Total number of scenarios in string format
    '''
    
    #--- Extract data from settings and clean up units ---
    number_init = len(settings['init'])
    number_parameters = len(settings['parameters'])
    addparam =  settings['parameters']
    unit_model = sbmlgen.unitlookup(settings)
    total_scenarios = number_init * number_parameters
    print(total_scenarios)
    scenario_name = core_model["system_type"]
    scenario_name = scenario_name.replace(", ", "_")
    modelname_file = []
    antimony_final = []
    
    #--- Generates SBML string and adds to list
    #based on the number of combinations with init 
    #and parameter amts ---
    for j in range(number_init): #Cycle through number of init
        for k in range(number_parameters): #Cycle through number of parameters
            sbmlstr = sbmlgen.SBMLcreation(core_model, settings, unit_model, addparam, j, k) 
            antimony_final.append(te.sbmlToAntimony(sbmlstr))
    
    #--- Generates the scenario name for each SBML string generated ---
    scenario_placeholder = []
    for l in range(total_scenarios):
        for j in range(number_init): #Cycle through number of init
            for k in range(number_parameters):
              temp_scenario_name = '_' + str(j+1)+ '_' + str(k+1)
              scenario_placeholder.append(temp_scenario_name)
              
    #--- Names the models in antimony string according the scenario ---         
    inline_omex = '\n'
    for l in range(total_scenarios):
        scenario_number = l + 1
        scenario_name = scenario_name + scenario_placeholder[l]
        modelname_file.append(scenario_name)
        antimony_final[l] = antimony_final[l].replace('*doc0', modelname_file[l])
        scenario_name = scenario_name.replace(scenario_placeholder[l], "")
        inline_omex = inline_omex + str(antimony_final[l])
        print("This is antimony_final", scenario_number,": \n", antimony_final[l])
    
    #--- Generates phrasedml file ---    
    phrasedml_final = gen_phrasedml(settings, modelname_file, Plot_Variable, KISAO_algorithm)    
    
    #--- Generates and outputs OMEX file---
    inline_omex = inline_omex + phrasedml_final
    combine_filename = 'COMBINE_' + scenario_name + '.omex'
    archive = os.path.join(outputpath, combine_filename)
    print('COMBINE Archive output: ', archive)
    te.exportInlineOmex(inline_omex, archive)
    return combine_filename, total_scenarios


#--- phrasedml generator and its functions ---    
def gen_phrasedml(settings, modelname_file, Plot_Variable, KISAO_algorithm):
    '''
    Generates the phrasedml task statement.
    :param settings: settings database of model
    :param modelname_file: Scenario Model in list format
    :param Plot_Variable: Variables to be plotted in list format
    :param KISAO_algorithm:  Kinetic Simulation Algorithm Ontology number in string format 
    :return: phrasedml in string format
    
    '''
    
    model_statement = ""    
    tspan = settings['tspan']
    
    #--- Generates the tasks statements based on models and sims (number of models * number of sims) --- 
    task_statement = ""
    task_count = 1
    for model_name in range(len(modelname_file)):
        model_statement = model_statement + 'model' + str(model_name+1) + ' = model "' +  modelname_file[model_name] + '"\n'
        for tasksim_count in range(len(tspan)):
            task_statement = task_statement + 'task' + str(task_count)
            task_statement = task_statement + ' = run sim' + str(tasksim_count+1) + ' on '
            task_count += 1
            task_statement = task_statement + 'model' + str(model_name+1) + '\n'
    
    print("Task_statement = \n", task_statement)    
    
    
    print('this is tspan length = ', len(tspan))
    
    #--- Generates simulation statements with tspan (depended on number of tspans declared) ---
    sim_statement = gen_simstatements(tspan, KISAO_algorithm)
    
    #--- Generates the plot variables for each figure ---  
    variabletask_list, task_total = gen_plotvariables(modelname_file, tspan, Plot_Variable)
    
    #--- Groups variables pertaining to the same plot figure together ---                             
    variable_statement, Total_Fig = clean_groupvariables(Plot_Variable, tspan, task_total, variabletask_list) 
      
    #--- Generates the 'plot figure' statements based on tasks and sims --- 
    Plot_statement = gen_figurestatment(Total_Fig, variable_statement, tspan)
    
    phrasedml_final = model_statement + sim_statement + task_statement + Plot_statement

    print("This is phrasedml_final: \n" , phrasedml_final)
    return phrasedml_final
 
def gen_simstatements(tspan, KISAO_algorithm):
    '''
    Generates simulation statements with tspan (depended on number of tspans declared)    
    :param tspan: tspan of model in list of arrays
    :param KISAO_algorithm:  Kinetic Simulation Algorithm Ontology number in string format 
    :return: simulations statements with KISAO algorithm in string format
    '''
    sim_statement = "" 
    for sim_count in range(len(tspan)): 
        tspan_start = float(tspan[sim_count][0])
        tspan_end = float(tspan[sim_count][-1])
        tspan_interval = len(tspan[sim_count])
        sim_statement = sim_statement + 'sim' + str(sim_count+1) + ' = simulate uniform(' 
        sim_statement = sim_statement + str(tspan_start) + ", "+ str(tspan_end) + ", " + str(tspan_interval) + ')\n'
        if KISAO_algorithm != '0':
            sim_statement = sim_statement + 'sim' + str(sim_count+1) + '.algorithm = ' + KISAO_algorithm + '\n'
    return sim_statement


def gen_plotvariables(modelname_file, tspan, Plot_Variable):
    '''
    Generates the plot variables for each figure   
    :param modelname_file: the name of model as per scenario in list format
    :param tspan: tspan of model in list of arrays
    :param Plot_Variable:  Variables to be plotted in list format
    :return variabletask_list: variables in list format 
    :return task_total: total number of tasks (number of sims * number of scenario models) in int format
    '''
    task_total = len(modelname_file) * len(tspan) 
    variabletask_list = []
    for taskvariable in range(task_total):
        for variable_count in range(len(Plot_Variable)):
            variabletask_list.append('task' + str(taskvariable+1) + '.' + Plot_Variable[variable_count])
    print(variabletask_list, len(Plot_Variable))
    
    return variabletask_list, task_total



def clean_groupvariables(Plot_Variable, tspan, task_total, variabletask_list):
    '''
    Groups variables pertaining to the same plot figure together   
    :param Plot_Variable:  Variables to be plotted in list format
    :param tspan: tspan of model in list of arrays
    :param task_total: total number of tasks in int format
    :param variabletask_list: variables in list format
    :return variable_statement: variables for each plot in list format 
    :return Total_Fig: total number of plots (number of sims * number of variables to plot) in int format
    '''
    Total_Fig = len(Plot_Variable) * len(tspan)
    variable_statement = ['']*Total_Fig  
    var_stepjump = len(Plot_Variable) * len(tspan)   
    fig_variable = 0                                                
    for plot_count in range(Total_Fig):
        while fig_variable < (task_total*len(Plot_Variable)): 
            if (fig_variable+var_stepjump) < (task_total*len(Plot_Variable)):
                variable_statement[plot_count] = variable_statement[plot_count] + variabletask_list[fig_variable] + ', ' 
            else:
                variable_statement[plot_count] = variable_statement[plot_count] + variabletask_list[fig_variable]
            fig_variable = fig_variable + var_stepjump
        fig_variable = plot_count + 1
      
    return variable_statement, Total_Fig
  
    
  
def gen_figurestatment(Total_Fig, variable_statement, tspan):
    '''
    Generates the 'plot figure' statements based on tasks and sims
    :param variable_statement: variables for each plot in list format 
    :param Total_Fig: total number of plots in int format
    :return Plot_statement: Plot figure statements in str format
    '''
    Figure_Statement = []
    Plot_statement="" 
    time_count = 1
    for plot_count in range(Total_Fig):#Change to meet fig count
        Figure_Statement.append('plot "Figure ' + str(plot_count+1) + '" task' + str(time_count) +'.time vs ')
        Plot_statement = Plot_statement + Figure_Statement[plot_count] + variable_statement[plot_count] + '\n'
        if (plot_count+1)%len(tspan) == 0:
            time_count +=1
    return Plot_statement

def KISAOchecker(KISAO_algorithm):
    '''
    Checks if KISAO_algorithm is under tellurium's accepted KISAO list'
    :param KISAO_algorithm:  Kinetic Simulation Algorithm Ontology number in string format
    :return: True if in tellurium list, false otherwise
    '''
    
    accepted_KISAO_list = ['kisao.0000019', 'kisao.0000433', 'kisao.0000407',
                           'kisao.0000099', 'kisao.0000035', 'kisao.0000071',
                           'kisao.0000288', 'kisao.0000280', 'kisao.0000032',
                           'kisao.0000064', 'kisao.0000435', 'kisao.0000321',
                           'kisao.0000087', 'kisao.0000086', 'kisao.0000434',
                           'kisao.0000088', 'kisao.0000241', 'kisao.0000029',
                           'kisao.0000319', 'kisao.0000274', 'kisao.0000333',
                           'kisao.0000329', 'kisao.0000323', 'kisao.0000331',
                           'kisao.0000027', 'kisao.0000082', 'kisao.0000324',
                           'kisao.0000350', 'kisao.0000330', 'kisao.0000028',
                           'kisao.0000038', 'kisao.0000039', 'kisao.0000048',
                           'kisao.0000074', 'kisao.0000081', 'kisao.0000045',
                           'kisao.0000351', 'kisao.0000084', 'kisao.0000040',
                           'kisao.0000046', 'kisao.0000003', 'kisao.0000051',
                           'kisao.0000335', 'kisao.0000336', 'kisao.0000095',
                           'kisao.0000022', 'kisao.0000076', 'kisao.0000015',
                           'kisao.0000075', 'kisao.0000278', 'kisao.0000099',
                           'kisao.0000274', 'kisao.0000282', 'kisao.0000283',
                           'kisao.0000355', 'kisao.0000356', 'kisao.0000407',
                           'kisao.0000408', 'kisao.0000409', 'kisao.0000410',
                           'kisao.0000411', 'kisao.0000412', 'kisao.0000413',
                           'kisao.0000432', 'kisao.0000437', '0']
    
    if KISAO_algorithm in accepted_KISAO_list:
        return
    else:
        raise AttributeError('KISAO Algorithm not accepted in Tellurium')
    
    


    

    
    