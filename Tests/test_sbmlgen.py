from pathlib import Path
import os
import glob

import add_BMSS_to_path as lab
import BMSS.standardfiles_generators.sbmlgen as sbmlgen
import BMSS.models.model_handler as mh
import BMSS.models.settings_handler as sh
import tempfile
import BMSS.standardfiles_generators.simplesbml as simplesbml
import pytest


system_type       = 'TestModel, BMSS, LogicGate, gate, DelayActivationInput2'
settings_name     = '__default__'
core_model_1 = mh.quick_search(system_type)
settings = sh.quick_search(system_type=system_type, settings_name=settings_name)
addparam          = settings['parameters']
number_init       = len(settings['init'])
number_parameters = len(settings['parameters'])
unit_model        = sbmlgen.unitlookup(settings)
init_scenario     = 0
param_scenario    = 0
output_path = tempfile.gettempdir()

model_2 = simplesbml.SbmlModel()
model_2.addSpecies('Inde', 0)
model_2.addSpecies('Indi', 0)
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
model_2.addParameter('Km', 35, units = 'Dimension_less')
model_2.addParameter('state1', 0, units = 'Dimension_less')
model_2.addParameter('state2', 0, units = 'Dimension_less')
model_2.addRateRule('Inde', '-(Inde/(Inde+Km))*Inde')
model_2.addRateRule('Indi', '(Inde/(Inde+Km))*Inde')
model_2.addRateRule('mRNA1', 'syn_mRNA1*(state1) - (deg_mRNA *mRNA1)')
model_2.addRateRule('Pep1', '(syn_Pep*mRNA1) - (deg_Pep*Pep1)')
model_2.addRateRule('mRNA2', 'syn_mRNA2*Indi*(state2) - (deg_mRNA *mRNA2)')
model_2.addRateRule('Pep2', '(syn_Pep*mRNA2) - (deg_Pep*Pep2)')
model_2.addRateRule('mRNA3', '(syn_mRNA3*((Pep1+Pep2)/Pepmax))-(deg_mRNA *mRNA3)')
model_2.addRateRule('Pep3', '(syn_Pep*mRNA3)-(deg_Pep*Pep3)')
sample_sbml = model_2.toSBML()

sample_units = {'syn_mRNA1': 'molperLmin',
                'syn_mRNA2': 'molperLmin',
                'syn_mRNA3': 'molperLmin',
                'deg_mRNA' : 'per_min',
                'syn_Pep'  : 'per_min',
                'deg_Pep'  : 'per_min',
                'Pepmax'   : 'molperL',
                'Km'      : 'Dimension_less',
                'state1'   : 'Dimension_less',
                'state2'   : 'Dimension_less'
                }

class TestSBMLGen:
    def test_unitlookup(self):
               
        unit_model_test = sbmlgen.unitlookup(settings)
        
        assert unit_model_test == sample_units, "Sample and Generated Units do not match"
        
        return unit_model_test
    
    @pytest.mark.xfail(strict=True) 
    def test_unitlookup_fail(self):
        #Unit not declared for parameter state 1
        #Check is done at beginning of unitlookup function 
        unit_model_test = sbmlgen.unitlookup(settings)
        fail_units = {'syn_mRNA1': 'molperLmin',
                'syn_mRNA2': 'molperLmin',
                'syn_mRNA3': 'molperLmin',
                'deg_mRNA' : 'per_min',
                'syn_Pep'  : 'per_min',
                'deg_Pep'  : 'per_min',
                'Pepmax'   : 'molperL',
                'Km'      : 'Dimension_less',
                'state2'   : 'Dimension_less'
                }
        
        assert len(fail_units) == len(unit_model_test), "Not all Parameters have Units Declared"
        
        return 
        
    def test_sbmlcreation_1(self):
        
        sbmlstrtest = sbmlgen.SBMLcreation(core_model_1, settings, unit_model, addparam, init_scenario, param_scenario)
        assert sbmlstrtest == sample_sbml, "Sample and Generated Units do not match"
