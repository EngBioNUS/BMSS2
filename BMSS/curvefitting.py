import matplotlib.pyplot as plt 
import numpy             as np
import pandas            as pd
import seaborn           as sns
from matplotlib          import get_backend
from numba               import jit
from scipy.integrate     import odeint

###############################################################################
#Non-Standard Imports
###############################################################################
try:
    from .mcmc       import *
    from .simulation import piecewise_integrate, palette_types, all_colors, apply_titles_and_legend, fs
    from .           import scipy_wrappers as wrappers
except:
    from mcmc import *
    from simulation import piecewise_integrate, palette_types, all_colors, apply_titles_and_legend, fs
    import scipy_wrappers as wrappers
    
###############################################################################
#SSE Calculation
###############################################################################
def get_SSE_data(data, models, params={}, t_indices={}, params_array=np.array([]), params_index={}):
    '''
    Calculates SSE for data against models and returns the negative of the SSE.
    
    For testing/single calls:
        1. Supply the parameters as a dict. Ignore all other optional arguments.
    For iterative calls:
        1. Ignore the params argument.
        2. Provide a numpy array of parameters instead.
        3. Use the function get_liklihood_args to set up the other arguments.

    Parameters
    ----------
    data : dict
        Experimental data.
    models : dict
        Dictionary of model data structures.
    params : dict, optional
        For backend use only. The default is {}.
    t_indices : dict, optional
        For backend use only. The default is {}.
    params_array : nupy.array, optional
        An array of parameter values. The default is np.array([]).
    params_index : dict, optional
        Required to work with the params_array. The default is {}.

    Returns
    -------
    float
        The negative of the SSE.

    '''
    if params:
        params_array1  = np.array(list(params.values()))
        name_to_num   = {name: num for num, name in enumerate(params)}
        params_index1  = {model_num: [name_to_num[param] for param in models[model_num]['params']] for model_num in models}
    else:
        params_array1 = params_array
        params_index1 = params_index
    
    t_indices1 = t_indices if t_indices else get_t_indices(data, models)
        
    SSE  = 0
    
    for model_num in data:
        
        params_  = params_array1[params_index1[model_num]] 
        SSE     += get_SSE_dataset(model_num, data, models, params_, t_indices1)

    return -SSE #Negated as required by likelihood function

###############################################################################
#Supporting Functions for SSE Calculation. Do not run.
###############################################################################
def get_SSE_dataset(model_num, data, models, params, t_indices):
    '''
    :meta private:
    '''
    SSE = 0

    dataset  = data[model_num]
    model    = models[model_num]
    tspan    = get_tspan(model)
    init     = model['init']
    int_args = model.get('int_args', {})
    
    for scenario in range(1, len(init)+1):
        y_model, t_model  = piecewise_integrate(model['function'], init[scenario], tspan, params, model_num, scenario, **int_args, overlap=False)
        
        for i in range(len(model['states'])):
            state      = model['states'][i]
            if state not in dataset:
                continue
            SSE_column = i
            y_data     = dataset[state][scenario]
            indices    = t_indices[model_num][state]
            y_model_   = y_model[indices,SSE_column] 
            sd_dataset = model['sd'][state]
            SSE += get_SSE(y_data, y_model_, sd_dataset)

    return SSE

@jit(nopython=True)
def get_SSE(y_data, y_model, sd_dataset=1):
    '''
    :meta private:
    '''
    error  = (y_data - y_model)**2
    return error.sum()/sd_dataset**2 

def get_t_indices(data, models):
    '''
    :meta private:
    '''
    t_indices = {}
    for model_num in data:
        dataset, model         = data[model_num], models[model_num]
        t_indices[model_num] = get_indices_dataset(dataset, model)
    return t_indices
    
def get_indices_dataset(dataset, model):
    '''
    :meta private:
    '''
    indices = {}
    for state in dataset:
        t_model            = flatten_tspan(model['tspan'])
        indices[state] = get_indices(dataset[state][0], t_model)
    return indices
        
def get_indices(t_data, t_model):
    '''
    :meta private:
    '''
    indices = []
    for t in t_data:
        index = np.where(t_model == t)

        if len(index) > 0:
            if len(index[0]) > 0:
                indices.append(int(index[0]))
            else:
                raise Exception(str(t)+' not in t_model.')
    return indices

