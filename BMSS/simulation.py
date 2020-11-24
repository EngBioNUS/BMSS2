import matplotlib.pyplot as plt 
import numpy             as np
import os
import pandas            as pd
import re
import seaborn           as sns
from matplotlib          import get_backend
from numba               import jit
from scipy.integrate     import odeint

from numba import jit

###############################################################################
#Globals
###############################################################################
#Refer for details: https://seaborn.pydata.org/tutorial/color_palettes.html
palette_types = {'color':     lambda n_colors, **kwargs : sns.color_palette(n_colors=n_colors,     **{**{'palette': 'muted'}, **kwargs}),
                 'light':     lambda n_colors, **kwargs : sns.light_palette(n_colors=n_colors+2,   **{**{'color':'steel'}, **kwargs})[2:],
                 'dark' :     lambda n_colors, **kwargs : sns.dark_palette( n_colors=n_colors+2,   **{**{'color':'steel'}, **kwargs})[2:],
                 'diverging': lambda n_colors, **kwargs : sns.diverging_palette(n=n_colors,        **{**{'h_pos': 250, 'h_neg':15}, **kwargs}),
                 'cubehelix': lambda n_colors, **kwargs : sns.cubehelix_palette(n_colors=n_colors, **kwargs),
                 }    
#Refer for details: https://xkcd.com/color/rgb/
all_colors    = sns.colors.xkcd_rgb

###############################################################################
#Integration
###############################################################################
def piecewise_integrate(function, init, tspan, params, model_num, scenario_num, modify_init=None, modify_params=None, solver_args={}, solver=odeint, overlap=True, args=()):
    '''Piecewise integration function with scipy.integrate.odeint as default. 
    Can be changed using the solver argument.

    Parameters
    ----------
    function : function
        A function for numerical integration that takes in the form f(states, 
        time, params, args). states, params and args are numpy arrays while time 
        is a float or numpy float. Will be integrated using scipy.integrate.odeint
    init : numpy.array
        Initial values of states for numerical integration.
    tspan : list of numpy.array
        Segments for piecewise integration where each segment is a numpy array of 
        time points in ascending order.
    params : numpy.array
        An array of parameter values.
    model_num : int
        Number of the model.
    scenario_num : int
        Number of the scenario.
    modify_init : function, optional
        Function for modifying initial values before integrating over a time 
        segment. The default is None.
    modify_params : function, optional
        Function for modifying parameter values before integrating over a time 
        segment. The default is None.
    solver_args : dict, optional
        Dictionary of keyword arguments for scipy.integrate.odeint. The default is {}.
    solver : scipy.integrate.odeint, optional
        The integrating function. The default is odeint. Do not touch unless you 
        know what you are doing.
    overlap : bool, optional
        Avoids double counting between segments. In general, False is required 
        only for plotting. The default is True.
    args : tuple, optional
        A tuple of arguments. The default is ().

    Returns
    -------
    y_model : numpy.array
        An array of values from numerical integration.
    t_model : numpy.array
        An array of time points.

    '''
    solver_args1 = solver_args if solver_args else {}
    
    tspan_     = tspan[0]
    init_      = modify_init(init_values=init,    params=params, model_num=model_num, scenario_num=scenario_num, segment=0) if modify_init   else init
    params_    = modify_params(init_values=init_, params=params, model_num=model_num, scenario_num=scenario_num, segment=0) if modify_params else params 
    y_model    = solver(function, init_, tspan_, args=tuple([params_]) + args, **solver_args1)
    t_model    = tspan[0]
    
    for segment in range(1, len(tspan)):
        tspan_   = tspan[segment]
        init_    = modify_init(init_values=y_model[-1], params=params, model_num=model_num, scenario_num=scenario_num, segment=segment) if modify_init   else y_model[-1]
        params_  = modify_params(init_values=init_,     params=params, model_num=model_num, scenario_num=scenario_num, segment=segment) if modify_params else params 
        y_model_ = solver(function, init_, tspan_, args=tuple([params_]) + args, **solver_args1)       
        y_model  = np.concatenate((y_model, y_model_), axis=0) if overlap else np.concatenate((y_model[:-1],  y_model_), axis=0)   
        t_model  = np.concatenate((t_model, tspan_), axis=0)   if overlap else np.concatenate((t_model[:,-1], tspan_),   axis=0)

    return y_model, t_model

#Templates for modify_init
def modify_init(init_values, params, model_num, scenario_num, segment):
    '''
    Return a new np.array of initial values. For safety, DO NOT MODIFY IN PLACE.
    
    :meta private:
    '''
    new_init = init_values.copy()
    return new_init

def modify_params(init_values, params, model_num, scenario_num, segment):
    '''
    Return a new np.array of initial values. For safety, DO NOT MODIFY IN PLACE.
    
    :meta private:
    '''
    new_params = params.copy()
    return new_params