<<<<<<< Updated upstream
        
    

    @pytest.mark.xfail(strict=True) 
    def test_sbmlcreation_fail_1(self):
        #Core Model System Type does not match with settings system type
        #Check is done at beginning of SBMLcreation function 
        
        wrong_model = {'system_type' : ['TestModel', 'Dummy'],
                      'states'      : ['mRNA'], 
                      'parameters'  : ['syn_mRNA', 'deg_mRNA', 'syn_Pep', 'deg_Pep', 'Ki'],
                      'inputs'      : ['Ind'],
                      'equations'   : ['dmRNA = syn_mRNA*Ind/(Ind + Ki) - deg_mRNA*mRNA',
                                      'dPep  = syn_Pep*mRNA - deg_Pep'
                                      ],
                      'ia'          : 'ia_result_bmss01001.csv'
                  }
        
        sbmlstrtest = sbmlgen.SBMLcreation(wrong_model, settings, unit_model, addparam, init_scenario, param_scenario)
        
         
    @pytest.mark.xfail(strict=True) 
    def test_sbmlcreation_fail_2(self):
        #Missing Parameter in core model(syn_mRNA1)
        #Check is done at beginning of SBMLcreation function

        wrong_model = {'system_type' : 'TestModel, LogicGate, ORgate, DelayActivation, DelayActivation',
                      'states'      : ['Inde1', 'Indi1', 'Inde2', 'Indi2', 'mRNA1', 'Pep1',
                                       'mRNA2', 'Pep2', 'mRNA3', 'Pep3'], 
                      'parameters'  : ['syn_mRNA2', 'syn_mRNA3', 'deg_mRNA', 'syn_Pep',
                                       'deg_Pep', 'Pepmax', 'Km1', 'Km2', 'state1', 'state2'],
                      'equations'   : ['dInde1 = -(Inde1/(Inde1+Km1))*Inde1',
                                       'dIndi1 = (Inde1/(Inde1+Km1))*Inde1',
                                       'dInde2 = -(Inde2/(Inde2+Km2))*Inde2',
                                       'dIndi2 = (Inde2/(Inde2+Km2))*Inde2',
                                       'dmRNA1 = syn_mRNA1*(Indi1)*(state1) - (deg_mRNA *mRNA1)',
                                       'dPep1 = (syn_Pep*mRNA1) - (deg_Pep*Pep1)',
                                       'dmRNA2 = syn_mRNA2*(Indi2)*(state2) - (deg_mRNA *mRNA2)',
                                       'dPep2 = (syn_Pep*mRNA2) - (deg_Pep*Pep2)',
                                       'dmRNA3 = (syn_mRNA3*((Pep1+Pep2)/Pepmax))-(deg_mRNA *mRNA3)',
                                       'dPep3 = (syn_Pep*mRNA3)-(deg_Pep*Pep3)'],
                      }
        
        sbmlstrtest = sbmlgen.SBMLcreation(wrong_model, settings, unit_model, addparam, init_scenario, param_scenario)
        
    def test_config_to_sbml(self):
        #Test if files are output correctly
        filelist = ['TestModel_LogicGate_ORgate_DelayActivation_DelayActivation.ini',
                    'TestModel_CellModel_CellularResources_ProteomeAllocation_RibosomeLimitation.ini']

        sbmlgen.config_to_sbml(filelist, output_path)
        
        for file in filelist:
            core_model_test = mh.from_config(file)
            system_type = core_model_test['system_type']
            settings_name = 'Setting_test1'
            mh.delete(system_type)
            sh.delete(system_type=system_type, settings_name=settings_name)
            
        for outputfile in filelist:
            placeholder = outputfile.replace('.ini', '')
            filename = os.path.join(output_path, 'DatabasetoSBML_' + placeholder +'.xml')
            assert os.path.exists(filename) == True, "File did not output properly"
            
    @pytest.mark.xfail(strict=True)        
    def test_config_to_sbml_fail(self):
        #Test if files declared exists
        #Both files do not exist
        filelist = ['TestModel_fail_1.ini',
                    'TestModel_fail_2.ini']
        inputpath = Path.cwd()
        for file in filelist:
            filepath = os.path.join(inputpath, file)
            assert os.path.exists(filepath) == True, "Input file(s) does not exist" 
    
    def test_autogenerate_sbml_from_folder(self):
        #Test if the function is correctly taking in Config files from folder 
        #and outputting to Tempdir
        inputpath = (Path.cwd()/'ConfigSBML')
        output_path_auto = os.path.join(output_path, 'ConfigSBML')
        try:
            os.mkdir(output_path_auto)
        except OSError:
            print()
        else:
            print()
            
        files = [f for f in glob.glob(os.path.join(inputpath,"**/*.ini"), recursive=True)]

        sbmlgen.autogenerate_sbml_from_folder(inputpath, output_path_auto)
        
        for file in files:
            core_model_test = mh.from_config(file)
            system_type = core_model_test['system_type']
            settings_name = 'Setting_test1'
            mh.delete(system_type)
            sh.delete(system_type=system_type, settings_name=settings_name)
        
        for outputfile in files:
            placeholder = outputfile.replace(str(inputpath), '')
            placeholder = placeholder.replace('.ini', '')
            placeholder = placeholder.replace('\\', '')
            filename = os.path.join(output_path_auto, 'DatabasetoSBML_' + placeholder +'.xml')
            print('This is the file name:', filename)
            print()
            assert os.path.exists(filename) == True, "File did not output properly" 
        
    @pytest.mark.xfail(strict=True)     
    def test_autogenerate_sbml_from_folder_fail(self):
        #Test if input path exists
        #Input path does not exist
        inputpath = (Path.cwd()/'ConfigSBML_fail')
        output_path_auto = os.path.join(output_path, 'ConfigSBML')
        sbmlgen.autogenerate_sbml_from_folder(inputpath, output_path_auto)
