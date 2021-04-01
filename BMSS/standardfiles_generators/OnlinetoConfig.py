# -*- coding: utf-8 -*-
"""
This module contains functions to generate config file to be used within BMSS2.

Features:
-to generate SBML string from a online database
-to generate Config File from SBML string
-to generate Setting Template File from SBML string for BMSS simulation
"""

import tellurium as te, os

import tempfile
import re
import io
import zipfile
import requests
from bs4 import BeautifulSoup 
from synbiopython import genbabel
import synbiopython as syn
#from synbiopython.genbabel import utilities

#--- Get Online Model From Website ---
def get_online_biomodel(Biomodels_ID, **kwargs):
    modelstr = syn.genbabel.SEDMLOMEXgen.get_sbml_biomodel(Biomodels_ID, **kwargs)
    return modelstr

#--- Main Bodys ---
def sbmltoconfig(sbmlstr, system_type, tspan, Model_name, output_path):
    '''
    Generates the config file statment and nested dictionary.
    :param sbmlstr: SBML string in string format
    :param system_type: System Type of Model defined in String Format
    :param tspan: Tspan of Model defined in String Format
    :param Model_name: Name of Model defined in String Format, Used to name files
    :return: config file in string format and nested dictionary for settings
    
    '''
    #--Ensure Tspan declared correctly--
    tspanchecker(tspan)
    #--Ensure that sbmlstr can be converted--
    configpossiblechecker(sbmlstr)
    
    species_store, parameters_store, reactions_store, rules_store, antimony_str, description_store = gen_dictionary(sbmlstr)

    
    species_clean = clean_id(species_store)
    parameter_clean = clean_id(parameters_store)
    speciesvalue_clean = gen_cleanvalue(species_store)
    parametersvalue_clean = gen_cleanvalue(parameters_store)
    units_clean = clean_units(parameters_store)
    
    species_dict = build_settings(species_clean, speciesvalue_clean)
    parameter_dict = build_settings(parameter_clean, parametersvalue_clean)
    parametersunits_dict = build_settings(parameter_clean, units_clean)
    equations = gen_eqns(antimony_str)
    settings_combine = {
        "Species" : species_dict,
        "parameters" : parameter_dict,
        "units" : parametersunits_dict,
        "equations" : equations,
        "description": description_store}
    
    config_statement = gen_config(settings_combine, system_type, tspan)
    settings_statement = gen_settingstemplate(settings_combine, system_type, tspan, Model_name)
    Config_filepath = os.path.join(str(output_path), str(Model_name) + '_coremodel.ini')
    settings_filepath = os.path.join(str(output_path), 'sim_settings_' + str(Model_name) + '.ini')
    
    with open(Config_filepath, "w") as f:
        f.write(config_statement) 
    with open(settings_filepath, "w") as f:
        f.write(settings_statement) 

    print()
    print('The Config file path:')
    print(Config_filepath)
    print()
    print('The settings template file path:')
    print(settings_filepath)
    
    return config_statement, settings_combine

def gen_config(settings, system_type, tspan):
    '''
    Generates config statment for config file
    :param settings: Nested Dictionary for all settings
    :param system_type: System Type of Model defined in String Format
    :param tspan: Tspan of Model defined in String Format
    :return: full config statement in string format
    '''
    systemtype_section = '''[system_type]
system_type = ''' + system_type + '\n'
    
    statestop_section = '''
[states]
states = ''' 
    statestop_section = statestop_section + build_section_top(settings, 'Species')
    
    parametertop_section = '''
[parameters]
parameters = '''
    parametertop_section = parametertop_section + build_section_top(settings, 'parameters')
    
    inputs_section = '''
[inputs]
inputs = 
'''
    
    equations_section = '''
[equations]
equations =
''' 
    equations_section = build_section(equations_section, settings, 'equations')

    
    combined_top = systemtype_section + statestop_section + parametertop_section + inputs_section + equations_section + settings['description']
    
    
    species_section = 'init = \n'
    species_section = build_section(species_section, settings, 'Species')
    parameters_section = 'parameter_values = \n'
    parameters_section = build_section(parameters_section, settings, 'parameters')
    units_section = 'units = \n'
    assert len(settings['units']) == len(settings['parameters']), 'Missing Unit for Parameter'
    units_section = build_section(units_section, settings, 'units')
    priors, parameter_bounds = gen_prior_bounds(settings)
    
    
    combined_bottom = '[_]\n' + 'system_type = '+ system_type + ' \n\n' + species_section + parameters_section 
    combined_bottom = combined_bottom + priors + parameter_bounds + units_section
    combined = combined_top + combined_bottom + 'tspan = \n' + ' '*4 + tspan
    
    return combined

