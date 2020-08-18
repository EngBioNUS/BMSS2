if __name__ == '__main__':
    from _backend_setup_sim import (from_config, compile_models, get_models_and_params, 
                                    make_settings_template)
else:
    from ._backend_setup_sim import (from_config, compile_models, get_models_and_params, 
                                     make_settings_template)