=======
        
    

    @pytest.mark.xfail(strict=True) 
    def test_sbmlcreation_fail_1(self):
        #Core Model System Type does not match with settings system type
        #Check is done at beginning of SBMLcreation function 
        
        wrong_model = {'system_type' : ['TestModel', 'Dummy'],
                      'states'      : ['mRNA'], 
                      'parameters'  : ['syn_mRNA', 'deg_mRNA', 'syn_Pep', 'deg_Pep', 'Ki'],
                      'inputs'      : ['Ind'],
                      'equations'   : ['dmRNA = syn_mRNA*Ind/(Ind + Ki) - deg_mRNA*mRNA',
                                      'dPep  = syn_Pep*mRNA - deg_Pep'
                                      ],
                      'ia'          : 'ia_result_bmss01001.csv'
                  }
        
        sbmlstrtest = sbmlgen.SBMLcreation(wrong_model, settings, unit_model, addparam, init_scenario, param_scenario)
        
         
    @pytest.mark.xfail(strict=True) 
    def test_sbmlcreation_fail_2(self):
        #Missing Parameter in core model(syn_mRNA1)
        #Check is done at beginning of SBMLcreation function

        wrong_model = {'system_type' : 'TestModel, LogicGate, ORgate, DelayActivation, DelayActivation',
                      'states'      : ['Inde1', 'Indi1', 'Inde2', 'Indi2', 'mRNA1', 'Pep1',
                                       'mRNA2', 'Pep2', 'mRNA3', 'Pep3'], 
                      'parameters'  : ['syn_mRNA2', 'syn_mRNA3', 'deg_mRNA', 'syn_Pep',
                                       'deg_Pep', 'Pepmax', 'Km1', 'Km2', 'state1', 'state2'],
                      'equations'   : ['dInde1 = -(Inde1/(Inde1+Km1))*Inde1',
                                       'dIndi1 = (Inde1/(Inde1+Km1))*Inde1',
                                       'dInde2 = -(Inde2/(Inde2+Km2))*Inde2',
                                       'dIndi2 = (Inde2/(Inde2+Km2))*Inde2',
                                       'dmRNA1 = syn_mRNA1*(Indi1)*(state1) - (deg_mRNA *mRNA1)',
                                       'dPep1 = (syn_Pep*mRNA1) - (deg_Pep*Pep1)',
                                       'dmRNA2 = syn_mRNA2*(Indi2)*(state2) - (deg_mRNA *mRNA2)',
                                       'dPep2 = (syn_Pep*mRNA2) - (deg_Pep*Pep2)',
                                       'dmRNA3 = (syn_mRNA3*((Pep1+Pep2)/Pepmax))-(deg_mRNA *mRNA3)',
                                       'dPep3 = (syn_Pep*mRNA3)-(deg_Pep*Pep3)'],
                      }
        
        sbmlstrtest = sbmlgen.SBMLcreation(wrong_model, settings, unit_model, addparam, init_scenario, param_scenario)
        
    def test_config_to_sbml(self):
        #Test if files are output correctly
        filelist = ['TestModel_LogicGate_ORgate_DelayActivation_DelayActivation.ini',
                    'TestModel_CellModel_CellularResources_ProteomeAllocation_RibosomeLimitation.ini']
