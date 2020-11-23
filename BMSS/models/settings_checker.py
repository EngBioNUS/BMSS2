import numpy  as np
import pandas as pd

###############################################################################
#Template Based Checkers
###############################################################################
def check_and_assign_param_values(core_model, parameters):
    '''
    Checks if parameters are valid and returns a DataFrame.
    
    Accepts parameters as:
        1. dict of floats/np.float where keys are parameter names
        2. dict of arrays  where keys are parameter names
        3. Series where where indices are parameter names
        4. DataFrame where columns are parameter names
    
    Parameter names may be suffixed with an underscore i.e. param1_1_1 will
    be treated as param1_1
    
    Raises an error if parameter names cannot be matched.
    
    Returns a DataFrame of parameters with columns in order.
    '''
    if type(parameters) == pd.DataFrame:
        parameter_df = pd.DataFrame(parameters)
    elif type(parameters) == pd.Series:
        parameter_df = pd.DataFrame(parameters).T
    elif type(parameters) == dict:
        parameter_df = pd.DataFrame(parameters)
        try:
            parameter_df = pd.DataFrame(parameters)
        except:
            parameter_df = pd.DataFrame([parameters])
    else:
        raise Exception('Error in parameters. Parameters must be dict, DataFrame or Series.')
    
    parameter_df.reset_index(drop=True, inplace=True)
    
    df_columns        = list(parameter_df.columns)
    core_model_params = core_model['parameters'] + core_model['inputs']
    
    #Check that parameter names match
    if set(df_columns).difference(core_model_params):#Not match
        #Assume parameters have been suffixed
        #Remove the suffix, reassign and rearrange
        df_columns_ = ['_'.join(p.split('_')[:-1]) for p in df_columns]
        
        if set(df_columns_).difference(core_model_params):
            raise Exception('Could not match parameter names with that of core_model')
        else:
            parameter_df.columns = df_columns_
            
            parameter_df         = parameter_df[core_model_params]
            return parameter_df
    else:#Match
        #Ensure order is correct
        parameter_df = parameter_df[core_model_params]
        return parameter_df

def check_and_assign_solver_args(solver_args):
    '''
    Accepts a dict of solver_args and checks if it is valid against a template.
    
    Raises an exception if 
        1. Unexpected keys are found.
        2. Value indexed by tcrit cannot be converted into a list
        3. Value indexed by other keys cannot be converted in a float
    
    Returns the template but with new values from solver_args.
    '''
    
    template = {'rtol'   : 1.49012e-8,
                'atol'   : 1.49012e-8,
                'tcrit'  : [],
                'h0'     : 0.0,
                'hmax'   : 0.0,
                'hmin'   : 0.0,
                'mxstep' : 0
                }
    
    if not solver_args:
        return template
    
    for key in solver_args:
        if key not in template:
            raise Exception('Error in solver_args. Unexpected key found: ' + str(key))
        
        elif key == 'tcrit':
            try:
                template[key] = list(solver_args[key])
            except:
                raise Exception('Error in solver_args. value indexed by key ' + str(key) + ' must be list-like.')
        else:
            try:
                template[key] = float(solver_args[key])
            except:
                raise Exception('Error in solver_args. value indexed by key ' + str(key) + ' must be a number.')                                

    return template

def check_and_assign_init(states, init, init_orient='scenario'):
    '''
    Accepts init in the form of {scenario_num : array} if init_orient is "scenario".
    Accepts init in the form of {state : array} if init_orient is "state".
    
    Formats init in the form required by the models datastructure.
    
    Accepts init in the form:
        1. {scenario_num : array} if init_orient is scenario
        2. {state : array} if init_orient is "state"
        3. A DataFrame where the columns are the states if init_orient is "state"
        4. A Series where the indices are the states if init_orient is "state"
        5. A numpy array where each column corresponds the states in order
    
    Raises an exception in (1) if the length of any array does not match the length
    of states.
    
    Raises an exception in (2) if 
    
    '''
    def check_valid_scenario_num(scenario_num):
        if type(scenario_num) != int:
            raise Exception('Error in init argument. Only positive integers can be used as scenario_num.')
        elif scenario_num < 1:
            raise Exception('Error in init argument. Only positive integers can be used as scenario_num.')
                
        else:
            return
    
    def check_valid_num_states(states, row):
        if len(states) == len(row):
            return
        else:
            raise Exception('Error in init. Number of states does not match core model. Expected:\n' + str(states) + '\nDetected:\n' + str(row))
    
    def check_valid_states(states, columns):
        if set(states).difference(columns):
            raise Exception('Error in init. Unexpected states found. Expected:\n' + str(states) + '\nDetected:\n' + str(columns))
    if init is not None:
        if init_orient == 'scenario':
            for key in init:
                check_valid_num_states(states, init[key])
                check_valid_scenario_num(key)
            return init
        
        else:
            if type(init) == dict:
                init1 = pd.DataFrame([init])
                init1.index += 1
                check_valid_states(states, list(init1.columns))
            elif type(init) == pd.DataFrame:
                init1 = init.reset_index(drop=True)
                init1.index += 1
                check_valid_states(states, list(init1.columns))
            elif type(init) == pd.Series:
                init1 = pd.DataFrame(init).T
                init1.index += 1
                check_valid_states(states, list(init1.columns))
            
            else: #Array based
                init1 = pd.DataFrame(init)
                init1.index += 1
                try:
                    init1.columns = states
                except:
                    raise Exception('Number of states does not match width of init')
            
            check_valid_num_states(states, list(init1.columns))
            [check_valid_scenario_num(x)  for x in list(init1.index)]
                    
            return init1
    else:
        return {1: np.array([0]*len(states))}

def check_and_assign_parameter_bounds(parameter_df, parameter_bounds):
    '''
    Accepts parameters as DataFrame. Parameter names must match core model.
    '''
    bounds1 = {}
    for key in parameter_df:
        if key in parameter_bounds:
            min_val, max_val = parameter_bounds[key]
        else:
            min_val = float(np.min(parameter_df[key]))/10
            max_val = float(np.max(parameter_df[key]))*10
            
        bounds1[key] = [min_val, max_val]
    return bounds1

def check_and_assign_priors(parameter_df, priors):
    '''
    Parameter names must match core model.
    '''
    priors1 = {}
    if priors is None:
        return priors1
    
    for key in priors:
        if key not in parameter_df:
            raise Exception('Unexpected parameter name in priors: ' + str(key))
        try:
            priors1[key] = np.array(priors[key])
        except:
            raise Exception('Error in ' + str(key) + '. Values indexed by priors must be list-like.')
    
    return priors1

def check_and_assign_tspan(tspan):
    if tspan:
        try:
            tspan1 = [np.linspace(*span) for span in tspan]
        except:      
            try:
                tspan1 = [np.array(span) for span in tspan]
            except:
                raise Exception('Error in tspan. tspan must be a list of list-like structures.')
            
    else:
        tspan1 = [np.linspace(0, 600, 31)]
    return tspan1