def flatten_tspan(tspan):
    '''
    :meta private:
    '''
    return [t for segment in tspan for t in segment]

###############################################################################
#Set Up Objective Args
###############################################################################
def get_likelihood_args(data, models, params):
    '''
    Meant to be used with get_SSE. Accepts data, models and a dict of params to 
    generate the remaining arguments for get_SSE.
    
    Note: Actual values of the params do not matter. Only the order.
    
    :meta private:
    '''
    name_to_num   = {name: num for num, name in enumerate(params)}
    params_index  = {model_num: [name_to_num[param] for param in models[model_num]['params']] for model_num in models}
    t_indices     = get_t_indices(data, models)
    result        =  {'data'        : data, 
                      'models'      : models, 
                      't_indices'   : t_indices, 
                      'params_index': params_index
                      }
    return result        

###############################################################################
#Main Algorithm
###############################################################################
def simulated_annealing(data,         models,    guess,     priors,    step_size, 
                        trials=10000, bounds={}, blocks=[], SA=True, 
                        fixed_parameters=[],
                        likelihood_function=get_SSE_data,
                        **kwargs
                        ):  
    
    '''
    BMSS2's primary curve-fitting algorithm.
    
    Parameters
    ----------
    data : dict
        Experimental data.
    models : dict
        Dictionary of model data structures.
    guess : dict
        The initial guess. The default is {}.
    priors : dict, optional
        Priors if any. The default is {}.
    step_size : dict, optional
        A dictionary mapping parameter names to median step-size during the 
        stochastic transition step.
    trials : int, optional
        The number of iterations. The default is 10000.
    bounds : dict, optional
        A dictionary mapping parameter names to tuples (lower, upper). The 
        default is {}.
    blocks : list of lists, optional
        A list of lists grouping parameter names into blocks for blocked Gibbs 
        sampling
    SA : bool, optional
        True if you want to apply the temperature criterion. False if you want 
        to use a constant cutoff criterion. The default is True.
    fixed_parameters : list, optional
        A list of parameters that will be fixed. The default is [].
    likelihood_function : function, optional
        The likelihood function to be calculated. Do not change unless you know 
        what you are doing.
    
    Returns
    ---------- 
    result : dict
        A dictionary with the following mapping:
            "a" : The accepted samples
            "r" : The rejected samples
    '''
    
    likelihood_args = get_likelihood_args(data, models, guess)
    
    return sampler(guess,         priors,        step_size, 
                   trials=trials, skip=fixed_parameters, bounds=bounds, blocks=blocks, SA=SA, 
                   likelihood_function=get_SSE_data,
                   likelihood_args=likelihood_args,
                   **kwargs)

def scipy_basinhopping(data,    models,    guess, priors, step_size=0.1, bounds={},  
                       step_size_is_ratio=True,
                       fixed_parameters=[],
                       likelihood_function=get_SSE_data, 
                       scipy_args={},
                       **kwargs):
    '''
    Wrapper for scipy's basin-hopping algorithm.
    
    Parameters
    ----------
    data : dict
        Experimental data.
    models : dict
        Dictionary of model data structures.
    guess : dict
        The initial guess. The default is {}.
    priors : dict, optional
        Priors if any. The default is {}.
    step_size : float or dict, optional
        Step size.
    step_size_is_ratio : bool, optional
        If True, step size is a proportion of the initial guess. If False, 
        absolute values are used.
    bounds : dict, optional
        A dictionary mapping parameter names to tuples (lower, upper). The 
        default is {}.
    fixed_parameters : list, optional
        A list of parameters that will be fixed. The default is [].
    likelihood_function : function, optional
        The likelihood function to be calculated. Do not change unless you know 
        what you are doing.
    
    Returns
    ---------- 
    result : dict
        A dictionary with the following mapping:
            "a" : The accepted samples
            "r" : The rejected samples
    '''
    likelihood_args = get_likelihood_args(data, models, guess)
    
    result = wrappers.basinhopping(guess,         priors,  step_size=step_size, 
                                   skip=fixed_parameters, bounds=bounds,  
                                   likelihood_function=likelihood_function, 
                                   likelihood_args=likelihood_args,
                                   **scipy_args,
                                   **kwargs)
    
    return result

