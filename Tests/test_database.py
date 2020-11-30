import add_BMSS_to_path
import pytest

import numpy  as np
import pandas as pd

'''
Due to the dependency of settings_handler on model_handler, these two are tested
together
'''

import BMSS.models.model_handler    as mh
import BMSS.models.settings_handler as sh

core_model_1 = None
settings_1   = None 

core_model_2 = None
settings_2   = None


#add test for model code

class TestModelHandler:
    
    def test_make_core_model(self):
        global core_model_1
        __model__ = {'system_type' : ['TestModel', 'Dummy'],
                     'states'      : ['mRNA', 'Pep'], 
                     'parameters'  : ['syn_mRNA', 'deg_mRNA', 'syn_Pep', 'deg_Pep', 'Ki'],
                     'inputs'      : ['Ind'],
                     'equations'   : ['dmRNA = syn_mRNA*Ind/(Ind + Ki) - deg_mRNA*mRNA',
                                      'dPep  = syn_Pep*mRNA - deg_Pep'
                                      ],
                      'ia'          : 'ia_result_bmss01001.csv'
                  }
        core_model = mh.make_core_model(**__model__)
        
        #Assert here
        for key in __model__:
            assert core_model[key] is not None
        
        #Save for reuse
        core_model_1 = core_model
        
    @pytest.mark.xfail
    def test_make_core_model_fail_1(self):
        
        #Division by zero
        __model__ = {'system_type' : ['TestModel', 'Dummy'],
                      'states'      : ['mRNA', 'Pep'], 
                      'parameters'  : ['syn_mRNA', 'deg_mRNA', 'syn_Pep', 'deg_Pep', 'Ki'],
                      'inputs'      : ['Ind'],
                      'equations'   : ['dmRNA = syn_mRNA*Ind/(Ind + Ki) - deg_mRNA*mRNA',
                                      'dPep  = syn_Pep*mRNA - deg_Pep/0'
                                      ],
                      'ia'          : 'ia_result_bmss01001.csv'
                  }
        core_model = mh.make_core_model(**__model__)
    
    @pytest.mark.xfail
    def test_make_core_model_fail_2(self):
        #Missing state
        __model__ = {'system_type' : ['TestModel', 'Dummy'],
                      'states'      : ['mRNA'], 
                      'parameters'  : ['syn_mRNA', 'deg_mRNA', 'syn_Pep', 'deg_Pep', 'Ki'],
                      'inputs'      : ['Ind'],
                      'equations'   : ['dmRNA = syn_mRNA*Ind/(Ind + Ki) - deg_mRNA*mRNA',
                                      'dPep  = syn_Pep*mRNA - deg_Pep'
                                      ],
                      'ia'          : 'ia_result_bmss01001.csv'
                  }
        core_model = mh.make_core_model(**__model__)
    
    @pytest.mark.xfail
    def test_make_core_model_fail_3(self):
        #Missing parameter
        __model__ = {'system_type' : ['TestModel', 'Dummy'],
                     'states'      : ['mRNA', 'Pep'], 
                     'parameters'  : ['deg_mRNA', 'syn_Pep', 'deg_Pep', 'Ki'],
                     'inputs'      : ['Ind'],
                     'equations'   : ['dmRNA = syn_mRNA*Ind/(Ind + Ki) - deg_mRNA*mRNA',
                                      'dPep  = syn_Pep*mRNA - deg_Pep'
                                      ],
                      'ia'          : 'ia_result_bmss01001.csv'
                  }
        core_model = mh.make_core_model(**__model__)
    
    @pytest.mark.xfail
    def test_make_core_model_fail_4(self):
        #Unused variable
        __model__ = {'system_type' : ['TestModel', 'Dummy'],
                     'states'      : ['mRNA', 'Pep', 'UnsedDummy'], 
                     'parameters'  : ['syn_mRNA', 'deg_mRNA', 'syn_Pep', 'deg_Pep', 'Ki'],
                     'inputs'      : ['Ind'],
                     'equations'   : ['dmRNA = syn_mRNA*Ind/(Ind + Ki) - deg_mRNA*mRNA',
                                      'dPep  = syn_Pep*mRNA - deg_Pep/0'
                                     ],
                     'ia'          : 'ia_result_bmss01001.csv'
                  }
        core_model = mh.make_core_model(**__model__)
    
    def test_copy_core_model(self):
        global core_model_1
        
        copy = core_model_1.copy()
        
        for key in copy:
            assert copy[key] == core_model_1[key]
        
    def test_add_to_database(self):
        '''
        Note: add_to_database already makes calls to search/quick_search
        '''
        global core_model_1
        
        core_model = core_model_1
        
        mh.add_to_database(core_model,  dialog=False)
        
        #Check if in database
        lst = mh.list_models()
        assert core_model['system_type'] in lst
        
    def test_delete(self):
        global core_model_1
        
        system_type = core_model_1['system_type']
        mh.delete(system_type)
        
        #Check if in database
        lst = mh.list_models()
        assert system_type not in lst
    
    def test_restore(self):
        global core_model_1
        
        system_type = core_model_1['system_type']
        mh.restore(system_type)
        
        #Check if in database
        lst = mh.list_models()
        assert system_type in lst
    
    def test_from_config(self):
        global core_model_2
        
        core_model_2 = mh.from_config('testmodel.ini')
        
