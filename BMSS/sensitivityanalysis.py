import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy             as np
import pandas            as pd
import seaborn           as sns
from SALib.analyze import sobol, fast, rbd_fast, delta
from SALib.sample import saltelli, fast_sampler, latin

###############################################################################
#Non-Standard Imports
###############################################################################
try:
    from . import simulation as sim
except:
    import simulation as sim
    
###############################################################################
#High Level Wrappers
###############################################################################
def analyze(params, models, fixed_parameters, objective, parameter_bounds={}, mode='np', analysis_type='sobol', N=100):
    '''Main algorithm for sensitivity analysis. Wraps analyze_sensitivty and sample_and_integrate.
    '''
    
    #Check for input errors
    if len(parameter_bounds) and len(parameter_bounds) != len(params.columns) - len(fixed_parameters):
        raise Exception('len(parameter_bounds) not equal to len(params) - len(fixed_parameters)')

    if not all(list(map(lambda x: x in params, fixed_parameters))):
        raise Exception('One or more unexpected parameters in fixed_parameters.' )
    
    if mode not in ['np' , 'df']:
        raise Exception('mode must be np or df')
    
    if analysis_type not in ['sobol', 'fast', 'rbd-fast' ,'delta']:
        raise Exception('analysis_type must be sobol, fast or delta.')
        
    #Generate samples and integrate
    em, samples, problems = sample_and_integrate(models, params, fixed_parameters, parameter_bounds, objective, analysis_type=analysis_type, N=N)
    
    #Analyze results
    analysis_result  = analyze_sensitivity(em, samples, problems, analysis_type=analysis_type)
    
    return analysis_result, em, samples, problems

def sample_and_integrate(models, params, fixed_parameters, parameter_bounds, objective, analysis_type='sobol', N=1000):
    
    samples, problems = make_samples(models, params, fixed_parameters, parameter_bounds, analysis_type=analysis_type, N=N)
    em                = integrate_samples(models, samples, objective)
    
    return em, samples, problems

###############################################################################
#Output Evaluation and Sensitivity Analysis
###############################################################################
def analyze_sensitivity(objective_function_values, samples, problems, analysis_type='sobol', **kwargs):
    s = {}
    e = objective_function_values
    
    for model_num in e:
        s[model_num] = {}  
        for scenario in e[model_num]:
            s[model_num][scenario] = {}
            for row_name in e[model_num][scenario]:
                s[model_num][scenario][row_name] = {}
                for func in e[model_num][scenario][row_name]:
                    problem  = problems[model_num][row_name]
                    permuted = problem['names'] 
                    x        = samples[model_num][row_name][permuted]
                    y_val    = e[model_num][scenario][row_name][func]
                    
                    s[model_num][scenario][row_name][func] = salib_wrapper(problem, y_val, x, analysis_type, **kwargs)
    
    return s