def scipy_dual_annealing(data, models, guess, priors, bounds={},  
                         fixed_parameters=[], 
                         likelihood_function=get_SSE_data, 
                         scipy_args={},
                         **kwargs):
    '''
    Wrapper for scipy's dual annealing algorithm.
    
    Parameters
    ----------
    data : dict
        Experimental data.
    models : dict
        Dictionary of model data structures.
    guess : dict
        The initial guess. The default is {}.
    priors : dict, optional
        Priors if any. The default is {}.
    bounds : dict, optional
        A dictionary mapping parameter names to tuples (lower, upper). The 
        default is {}.
    fixed_parameters : list, optional
        A list of parameters that will be fixed. The default is [].
    likelihood_function : function, optional
        The likelihood function to be calculated. Do not change unless you know 
        what you are doing.
    
    Returns
    ---------- 
    result : dict
        A dictionary with the following mapping:
            "a" : The accepted samples
            "r" : The rejected samples
    '''
    likelihood_args = get_likelihood_args(data, models, guess)
    
    result = wrappers.dual_annealing(guess,     priors, 
                                     skip=fixed_parameters, bounds=bounds,  
                                     likelihood_function=likelihood_function, 
                                     likelihood_args=likelihood_args,
                                     **scipy_args,
                                     **kwargs)
    
    return result

def scipy_differential_evolution(data, models, guess, priors, 
                                 fixed_parameters, bounds, 
                                 likelihood_function=get_SSE_data,
                                 scipy_args={}):
    '''
    Wrapper for scipy's differential evolution algorithm.
    
    Parameters
    ----------
    data : dict
        Experimental data.
    models : dict
        Dictionary of model data structures.
    guess : dict, optional
        The initial guess. The default is {}.
    priors : dict, optional
        Priors if any. The default is {}.
    bounds : dict, optional
        A dictionary mapping parameter names to tuples (lower, upper). The 
        default is {}.
    fixed_parameters : list, optional
        A list of parameters that will be fixed. The default is [].
    likelihood_function : function, optional
        The likelihood function to be calculated. Do not change unless you know 
        what you are doing.
    
    Returns
    ---------- 
    result : dict
        A dictionary with the following mapping:
            "a" : The accepted samples
    '''
    if guess:
        guess1          = guess if type(guess) == dict else guess.to_dict() 
    else:
        guess1          = {key: np.mean(bounds[key]) for key in bounds}
        
    likelihood_args = get_likelihood_args(data, models, guess1)
    
    result = wrappers.differential_evolution(guess=guess1, priors=priors, skip=fixed_parameters, bounds=bounds, 
                                             likelihood_function=likelihood_function, 
                                             likelihood_args=likelihood_args, 
                                             **scipy_args)
    
    return result

###############################################################################
#Visualization
###############################################################################
#Plot everything
def plot(posterior={},   guess={},       models={},   data={}, 
         data_sd={},     plot_index={},  titles={},   labels={},
         legend_args={}, figs=[],        AX={},       palette='color',
         line_args={'linewidth': 1.5},   guess_palette='white'):
    '''
    Wrapper for plotting function for data, guess and posterior in one function call.
    '''
    first    = True
    
    if len(posterior) > 0:
        figs1, AX1 = plot_model(models, posterior, plot_index=plot_index, titles=titles, labels=labels, legend_args=legend_args, palette=palette, figs=figs, AX=AX, line_args=line_args)
        first = False

    if len(data) > 0:
        if first:
            figs1, AX1 = plot_data(data, data_sd=data_sd, plot_index=plot_index, titles=titles, labels=labels, legend_args=legend_args, palette=palette, figs=figs, AX=AX) 
            first      = False
        else:
            figs1, AX1 = plot_data(data, data_sd=data_sd, plot_index=plot_index, titles={},     labels={},     legend_args={},          palette=palette, figs=figs1, AX=AX1) 
        
    if len(guess) > 0:
        if first:
            figs1, AX1 = plot_model(models, guess, plot_index=plot_index, titles=titles, labels=labels, legend_args=legend_args, palette=guess_palette, figs=figs,  AX=AX, line_args={'linewidth':3})
            first      = False
        else:
            figs1, AX1 = plot_model(models, guess, plot_index=plot_index, titles={},     labels={},     legend_args={},          palette=guess_palette, figs=figs1, AX=AX1, line_args={'linewidth':3})  
    
    return figs1, AX1    

