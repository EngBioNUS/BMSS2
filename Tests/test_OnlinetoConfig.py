#!pytest test_OnlinetoConfig.py -W ignore::DeprecationWarning

from pathlib import Path

import add_BMSS_to_path
import pytest
import tellurium as te, os
import BMSS.standardfiles_generators.OnlinetoConfig as onlinegen

Model_name = "Repressilator_TestModel"
#antimony_str = te.sbmlToAntimony(samplesbmlstr)
system_type = 'Test_Model, Repressilator'
tspan = '[0, 600, 61]'
species_dict = {'PX': '0',
                'PY': '0',
                'PZ': '0',
                'X': '0',
                'Y': '20',
                'Z': '0'
                }
parameter_dict = {'beta':'0.2',
                  'alpha0':'0.2164',
                  'alpha':'216.404',
                  'eff':'20',
                  'n':'2',
                  'KM':'40',
                  'tau_mRNA':'2',
                  'tau_prot':'10',
                  't_ave':'0',
                  'kd_mRNA':'0',
                  'kd_prot':'0',
                  'k_tl':'0',
                  'a_tr' : '0',
                  'ps_a':'0.5',
                  'ps_0':'0.0005',
                  'a0_tr': '0',
                  }
parametersunits_dict ={'beta': 'per_sec',
                      'alpha0':'per_sec',
                      'alpha': 'per_sec',
                      'eff': 'per_sec',
                      'n': 'per_sec',
                      'KM': 'per_sec',
                      'tau_mRNA': 'per_sec',
                      'tau_prot': 'per_sec',
                      't_ave': 'per_sec',
                      'kd_mRNA': 'per_sec',
                      'kd_prot': 'per_sec',
                      'k_tl': 'per_sec',
                      'a_tr' : 'per_sec',
                      'ps_a': 'per_sec',
                      'ps_0': 'per_sec',
                      'a0_tr': 'per_sec',

                       }
equations = ['  beta = tau_mRNA/tau_prot',
             '  alpha0 = a0_tr*eff*tau_prot/(ln(2)*KM)',
             '  a0_tr = ps_0*60',
             '  alpha = a_tr*eff*tau_prot/(ln(2)*KM)',
             '  a_tr = (ps_a - ps_0)*60',
             '  t_ave = tau_mRNA/ln(2)',
             '  kd_mRNA = ln(2)/tau_mRNA',
             '  kd_prot = ln(2)/tau_prot',
             '  k_tl = eff/t_ave',
             '',
             '  dPX = +(k_tl*X) -(kd_prot*PX)',
             '  dPY = +(k_tl*Y) -(kd_prot*PY)',
             '  dPZ = +(k_tl*Z) -(kd_prot*PZ)',
             '  dX = +(a0_tr + a_tr*KM**n/(KM**n + PZ**n)) -(kd_mRNA*X)',
             '  dY = +(a0_tr + a_tr*KM**n/(KM**n + PX**n)) -(kd_mRNA*Y)',
             '  dZ = +(a0_tr + a_tr*KM**n/(KM**n + PY**n)) -(kd_mRNA*Z)'    
             ]
description_store = '''[descriptions]
Description =  This model describes the deterministic version of the repressilator system. The authors of this model (see reference) use three transcriptional repressor systems that are not part of any natural biological clock to build an oscillating network that they called the repressilator. The model system was induced in Escherichia coli. In this system, LacI (variable X is the mRNA, variable PX is the protein) inhibits the tetracycline-resistance transposon tetR (Y, PY describe mRNA and protein). Protein tetR inhibits the gene Cl from phage Lambda (Z, PZ: mRNA, protein),and protein Cl inhibits lacI expression. With the appropriate parameter values this system oscillates.  

'''

settings_test = {
"Species" : species_dict,
"parameters" : parameter_dict,
"units" : parametersunits_dict,
"equations" : equations,
"description": description_store 
    }