>>>>>>> Stashed changes

        sbmlgen.config_to_sbml(filelist, output_path)
        
        for file in filelist:
            core_model_test = mh.from_config(file)
            system_type = core_model_test['system_type']
            settings_name = 'Setting_test1'
            mh.delete(system_type)
            sh.delete(system_type=system_type, settings_name=settings_name)
            assert system_type not in (mh.list_models()), 'Model was not deleted'
            assert system_type not in (sh.list_settings()), 'settings was not deleted'
            
        for outputfile in filelist:
            placeholder = outputfile.replace('.ini', '')
            filename = os.path.join(output_path, 'DatabasetoSBML_' + placeholder +'.xml')
            assert os.path.exists(filename) == True, "File did not output properly"
            
    @pytest.mark.xfail(strict=True)        
    def test_config_to_sbml_fail(self):
        #Test if files declared exists
        #Both files do not exist
        filelist = ['TestModel_fail_1.ini',
                    'TestModel_fail_2.ini']
        inputpath = Path.cwd()
        for file in filelist:
            filepath = os.path.join(inputpath, file)
            assert os.path.exists(filepath) == True, "Input file(s) does not exist" 
    
    def test_autogenerate_sbml_from_folder(self):
        #Test if the function is correctly taking in Config files from folder 
        #and outputting to Tempdir
        inputpath = (Path.cwd()/'ConfigSBML')
        output_path_auto = os.path.join(output_path, 'ConfigSBML')
            
        files = [f for f in glob.glob(os.path.join(inputpath,"**/*.ini"), recursive=True)]

<<<<<<< Updated upstream
=======
        sbmlgen.autogenerate_sbml_from_folder(inputpath, output_path_auto)
        
        for file in files:
            core_model_test = mh.from_config(file)
            system_type = core_model_test['system_type']
            settings_name = 'Setting_test1'
            mh.delete(system_type)
            sh.delete(system_type=system_type, settings_name=settings_name)
            assert system_type not in (mh.list_models()), 'Model was not deleted'
            assert system_type not in (sh.list_settings()), 'settings was not deleted'
            
        for outputfile in files:
            placeholder = outputfile.replace(str(inputpath), '')
            placeholder = placeholder.replace('.ini', '')
            placeholder = placeholder.replace('\\', '')
            filename = os.path.join(output_path_auto, 'DatabasetoSBML_' + placeholder +'.xml')
            print('This is the file name:', filename)
            print()
            assert os.path.exists(filename) == True, "File did not output properly" 
        
    @pytest.mark.xfail(strict=True)     
    def test_autogenerate_sbml_from_folder_fail(self):
        #Test if input path exists
        #Input path does not exist
        inputpath = (Path.cwd()/'ConfigSBML_fail')
        output_path_auto = os.path.join(output_path, 'ConfigSBML')
        sbmlgen.autogenerate_sbml_from_folder(inputpath, output_path_auto)


>>>>>>> Stashed changes
    def test_database_to_sbml(self):
        #Test if the function is correctly taking model from database
        #Should output to Tempdir
        sbmlgen.database_to_sbml(system_type, settings_name, output_path)
        filename = os.path.join(output_path, 'DatabasetoSBML_1' + '.xml')
        assert os.path.exists(filename) == True, "File did not output properly" 
        
    @pytest.mark.xfail(strict=True)     
    def test_database_to_sbml_fail(self):
        #Test if model declared is in database
        system_type_fail = "TestModel_fail"
        assert system_type_fail in mh.list_models(), 'Model not in database'
        sbmlgen.database_to_sbml(system_type, settings_name, output_path)
        
if __name__ == '__main__':
    t = TestSBMLGen()
<<<<<<< Updated upstream
=======
    t.test_config_to_sbml()
>>>>>>> Stashed changes
    
    