def plot_model(models,         params,          plot_index={}, titles=[], labels={}, 
               legend_args={}, palette='color', figs=[],       AX={},     line_args={'linewidth': 1.5}):
    '''
    Plots the models.

    Parameters
    ----------
    models : dict
        A dictionary of model data structures.
    params : pandas.DataFrame
        A DataFrame of parameter values for integration.
    plot_index : dict
        A dictionary of states and extra variables to plot.    
    titles : dict, optional
        A dictionary of axes titles. The default is {}.
    labels : TYPE, optional
        A dictionary of line labels. The default is {}.
    figs : list of matplotlib.Figure, optional
        A list of Figure objects that will be maximized after plotting. The 
        default is ().
    AX : dict of matplotlib.Axes, optional
        A dictionary of Axes objects for plotting. If {}, the Axes will be 
        automatically generated. The default is {}.
    palette : dict, optional
        A dictionary that controls the color of the plots. The default is {}.
    line_args : dict, optional
        Keyword arguments for the plot method of the Axes class. The default is 
        {}.
    legend_args : dict, optional
        Keyword arguments for controlling the appearance of the legend. The 
        default is The default is {'linewidth': 1.5}..
        
    Returns
    -------
    figs : list
        A list of Figure objects.
    AX : dict
        A dict of Axes objects.
    '''
    figs1, AX1     = (figs, AX) if AX else make_AX(plot_index=plot_index, data={})
    params_array   = params_to_array(params)
    name_to_num    = {name: num for num, name in enumerate(params)}
    params_index   = {model_num: [name_to_num[param] for param in models[model_num]['params']] for model_num in models}
    parameter_sets = len(params_array)
    colors         = make_colors(palette=palette, models=models, parameter_sets=parameter_sets)

    for model_num in AX1:
        
        model  = models[model_num]
        tspan  = get_tspan(model)
        var    = {pair[1]: pair[0] for pair in enumerate(model['states'])}
         
        for index in range(len(params_array)):
            row         = params_array[index]
            params_     = row[params_index[model_num]]
            init        = model['init']
            int_args    = model.get('int_args', {})
            
            for scenario in range(1, len(init)+1):
                label = get(labels, model_num, scenario, no_result='')
                
                if type(label) == str:
                    label = None if index != len(params_array) - 1 else label
                else:
                    label = label[index]
                
                color = colors[model_num][scenario]
                if type(color) == dict:
                    color = colors[model_num][scenario][index]

                y, t  = piecewise_integrate(model['function'], init[scenario], tspan, params_, model_num, scenario, **int_args)
                
                for state in plot_index[model_num]:
                    ax = AX1[model_num][state]
                    ax.ticklabel_format(style='sci', scilimits=(-2,3))  
                    if type(state) in [int, str, tuple]:
                        ax.plot(t, y[:,var[state]], '-', label=label, color=color, **line_args)
                        
                    else:
                        #For extra functions
                        y_, t_, marker, kwargs = extra_state(state, y, t, params_)
                        
                        if not kwargs.get('linewidth', False):
                            kwargs['linewidth'] = line_args.get('linewidth', 1.5)
                        
                        ax.plot(t_, y_, marker, label=label, color=color, **line_args)
                     
    
    [fs(fig) for fig in figs1]      
    
    apply_titles_and_legend(AX1, titles, legend_args)
    return figs1, AX1

