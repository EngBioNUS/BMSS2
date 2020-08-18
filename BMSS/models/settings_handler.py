if __name__ == '__main__':
    from _backend_settings_handler import (config_to_database, from_config, add_to_database, 
                                           list_settings, to_df,
                                           quick_search, search_database,
                                           delete, restore,
                                           make_settings, make_settings_template)
else:
    from ._backend_settings_handler import (config_to_database, from_config, add_to_database, 
                                            list_settings, to_df,
                                            quick_search, search_database,
                                            delete, restore,
                                            make_settings, make_settings_template)

if __name__ == '__main__':
    from os.path import dirname, join
    from os import getcwd

    __model__ = {'system_type' : ['DUMMY', 'DUMMY'],
                 'states'      : ['mRNA', 'Pep'], 
                 'parameters'  : ['syn_mRNA', 'deg_mRNA', 'syn_Pep', 'deg_Pep', 'Ki'],
                 'inputs'      : ['Ind'],
                 'equations'   : ['dmRNA = syn_mRNA*Ind/(Ind + Ki) - deg_mRNA*mRNA',
                                  'dPep  = syn_Pep*mRNA - deg_Pep'
                                  ],
                 'ia'          : 'ia_result_bmss01001.csv'
                 
                 }
    
    # core_model = make_core_model(**__model__)
    # add_core_model_to_database(core_model)
    # search_result = quick_search('DUMMY, DUMMY')
    # print(search_result)
    
    # filename = 'dummy.ini'
    # core_model = from_config(filename)
    # to_config(core_model, 'writeout.ini')
    