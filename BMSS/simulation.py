import matplotlib.pyplot as plt 
import numpy             as np
import pandas            as pd
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
                 'light':     lambda n_colors, **kwargs : sns.light_palette(n_colors=n_colors+4,   **{**{'color':'steel'}, **kwargs})[4:],
                 'dark' :     lambda n_colors, **kwargs : sns.dark_palette( n_colors=n_colors+4,   **{**{'color':'steel'}, **kwargs})[4:],
                 'diverging': lambda n_colors, **kwargs : sns.diverging_palette(n=n_colors,        **{**{'h_pos': 250, 'h_neg':15}, **kwargs}),
                 'cubehelix': lambda n_colors, **kwargs : sns.cubehelix_palette(n_colors=n_colors, **kwargs),
                 }    
#Refer for details: https://xkcd.com/color/rgb/
all_colors    = sns.colors.xkcd_rgb

###############################################################################
#Integration
###############################################################################
def piecewise_integrate(function, init, tspan, params, model_num, scenario, modify_init=None, modify_params=None, solver_args={}, solver=odeint, overlap=True):
    '''
    Piecewise integration function with scipy.integrate.odeint as default. 
    Can be changed using the solver argument.
    '''

    tspan_     = tspan[0]
    init_      = modify_init(init_values=init,    params=params, model_num=model_num, scenario=scenario, segment=0) if modify_init   else init
    params_    = modify_params(init_values=init_, params=params, model_num=model_num, scenario=scenario, segment=0) if modify_params else params 
    y_model    = solver(function, init_, tspan_, args=tuple([params_]), **solver_args)
    t_model    = tspan[0]
    
    for segment in range(1, len(tspan)):
        tspan_   = tspan[segment]
        init_    = modify_init(init_values=y_model[-1], params=params, model_num=model_num, scenario=scenario, segment=segment) if modify_init   else y_model[-1]
        params_  = modify_params(init_values=init_,     params=params, model_num=model_num, scenario=scenario, segment=segment) if modify_params else params 
        y_model_ = solver(function, init_, tspan_, args=tuple([params_]), **solver_args)       
        y_model  = np.concatenate((y_model, y_model_), axis=0) if overlap else np.concatenate((y_model[:-1],  y_model_), axis=0)   
        t_model  = np.concatenate((t_model, tspan_), axis=0)   if overlap else np.concatenate((t_model[:,-1], tspan_),   axis=0)

    return y_model, t_model

#Templates for modify_init
def modify_init(init_values, params, model_num, scenario, segment):
    '''
    Return a new np.array of initial values. For safety, DO NOT MODIFY IN PLACE.
    '''
    return init_values.copy()

def modify_params(init_values, params, model_num, scenario, segment):
    '''
    Return a new np.array of initial values. For safety, DO NOT MODIFY IN PLACE.
    '''
    return params.copy()

###############################################################################
#Multi-Model Integration
###############################################################################
def integrate_models(models, params, *extra_variables, overlap=True):
    y_models = {}
    t_models = {}
    e_models = {v: {model_num: {scenario: {} for scenario in models[model_num]['init']} for model_num in models} for v in extra_variables}
    
    
    if type(params) == dict:
        try: 
            params_ = pd.DataFrame(params)
        except:
            params_ = pd.DataFrame([params])

        return integrate_models(models, params_, *extra_variables, overlap=overlap)
    
    if len(params.shape) == 1:
        return integrate_models(models, np.array([params]), *extra_variables, overlap=overlap)
    
    else:
        params1 = pd.DataFrame(params)
        for model_num in models:
            model               = models[model_num]
            y_models[model_num] = {}
            
            for scenario in models[model_num]['init']:
                if type(scenario) == int:
                    if scenario < 1:
                        continue
                y_models[model_num][scenario] = {}
                
                for name, row in params1.iterrows():
                    y_model, t_model = piecewise_integrate(params        = row.values,
                                                           function      = model['function'], 
                                                           init          = model['init'][scenario],
                                                           tspan         = model['tspan'],
                                                           modify_init   = model['int_args']['modify_init'],
                                                           modify_params = model['int_args']['modify_params'],
                                                           solver_args   = model['int_args']['solver_args'],
                                                           model_num     = model_num, 
                                                           scenario      = scenario, 
                                                           overlap       = overlap,
                                                           )
                    y_models[model_num][scenario][name] = y_model
                    
                    
                    for func in extra_variables:
                        variable = func(y_model, t_model, row.values)
                        e_models[func][model_num][scenario][name] = variable 
                        
                        
            y_models[model_num][0] = t_model
        
        return y_models, e_models

###############################################################################
#Plot
###############################################################################
def plot_model(plot_index, y, e={}, titles={}, labels={}, figs=[], AX={}, palette={}, line_args={}, legend_args={}):
    
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
                    color = colors[model_num][scenario_num][row_name]
                    x_arr = e[state][model_num][scenario_num][row_name][1] if callable(state) else y[model_num][0] 
                    y_arr = e[state][model_num][scenario_num][row_name][0] if callable(state) else y[model_num][scenario_num][row_name]
                    label = get_label(labels, model_num, scenario_num, first=first, row_name=row_name)
                    
                    ax.plot(x_arr, y_arr, label=label, color=color, **line_args)
                    
                    first = False

    [fs(fig) for fig in figs1]
    apply_titles_and_legend(AX1, titles, legend_args)
                
    return figs1, AX1 

###############################################################################
#Supporting Functions. Do not run.
############################################################################### 
def get_label(labels, model_num, scenario_num, first, row_name=None):

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
    for model_num in AX:
        for state in AX[model_num]:
            ax    = AX[model_num][state]
            ax.legend(**legend_args)
            ax.set_title(titles.get(model_num, {}).get(state, ''))
    # [AX[model_num][state].set_title(titles.get(model_num, {}).get(state, '')) for model_num in AX for state in AX[model_num]]

def fs(figure):
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
    
if __name__ == '__main__':
    pass