def salib_wrapper(problem, y_val, x, analysis_type='sobol', **kwargs):
    '''
    Backend wrapper for sobol, fast and delta analysis.
    
    :meta private:
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
def integrate_samples(models, samples, objective, args=()):
    '''
    Integrates the samples and evaluates the objective function for each.

    Parameters
    ----------
    models : dict
        A dictionary of model data structures.
    samples : dict
        A dictionary of parameter values for sampling.
    objective : dict
        A dictionary of objective functions to evaluate indexed by model_num.
    args : tuple, optional
        Additional arguments for integration. The default is ().

    Returns
    -------
    e_models : dict
        The objective function values.
    '''
    e_models = {}
    samples1 = {}
    for model_num in samples:
        samples1[model_num] = {}
        for row_name in samples[model_num]:
            if type(samples[model_num][row_name]) != pd.DataFrame:
                try:
                    samples1[model_num][row_name] = pd.DataFrame(samples[model_num][row_name])
                except:
                    samples1[model_num][row_name] = pd.DataFrame([samples[model_num][row_name]])
            else:
                samples1[model_num][row_name] = samples[model_num][row_name]
                
    for model_num in models:
        model               = models[model_num]
        e_models[model_num] = {}
        for scenario_num in models[model_num]['init']:
            if type(scenario_num) == int:
                if scenario_num < 1:
                    continue
            e_models[model_num][scenario_num] = {}
            for row_name in samples[model_num]:
                params1 = samples[model_num][row_name]
                temp    = {func: [] for func in objective.get(model_num)}
                
                e_models[model_num][scenario_num][row_name] = {}      
                for _, row in params1.iterrows():
                    y_model, t_model = sim.piecewise_integrate(params        = row.values,
                                                               function      = model['function'], 
                                                               init          = model['init'][scenario_num],
                                                               tspan         = model['tspan'],
                                                               modify_init   = model['int_args']['modify_init'],
                                                               modify_params = model['int_args']['modify_params'],
                                                               solver_args   = model['int_args']['solver_args'],
                                                               model_num     = model_num, 
                                                               scenario_num  = scenario_num, 
                                                               overlap       = True,
                                                               *args
                                                               )
                   
                
                    for func in objective.get(model_num):
                        y_model_ = pd.DataFrame(y_model) if 'mode=pd' in str(func.__doc__) else y_model
                        variable = func(y_model_, t_model, row.values)
                        temp[func].append(variable)
                
                for func in objective.get(model_num):
                    e_models[model_num][scenario_num][row_name][func] = np.array(temp[func])
    
        return e_models
    
###############################################################################
#Sample Generation
###############################################################################
def make_samples(models, params, fixed_parameters, parameter_bounds, analysis_type='sobol', N=1000):
    '''Generates samples for each model.
    '''
    try:
        params1 = pd.DataFrame(params)
    except:
        params1 = pd.DataFrame([params])
    
    samples  = {}
    problems = {}
    
    for model_num in models:
        samples[model_num]  = {}
        problems[model_num] = {}
        
        for name, row in params1.iterrows():
            row_samples, row_problem = make_samples_for_row(row, 
                                                            models[model_num], 
                                                            fixed_parameters, 
                                                            parameter_bounds, 
                                                            analysis_type=analysis_type, 
                                                            N=N
                                                            )
            samples[model_num][name]  = row_samples
            problems[model_num][name] = row_problem
    
    return samples, problems

def make_samples_for_row(row, model, fixed_parameters, parameter_bounds={}, analysis_type='sobol', N=1000, **kwargs):
    '''
    Supporting function for sample_and_integrate. Do not run.
    row must be a pandas Series
    
    :meta private:
    '''

    param_names      = model['params']
    base_value       = row[param_names]
    to_permute       = [p for p in param_names if p not in fixed_parameters]
    to_keep          = [p for p in param_names if p     in fixed_parameters]
    if parameter_bounds:
        bounds = np.array([parameter_bounds[p] for p in to_permute])
    else:
        bounds = [[base_value[p]/10, base_value[p]*10] for p in to_permute] 
    
    problem = {'num_vars' : len(to_permute),
               'names'    : to_permute,
               'bounds'   : bounds,
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
    
    fixed_parametersped_values = np.repeat(base_value[to_keep].values[np.newaxis,:], len(new_values), 0)
            
    samples = np.concatenate((new_values, fixed_parametersped_values), axis=1)
    samples = pd.DataFrame(samples, columns = to_permute+to_keep)
    samples = samples[param_names]
    
    return samples, problem

###############################################################################
#Visualization
###############################################################################
def plot_first_order(analysis_result, problems={}, titles={}, analysis_type='sobol', figs=None, AX=None, analysis_keys=(), **heatmap_args):
    '''
    If analysis_type is neither sobol, fast nor delta, use analysis_keys to specify which 
    keys/columns to use.
    '''
    
    #Fix this
    figs1, AX1 = (figs, AX) if AX else make_AX1(analysis_result) 

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
        for scenario_num in analysis_result[model_num]:
            for row_name in analysis_result[model_num][scenario_num]:
                for func in analysis_result[model_num][scenario_num][row_name]:
                    
                    r  = analysis_result[model_num][scenario_num][row_name][func]
                    p  = problems[model_num][row_name]['names'] if problems else None
                    df = pd.DataFrame({key: r[key] for key in keys}, columns=keys, index=p)
                    ax = AX1[model_num][scenario_num][row_name][func]
                    
                    sns.heatmap(df, ax=ax, **heatmap_args)
                    
                    try:
                        title = titles[model_num][scenario_num][row_name][func]
                    except:
                        try:
                            title = titles[model_num][scenario_num][func]
                        except:
                            if titles.get(model_num, {}).get(func, None):
                                title = make_default_title(model_num, scenario_num, row_name, titles[model_num][func])
                            else:
                                title = make_default_title(model_num, scenario_num, row_name, func.__name__)
                    ax.set_title(title)
    
    [sim.fs(fig) for fig in figs1]
    
    return figs1, AX1
    

def plot_second_order(analysis_result, problems={}, titles={}, analysis_type='sobol', figs=None, AX=None, analysis_keys=(), **heatmap_args):
    '''
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

    for model_num in analysis_result:
        for scenario_num in analysis_result[model_num]:
            for row_name in analysis_result[model_num][scenario_num]:
                for func in analysis_result[model_num][scenario_num][row_name]:
                    r  = analysis_result[model_num][scenario_num][row_name][func]
                    p  = problems[model_num][row_name]['names'] if problems else None
                    
                    for key in keys:
                        ax = AX1[model_num][scenario_num][row_name][func][key]
                        df = pd.DataFrame(r[key], columns=p, index=p)
                    
                        sns.heatmap(df, ax=ax, **heatmap_args)
                    
                        try:
                            title = titles[model_num][scenario_num][row_name][func]
                        except:
                            try:
                                title = titles[model_num][scenario_num][func]
                            except:
                                if titles.get(model_num, {}).get(func, None):
                                    title = make_default_title(model_num, scenario_num, row_name, titles[model_num][func])
                                else:
                                    title = make_default_title(model_num, scenario_num, row_name, func.__name__)
                        ax.set_title(title + ' (' + key + ')')
    
    [sim.fs(fig) for fig in figs1]
    
    return figs1, AX1

