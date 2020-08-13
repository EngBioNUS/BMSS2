import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy             as np
import pandas            as pd
import seaborn           as sns
from SALib.analyze import sobol, fast, rbd_fast, delta
from SALib.sample import saltelli, fast_sampler, latin

try:
    from . import curvefitting as cf
except:
    import curvefitting as cf

###############################################################################
#Main Algorithm
###############################################################################
def analyze(params, models, skip, func, parameter_bounds=np.array([]), mode='np', analysis_type='sobol', N=100):
    '''
    Main algorithm for sensitivity analysis. Wraps analyze_sensitivty and sample_and_integrate.
    '''
    
    parameter_bounds1 = parameter_bounds if type(parameter_bounds) == np.ndarray else np.array(list(parameter_bounds.values()))
    
    #Check for input errors
    if len(parameter_bounds1) and len(parameter_bounds1) != len(params) - len(skip):
        raise Exception('len(parameter_bounds) not equal to len(params) - len(skip)')

    if not all(list(map(lambda x: x in params, skip))):
        raise Exception('One or more unexpected parameters in skip.' )
    
    if mode not in ['np' , 'df']:
        raise Exception('mode must be np or df')
    
    if analysis_type not in ['sobol', 'fast', 'rbd-fast' ,'delta']:
        raise Exception('analysis_type must be sobol, fast or delta.')
        
    #Generate samples and integrate
    y, t, s, p       = sample_and_integrate(params, models, skip, parameter_bounds=parameter_bounds1, analysis_type=analysis_type, N=N)
    
    #Analyze results
    analysis_result  = analyze_sensitivity(y, t, samples=s, problems=p, func=func, mode=mode, analysis_type=analysis_type)
    
    return y, t, s, p, analysis_result

###############################################################################
#Output Evaluation and Sensitivity Analysis
###############################################################################
def analyze_sensitivity(y, t, samples, problems, func, mode='np', analysis_type='sobol', **analyzer_args):
    '''
    Accepts dict y where y[model_num][scenario] is the model output as either 
    a numpy array or pandas DataFrame. problems is a dict of where problems[model_num]
    is a dict defined according to https://salib.readthedocs.io/en/latest/basics.html
    
    Iterates across models and scenarios and evaluates each output in 
    y[model_num][scenario] according to func. If mode is np, the values in
    y[model_num][scenario] are converted to numpy arrays first. If mode is df,
    the pandas DataFrames are used.
    
    '''
    result = {}
    for model_num in y:
        result[model_num] = {}
        p_                = problems[model_num]
        s_                = samples[model_num][p_['names']].values
        t_                = t[model_num]
        
        for scenario in y[model_num]:
            y_ = y[model_num][scenario]
            y_ = evaluate_output(y_, t_, s_, func, mode=mode)
            
            Si = salib_wrapper(p_, y_, s_, analysis_type=analysis_type, **analyzer_args)
            result[model_num][scenario] = Si
    return result

def evaluate_output(y_scenario, t_scenario, param_array, func, mode='np'):
    '''
    Accepts a dict of model outputs and evaluates it according to func. If the outputs
    are pandas DataFrames, they can be converted to numpy arrays by setting mode to
    np or evaluated as-is by setting mode to df.
    If the outputs are numpy arrays, they are evaluated as-is.
    '''

    def helper(y_sample, param_sample):
        result = func(y_sample, t_scenario, param_sample)
        try:
            float(result)
        except:
            try: 
                result = float(result[0])
            except:
                raise Exception('Invalid return value for func ' + str(func) + '. Ensure return value/first value is a scalar.')
        return result
        
    if type(y_scenario[next(iter(y_scenario))]) == pd.DataFrame:
        if mode == 'df':
            y_ = list(map(helper, y_scenario.values() ,param_array))
        
        else :
            y_ = list(map(helper, [y_scenario[key].values for key in y_scenario] ,param_array))
    else:
        y_ = list(map(helper, y_scenario.values() ,param_array))
    return np.array(y_)