###############################################################################
#Multi-Model Integration
###############################################################################
def integrate_models(models, params, *extra_variables, args=(), mode='np', overlap=True):
    '''Integrates models with params    

    Parameters
    ----------
    models : dict
        A dictionary of model data structures.
    params : pandas.DataFrame
        A DataFrame of parameter values for integration.
    *extra_variables : function
        Additional functions for evaluating the integrated results.
    args : tuple, optional
        Additional arguments for the functions to be integrated. The default is ().
    mode : {'np', 'df'}, optional
        Use 'np' if the functions in extra_variables are meant to work with numpy 
        arrays and 'pd' if functions are meant to work with DataFrames. The 
        default is 'np'.
    overlap : TYPE, optional
        DESCRIPTION. The default is True.

    Returns
    -------
    dict
        A dictionary of the integrated results.
    dict
        A dictionary of the calculated extra variables.
    '''
    print('Simulating models')
    y_models = {}
    e_models = {v: {model_num: {scenario_num: {} for scenario_num in models[model_num]['init']} for model_num in models} for v in extra_variables}
    
    
    if type(params) == dict:
        try: 
            params_ = pd.DataFrame(params)
        except:
            params_ = pd.DataFrame([params])

        return integrate_models(models, params_, *extra_variables, args=args, overlap=overlap)
    
    if len(params.shape) == 1:
        return integrate_models(models, np.array([params]), *extra_variables, args=args, overlap=overlap)
    
    else:
        for model_num in models:
            model               = models[model_num]
            param_names         = model['params']
            params1             = params[param_names]
            y_models[model_num] = {}
            
            for scenario_num in models[model_num]['init']:
                if type(scenario_num) == int:
                    if scenario_num < 1:
                        continue
                y_models[model_num][scenario_num] = {}
                
                for name, row in params1.iterrows():
                    y_model, t_model = piecewise_integrate(params        = row.values,
                                                           function      = model['function'], 
                                                           init          = model['init'][scenario_num],
                                                           tspan         = model['tspan'],
                                                           modify_init   = model['int_args']['modify_init'],
                                                           modify_params = model['int_args']['modify_params'],
                                                           solver_args   = model['int_args']['solver_args'],
                                                           model_num     = model_num, 
                                                           scenario_num  = scenario_num, 
                                                           overlap       = overlap,
                                                           args          = args
                                                           )
                    y_models[model_num][scenario_num][name] = pd.DataFrame(y_model, columns=models[model_num]['states'])
                    
                    
                    for func in extra_variables:
                        y_model_ = y_models[model_num][scenario_num][name] if mode == 'pd' else y_model
                        variable = func(y_model_, t_model, row.values)
                        e_models[func][model_num][scenario_num][name] = variable 
                                       
            y_models[model_num][0] = t_model
        
        print('Simulation complete')
        return y_models, e_models

###############################################################################
#Plot
###############################################################################
def plot_model(plot_index, y, e={}, titles={}, labels={}, figs=(), AX={}, palette={}, line_args={}, legend_args={}):
    '''Plots the integrated results.

    Parameters
    ----------
    plot_index : dict
        A dictionary of states and extra variables to plot.
    y : dict
        The values of the integrated results from integrate_models.
    e : dict, optional
        The values of the integrated results from integrate_models. The default 
        is {}.
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
        default is {}.

    Returns
    -------
    figs : list
        A list of Figure objects.
    AX : dict
        A dict of Axes objects.

    '''
    figs1, AX1 = (figs, AX) if AX else make_AX(plot_index)
    palette1   = palette if palette else {'palette_type': 'color'}
    colors     = make_colors_from_simulation(y, e, palette1)

    for model_num in plot_index:
        for state in plot_index[model_num]:
            try:
                ax = AX1[model_num][state]
            except:
                raise Exception('No Axes provided for state ' + str(state) + ' in model ' + str(model_num) +'.')
            
            if callable(state):
                temp = e[state]
            else:       
                temp = y
                
            for scenario_num in temp[model_num]:
                if scenario_num < 1:
                    continue
                
                first=True
                for row_name in temp[model_num][scenario_num]:
                    color = colors[model_num][scenario_num]
                    if type(color) == dict:
                        color = color[row_name]                        
                    x_arr = e[state][model_num][scenario_num][row_name][1] if callable(state) else y[model_num][0] 
                    y_arr = e[state][model_num][scenario_num][row_name][0] if callable(state) else y[model_num][scenario_num][row_name][state]
                    label = get_label(labels, model_num, scenario_num, first=first, row_name=row_name)
                    
                    ax.plot(x_arr, y_arr, label=label, color=color, **line_args)
                    ax.ticklabel_format(style='sci', scilimits=(-2,3))
                    
                    first = False

    [fs(fig) for fig in figs1]
    apply_titles_and_legend(AX1, titles, legend_args)
                
    return figs1, AX1 

###############################################################################
#Supporting Functions. Do not run.
############################################################################### 
def get_label(labels, model_num, scenario_num, first, row_name=None):
    '''
    :meta private:
    '''
    if row_name is None:
        label = labels.get(model_num, {}).get(scenario_num, '')
    else:
        label = labels.get(model_num, {}).get(scenario_num, {})
        
        if type(label) == str:
            if not first:
                label = None
        else:
            try:
                label = label[row_name]
            except:
                if not first:
                    label = None
        
    return label

