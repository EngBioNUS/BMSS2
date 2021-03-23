# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 11:14:39 2021

@author: Wilbert
"""

import setup_bmss as lab
import BMSS.standardfiles_generators.OnlinetoConfig as onlinegen
import tellurium as te
import BMSS.models.model_handler    as mh
import BMSS.models.setup_sim        as sm
import BMSS.simulation       as sim

    
if __name__ == '__main__':
    
    '''
    Use following function to create SBML from BIOModel online database
    ''' 
    
    Biomodels_ID = 'BIOMD0000000012' #input biomodels ID number
    
    onlinemodelstr = onlinegen.get_online_biomodel(Biomodels_ID)
     
    
    
    
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
    

    
    
    
    


    
    