# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 11:14:39 2021

@author: Wilbert
"""
from pathlib import Path

import matplotlib

import setup_bmss as lab
import BMSS.standardfiles_generators.OnlinetoConfig as onlinegen
import tellurium as te
import BMSS.models.model_handler    as mh
import BMSS.models.setup_sim        as sm
import BMSS.simulation       as sim

<<<<<<< HEAD
#Use Qt5Agg if plotting with tellurium
import matplotlib 
matplotlib.use('Qt5Agg')

=======
matplotlib.use('Qt5Agg')
>>>>>>> 202db9ee9eb0f33a51904d140104a71154cbacb7
    
if __name__ == '__main__':
    
    '''
    Use following function to create SBML from BIOModel online database
    Outputs both the sbmlstring and the XML file
    '''
    
    Biomodels_ID    = 'BIOMD0000000012' 
    #Input biomodels ID number
    SBMLfilename    = 'Repressilator_TestModel_SBML.xml' #Name the XML file
    outputpath      = str(Path.cwd()/SBMLfilename)
    onlinemodelstr  = onlinegen.get_online_biomodel(Biomodels_ID, outputfile=outputpath)
    antimony_str        = te.sbmlToAntimony(onlinemodelstr)
    
    
    '''
    Use the following function to create SBML from local folder.
    XML file must be in same folder as this Tutorial
    '''
    
    inputpath       = str(Path.cwd()/'Repressilator_TestModel_SBML_1.xml')
    with open(inputpath, 'r', encoding='utf8', errors='ignore') as f:
        localmodelstr = f.read()
    
      
    '''
    To create config ini file from SBML file in folder
    Reading the data inside the xml file to a variable 
    data 
    '''
    config_output_path  = Path.cwd()
    Model_name          = "Repressilator_TestModel"
    antimony_str        = te.sbmlToAntimony(onlinemodelstr)
    
    system_type         = 'Test_Model, Repressilator'
    tspan               = '[0, 600, 601]' 
    #Name the Tspan to be simulated [x, y ,z] x = start time, y = end time, z = number of points inbetween

    inicomplete, settings_database = onlinegen.sbmltoconfig(onlinemodelstr, system_type, tspan, Model_name, config_output_path)
    #Returns the config file statement and the nested dictionary of the settings  
    #Change onlinemodelstr to localmodelstr to convert local xml file 
    
    
    
    '''
    To plot based on Tutorial 2 Simulation 
    Refer to Tutorial 2 for in detail explaination 
    of each line
    '''
    
    #Add model to database; refer to Tutorial 1 Part 2
    filename        = 'Repressilator_TestModel_coremodel.ini' #Enter config to be added to database
    sim_system_type = mh.config_to_database(filename)
    
    #Reading the Arguments File
    filename    = 'sim_settings_Repressilator_TestModel.ini'
    config_data = sm.from_config(filename)
    
    #Compiling Arguments
    models, params, config_data = sm.get_models_and_params(filename)
    
    ym, _ = sim.integrate_models(models, params)
    
    #Plot Settings
    plot_index  = {1: ['PX', 'Y'],
                   }
    titles      = {1: {'PX': 'LacI Protein', 'Y': 'tetR mRNA'},
                   }
    labels      = {1: {1: 'Scenario 1'}
                   }
    
    figs, AX = sim.plot_model(plot_index, ym, titles=titles, labels=labels)
    
    
    
    
    
    
    
    #Other Example Models
    '''
    Example Model: Smallbone2015 - Michaelis Menten
    Bio-Model ID: MODEL1503180002
    A model showing Michaelis–Menten kinetics
    '''    
    Biomodels_ID                    = 'MODEL1503180002'
    toggleswitchSBMLfilename        = 'MichaelisMenten_TestModel_SBML.xml' #Name the XML file
    outputpath                      = str(Path.cwd()/toggleswitchSBMLfilename)
    onlinemodelstr                  = onlinegen.get_online_biomodel(Biomodels_ID, outputfile=outputpath)
    config_output_path              = Path.cwd()
    Model_name                      = "MichaelisMenten_TestModel"
    antimony_str                    = te.sbmlToAntimony(onlinemodelstr)
    
    system_type                     = 'Test_Model, Michaelis_Menten'
    tspan                           = '[0, 20000, 20001]' 
    inicomplete, settings_database  = onlinegen.sbmltoconfig(onlinemodelstr, system_type, tspan, Model_name, config_output_path)

    filename                        = 'MichaelisMenten_TestModel_coremodel.ini' #Enter config to be added to database
    sim_system_type                 = mh.config_to_database(filename)
    #Reading the Arguments File
    filename                        = 'sim_settings_MichaelisMenten_TestModel.ini'
    config_data                     = sm.from_config(filename)
    
    #Compiling Arguments
    models, params, config_data     = sm.get_models_and_params(filename)
    
    ym, _                           = sim.integrate_models(models, params)
    
    #Plot Settings
    plot_index                      = {1: ['S', 'P'],
                                       }
    titles                          = {1: {'S': 'Substrate', 'P': 'Product'},
                                       }
    labels                          = {1: {1: 'Scenario 1'}
                                       }

    figs, AX                        = sim.plot_model(plot_index, ym, titles=titles, labels=labels)
    

    '''
    Example Model: Proctor2017 - Identifying microRNA for muscle regeneration during ageing (Mir181_in_muscle)
    Bio-Model ID: MODEL1704110001
    Skeletal muscle expresses many different miRNAs with important roles in adulthood myogenesis (regeneration) 
    and myofibre hypertrophy and atrophy, processes associated with muscle ageing.
    The first model of miRNA:target interactions in myogenesis based on experimental evidence of individual miRNAs 
    which were next validated and used to make testable predictions. 
    '''    
    Biomodels_ID                    = 'MODEL1704110001'
    NegFeedbackSBMLfilename         = 'mRNAmuscle_TestModel_SBML.xml' #Name the XML file
    outputpath                      = str(Path.cwd()/NegFeedbackSBMLfilename)
    onlinemodelstr                  = onlinegen.get_online_biomodel(Biomodels_ID, outputfile=outputpath)
    config_output_path              = Path.cwd()
    Model_name                      = "mRNAmuscle_TestModel"
    antimony_str                    = te.sbmlToAntimony(onlinemodelstr)
    
    system_type                     = 'Test_Model, mRNAmuscle'
    tspan                           = '[0, 600, 61]' 
    inicomplete, settings_database  = onlinegen.sbmltoconfig(onlinemodelstr, system_type, tspan, Model_name, config_output_path)
    filename                        = 'mRNAmuscle_TestModel_coremodel.ini' #Enter config to be added to database
    sim_system_type                 = mh.config_to_database(filename)
    #Reading the Arguments File
    filename                        = 'sim_settings_mRNAmuscle_TestModel.ini'
    config_data                     = sm.from_config(filename)
    
    #Compiling Arguments
    models, params, config_data     = sm.get_models_and_params(filename)
    
    ym, _                           = sim.integrate_models(models, params)
    
    #Plot Settings
    plot_index                      = {1: ['miR181', 'miR181_HoxA11_mRNA'],
                                       }
    titles                          = {1: {'miR181': 'miR181', 'miR181_HoxA11_mRNA': 'miR181_HoxA11_mRNA'},
                                       }
    labels                          = {1: {1: 'Scenario 1'}
                                       }
    
    figs, AX                        = sim.plot_model(plot_index, ym, titles=titles, labels=labels)
    
    '''
    Example Model: Chance1952_Catalase_Mechanism
    Bio-Model ID: BIOMD0000000282
    The mechanism of catalase action. II. Electric analog computer studies.
    '''    
    Biomodels_ID                    = 'BIOMD0000000282'
    OscillatorSBMLfilename          = 'Catalase_TestModel_SBML.xml' #Name the XML file
    outputpath                      = str(Path.cwd()/OscillatorSBMLfilename)
    onlinemodelstr                  = onlinegen.get_online_biomodel(Biomodels_ID, outputfile=outputpath)
    config_output_path              = Path.cwd()
    Model_name                      = "Catalase_TestModel"
    antimony_str                    = te.sbmlToAntimony(onlinemodelstr)
    
    system_type                     = 'Test_Model, Catalase'
    tspan                           = '[0, 1, 1001]' 
    inicomplete, settings_database  = onlinegen.sbmltoconfig(onlinemodelstr, system_type, tspan, Model_name, config_output_path)
    
    filename        = 'Catalase_TestModel_coremodel.ini' #Enter config to be added to database
    sim_system_type = mh.config_to_database(filename)
    
    #Reading the Arguments File
    filename    = 'sim_settings_Catalase_TestModel.ini'
    config_data = sm.from_config(filename)
    
    #Compiling Arguments
    models, params, config_data = sm.get_models_and_params(filename)
    
    ym, _ = sim.integrate_models(models, params)
    
    #Plot Settings
    plot_index  = {1: ['x', 'p1'],
                   }
    titles      = {1: {'x': 'substrate S (hydrogen peroxide)', 'p1': 'product 1'},
                   }
    labels      = {1: {1: 'Scenario 1'}
                   }
    
    figs, AX = sim.plot_model(plot_index, ym, titles=titles, labels=labels)
    
    '''
    Example Model: Tyson1991 - Cell Cycle 2 var
    Bio-Model ID: BIOMD0000000006
    Mathematical model of the interactions of cdc2 and cyclin
    '''    
    Biomodels_ID                    = 'BIOMD0000000006'
    OscillatorSBMLfilename          = 'CellCycle_TestModel_SBML.xml' #Name the XML file
    outputpath                      = str(Path.cwd()/OscillatorSBMLfilename)
    onlinemodelstr                  = onlinegen.get_online_biomodel(Biomodels_ID, outputfile=outputpath)
    config_output_path              = Path.cwd()
    Model_name                      = "CellCycle_TestModel"
    antimony_str                    = te.sbmlToAntimony(onlinemodelstr)
    
    system_type                     = 'Test_Model, Cell_Cycle'
    tspan                           = '[0, 100, 1001]' 
    inicomplete, settings_database  = onlinegen.sbmltoconfig(onlinemodelstr, system_type, tspan, Model_name, config_output_path)
    
    filename        = 'CellCycle_TestModel_coremodel.ini' #Enter config to be added to database
    sim_system_type = mh.config_to_database(filename)
    
    #Reading the Arguments File
    filename    = 'sim_settings_CellCycle_TestModel.ini'
    config_data = sm.from_config(filename)
    
    #Compiling Arguments
    models, params, config_data = sm.get_models_and_params(filename)
    
    ym, _ = sim.integrate_models(models, params)
    
    #Plot Settings
    plot_index  = {1: ['u', 'v'],
                   }
    titles      = {1: {'u': '[M]/[CT]', 'v': '[YT]/[CT]'},
                   }
    labels      = {1: {1: 'Scenario 1'}
                   }
    
    figs, AX = sim.plot_model(plot_index, ym, titles=titles, labels=labels)

    '''
    Example Model: Edelstein1996 - EPSP ACh event
    Bio-Model ID: BIOMD0000000001
    Model of a nicotinic Excitatory Post-Synaptic Potential in a Torpedo electric organ. 
    Acetylcholine is not represented explicitely, but by an event that changes the constants
    of transition from unliganded to liganded.
    '''    
    Biomodels_ID                    = 'BIOMD0000000001'
    OscillatorSBMLfilename          = 'EPSP_TestModel_SBML.xml' #Name the XML file
    outputpath                      = str(Path.cwd()/OscillatorSBMLfilename)
    onlinemodelstr                  = onlinegen.get_online_biomodel(Biomodels_ID, outputfile=outputpath)
    config_output_path              = Path.cwd()
    Model_name                      = "EPSP_TestModel"
    antimony_str                    = te.sbmlToAntimony(onlinemodelstr)
    
    system_type                     = 'Test_Model, EPSP'
    tspan                           = '[0, 20, 2001]' 
    inicomplete, settings_database  = onlinegen.sbmltoconfig(onlinemodelstr, system_type, tspan, Model_name, config_output_path)
    
    filename        = 'EPSP_TestModel_coremodel.ini' #Enter config to be added to database
    sim_system_type = mh.config_to_database(filename)
    
    #Reading the Arguments File
    filename    = 'sim_settings_EPSP_TestModel.ini'
    config_data = sm.from_config(filename)
    
    #Compiling Arguments
    models, params, config_data = sm.get_models_and_params(filename)
    
    ym, _ = sim.integrate_models(models, params)
    
    #Plot Settings
    plot_index  = {1: ['BLL', 'IL'],
                   }
    titles      = {1: {'BLL': 'BasalACh2', 'IL': 'IntermediateACh'},
                   }
    labels      = {1: {1: 'Scenario 1'}
                   }
    
    figs, AX = sim.plot_model(plot_index, ym, titles=titles, labels=labels)
    
    #Models that cause Memory Error: MODEL1604100000, BIOMD0000000636, BIOMD0000000334, 
    #MODEL1703060000, BIOMD0000000018, MODEL1109150002, MODEL1012090006
    
    


    
    