def plot_data(data,           data_sd={},      plot_index={}, titles={}, labels={}, 
              legend_args={}, palette='color', figs=[],       AX={},     marker='+'):  
    '''
    Plots the experimental data.

    Parameters
    ----------
    data : dict
        Experimental data.
    data_sd : dict, optional
        Standard deviation of experimental data. The default is {}.
    plot_index : dict
        A dictionary of states and extra variables to plot.    
    titles : dict, optional
        A dictionary of axes titles. The default is {}.
    labels : TYPE, optional
        A dictionary of line labels. The default is {}.
    figs : list of matplotlib.Figure, optional
        A list of Figure objects that will be maximized after plotting. The 
        default is ().
    AX : dict of matplotlib.Axes, optional
        A dictionary of Axes objects for plotting. If {}, the Axes will be 
        automatically generated. The default is {}.
    palette : dict, optional
        A dictionary that controls the color of the plots. The default is {}.
    line_args : dict, optional
        Keyword arguments for the plot method of the Axes class. The default is 
        {}.
    legend_args : dict, optional
        Keyword arguments for controlling the appearance of the legend. The 
        default is The default is {'linewidth': 1.5}.
    marker : TYPE, optional
        DESCRIPTION. The default is '+'.
        
    Returns
    -------
    figs : list
        A list of Figure objects.
    AX : dict
        A dict of Axes objects.
    '''
    figs1, AX1 = (figs, AX) if AX else make_AX(plot_index=plot_index, data=data)
    colors     = make_colors(palette=palette, data=data)
    
    for model_num in AX1:
        for state in plot_index[model_num]:
            ax = get(AX1, model_num, state, no_result=None)
            ax.ticklabel_format(style='sci', scilimits=(-2,3))  
            if ax:         
                if type(state) in [int, str, tuple]:
                    state_data = get(data, model_num, state, no_result=None)
                    if not state_data:
                        continue
                    time          = state_data[0]
                    
                    for scenario in state_data:
                        if scenario > 0:
                            y     = state_data[scenario]
                            label = get(labels, model_num, scenario, no_result='')
                            
                            color = colors[model_num][scenario]
                            if type(color) == dict:
                                color = color[next(iter(color))]
                                
                            if data_sd:
                                sd = data_sd[model_num][state][scenario]
                                ax.errorbar(time, y, yerr=sd, marker=marker, linestyle='', label=label, markersize=10, markeredgewidth=2, color=color)
                            else:
                                ax.plot(time, y, marker, label=label, markersize=10, markeredgewidth=2, color=color)
            else:
                pass
    

    [fs(fig) for fig in figs1]  
    apply_titles_and_legend(AX1, titles, legend_args)
        
    return figs1, AX1

def make_AX(plot_index={}, data={}):
    '''Generates a dictionary of axes objects using either plot_index OR data.
    '''
    dataset_keys = plot_index if plot_index else {model_num: list(data[model_num].keys()) for model_num in data}
    max_len      = 0

    for model_num in dataset_keys:
        max_len = max(max_len, len(plot_index[model_num]))
    
    figs = [plt.figure() for i in range(max_len)]
    AX_  = {}
    AX   = {}
    for i in range(max_len):
        fig = figs[i]
        cols = 0
        for model_num in dataset_keys:
            try:
                key           = dataset_keys[model_num][i]
                cols += 1
            except:
                pass
        AX_[i] = [fig.add_subplot(1, cols, i+1) for i in range(cols)]
        
        c = 0
        for model_num in dataset_keys:
            try:
                key           = dataset_keys[model_num][i]
                
                if model_num not in AX:
                    AX[model_num] = {}
                    
                AX[model_num][key] = AX_[i][c]
 
                c += 1
            except:
                pass
    return figs, AX

###############################################################################
#Supporting Functions for Visualization. Do not run.
###############################################################################    
def extra_state(func, y, t, params):
    '''
    :meta private:
    '''
    #return y_, t_, marker, kwargs
    result = func(y, t, params)
    if len(result) == 2:
        return result[0], result[1], '-', {}
    elif len(result) == 3 and type(result[2]) == str:
        return result[0], result[1], result[2], {}
    elif len(result) == 3:
        return result[0], result[1], '-', result[2]
    elif len(result) == 4:
        return result
    else:
        raise Exception('Wrong output for extra state: ' + ','.join([type(x) for x in result]))

def view_palette(palette):
    '''
    :meta private:
    '''
    return sns.palplot(palette)

