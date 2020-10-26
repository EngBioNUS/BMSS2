if __name__ == '__main__':
    from _backend_model_handler import (config_to_database, from_config, to_config, add_to_database, 
                                        list_models, to_df,
                                        quick_search, search_database, get_model_function,
                                        delete, restore,
                                        model_to_code, make_core_model, copy_core_model,
                                        update_ia, read_ia, reset_ia
                                        )

else:
    from ._backend_model_handler import (config_to_database, from_config, to_config, add_to_database, 
                                         list_models, to_df,
                                         quick_search, search_database, get_model_function,
                                         delete, restore,
                                         model_to_code, make_core_model, copy_core_model,
                                         update_ia, read_ia, reset_ia
                                         )

if __name__ == '__main__':
    from   pathlib import Path
    import os
    
    markup_directory = Path(os.getcwd()) /'markup'
    filename         = markup_directory  /'TestModel_Naringenin_RBSStrength.ini'
    
    from_config(filename)