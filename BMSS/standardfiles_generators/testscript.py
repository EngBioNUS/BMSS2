# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 15:50:45 2021

@author: Wilbert
"""
#pip install lxml to read xml files

from pathlib import Path

import setup_bmss as lab
import BMSS.standardfiles_generators.sbmlgen as sbmlgen
import BMSS.models.model_handler as mh
import BMSS.models.settings_handler as sh
import BMSS.standardfiles_generators.simplesbml as simplesbml

f = "TestModel_LogicGate_ORgate_DelayActivation_DelayActivation.ini"
xml = 'DatabasetoSBML_TestModel_LogicGate_ORgate_DelayActivation_DelayActivation.xml'
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
unit_model = sbmlgen.unitlookup(settings)
j = 0
k = 0

def samplemodel():
    model_2 = simplesbml.SbmlModel()
    model_2.addSpecies('Inde1', 0)
    model_2.addSpecies('Indi1', 0)
    model_2.addSpecies('Inde2', 0)
    model_2.addSpecies('Indi2', 0)
    model_2.addSpecies('mRNA1', 0)
    model_2.addSpecies('Pep1', 0)
    model_2.addSpecies('mRNA2', 0)
    model_2.addSpecies('Pep2', 0)
    model_2.addSpecies('mRNA3', 0)
    model_2.addSpecies('Pep3', 0)
    model_2.addParameter('syn_mRNA1', 2.53e-6, units = 'molperLmin')
    model_2.addParameter('syn_mRNA2', 2.53e-6, units = 'molperLmin')
    model_2.addParameter('syn_mRNA3', 2.53e-6, units = 'molperLmin')
    model_2.addParameter('deg_mRNA', 0.1386, units = 'per_min')
    model_2.addParameter('syn_Pep', 0.01, units = 'per_min')
    model_2.addParameter('deg_Pep', 0.0105, units = 'per_min')
    model_2.addParameter('Pepmax', 2.53e-6, units = 'molperL')
    model_2.addParameter('Km1', 35, units = 'Dimension_less')
    model_2.addParameter('Km2', 35, units = 'Dimension_less')
    model_2.addParameter('state1', 0, units = 'Dimension_less')
    model_2.addParameter('state2', 0, units = 'Dimension_less')
    model_2.addRateRule('Inde1', '-(Inde1/(Inde1+Km1))*Inde1')
    model_2.addRateRule('Indi1', '(Inde1/(Inde1+Km1))*Inde1')
    model_2.addRateRule('Inde2', '-(Inde2/(Inde2+Km2))*Inde2')
    model_2.addRateRule('Indi2', '(Inde2/(Inde2+Km2))*Inde2')
    model_2.addRateRule('mRNA1', 'syn_mRNA1*(Indi1)*(state1) - (deg_mRNA *mRNA1)')
    model_2.addRateRule('Pep1', '(syn_Pep*mRNA1) - (deg_Pep*Pep1)')
    model_2.addRateRule('mRNA2', 'syn_mRNA2*(Indi2)*(state2) - (deg_mRNA *mRNA2)')
    model_2.addRateRule('Pep2', '(syn_Pep*mRNA2) - (deg_Pep*Pep2)')
    model_2.addRateRule('mRNA3', '(syn_mRNA3*((Pep1+Pep2)/Pepmax))-(deg_mRNA *mRNA3)')
    model_2.addRateRule('Pep3', '(syn_Pep*mRNA3)-(deg_Pep*Pep3)')
    sbml_str = model_2.toSBML()
    return sbml_str

def sampleunits():
    unitmodel = {
    'syn_mRNA1': 'molperLmin',
    'syn_mRNA2': 'molperLmin',
    'syn_mRNA3': 'molperLmin',
    'deg_mRNA': 'per_min',
    'syn_Pep': 'per_min',
    'deg_Pep': 'per_min',
    'Pepmax': 'molperL',
    'Km1': 'Dimension_less',
    'Km2': 'Dimension_less',
    'state1': 'Dimension_less',
    'state2': 'Dimension_less'
    }
    return unitmodel

sample_sbml = samplemodel()
sample_units = sampleunits()



'''Test for unitlookup'''
 
unit_model_test = sbmlgen.unitlookup(settings)

assert unit_model_test == sample_units, "Something went wrong"
del unit_model_test



'''Test for SBMLcreation'''

sbmlstrtest = sbmlgen.SBMLcreation(core_model, settings, unit_model, addparam, j, k)

assert sbmlstrtest == sample_sbml, "Something went wrong"
del sbmlstrtest



'''Test for config_to_sbml'''

files = ['TestModel_LogicGate_ORgate_DelayActivation_DelayActivation.ini']
sbmlgen.config_to_sbml(files)

with open(xml, 'r') as f: 
    sbmlstrtest = f.read()  

assert sbmlstrtest == sample_sbml, "Something went wrong"
del sbmlstrtest



'''Test for autogenerate_sbml_from_folder'''
inputpath = (Path.cwd())
sbmlgen.autogenerate_sbml_from_folder(inputpath)

with open(xml, 'r') as f: 
    sbmlstrtest = f.read() 

assert sbmlstrtest == sample_sbml, "Something went wrong"
del sbmlstrtest



'''Test for database_to_sbml'''

model_name = "TestModel, LogicGate, ORgate, DelayActivation, DelayActivation" #Enter model name
settings_name = "Setting_test1" #usually "__default__" by default
sbmlgen.database_to_sbml(model_name, settings_name)

with open('DatabasetoSBML_1.xml', 'r') as f: 
    sbmlstrtest = f.read()  

assert sbmlstrtest == sample_sbml, "Something went wrong"
del sbmlstrtest





