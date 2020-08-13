import numpy  as np
import pandas as pd

###############################################################################
#Template Based Checkers
###############################################################################
def check_and_assign_solver_args(solver_args):
    '''
    Accepts a template as the first argument and attempts to reassign the 
    values using those in the second argument.
    '''
    
    template = {'rtol'   : 1.49012e-8,
                'atol'   : 1.49012e-8,
                'tcrit'  : [],
                'h0'     : 0.0,
                'hmax'   : 0.0,
                'hmin'   : 0.0,
                'mxstep' : 0
                }
    
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
    '''
    if init:
        if init_orient == 'scenario':
            for key in init:
                if len(init[key]) != len(states):
                    raise Exception('Length of init must match number of states.')
            return init
        
        else:
            if type(init) == dict or type(init) == pd.Series or type(init) == pd.DataFrame:
                try: 
                    init1 = pd.DataFrame(init)
                except:
                    init1 = pd.DataFrame([init])
                
                init1.index += 1
                
                try:
                    init1 = init1[states]
                except:
                    raise Exception('Error in init argument. States in init do not macth those in core model.')
                    
                return init1.T.to_dict('list')
            
            else: #Array based
                init1  = {}
                nested = True
                for i in range(len(init)):
                    try:
                        row    = np.array(list(init[i]))
                        nested = False
                    except:
                        if not nested:
                            raise Exception('init must be a dict, DataFrame or list-like.')
                        try:
                            row        = np.array(list(init))
                            init1[i+1] = row
                            return init1
                        except:
                            raise Exception('init must be a dict, DataFrame or list-like.')
                        
                    if len(row) != len(states):
                        raise Exception('Expected ' + str(len(states)) + ' states but length of init is ' + str(len(init)) + '.')
                    
                    init1[i+1] = row
                    
                return init1
    else:
        return {1: np.array([0]*len(states))}

def check_and_assign_parameter_bounds(parameter_df, parameter_bounds):
    '''
    Accepts parameters as DataFrame.
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
    priors1 = {}
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
            tspan1 = [np.array(span) for span in tspan]
        except:
            raise Exception('Error in tspan. tspan must be a list of list-like structures.')
            
    else:
        tspan1 = [np.linspace(0, 600)]
    return tspan1