eqn_sample =['', '  dPX = +(k_tl*X) -(kd_prot*PX)', 
             '  dPY = +(k_tl*Y) -(kd_prot*PY)', 
             '  dPZ = +(k_tl*Z) -(kd_prot*PZ)',
             '  dX = +(a0_tr + a_tr*KM**n/(KM**n + PZ**n)) -(kd_mRNA*X)',
             '  dY = +(a0_tr + a_tr*KM**n/(KM**n + PX**n)) -(kd_mRNA*Y)',
             '  dZ = +(a0_tr + a_tr*KM**n/(KM**n + PY**n)) -(kd_mRNA*Z)']

Biomodels_ID = 'BIOMD0000000012' #Represillator Model


class TestConfigGen:
    def test_makesampleconfig(self):
        global settings_sample
        global sampleconfig, settings_sample
        
                
        onlinemodelstr = onlinegen.get_online_biomodel(Biomodels_ID)
        sampleconfig, settings_sample = onlinegen.sbmltoconfig(onlinemodelstr, system_type, tspan, Model_name)
        #To use for later test as well
        
        
        testconfig = onlinegen.gen_config(settings_test, system_type, tspan)
        
        assert testconfig == sampleconfig, 'Config Statements are not the same'
        
        
        return testconfig, sampleconfig
    
    
    def test_compare_equations(self):
        #Tests whether reactions pertaining to the same species are combined
        global eqn_sample
        antimony_str_test = '''
// Reactions:
  Reaction1: X => ; kd_mRNA*X;
  Reaction2: Y => ; kd_mRNA*Y;
  Reaction3: Z => ; kd_mRNA*Z;
  Reaction4:  => PX; k_tl*X;
  Reaction5:  => PY; k_tl*Y;
  Reaction6:  => PZ; k_tl*Z;
  Reaction7: PX => ; kd_prot*PX;
  Reaction8: PY => ; kd_prot*PY;
  Reaction9: PZ => ; kd_prot*PZ;
  Reaction10:  => X; a0_tr + a_tr*KM^n/(KM^n + PZ^n);
  Reaction11:  => Y; a0_tr + a_tr*KM^n/(KM^n + PX^n);
  Reaction12:  => Z; a0_tr + a_tr*KM^n/(KM^n + PY^n);

'''
        reaction_test = onlinegen.gen_reactions(antimony_str_test)
        print(reaction_test)
        eqn_clean = ['']

        
        before = len(reaction_test)
        after = 0
        while before != after:
            before = len(reaction_test)
            reaction_test = onlinegen.clean_reactions(reaction_test)
            after = len(reaction_test)

        for eqn in reaction_test:
            eqn = onlinegen.eqnreplace(eqn)
            eqn_clean.append(eqn)
            
        assert eqn_clean == eqn_sample, 'Reactions not sorted properly'
        
    
    @pytest.mark.xfail(strict=True) 
    def test_compare_equations_fail(self):
        #Typo in Reaction 10 where it generates PX instead of X
        antimony_str_fail = '''
// Reactions:
  Reaction1: X => ; kd_mRNA*X;
  Reaction2: Y => ; kd_mRNA*Y;
  Reaction3: Z => ; kd_mRNA*Z;
  Reaction4:  => PX; k_tl*X;
  Reaction5:  => PY; k_tl*Y;
  Reaction6:  => PZ; k_tl*Z;
  Reaction7: PX => ; kd_prot*PX;
  Reaction8: PY => ; kd_prot*PY;
  Reaction9: PZ => ; kd_prot*PZ;
  Reaction10:  => PX; a0_tr + a_tr*KM^n/(KM^n + PZ^n);
  Reaction11:  => Y; a0_tr + a_tr*KM^n/(KM^n + PX^n);
  Reaction12:  => Z; a0_tr + a_tr*KM^n/(KM^n + PY^n);

'''
        reaction_test = onlinegen.gen_reactions(antimony_str_fail)
        eqn_clean = ['']
        
        before = len(reaction_test)
        after = 0
        while before != after:
            before = len(reaction_test)
            reaction_test = onlinegen.clean_reactions(reaction_test)
            after = len(reaction_test)

        for eqn in reaction_test:
            eqn = onlinegen.eqnreplace(eqn)
            eqn_clean.append(eqn)
            
        assert eqn_clean == eqn_sample, 'Reactions not sorted properly'
        
        return reaction_test, eqn_clean
    

        
    @pytest.mark.xfail(strict=True) 
    def test_missingparameterunit_fail(self):
        #missing unit parameter t_ave

        parametersunits_dict_fail ={'beta': 'per_sec',
                                    'alpha0':'per_sec',
                                    'alpha': 'per_sec',
                                    'eff': 'per_sec',
                                    'n': 'per_sec',
                                    'KM': 'per_sec',
                                    'tau_mRNA': 'per_sec',
                                    'tau_prot': 'per_sec',
                                    'kd_mRNA': 'per_sec',
                                    'kd_prot': 'per_sec',
                                    'k_tl': 'per_sec',
                                    'a_tr' : 'per_sec',
                                    'ps_a': 'per_sec',
                                    'ps_0': 'per_sec',
                                    'a0_tr': 'per_sec',
                                    }
        settings_test = {
        "Species" : species_dict,
        "parameters" : parameter_dict,
        "units" : parametersunits_dict_fail,
        "equations" : equations,
        "description": description_store 
            }

        testconfig = onlinegen.gen_config(settings_test, system_type, tspan)
        
         
    
    def test_configfileoutput(self):
        #Checking output of file. 
        #File output should be defined Model_name + '.ini'
        onlinemodelstr = onlinegen.get_online_biomodel(Biomodels_ID)
        sampleconfig, settings_sample = onlinegen.sbmltoconfig(onlinemodelstr, system_type, tspan, Model_name)
        filename = Model_name + '_coremodel.ini'
        assert os.path.exists(filename) == True, "File did not output properly"

    @pytest.mark.xfail(strict=True) 
    def test_configfileoutput_fail(self):
        #Searching for a file that does not exist
        #Wrong naming
        Model_name_fail = 'Repressilator_TestModel_Fail'
        filename = Model_name_fail + '_coremodel.ini'
        assert os.path.exists(filename) == True, "File did not output properly"
            
    def test_tspanchecker(self):
        #Check if tspan has been declared correctly
        #Checker is at the start of sbmltoconfig function
        tspan = '[0, 600, 61]'
        onlinegen.tspanchecker(tspan)        
    
    @pytest.mark.xfail(strict=True) 
    def test_tspanchecker_fail_1(self):
        #Missing '[' at start of tspan
        tspan = '0, 600, 61]'
        onlinegen.tspanchecker(tspan)
        
    @pytest.mark.xfail(strict=True) 
    def test_tspanchecker_fail_2(self):
        #Missing ']' at end of tspan
        tspan = '0, 600, 61]'
        onlinegen.tspanchecker(tspan)
        
    @pytest.mark.xfail(strict=True) 
    def test_tspanchecker_fail_3(self):
        #Start time larger than end time
        tspan = '[6000, 600, 61]'
        onlinegen.tspanchecker(tspan)        
    
    def test_configpossiblechecker(self):
        #Test is SBML string can be converted with this module
        #Checker is at the start of sbmltoconfig function
        Biomodels_ID = 'BIOMD0000000012' #Represillator Model
        
        onlinemodelstr = onlinegen.get_online_biomodel(Biomodels_ID)
        onlinegen.configpossiblechecker(onlinemodelstr)
        
    @pytest.mark.xfail(strict=True) 
    def test_configpossiblechecker_fail(self):
        #SBML string is too complex for module
        Biomodels_ID = 'MODEL1606100000' #Model too complicated to convert
        
        onlinemodelstr = onlinegen.get_online_biomodel(Biomodels_ID)
        onlinegen.configpossiblechecker(onlinemodelstr)
        
        
    

if __name__ == '__main__':
    t = TestConfigGen()
    #r, s = t.test_makesampleconfig()
    #reaction_test, eqn_clean, antimony_str = t.test_compare_equations()
    
    
        