#--- Settings Template Creator ---

def gen_settingstemplate(settings, system_type, tspan, Model_name):
    '''
    Generates settings template for Tutorial 2 Simulation
    :param settings: Nested Dictionary for all settings
    :param system_type: System Type of Model defined in String Format
    :param tspan: Tspan of Model defined in String Format
    :param Model_name: Name of Model defined in String Format, Used to name files
    :return: full settings template in string format
    '''
    settings_template = '[' + system_type + ']\n\n'
    species_section = 'init = \n'
    species_section = build_section(species_section, settings, 'Species')
    parameters_section = 'parameter_values = \n'
    parameters_section = build_section(parameters_section, settings, 'parameters')
    units_section = 'units = \n'
    units_section = build_section(units_section, settings, 'units')
    priors, parameter_bounds = gen_prior_bounds(settings)
    settings_template = settings_template + species_section + parameters_section
    settings_template = settings_template + priors + parameter_bounds + units_section
    settings_template = settings_template + 'tspan = \n' + ' '*4 + tspan
    
    
    
    return settings_template

# --- XML Parse to readable data ---
def gen_dictionary(data):
    '''
    Passes XML data through beautifulsoup parser
    making data more easily readable
    
    :param data: SBML string in XML string format
    :returns: all required data in list format

    '''

    antimony_str = te.sbmlToAntimony(data)
 
    Bs_data = BeautifulSoup(data, "xml") 
    b_species = Bs_data.find_all('listOfSpecies')
    species_store = Convert(str(b_species))
    b_parameters = Bs_data.find_all('listOfParameters')
    parameters_store = Convert(str(b_parameters))
    b_reactions = Bs_data.find_all('listOfReactions')
    reactions_store = Convert(str(b_reactions))
    b_rules = Bs_data.find_all('listOfRules')
    rules_store = Convert(str(b_rules)) 
    #soup.find_all("a", class_="sister")
    #print(Bs_data.find_all('div', class_='dc:description'))
    if Bs_data.find_all(class_='dc:description') != []:
        b_description = Bs_data.find_all(class_='dc:description')
        description_store = Convert(str(b_description))
        description_store = gen_description(description_store)
    else:
        description_store = ''
        
    '''
    print(species_store, '\n')
    print(parameters_store, '\n')
    print(reactions_store, '\n')
    print(rules_store, '\n')
    '''
    #print(description_store)
    return species_store, parameters_store, reactions_store, rules_store, antimony_str, description_store

#--- ID,Values Clean-up---
#Finds the ID of Species/Paramters and combines with values

def clean_id(store):
    '''
    Finds the IDs within the parsed data
    :param store: stored Species/Parameters data in list format
    :return: IDs for Species/Parameters in list format
    '''
    tempstore = ''
    store_clean = []
    for value in store:
        if 'listOfSpecies' not in value and 'listOfParameters' not in value:
            #if 'name=' in value:
            if 'id=' in value:
                id_find = value.index('id="')
                tempstore = value[id_find+4:] 
                id_end = tempstore.index('"')
                store_clean.append(tempstore[:id_end])
    #print(store_clean)
    return store_clean

def clean_value(value, store_clean):
    '''
    Finds the values within parsed data
    :param value: Line from parsed data in string format
    :param store_clean: Existing Values for Species/Parameters in list format
    :return: New added values for Species/Parameters in list format
    '''
    tempstore = ''
    if 'initialAmount=' in value:
        id_find = value.index('initialAmount="')
        tempstore = value[id_find+15:] 
        #print('this is tempstore\n', tempstore)
        id_end = tempstore.index('"')
        store_clean.append(tempstore[:id_end])    
    elif 'initialConcentration=' in value:
        id_find = value.index('initialConcentration="')
        tempstore = value[id_find+22:] 
        id_end = tempstore.index('"')
        store_clean.append(tempstore[:id_end])                  
    elif 'value=' in value:
        id_find = value.index('value="')
        tempstore = value[id_find+7:] 
        id_end = tempstore.index('"')
        store_clean.append(tempstore[:id_end])

    return store_clean