def apply_titles_and_legend(AX, titles, legend_args):
    '''
    :meta private:
    '''
    for model_num in AX:
        for state in AX[model_num]:
            ax    = AX[model_num][state]
            title = titles.get(model_num, {}).get(state, '')
            if title:
                ax.set_title(title)
            if legend_args:
                ax.legend(**legend_args)    
    
def fs(figure):
    '''
    :meta private:
    '''
    try:
        plt.figure(figure.number)
        backend   = get_backend()
        manager   = plt.get_current_fig_manager()
        
        if backend == 'TkAgg':
            manager.resize(*manager.window.maxsize())
        
        elif backend == 'Qt5Agg' or backend == 'Qt4Agg': 
            manager.window.showMaximized()
        
        else:
            manager.frame.Maximize(True)
        plt.pause(0.03)
    except:
        pass
    return figure

###############################################################################
#Color Generation
###############################################################################    
def make_colors_from_simulation(y, e={}, palette={'palette_type': 'color'}):
    '''
    :meta private:
    '''
    global palette_types
    global all_colors
    
    if type(palette[next(iter(palette))]) == dict: #Assume full dict in this case
        return palette
    
    scenario_names = set()
    tree           = {}
    def counter(y):
        for model_num in y:
            if model_num not in tree:
                tree[model_num] = {}
            for scenario_num in y[model_num]:
                if scenario_num > 0:
                    scenario_names.add(scenario_num)
                    if scenario_num not in tree[model_num]:
                        tree[model_num][scenario_num] = set()
                    tree[model_num][scenario_num].update([name for name in list(y[model_num][scenario_num].keys())]) 
                    
    
    counter(y), [counter(e[func]) for func in e]
    
    n_scenarios = len(scenario_names)
    
    func   = palette_types[palette['palette_type']]
    kwargs = {key: palette[key] for key in palette if key != 'secondary' and key != 'palette_type'}
    
    if 'color' in kwargs:
        try:
            kwargs['color'] = all_colors[kwargs['color']]
        except:
            pass
        
    base_colors = dict(zip(scenario_names, func(n_scenarios, **kwargs)))
    
    colors = {}
    if 'secondary' in palette:
        func   = palette_types[palette['secondary']]
        colors = {m: {s: dict(zip(tree[m][s], func(len(tree[m][s]), color=base_colors[s])))  for s in tree[m]} for m in tree}        
    else:
        colors = {m: {s: {r : base_colors[s] for r in tree[m][s]}  for s in tree[m]} for m in tree}        
        
    return colors
         
 
###############################################################################
#Axes Generation
###############################################################################
def make_AX(plot_index={}, data={}):
    '''
    Generates a dictionary of axes objects using either plot_index OR data.
    
    :meta: private
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

def export_simulation_results(y, e, prefix='', directory=None):
    '''Save the simulation results in csv format.

    Parameters
    ----------
    y : dict
        The simulation results returned by integrate_models.
    e : dict
        The simulation results for the extra variabes returned by integrate_models.
    prefix : str, optional
        A prefix for each file generated. The default is ''.
    directory : TYPE, optional
        The directory for storing the exported files. The default is None.

    Returns
    -------
    results : list
        Names of files generated.

    '''
    results = []
    
    if directory:
        cwd = os.getcwd()
        try:
            os.mkdir(directory)
        except:
            pass
        os.chdir(directory)
        
    for model_num in y:
        time = y[model_num][0]
        for scenario_num in y[model_num]:
            if scenario_num < 1:
                continue
            for row_name in y[model_num][scenario_num]:
                filename = '_'.join(['y', str(model_num), str(scenario_num), str(row_name)]) + '.csv'
                filename = prefix + '_' + filename if prefix else filename
                table    = y[model_num][scenario_num][row_name]
                table.insert(0, 'Time', value=time)
                table.to_csv(filename)
                
                results.append(filename)
    
    for func in e:
        doc     = func.__doc__
        columns = search_string_for_x_y(doc)
        columns = columns['x'], columns['y']
        for model_num in e[func]:
            for scenario_num in e[func][model_num]:
                if scenario_num < 1:
                    continue
                for row_name in e[func][model_num][scenario_num]:
                    y, x, _  = e[func][model_num][scenario_num][row_name]
                    table    = pd.DataFrame(np.stack((x,y), axis=1), columns=['x', 'y'])
                    filename = '_'.join([func.__name__, str(model_num), str(scenario_num), str(row_name)]) + '.csv'
                    filename = prefix + '_' + filename if prefix else filename
                    table.to_csv(filename)
                    
                    results.append(filename)
    
    if directory:
        os.chdir(cwd)

    return results

def search_string_for_x_y(string):
    '''
    :meta private:
    '''
    result = {'x' :'x',
              'y' :'y'
              }
    if not string:
        return result
    
    for key in ['x', 'y']:
        
        match = re.search('(?<=' + key + '=).*', string)
        if not match:
            pattern = re.search(key + '(\s+)*=', string)
            if pattern:
                pattern = '(?<=' + pattern + ').*'
                match   = re.search(pattern, string)

        if match:
            result[key] = match[0].strip()
        
    return result  
  
if __name__ == '__main__':
    pass