###############################################################################
#Color Palette Generation
###############################################################################
def make_palette(n=0, model={}, dataset={}, palette_type='color', **kwargs):
    '''
    :meta private:
    '''
    global palette_types
    global all_colors
    func = palette_types.get(palette_type)
    
    if model:
        n_scenarios = len(model['init'])
        if func:
            palette = func(n_scenarios, **kwargs)
            palette = palette
        else:
            palette = [all_colors[palette_type]]*n_scenarios
    elif dataset:
        state_data = dataset[next(iter(dataset))]
        n_scenarios = len([key for key in state_data if key > 0])

        if func:
            palette = func(n_scenarios, **kwargs)
            palette = palette
        else:
            palette = [all_colors[palette_type]]*n_scenarios
    else:
        if func:
            palette = func(n, **kwargs)
            palette = palette
        else:
            palette = [all_colors[palette_type]]*n_scenarios
            
    return palette       

def make_colors(palette, models={}, data={}, parameter_sets=0):
    '''
    :meta private:
    '''
    if type(palette) == dict:
        if type(next(iter(palette))) == int:
            #Assumes dictionary mapping
            return palette
        elif 'primary' in palette and models:
            result_ = make_colors(palette['primary'], models=models, parameter_sets=0)
            return add_secondary_palette(result_, palette['secondary'], parameter_sets)
        else:
            kwargs = palette
    elif type(palette) == str:
        kwargs = {'palette_type': palette}
    
    result = {}
    
    if models:
        for model_num in models:
            result[model_num] = {}
                    
            palette_            = make_palette(model=models[model_num], **kwargs)

            for scenario in range(1, len(models[model_num]['init'])+1):
                result[model_num][scenario] = palette_[scenario-1]
               
    if data:
        for model_num in data:
            result[model_num] = {}
            palette_            = make_palette(dataset=data[model_num], **kwargs)
            state_data       = data[model_num][next(iter(data[model_num]))]
            for scenario in state_data:
                if scenario > 0:
                    result[model_num][scenario] = palette_[scenario-1]

    return result

def add_secondary_palette(palette, secondary, parameter_sets):
    '''
    :meta private:
    '''
    kwargs = secondary.copy()
    for model_num in palette:
        for scenario in palette[model_num]:
            kwargs['color'] = palette[model_num][scenario]
        
            sec_palette                    = make_palette(n=parameter_sets, **kwargs)
            palette[model_num][scenario] = sec_palette
    return palette
      
def get(nested_dict, first_key, second_key, no_result=None):
    '''
    :meta private:
    '''
    try:
        return nested_dict[first_key][second_key]
    except:
        return no_result
    
def get_tspan(model):
    '''
    :meta private:
    '''
    result = model.get('tspan')
    if result:
        if type(result[0]) == np.ndarray:
            return result
        else:
            return np.array( [result] )
    else:
        raise Exception('Missing tspan')
        
###############################################################################
#Data Export
###############################################################################
def save_plots(file_name, figures):
    names = []
    if type(figures) == dict:
        for figure_type in figures:
            figure_name = file_name + '_' + figure_type
            if type(figures[figure_type]) == list:
                
                for figure in range(len(figures[figure_type])):
                    name = figure_name+'_'+str(figure + 1)
                    figures[figure_type][figure].savefig(name)
                    names.append(name)
            else:
                figures[figure_type].savefig(figure_name)
                names.append(figure_name)
    
    else:
        [figures[i].savefig(file_name + '_' + str(i+1)) for i in range(len(figures))]
        names = [file_name + '_' + str(i+1) for i in range(len(figures))]
    return names

###############################################################################
#Trace Handling
###############################################################################
def get_params_for_model(models, trace, model_num, row_index):
    '''
    Extracts the parameters for a particular model using the .loc method for 
    pandas.DataFrame.

    Parameters
    ----------
    models : dict
        Dictionary of model data structures.
    trace : pandas.DataFrame
        The accepted samples.
    model_num : int
        The number of the model you are interested in.
    row_index : int
        The row in the trace you want.

    Returns
    -------
    pandas.Series or pandas.DataFrame
        The parameters for the model.

    '''
    param_names = models[model_num]['params']
    return trace.loc[row_index, param_names]

