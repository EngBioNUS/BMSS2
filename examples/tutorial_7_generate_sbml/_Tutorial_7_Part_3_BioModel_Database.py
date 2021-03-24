# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 11:14:39 2021

@author: Wilbert
"""
from pathlib import Path

import setup_bmss as lab
import BMSS.standardfiles_generators.OnlinetoConfig as onlinegen
import tellurium as te
import BMSS.models.model_handler    as mh
import BMSS.models.setup_sim        as sm
import BMSS.simulation       as sim

    
if __name__ == '__main__':
    
    '''
    Use following function to create SBML from BIOModel online database
    Outputs both the sbmlstring and the XML file
    ''' 
    
    Biomodels_ID = 'BIOMD0000000012' 
    #input biomodels ID number
    #Examples:
    #Repressilator:BIOMD0000000012 (Converts without issue)
    #Network of a toggle switch: BIOMD0000000483
    #Negative Feedback By MicroRNA with Delay: MODEL1610100002 (Has boundary Species which not reflected in config)
    #Kim2011_Oscillator_ExtendedIII: MODEL1012090006 (Can convert but config file too big, crashes kernal)
    SBMLfilename = 'Repressilator_TestModel_SBML.xml' #Name the XML file
    outputpath = str(Path.cwd()/SBMLfilename)
    onlinemodelstr = onlinegen.get_online_biomodel(Biomodels_ID, outputfile=outputpath)
     
    
    
    
    '''
    Use the following function to create SBML from local folder.
    XML file must be in same folder as this Tutorial
    '''
    
    inputpath = str(Path.cwd()/'Repressilator_TestModel_SBML_1.xml')
    with open(inputpath, 'r', encoding='utf8', errors='ignore') as f:
        localmodelstr = f.read()
    
    
    
    
    
    '''
    To create config ini file from SBML file in folder
    Reading the data inside the xml file to a variable 
    data 
    '''
    
    Model_name = "Repressilator_TestModel"
    antimony_str = te.sbmlToAntimony(onlinemodelstr)
    system_type = 'Test_Model, Repressilator'
    tspan = '[0, 600, 61]' 
    #Name the Tspan to be simulated [x, y ,z] x = start time, y = end time, z = number of points inbetween

    inicomplete, settings_database = onlinegen.sbmltoconfig(onlinemodelstr, system_type, tspan, Model_name)
    #Returns the config file statement and the nested dictionary of the settings  
    #Change onlinemodelstr to localmodelstr to convert local xml file 
    
    
    
    
    
    '''
    To plot based on Tutorial 2 Simulation 
    Refer to Tutorial 2 for in detail explaination 
    of each line
    '''
    
    #Add model to database; refer to Tutorial 1 Part 2
    filename = 'Repressilator_TestModel.ini' #Enter config to be added to database
    sim_system_type = mh.config_to_database(filename)
    
    #Reading the Arguments File
    filename    = 'sim_settings_template_Repressilator_TestModel.ini'
    config_data = sm.from_config(filename)
    
    #Compiling Arguments
    models, params, config_data = sm.get_models_and_params(filename)
    
    ym, _ = sim.integrate_models(models, params)
    
    #Plot Settings
    plot_index  = {1: ['PX', 'Y'],
                   }
    titles      = {1: {'PX': 'LacI Protein', 'Y': 'tetR mRNA'},
                   }
    labels      = {1: {1: 'Scenario 1', 2: 'Scenario 2'}
                   }
    
    figs, AX = sim.plot_model(plot_index, ym, titles=titles, labels=labels)
    

    
    
    
    


    
    