def gen_cleanvalue(store):
    '''
    Fills in '0' amount for Species and Parameters
    without initial values
    :param store: List containing parsed data from Species/Parameters
    :return: Full Values for Species/Parameters in list format
    '''
    store_clean = []
    for value in store:
        #print(value)
        #if 'listOfSpecies' not in value and 'listOfParameters' not in value:
        if 'listOfParameters' in store[0] and 'id="' in value:
            len_store_clean = len(store_clean)
            store_clean = clean_value(value, store_clean)
            if len_store_clean == len(store_clean):
                store_clean.append('0')
        else:
            store_clean = clean_value(value, store_clean)
                
    #print('this is store_clean\n', store_clean)
    return store_clean

def clean_units(store):
    '''
    Finds the Units for Parameters if declared
    Feels in default units if not delcared (per_sec)
    :param store: List containing parsed data from Species/Parameters
    :return: full units in list format
    '''
    tempstore = ''
    store_clean = []
    for value in store:
        if 'listOfSpecies' not in value and 'listOfParameters' not in value:
            if 'substanceUnits' in value:
                id_find = value.index('substanceUnits="')
                tempstore = value[id_find+16:] 
                id_end = tempstore.index('"')
                store_clean.append(tempstore[:id_end])
            elif 'units' in value:
                id_find = value.index('units="')
                tempstore = value[id_find+7:]
                tempstore = tempstore.replace('_le', '_less')
                id_end = tempstore.index('"')
                store_clean.append(tempstore[:id_end])
            else:
                store_clean.append('per_sec')
                
    return store_clean  
  
def build_settings(idstore, valuestore):
    '''
    Combines the IDs with their respective values
    :param idstore: all IDs in list format
    :param valuestore: all values of IDS in list format
    :return: matched ID to values in dictionary format
    '''
    settings_dict = {}
    i=0
    for value in idstore:
        settings_dict[value] = valuestore[i]
        i += 1
    return settings_dict


#--- Equations/Reactions ---
def gen_eqns(antimony_str):
    '''
    Generates all equations from assignment rules, rate rules and reactions
    :param antimony_str: antimony string in string format
    :returns: all equations in list format
    '''
    eqn_clean = ['']
    if '// Assignment Rules:' in antimony_str:
        assignment_find = antimony_str.index('// Assignment Rules:')
        assignment_end = antimony_str.find('\n\n', assignment_find)
        tempstore_assignment = antimony_str[assignment_find+21:assignment_end]
        tempstore_assignment = eqnreplace(tempstore_assignment)
        assignment_clean = Convert(tempstore_assignment)
        
        eqn_clean = assignment_clean +['']
        
    if '// Rate Rules:' in antimony_str:
        
        rate_find = antimony_str.index('// Rate Rules:')
        rate_end = antimony_str.find('\n\n', rate_find)
        tempstore_rate = antimony_str[rate_find+15:rate_end]
        tempstore_rate = eqnreplace(tempstore_rate)
        tempstore_rate = tempstore_rate.replace("  ", '  d')
        rate_clean = Convert(tempstore_rate)
        
        eqn_clean = eqn_clean + [''] + rate_clean
        
    if '// Reactions:' in antimony_str:
        reaction_formula_store = gen_reactions(antimony_str)
        before = len(reaction_formula_store)
        after = 0
        while before != after:
            before = len(reaction_formula_store)
            reaction_formula_store = clean_reactions(reaction_formula_store)
            after = len(reaction_formula_store)
        #eqn_clean = eqn_clean + ['']
        for eqn in reaction_formula_store:
            eqn = eqnreplace(eqn)
            eqn_clean.append(eqn)

    
    return eqn_clean

def eqnreplace(tempstore):
    '''
    Removes unnecessary keys in reaction statement
    :param tempstore: equation statement in strign format
    :return: clean statement in string format
    '''
    tempstore = tempstore.replace(';', '')
    tempstore = tempstore.replace('^', '**')
    tempstore = tempstore.replace(':', '')
    tempstore = tempstore.replace("'", '')
    return tempstore