# ###############################################################################
# #Setup and Working with TimeSeries
# ###############################################################################
# def extract_from_timeseries(timeseries_dict, states, init={}, keys=[], start=0, stop=None, interval=1, skip=[], subtract_blank=True, subtract_initial=False):
#     '''
#     Accepts a dict of BMSS.timeseries.timeseries objects and performs preprocessing.
#     Includes truncation, thinning, skipping variables and blank subtraction.
#     Returns a dict with arguments required for running curvefitting.
#     '''
#     CFS                  = import_timeseries(timeseries_dict, keys=keys, start=start, stop=stop, interval=interval, skip=skip, subtract_blank=subtract_blank, subtract_initial=subtract_initial)    
#     all_data             = {}
#     all_data['init']     = make_init(states=states, data_dict=CFS['mu'], init=init)
#     all_data['data']     = get_states(states=states, data_dict=CFS['data'])
#     all_data['mu']       = get_states(states=states, data_dict=CFS['mu'])
#     all_data['sd']       = get_states(states=states, data_dict=CFS['sd'])
#     all_data['tspan']    = make_tspan(data_dict = CFS['data'])
#     all_data['state_sd'] = CFS['state_sd']
    
#     return all_data

# def import_timeseries(timeseries_dict, keys=[], start=0, stop=None, interval=1, skip=[], subtract_blank=True, subtract_initial=False):
#     '''
#     Supporting function for extrac_from_timeseries. Do not run.
#     '''
#     temp            = ts.unpack(timeseries_dict, keys=keys, dtype='curvefit', start=start, stop=stop, interval=interval, skip=skip, subtract_blank=subtract_blank, subtract_initial=subtract_initial)
#     CFS             = {}
#     CFS['data']     = {state: temp[state]['data'] for state in temp}
#     CFS['mu']       = {state: temp[state]['mu'] for state in temp}
#     CFS['sd']       = {state: temp[state]['sd'] for state in temp}
#     CFS['state_sd'] = extract_state_sd(CFS['sd'])
    
#     return CFS

# def extract_state_sd(CFS_sd):
#     '''
#     Supporting function for extrac_from_timeseries. Do not run.
#     '''
#     sd = {state: np.max( [ np.max(CFS_sd[state][key]) for key in CFS_sd[state] if key > 0] ) for state in CFS_sd}
#     return sd
    
# def make_init(states, init={}, data_dict={}, width=1):
#     '''
    
#     Supporting function for extrac_from_timeseries. Do not run.
    
#     Creates a dictionary of initial values for each state.
#     If data_dict is provided, this function returns the first value of the array for each key that is more than 0. 
#     Values in init that are numbers will be concatenated to the appropriate length.
#     Values in init that are list-like will be used as-is but must be of the correct length.
#     If data_dict is not provided, width will be used to control the array size.
#     Width is ignored when data_dict is provided.
#     Values in init will always override those in data_dict.
#     '''
#     first_value = {state:[] for state in states}
#     for state in data_dict:
#         d = data_dict[state]
            
#         first_value[state] = np.array([d[key][0] for key in d if key > 0])
    
#     n = len(first_value[next(iter(first_value))]) if data_dict else width
    
#     for state in init:
#         try:
#             next(iter(init[state]))
#             first_value[state] = np.array(init[state])
#         except:
#             first_value[state] = np.array([init[state]]*n)
    
#     init_array = []
#     for state in states:
#         if len(first_value[state]) != n:
#             raise Exception('Error in ' + state + '.\nMake sure all data has the same number of scenarios.')
#         init_array.append(first_value[state])
    
#     init_array = np.array(init_array).T
#     init_dict  = {i+1: init_array[i] for i in range(len(init_array))}
#     return init_dict

# def get_states(states, data_dict):
#     '''
#     Supporting function for extrac_from_timeseries. Do not run.
#     '''
#     return {state: data_dict[state] for state in states if data_dict.get(state)}

# def make_tspan(data_dict):
#     '''
#     Supporting function for extrac_from_timeseries. Do not run.
#     '''
#     tspan = np.concatenate([data_dict[state][0] for state in data_dict])
#     return np.unique(tspan)
    