class TestSettingsHandler:
    
    def test_make_settings(self):
        global settings_1
        global core_model_1
        
        core_model = core_model_1
        
        mh.add_to_database(core_model, dialog=False)

        __settings__ = {'system_type'      : ['TestModel', 'Dummy'],
                        'settings_name'    : '__default__',
                        'units'            : {'syn_mRNA' : 'M/min', 
                                              'deg_mRNA' : '1/min',
                                              'syn_Pep'  : '1/min',
                                              'deg_Pep'  : '1/min',
                                              'Ki'       : 'M',
                                              'Ind'      : 'M'
                                              },
                        'parameters'       : {'syn_mRNA' : np.array([0.02]), 
                                              'deg_mRNA' : np.array([0.15]),
                                              'syn_Pep'  : np.array([0.02]),
                                              'deg_Pep'  : np.array([0.012]),
                                              'Ki'       : np.array([0.5]),
                                              'Ind'      : np.array([1.0]) 
                                              },
                        'init'             : {1: [0, 0]},
                        'parameter_bounds' : {'deg_mRNA' : [0.001, 0.03], 
                                              'deg_Pep'  : [0.01, 0.5], 
                                              },
                        'solver_args'      : {'rtol'   : 1.49012e-8,
                                              'atol'   : 1.49012e-8,
                                              'tcrit'  : [],
                                              'h0'     : 0.0,
                                              'hmax'   : 0.0,
                                              'hmin'   : 0.0,
                                              'mxstep' : 0
                                              },
                    }
        
        settings = sh.make_settings(**__settings__)
        
        ###############################################################################
        #Testing Parameter Formats
        ###############################################################################
        __settings__['parameters'] = {key+'_1' : __settings__['parameters'][key] for key in __settings__['parameters']}
        settings = sh.make_settings(**__settings__, user_core_model=core_model)
        
        __settings__['parameters'] = pd.Series(__settings__['parameters'], name=500)
        settings = sh.make_settings(**__settings__, user_core_model=core_model)
        
        ##############################################################################
        #Testing Initial Value Formats
        ##############################################################################
        __settings__['init'] = {'mRNA' : [0],
                                'Pep'  : [0],
                                }
        settings = sh.make_settings(**__settings__, init_orient='states', user_core_model=core_model)
        
        __settings__['init'] = [[0, 0], [0, 0]]
        settings = sh.make_settings(**__settings__, init_orient='states', user_core_model=core_model)
        
        __settings__['init'] = pd.Series([0, 0], index=['mRNA', 'Pep'])
        settings = sh.make_settings(**__settings__, init_orient='states', user_core_model=core_model)
        
        __settings__['init'] = pd.DataFrame([[0, 0]], columns=['mRNA', 'Pep'], index=[1])
        settings = sh.make_settings(**__settings__, init_orient='states', user_core_model=core_model)
    
        
        #Assert here
        for key in __settings__:
            try:
                assert settings[key] is not None
            except ValueError as e:
                pass
            except Exception as e:
                raise e
        
        #Save for reuse
        settings_1 = settings
        
    @pytest.mark.xfail
    def test_make_settings_fail_1(self):
        #Init of wrong length
        __settings__ = {'system_type'      : ['TestModel, Dummy'],
                        'settings_name'    : '__default__',
                        'units'            : {'syn_mRNA' : 'M/min', 
                                              'deg_mRNA' : '1/min',
                                              'syn_Pep'  : '1/min',
                                              'deg_Pep'  : '1/min',
                                              'Ind'     : 'M'
                                              },
                        'parameters'       : {'syn_mRNA' : np.array([0.02]), 
                                              'deg_mRNA' : np.array([0.15]),
                                              'syn_Pep'  : np.array([0.02]),
                                              'deg_Pep'  : np.array([0.012]) ,
                                              'Ind'     : np.array([1.0]) 
                                              },
                        'init'             : {1: [0, 0, 0]},
                        'parameter_bounds' : {'deg_mRNA' : [0.001, 0.03], 
                                              'deg_Pep'  : [0.01, 0.5], 
                                              },
                        'solver_args'      : {'rtol'   : 1.49012e-8,
                                              'atol'   : 1.49012e-8,
                                              'tcrit'  : [],
                                              'h0'     : 0.0,
                                              'hmax'   : 0.0,
                                              'hmin'   : 0.0,
                                              'mxstep' : 0
                                              },
                    }
        settings = sh.make_settings(**__settings__)
    
    @pytest.mark.xfail
    def test_make_settings_fail_2(self):
        #Invalid parameter bounds
        __settings__ = {'system_type'      : ['TestModel, Dummy'],
                        'settings_name'    : '__default__',
                        'units'            : {'syn_mRNA' : 'M/min', 
                                              'deg_mRNA' : '1/min',
                                              'syn_Pep'  : '1/min',
                                              'deg_Pep'  : '1/min',
                                              'Ind'     : 'M'
                                              },
                        'parameters'       : {'syn_mRNA' : np.array([0.02]), 
                                              'deg_mRNA' : np.array([0.15]),
                                              'syn_Pep'  : np.array([0.02]),
                                              'deg_Pep'  : np.array([0.012]) ,
                                              'Ind'     : np.array([1.0]) 
                                              },
                        'init'             : {1: [0, 0]},
                        'parameter_bounds' : {'deg_mRNA' : [0.001, 0.03, 1], 
                                              'deg_Pep'  : [0.01, 0.5], 
                                              },
                        'solver_args'      : {'rtol'   : 1.49012e-8,
                                              'atol'   : 1.49012e-8,
                                              'tcrit'  : [],
                                              'h0'     : 0.0,
                                              'hmax'   : 0.0,
                                              'hmin'   : 0.0,
                                              'mxstep' : 0
                                              },
                    }
        settings = sh.make_settings(**__settings__)
    
    @pytest.mark.xfail
    def test_make_settings_fail_3(self):
        #Mismatched parameter length
        __settings__ = {'system_type'      : ['TestModel, Dummy'],
                        'settings_name'    : '__default__',
                        'units'            : {'syn_mRNA' : 'M/min', 
                                              'deg_mRNA' : '1/min',
                                              'syn_Pep'  : '1/min',
                                              'deg_Pep'  : '1/min',
                                              'Ind'     : 'M'
                                              },
                        'parameters'       : {'syn_mRNA' : np.array([0.02, 1]), 
                                              'deg_mRNA' : np.array([0.15]),
                                              'syn_Pep'  : np.array([0.02]),
                                              'deg_Pep'  : np.array([0.012]) ,
                                              'Ind'     : np.array([1.0]) 
                                              },
                        'init'             : {1: [0, 0]},
                        'parameter_bounds' : {'deg_mRNA' : [0.001, 0.03], 
                                              'deg_Pep'  : [0.01, 0.5], 
                                              },
                        'solver_args'      : {'rtol'   : 1.49012e-8,
                                              'atol'   : 1.49012e-8,
                                              'tcrit'  : [],
                                              'h0'     : 0.0,
                                              'hmax'   : 0.0,
                                              'hmin'   : 0.0,
                                              'mxstep' : 0
                                              },
                    }
        settings = sh.make_settings(**__settings__)
    
    def test_copy_settings(self):
        global settings_1
        
        copy = settings_1.copy()
        
        for key in copy:
            try:
                assert copy[key] == settings_1[key]
            except ValueError as e:
                pass
            except Exception as e:
                raise e
        
    def test_add_to_database(self):
        '''
        Note: add_to_database already makes calls to search/quick_search
        '''
        global settings_1
        
        settings = settings_1
        
        sh.add_to_database(settings, dialog=False)
        
        #Check if in database
        lst = sh.list_settings()
        assert (settings['system_type'], settings['settings_name']) in lst
        
    def test_delete(self):
        global settings_1
        
        system_type   = settings_1['system_type']
        settings_name = settings_1['settings_name']
        sh.delete(system_type, settings_name)
        
        #Check if in database
        lst = sh.list_settings()
        assert (system_type, settings_name) not in lst
    
    def test_restore(self):
        global settings_1
        
        system_type   = settings_1['system_type']
        settings_name = settings_1['settings_name']
        sh.restore(system_type, settings_name)
        
        #Check if in database
        lst = sh.list_settings()
        assert (system_type, settings_name) in lst
    
    def test_from_config(self):
        global core_model_2
        global settings_2
        
        user_core_models = {core_model_2['system_type'] : core_model_2}
        
        settings_2 = sh.from_config('testmodel.ini', user_core_models=user_core_models)