def clean_eqns(store_species):
    '''
    Converts Reaction statements in antimony string
    to format in config file. Returns a multiplier for reaction
    :param store_species: ID of species in reaction
    :returns store_species: list format if reactions have more than 1 variable in reaction
    :returns store_species: string format if reactions only have 1 variable in reaction
    :returns species_multiplier: list format if reactions have more than 1 variable in reaction
    :returns species_multiplier: string format if reactions only have 1 variable in reaction
    '''
    if store_species.count('+') > 0:
        store_species = Convertplus(store_species)
        species_multiplier = []
        multiplier_remove = ''
        for index, item in enumerate(store_species):
            store_species[index] = item.replace(" + ", '')
            store_species[index] = item.replace("$", '')
            if bool(re.search(r'\d+', store_species[index])) == True:
                species_multiplier.append(re.search(r'\d+', store_species[index]).group())
                multiplier_remove = str(re.search(r'\d+', store_species[index]).group())
            else:
                species_multiplier.append('')
            store_species[index] = item.replace(" ", '')
            store_species[index] = 'd' + store_species[index]
            store_species[index] = store_species[index].replace(str(multiplier_remove), '')

    else:
        species_multiplier = ''
        multiplier_remove = ''
        store_species = store_species.replace("+", '')
        store_species = store_species.replace('$', '')
        if bool(re.search(r'\d+', store_species)) == True:
            species_multiplier = re.search(r'\d+', store_species).group()
            multiplier_remove = str(re.search(r'\d+', store_species).group())

        store_species = store_species.replace(' ', '')
        store_species = 'd' + store_species
        store_species = store_species.replace(str(multiplier_remove), '')

    
    return store_species, species_multiplier

def get_posreaction(reaction_formula_store, value, reaction_reactant_end, reaction_product_end, reactioneqns):
    '''
    Gets the reaction equation is the reactions creates only a product
    :param reaction_formula_store: List containing all reactions
    :param value: Line of equation in reaction in string format
    :param reaction_reactant_end: Index number of the position of the start of the ID
    :param reaction_product_end: Index number of the position of the end of the ID
    :param reactioneqns: reaction equation in string format
    :returns: added "create product" reactions in list format
    '''
    tempstore_product = value[reaction_reactant_end+2:reaction_product_end]
    tempstore_product_list, species_multiplier = clean_eqns(tempstore_product)
    if isinstance(tempstore_product_list, list) == True:
        for index, item in enumerate(tempstore_product_list):
            if species_multiplier[index] != '':
                reaction_formula_store.append('  ' + item + ' = +(1/' + species_multiplier[index] + ')' + '(' + reactioneqns + ')')
            else:
                reaction_formula_store.append('  ' + item + ' = +(' + reactioneqns + ')')
    else:
            if species_multiplier != '':
                reaction_formula_store.append('  ' + tempstore_product_list + ' = +(1/' + species_multiplier + ')' + '(' + reactioneqns + ')')
            else:
                reaction_formula_store.append('  ' + tempstore_product_list + ' = +(' + reactioneqns + ')')
    
    return reaction_formula_store 

def get_negreaction(reaction_formula_store, value, reaction_reactant_start, reaction_reactant_end, reactioneqns):
    '''
    Gets the reaction equation is the reactions shows a usage of a reactant
    :param reaction_formula_store: List containing all reactions
    :param value: Line of equation in reaction in string format
    :param reaction_reactant_start: Index number of the position of the start of the ID
    :param reaction_reactant_end: Index number of the position of the end of the ID
    :param reactioneqns: reaction equation in string format
    :returns: added "use reactant" reactions in list format
    '''
    tempstore_reactant = value[reaction_reactant_start+1:reaction_reactant_end]
    tempstore_reactant_list, species_multiplier = clean_eqns(tempstore_reactant)
    if isinstance(tempstore_reactant_list, list) == True:
        for index, item in enumerate(tempstore_reactant_list):
            if species_multiplier[index] != '':
                reaction_formula_store.append('  ' + item + ' = -(1/' + species_multiplier[index] + ')' +'(' + reactioneqns + ')')
            else:
                reaction_formula_store.append('  ' + item + ' = -(' + reactioneqns + ')')
    else:
        if species_multiplier != '':
            reaction_formula_store.append('  ' + tempstore_reactant_list + ' = -(1/' + species_multiplier + ')' + '(' + reactioneqns + ')')
        else:
            reaction_formula_store.append('  ' + tempstore_reactant_list + ' = -(' + reactioneqns + ')')
    return reaction_formula_store
 
