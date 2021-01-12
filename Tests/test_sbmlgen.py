from pathlib import Path

import add_BMSS_to_path as lab
import BMSS.standardfiles_generators.sbmlgen as sbmlgen
import BMSS.models.model_handler as mh
import BMSS.models.settings_handler as sh
import BMSS.standardfiles_generators.simplesbml as simplesbml

filename_1 = "TestModel_LogicGate_ORgate_DelayActivation_DelayActivation.ini"

system_type       = 'TestModel, LogicGate, ORgate, DelayActivation, DelayActivation'
settings_name     = 'Setting_test1'
core_model_1      = mh.from_config(filename_1)
settings          = sh.from_config(filename_1)[0]
addparam          =  settings['parameters']
number_init       = len(settings['init'])
number_parameters = len(settings['parameters'])
unit_model        = sbmlgen.unitlookup(settings)

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


sample_sbml  = samplemodel()
sample_units = {'syn_mRNA1': 'molperLmin',
                'syn_mRNA2': 'molperLmin',
                'syn_mRNA3': 'molperLmin',
                'deg_mRNA' : 'per_min',
                'syn_Pep'  : 'per_min',
                'deg_Pep'  : 'per_min',
                'Pepmax'   : 'molperL',
                'Km1'      : 'Dimension_less',
                'Km2'      : 'Dimension_less',
                'state1'   : 'Dimension_less',
                'state2'   : 'Dimension_less'
                }

class TestSBMLGen:
    def test_unitlookup_1(self):
        global settings
        
        unit_model_test = sbmlgen.unitlookup(settings)
        
        assert unit_model_test == sample_units, "Something went wrong"
        
        return unit_model_test
    
    def test_sbmlcreation_1(self):
        global core_model_1
        global settings_name
        global unit_model
        global addparam
        global j
        global k
        
        sbmlstrtest = sbmlgen.SBMLcreation(core_model_1, settings, unit_model, addparam, j, k)
        
        assert sbmlstrtest == sample_sbml, "Something went wrong"
        
        return sbmlstrtest 


if __name__ == '__main__':
    t = TestSBMLGen()
    r = t.test_unitlookup_1()
    
