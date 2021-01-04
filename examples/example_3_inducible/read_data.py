import numpy  as np
import pandas as pd

def read_data(states_and_filenames, n_models=1):
    data_mu   = {}
    data_sd   = {}
    state_sd  = {}
    tspan     = []
    init      = {}
    
    for state, filename in states_and_filenames.items():
        df         = pd.read_csv(filename)
        scenarios  = []
        
        for column in df.columns:
            if 'std' in column:
                continue
            elif 'Time' in column:
                scenarios = [column] + scenarios
                tspan.append(df[column].values)
            else:
                scenarios.append(column)
              
        #Set up data_mu, data_sd, init, tspan
        for model_num in range(1, n_models+1):
            data_mu.setdefault(model_num, {})[state] = {}
            data_sd.setdefault(model_num, {})[state] = {}
            init.setdefault(model_num, {})
            
            for i, scenario in enumerate(scenarios):
                
                #Add experimental data and time to data_mu
                data_mu[model_num][state][i] = df[scenario].values    
                
                if 'Time' in scenario:
                    #Add time to data_sd
                    data_sd[model_num][state][i] = df[scenario].values
                
                else:
                    #Add sd of experimental data to data_sd
                    data_sd[model_num][state][i] = df[scenario + 'std'].values         
                    
                    #Set up initial values for integration
                    #Take first value of experimental data and add to init
                    init_val           = data_mu[model_num][state][i][0]              
                    init[model_num][i] = {state:init_val}
        
            #Add scenarios for reference    
            data_mu[model_num][state][-1] = scenarios
            data_sd[model_num][state][-1] = scenarios
        
        #Set up state_sd
        df_sd           = df[[scenario + 'std' for scenario in scenarios if 'Time' not in scenario]]
        state_sd[state] = df_sd.mean().mean()
    
    #Reformat tspan into a 1-D array and sort uniquely.
    tspan = np.unique(np.concatenate(tspan))
    return data_mu, data_sd, init, state_sd, tspan