def gen_reactions(antimony_str):
    '''
    Generates the all rate rules equations from reactions from antimony string
    :param antimony_str: antimony string in string format
    :returns: all reactions in list format
    '''
    reactioneqns = ''
    reaction_formula_store = []
    reaction_find = antimony_str.index('// Reactions:')
    reaction_start = antimony_str.find('\n', reaction_find)
    reaction_end = antimony_str.find('\n\n', reaction_find)
    tempstore_reaction = antimony_str[reaction_start+1:reaction_end]
    tempstore_reaction = Convert(tempstore_reaction)
    for value in tempstore_reaction:
        reaction_reactant_start = value.find(':')
        reaction_reactant_end = value.find('=>')
        if reaction_reactant_end == -1:
            reaction_reactant_end = value.find('->')
        reaction_product_end = value.find(';')
        reaction_formula_end = value.find(';', reaction_product_end+1)
        reactioneqns = value[reaction_product_end+2:reaction_formula_end]
        #Replaces compartment name in reactions
        if '// Compartments' in antimony_str:
            compartment_name = clean_compartment(antimony_str)
            reactioneqns = reactioneqns.replace(compartment_name, '1')
  
        if value[reaction_reactant_start+1:reaction_reactant_end] != "  " and value[reaction_reactant_end+2:reaction_product_end] == " ":
            #print('only reactant present in reaction statement\n')
            reaction_formula_store = get_negreaction(reaction_formula_store, value, reaction_reactant_start, reaction_reactant_end, reactioneqns)

        if value[reaction_reactant_start+1:reaction_reactant_end] == "  " and value[reaction_reactant_end+2:reaction_product_end] != " ":
            #print('only product present in reaction statement\n')
            reaction_formula_store = get_posreaction(reaction_formula_store, value, reaction_reactant_end, reaction_product_end, reactioneqns)
           
        if value[reaction_reactant_start+1:reaction_reactant_end] != "  " and value[reaction_reactant_end+2:reaction_product_end] != " ":
            #print('reactant and product present in reaction statement\n')
            reaction_formula_store = get_negreaction(reaction_formula_store, value, reaction_reactant_start, reaction_reactant_end, reactioneqns)
            reaction_formula_store = get_posreaction(reaction_formula_store, value, reaction_reactant_end, reaction_product_end, reactioneqns)
    
    return reaction_formula_store

def clean_reactions(reaction):
    '''
    Cleans up reactions by combining equations pertaining to the same species
    :param reaction: Raw equations before cleaning in list format
    :return: cleaned reactions in list format
    '''
    
    new_equations = sorted(reaction)
    equations_final = []
    for index, item in enumerate(new_equations):
        equation_before_start = new_equations[index-1].find('d')
        equation_before_end = new_equations[index-1].find('=')
        equation_before = new_equations[index-1][equation_before_start:equation_before_end]
        equation_current_start = item.find('d')
        equation_current_end = item.find('=')
        equation_current = item[equation_current_start:equation_current_end]
        if (index+1) != len(new_equations):
            equation_after_start = new_equations[index+1].find('d')
            equation_after_end = new_equations[index+1].find('=')        
            equation_after = new_equations[index+1][equation_after_start:equation_after_end]
        else:
            equation_after = 'null'
            
        if equation_current == equation_before:
            new_equation = str(new_equations[index-1]) + str(item[equation_current_end+1:])
            equations_final.append(new_equation)
        elif equation_current != equation_before and equation_current != equation_after:
            equations_final.append(item)

    return equations_final

def clean_compartment(antimony_str):
    '''
    Finds the compartment to remove it from equations for simplicity
    :param antimony_str: antimony string in string format
    :returns: compartment name in string format
    '''
    compartment_find = antimony_str.index('// Compartments')
    compartment_start = antimony_str.find('t ', compartment_find)
    compartment_end = antimony_str.find(';', compartment_start)
    compartment_name = antimony_str[compartment_start+2:compartment_end]
    #print(compartment_name)
    return compartment_name


# --- Section Creators ---
def build_section(section, settings, key):
    '''
    Builds Section according to key
    :param section: config file statement in string format
    :param settings: settings in nested dictionary format
    :param key: variable that determines which if statement to follow, string format
    :return: updated section in string format
    '''
    indent = ' '*4
    if key == 'units':
        for species in settings[key].keys():
            section = section + indent + str(species) + ' = '  + str(settings[key].get(species))
            if species == list(settings[key])[-1]:
                section = section + '\n\n'
            else:
                section = section + ',\n'
    elif key == 'equations':
        for species in settings[key]:
            section = section + (' '*2) + str(species)
            if species == list(settings[key])[-1]:
                section = section + '\n\n'
            else:
                section = section + '\n'  
    else:
        for species in settings[key].keys():
            section = section + indent + str(species) + ' = ['  + str(settings[key].get(species)) +']'
            if species == list(settings[key])[-1]:
                section = section + '\n\n'
            else:
                section = section + ',\n'
    
    return section