def make_AX1(analysis_result):
    '''
    :meta private:
    '''
    figs = []
    AX   = {}
    for model_num in analysis_result:
        AX[model_num] = {}
        for scenario_num in analysis_result[model_num]:
            AX[model_num][scenario_num] = {}
            for row_name in analysis_result[model_num][scenario_num]:
                AX[model_num][scenario_num][row_name] = {}
                
                n    = len(analysis_result[model_num][scenario_num][row_name])
                rows = int(n**0.5)
                cols = int(n/rows + 0.5)
                fig  = plt.figure()
                AX_  = [fig.add_subplot(rows, cols, i+1) for i in range(n)] 
                i    = 0
                figs.append(fig)
                for func in analysis_result[model_num][scenario_num][row_name]:
                    AX[model_num][scenario_num][row_name][func] = AX_[i]
                    i += 1
    return figs, AX

def make_AX2(analysis_result, keys):
    '''
    :meta private:
    '''
    figs = []
    AX   = {}
    for model_num in analysis_result:
        AX[model_num] = {}
        for scenario_num in analysis_result[model_num]:
            AX[model_num][scenario_num] = {}
            for row_name in analysis_result[model_num][scenario_num]:
                AX[model_num][scenario_num][row_name] = {}

                for func in analysis_result[model_num][scenario_num][row_name]:
                    fig  = plt.figure()
                    AX_  = [fig.add_subplot(1, 2, i+1) for i in range(2)] 
                    AX[model_num][scenario_num][row_name][func] = dict(zip(keys, AX_))
                    figs.append(fig)

    return figs, AX

def make_default_title(model_num, scenario_num, row_name, func_name):
    '''
    :meta private:
    '''
    return 'Model {model_num}, Scenario {scenario_num}, Row {row_name}, {func}'.format(model_num    = model_num, 
                                                                                  scenario_num = scenario_num,
                                                                                  row_name     = row_name,
                                                                                  func         = func_name
                                                                                  )
