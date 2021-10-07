# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 11:14:39 2021

@author: Wilbert
"""
#Use Qt5Agg if plotting with tellurium
import matplotlib 
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

matplotlib.use('Qt5Agg')
matplotlib.use('Qt5Agg')
plt.close('all')

import setup_bmss                as lab
import BMSS.sbml                 as sb
import tellurium                 as te
import BMSS.models.model_handler as mh
import BMSS.models.setup_sim     as sm
import BMSS.simulation           as sim


    
if __name__ == '__main__':
    '''
    Example Model: Smallbone2015 - Michaelis Menten
    Bio-Model ID: MODEL1503180002
    A model showing Michaelis–Menten kinetics
    '''    
    Biomodels_ID                    = 'MODEL1503180002'
    toggleswitchSBMLfilename        = 'MichaelisMenten_TestModel_SBML.xml' #Name the XML file
    outputpath                      = str(Path.cwd()/toggleswitchSBMLfilename)
    onlinemodelstr                  = sb.get_online_biomodel(Biomodels_ID, outputfile=outputpath)
    config_output_path              = Path.cwd()
    Model_name                      = "MichaelisMenten_TestModel"
    antimony_str                    = te.sbmlToAntimony(onlinemodelstr)
    
    system_type                     = 'Test_Model, Michaelis_Menten'
    tspan                           = list(range(0, 20000, )) 
    inicomplete, settings_database  = sb.sbml_to_config(onlinemodelstr, system_type, config_output_path, tspan=tspan, is_path=False)

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
    onlinemodelstr                  = sb.get_online_biomodel(Biomodels_ID, outputfile=outputpath)
    config_output_path              = Path.cwd()
    Model_name                      = "mRNAmuscle_TestModel"
    antimony_str                    = te.sbmlToAntimony(onlinemodelstr)
    
    system_type                     = 'Test_Model, mRNAmuscle'
    tspan                           = list(range(0, 600))
    inicomplete, settings_database  = sb.sbml_to_config(onlinemodelstr, system_type, config_output_path, tspan=tspan, is_path=False)
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
    onlinemodelstr                  = sb.get_online_biomodel(Biomodels_ID, outputfile=outputpath)
    config_output_path              = Path.cwd()
    Model_name                      = "Catalase_TestModel"
    antimony_str                    = te.sbmlToAntimony(onlinemodelstr)
    
    system_type                     = 'Test_Model, Catalase'
    tspan                           = np.linspace(0, 1, 101)
    inicomplete, settings_database  = sb.sbml_to_config(onlinemodelstr, system_type, config_output_path, tspan=tspan, is_path=False)
    
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
    onlinemodelstr                  = sb.get_online_biomodel(Biomodels_ID, outputfile=outputpath)
    config_output_path              = Path.cwd()
    Model_name                      = "CellCycle_TestModel"
    antimony_str                    = te.sbmlToAntimony(onlinemodelstr)
    
    system_type                     = 'Test_Model, Cell_Cycle'
    tspan                           = list(range(0, 100))
    inicomplete, settings_database  = sb.sbml_to_config(onlinemodelstr, system_type, config_output_path, tspan=tspan, is_path=False)
    
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
    onlinemodelstr                  = sb.get_online_biomodel(Biomodels_ID, outputfile=outputpath)
    config_output_path              = Path.cwd()
    Model_name                      = "EPSP_TestModel"
    antimony_str                    = te.sbmlToAntimony(onlinemodelstr)
    
    system_type                     = 'Test_Model, EPSP'
    tspan                           = np.linspace(0, 20, 2001)
    inicomplete, settings_database  = sb.sbml_to_config(onlinemodelstr, system_type, config_output_path, tspan=tspan, is_path=False)
    
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
    
    


    
    