def build_section_top(settings, key):
    '''
    Build section for top only of config file
    :param settings: settings in nested dictionary format
    :param key: variable that determines which if statement to follow, string format
    :return: top section in string format
    '''
    statetemp = ''
    for species in settings[key].keys():
        if species == list(settings[key])[-1]:
            statetemp = statetemp + species + '\n'
        else:
            statetemp = statetemp + species + ', '
    
    return statetemp

def gen_prior_bounds(settings):
    '''
    Generates Priors and Bounds from settings
    :param settings: settings in nested dictionary format
    :return: priors and bounds in string format
    '''
    priors = ''
    bounds = 'parameter_bounds = \n'
    
    for parameter in settings['parameters']:
        upperbound_value = float(settings['parameters'][parameter]) + 0.5
        bounds = bounds + ' '*4 + str(parameter) + ' = [0, ' 
        if parameter != list(settings['parameters'])[-1]:
            if upperbound_value > 0.5:
                upperbound = str(round((upperbound_value)))
                bounds = bounds + upperbound + '],\n'
            else:
                bounds = bounds + '1],\n'    
            #print(settings['parameters'][parameter])
        else:
            if upperbound_value > 0.5:
                upperbound = str(round((upperbound_value)))
                bounds = bounds + upperbound + ']\n\n'
            else:
                bounds = bounds + '1]\n\n'
                
    
    ''' #Example statement
priors = 
	degm  = [0.015, 0.05],
	degp  = [0.012, 0.04]

parameter_bounds = 
	k_ind = [1e-3, 1],
	synm  = [1e-6, 1e-4],
	degm  = [0.01, 0.5],
	synp  = [1e-3, 1],
	degp  = [1e-3, 0.3],
	ind   = [0, 1]   
    ''' 
    
    return priors, bounds

def gen_description(string):
    '''
    Generates Description section
    :param string: parsed description data from XML 
    :return: cleaned description in string format
    '''
    clean_string = '[descriptions]\n' + 'Description = '
    for value in string:
        value = value.replace('<p>', '')
        value = value.replace('</p>', '')
        value = value.replace('</div>', '')
        value = value.replace('[', '')
        value = value.replace(']', '')
        value = value.replace('<div class="dc:description">', '')
        clean_string = clean_string + value + ' '
    clean_string = clean_string + '\n\n'
    return clean_string 

#--- Other Functions ---
def Convert(string): 
    '''
    Converts string into list
    New row based on occurence of '\n'
    '''
    li = list(string.split("\n")) 
    return li 

def Convertplus(string): 
    '''
    Converts string into list
    New row based on occurence of '+'
    '''
    li = list(string.split("+"))
    return li

def tspanchecker(tspan):
    assert '[' in tspan, 'Include "[" at the start of tspan'
    assert ']' in tspan, 'Include "]" at the end of tspan'
    
    start_tspan = tspan.index('[') + 1
    firstcomma = tspan.index(',')
    start_time = tspan[start_tspan:firstcomma]
    secondcomma = tspan.find(',', firstcomma+1)
    end_time = tspan[firstcomma+2:secondcomma]
    
    end_tspan = tspan.index(']')
    temp_tspan = tspan[start_tspan:end_tspan]
    matched = re.match("^[0-9]+\, [0-9]+\, [0-9]+$", temp_tspan)
    matched_2 = re.match("^[0-9]+\,[0-9]+\,[0-9]+$", temp_tspan)
    is_match = bool(matched)
    is_match_2 = bool(matched_2)
    if is_match_2 == True:
        is_match = is_match_2
    if start_time>end_time:
        raise ValueError('first value declared cannot be larger than second')
    if is_match == False:
        raise NameError('Tspan was not declared in proper format(e.g. [0, 600, 61])')
    return

def configpossiblechecker(sbmlstr):
    antimony_str = te.sbmlToAntimony(sbmlstr)
    is_match = bool(re.search('function', antimony_str))
    if is_match==True:
        raise NotImplementedError('SBML string is too complex for module to convert')
    else:
        return