def salib_wrapper(problem, y_val, x, analysis_type='sobol', **kwargs):
    '''
    Backend wrapper for sobol, fast and delta analysis.
    '''
    if analysis_type == 'sobol':
        return sobol.analyze(problem, y_val, **kwargs)
    elif analysis_type == 'fast':
        return fast.analyze(problem, y_val, **kwargs)
    elif analysis_type == 'delta':
        return delta.analyze(problem, x, y_val, **kwargs)
    elif analysis_type == 'rbd-fast':
        return rbd_fast.analyze(problem, x, y_val, **kwargs)
    else:
        raise Exception('Could not find analyzer. analysis_type must be sobol, fast, rbd-fast or delta.')    
   

###############################################################################
#Sampling and Integration 
###############################################################################
def sample_and_integrate(params, models, skip, 
                         samples=None, 
                         int_args={},
                         parameter_bounds=np.array([]),
                         analysis_type='sobol', 
                         N=1000, 
                         sample_args={}):  
    '''
    Generates samples and integrates them. You can provide your own samples 
    instead using the samples argument. parameteter_bounds will then be ignored.
    
    Returns the follwoing:
        1. y, the model output as a dict in the form y[model_num][scenario] 
        2. t, the timespan for each model in the form t[model_num]
        2. s, the samples generated as a dict in the form s[model_num]
        3. p, the problems generated as a dict in the form p[model_num] where
           p[model_num] is defined according to https://salib.readthedocs.io/en/latest/basics.html
    '''
    y = {}
    t = {}
    s = {}
    p = {}
    
    #Convert params to a Pandas Series
    try:
        params_series = pd.DataFrame(params).iloc[0]
    except:
        params_series = pd.Series(params)
    
    #If user provides samples, convert it to DataFrame
    if samples is None:
        samples1 = pd.DataFrame()
    else:
        samples1 = pd.DataFrame(samples)
    
    for model_num in models:
        y[model_num]      = {}
        t[model_num]      = {}
        model             = models[model_num]
        tspan             = model['tspan']
        init              = model['init']
        int_args          = model.get('int_args', {})
        samples_, problem = samples1[model['params']] if len(samples1) else make_samples(params_series, model, skip, N=N, parameter_bounds=parameter_bounds, analysis_type=analysis_type, **sample_args) 
        s[model_num]      = samples_
        p[model_num]      = problem
        
        for scenario in range(1, len(init)+1):
            y[model_num][scenario] = {}
            
            for row_num in range(len(samples_)):
                row    = samples_.iloc[row_num].values
                y_, t_ = cf.piecewise_integrate(model['function'], init[scenario], tspan, row, model_num, scenario, **int_args)
                
                y[model_num][scenario][row_num] = pd.DataFrame(y_, columns=model['states'])
                t[model_num]                    = t_          
    
    return y, t, s, p

###############################################################################
#Sample Generation
###############################################################################
def make_samples(params, model, skip, parameter_bounds=np.array([]), analysis_type='sobol', N=1000, **kwargs):
    '''
    Supporting function for sample_and_integrate. Do not run.
    params must be a pandas Series
    '''

    param_names      = model['params']
    base_value       = params[param_names]
    to_permute       = [p for p in param_names if p not in skip]
    to_keep          = [p for p in param_names if p     in skip]
    bounds           = parameter_bounds if len(parameter_bounds) else [[base_value[p]/10, base_value[p]*10] for p in to_permute] 
    
    problem = {'num_vars' : len(to_permute),
               'names'   : to_permute,
               'bounds'  : bounds,
               }
    
    if analysis_type == 'sobol':          
        new_values   = saltelli.sample(problem, N, **kwargs)
    elif analysis_type == 'fast':   
        new_values   = fast_sampler.sample(problem, N, **kwargs)
    elif analysis_type == 'delta':
        new_values   = latin.sample(problem, N)
    elif analysis_type == 'rbd-fast':
        new_values   = latin.sample(problem, N)
    else:
        raise Exception('Could not find analyzer. analysis_type must be sobol, fast, rbd-fast or delta.')    
        
    new_values   = pd.DataFrame(new_values, columns=to_permute)
    
    skipped_values = np.repeat(base_value[to_keep].values[np.newaxis,:], len(new_values), 0)
            
    samples = np.concatenate((new_values, skipped_values), axis=1)
    samples = pd.DataFrame(samples, columns = to_permute+to_keep)
    samples = samples[param_names]
    
    return samples, problem    

