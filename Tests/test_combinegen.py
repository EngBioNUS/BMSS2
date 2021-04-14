#!pytest test_combinegen.py -W ignore::DeprecationWarning

import add_BMSS_to_path
import pytest
import tempfile
import tellurium as te, os
import BMSS.standardfiles_generators.combinegen as combinegen
import BMSS.models.model_handler    as mh
import BMSS.models.settings_handler as sh

outputpath = tempfile.gettempdir()
model_name = "TestModel, Dummy, CellModel, CellularResources, ProteomeAllocation, RibosomeLimitation" #Enter model name
settings_name = "__default__" #usually "__default__" by default
Plot_Variable = ["r", "a", "p"] #, "rmq"] #Assign which variables you would like to plot
KISAO_algorithm = "kisao.0000071"
#Define which KISAO algorithm to use for tspan, write "0" if to use default CVODE

search_result_settings = sh.search_database(model_name, settings_name)
search_result_model = mh.quick_search(model_name)
core_model = search_result_model
settings = search_result_settings[0]


combinegen.database_to_combine(model_name, settings_name, Plot_Variable, outputpath, KISAO_algorithm)

class TestCombinecreator:
    
    def test_model_in_database(self):
        #Model needs to be in databases for COMBINE to be generated
        #Checker is called in beginning of database_to_combine 
        test_model_name = "TestModel, Dummy, CellModel, CellularResources, ProteomeAllocation, RibosomeLimitation"
        combinegen.database_to_combine(test_model_name, settings_name, Plot_Variable, outputpath, KISAO_algorithm)
        
    @pytest.mark.xfail(strict=True) 
    def test_model_in_database_fail(self):
        #Model not in databases for COMBINE to be generated
        #Checker is called in beginning of database_to_combine 
        test_model_name_fail = "TestModel, Dummynot, CellModel, CellularResources, ProteomeAllocation, RibosomeLimitation"
        combinegen.database_to_combine(test_model_name_fail, settings_name, Plot_Variable, outputpath, KISAO_algorithm)        
    
    def test_KISAOalgorithmchecker(self):
        #Test if KISAO algorithm declared is accepted by tellurium
        #Checker is called in beginning of database_to_combine 
        combinegen.KISAOchecker(KISAO_algorithm)
    
    @pytest.mark.xfail(strict=True)     
    def test_KISAOalgorithmchecker_fail(self):
        #Test if KISAO algorithm declared is accepted by tellurium
        #Checker is called in beginning of database_to_combine 
        KISAO_algorithm_fail = "kisao.0000000"
        combinegen.KISAOchecker(KISAO_algorithm_fail)
        
    
    def test_outputOMEX(self):
        #Test if OMEX was output correctly
        combinegen.database_to_combine(model_name, settings_name, Plot_Variable, outputpath, KISAO_algorithm)
        filename = model_name.replace(", ", "_")
        filename = 'COMBINE_' + filename + '.omex'
        filename = os.path.join(outputpath, filename)
        assert os.path.exists(filename) == True, "File did not output properly"
        
    @pytest.mark.xfail(strict=True) 
    def test_outputOMEX_fail(self):
        #OMEX file does not exist
        combinegen.database_to_combine(model_name, settings_name, Plot_Variable, outputpath, KISAO_algorithm)
        filename = model_name.replace(", ", "_")
        filename = 'COMBINE_fail_' + filename + '.omex'
        filename = os.path.join(outputpath, filename)
        assert os.path.exists(filename) == True, "File did not output properly"
        
    
    def test_plotvariablechecker(self):
        #Test if plot variable declared is in the species
        #Checker is called in beginning of database_to_combine
        Plot_Variable_Test = ["r", "a", "p"]
        combinegen.plotvariablechecker(Plot_Variable_Test, core_model)
        
    @pytest.mark.xfail(strict=True) 
    def test_plotvariablechecker_fail_1(self):
        #Test if plot variable declared is in the species
        #None of the variables exist in the model
        #Checker is called in beginning of database_to_combine
        Plot_Variable_fail_1 = ["z", "y", "x"]
        combinegen.plotvariablechecker(Plot_Variable_fail_1, core_model)
        
    @pytest.mark.xfail(strict=True) 
    def test_plotvariablechecker_fail_2(self):
        #No Plot Variable was declared
        #Checker is called in beginning of database_to_combine
        Plot_Variable_fail_2 = []
        combinegen.plotvariablechecker(Plot_Variable_fail_2, core_model)
        
    def test_Combinecreator(self):
        #Test if number of scenarios generated match
        #Number of scenarios is based on the number combinations of init values and parameter values
        combinefilename, number_scenario = combinegen.Combinecreator(core_model, settings, Plot_Variable, outputpath, KISAO_algorithm)
        number_scenarios_test = len(settings['init']) * len(settings['parameters'])
        assert number_scenario == number_scenarios_test, 'Wrong number of scenarios was outputted'
    
    def test_gen_phrasedml(self):
        #Test if phrasedml outputted normally. 
        #It should output as many models as there are scenarios 
        #It should also plot each variable on each tspan declared
        #modelname_file contains the names for all the models of the different scenarios
        phrasedml_sample = '''model1 = model "TestModel_Dummy_CellModel_CellularResources_ProteomeAllocation_RibosomeLimitation_1_1"
                            model2 = model "TestModel_Dummy_CellModel_CellularResources_ProteomeAllocation_RibosomeLimitation_1_2"
                            model3 = model "TestModel_Dummy_CellModel_CellularResources_ProteomeAllocation_RibosomeLimitation_1_3"
                            model4 = model "TestModel_Dummy_CellModel_CellularResources_ProteomeAllocation_RibosomeLimitation_2_1"
                            model5 = model "TestModel_Dummy_CellModel_CellularResources_ProteomeAllocation_RibosomeLimitation_2_2"
                            model6 = model "TestModel_Dummy_CellModel_CellularResources_ProteomeAllocation_RibosomeLimitation_2_3"
                            sim1 = simulate uniform(0.0, 100000.0, 1000)
                            sim1.algorithm = kisao.0000071
                            sim2 = simulate uniform(100000.0, 1000000.0, 1000)
                            sim2.algorithm = kisao.0000071
                            task1 = run sim1 on model1
                            task2 = run sim2 on model1
                            task3 = run sim1 on model2
                            task4 = run sim2 on model2
                            task5 = run sim1 on model3
                            task6 = run sim2 on model3
                            task7 = run sim1 on model4
                            task8 = run sim2 on model4
                            task9 = run sim1 on model5
                            task10 = run sim2 on model5
                            task11 = run sim1 on model6
                            task12 = run sim2 on model6
                            plot "Figure 1" task1.time vs task1.r, task3.r, task5.r, task7.r, task9.r, task11.r
                            plot "Figure 2" task1.time vs task1.a, task3.a, task5.a, task7.a, task9.a, task11.a
                            plot "Figure 3" task1.time vs task1.p, task3.p, task5.p, task7.p, task9.p, task11.p
                            plot "Figure 4" task2.time vs task2.r, task4.r, task6.r, task8.r, task10.r, task12.r
                            plot "Figure 5" task2.time vs task2.a, task4.a, task6.a, task8.a, task10.a, task12.a
                            plot "Figure 6" task2.time vs task2.p, task4.p, task6.p, task8.p, task10.p, task12.p
                            '''
                            
        phrasedml_sample = phrasedml_sample.replace((' '*28), '') #Remove indent
        modelname_file = ['TestModel_Dummy_CellModel_CellularResources_ProteomeAllocation_RibosomeLimitation_1_1',
                          'TestModel_Dummy_CellModel_CellularResources_ProteomeAllocation_RibosomeLimitation_1_2',
                          'TestModel_Dummy_CellModel_CellularResources_ProteomeAllocation_RibosomeLimitation_1_3',
                          'TestModel_Dummy_CellModel_CellularResources_ProteomeAllocation_RibosomeLimitation_2_1',
                          'TestModel_Dummy_CellModel_CellularResources_ProteomeAllocation_RibosomeLimitation_2_2',
                          'TestModel_Dummy_CellModel_CellularResources_ProteomeAllocation_RibosomeLimitation_2_3']
        phrased_test = combinegen.gen_phrasedml(settings, modelname_file, Plot_Variable, KISAO_algorithm)
        assert phrasedml_sample == phrased_test, 'Phrasedml statement did not output correctly'
            
if __name__ == '__main__':
    t = TestCombinecreator()
    