###############################################################################
#Visualization
###############################################################################
def plot_first_order(analysis_result, problems={}, titles={}, analysis_type='sobol', figs=None, AX=None, analysis_keys=(), **heatmap_args):
    '''
    Accepts a dict analysis_result where analysis_result[model_num][scenario] is a 
    dict or DataFrame of sensitivity analysis results.
    
    If analysis_type is neither sobol, fast nor delta, use analysis_keys to specify which 
    keys/columns to use.
    '''

    figs1, AX1 = (figs, AX) if AX else make_AX(analysis_result) 
    dfs        = {}

    if analysis_type == 'sobol':
        keys = ['S1', 'S1_conf', 'ST', 'ST_conf']
    elif analysis_type == 'fast':
        keys = ['S1', 'ST']
    elif analysis_type == 'delta':
        keys = ['delta', 'delta_conf', 'S1', 'S1_conf']
    elif analysis_type == 'rbd-fast':
        keys = ['S1']
    else:
        if analysis_keys:
            keys = analysis_keys
        else:
            raise Exception('analysis_key must be specified if using custom analysis.')
    for model_num in analysis_result:
        dfs[model_num] = {}
        for scenario in analysis_result[model_num]:
            r  = analysis_result[model_num][scenario]
            p  = problems[model_num]['names'] if problems else None
            df = pd.DataFrame({key: r[key] for key in keys}, columns=keys, index=p)
            ax = AX1[model_num][scenario]
            
            sns.heatmap(df, ax=ax, **heatmap_args)
            title = titles.get(model_num, {}).get(scenario, str(scenario))
            ax.set_title(title)
            dfs[model_num][scenario] = df
    
    list(map(cf.fs, figs1))
    
    return figs1, AX1, dfs 
    

def plot_second_order(analysis_result, problems={}, titles={}, analysis_type='sobol', figs=None, AX=None, analysis_keys=(), **heatmap_args):
    '''
    Accepts a dict analysis_result where analysis_result[model_num][scenario] is a 
    dict of sensitivity analysis results and each value is a 2d array or DataFrame.
    
    If analysis_type is not sobol, use analysis_keys to specify which keys/columns to use.
    '''

    if analysis_type == 'sobol':
        keys = ['S2', 'S2_conf']
    else:
        if analysis_keys:
            keys = analysis_keys
        else:
            raise Exception('analysis_key must be specified if using custom analysis.')
    
    figs1, AX1 = (figs, AX) if AX else make_AX2(analysis_result, keys) 
    dfs        = {}
    
    for model_num in analysis_result:
        dfs[model_num] = {}
        for scenario in analysis_result[model_num]:
            r  = analysis_result[model_num][scenario]
            p  = problems[model_num]['names'] if problems else None
            
            dfs[model_num][scenario] = {}
            
            for key in keys:
                
                df = pd.DataFrame(r[key], columns=p, index=p)
                ax = AX1[model_num][scenario][key]
            
                sns.heatmap(df, ax=ax, **heatmap_args)
                title = titles.get(model_num, {}).get(scenario, str(key) + ' ' + str(scenario))
                ax.set_title(title)
            
                dfs[model_num][scenario][key] = df
    
    list(map(cf.fs, figs1))
    
    return figs1, AX1, dfs 

def make_AX(analysis_result):
    figs = {key: plt.figure() for key in analysis_result}
    
    AX = {}
    for model_num in analysis_result:
        n    = len(analysis_result[model_num])
        rows = int(n**0.5)
        cols = int(n/rows + 0.5)
        
        axes      = [figs[model_num].add_subplot(rows, cols, i+1) for i in range(n)]
        scenarios = analysis_result[model_num].keys()
        
        AX[model_num]  = dict(zip(scenarios, axes))
    
    return list(figs.values()), AX

def make_AX2(analysis_result, keys):
    figs = {(model_num, scenario): plt.figure() for model_num in analysis_result for scenario in analysis_result[model_num]}

    AX = {}
    for model_num in analysis_result:
        AX[model_num] = {}
        for scenario in analysis_result[model_num]:
            n    = len(keys)
            rows = int(n**0.5)
            cols = int(n/rows + 0.5)
        
            axes = [figs[(model_num,scenario)].add_subplot(rows, cols, i+1) for i in range(n)]
            axes = dict(zip(keys, axes))
            
        
            AX[model_num][scenario] = axes
    
    return list(figs.values()), AX
