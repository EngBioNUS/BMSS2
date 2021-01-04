import matplotlib.pyplot as plt
import numpy             as np
import pandas            as pd
import seaborn           as sns
from matplotlib          import get_backend
from scipy.stats         import skewtest, kurtosistest

###############################################################################
#Globals
###############################################################################
#Refer for details: https://seaborn.pydata.org/tutorial/color_palettes.html
palette_types = {'color':     lambda n_colors, palette='bright', **kwargs : sns.color_palette(palette=palette, n_colors=n_colors),
                 'light':     lambda n_colors, color, **kwargs            : sns.light_palette(n_colors=n_colors+2, color=color, **kwargs)[2:],
                 'dark' :     lambda n_colors, color, **kwargs            : sns.dark_palette( n_colors=n_colors+2, color=color, **kwargs)[2:],
                 'cubehelix': lambda n_colors, **kwargs                   : sns.cubehelix_palette(n_colors=n_colors, **kwargs),
                 'diverging': lambda n, **kwargs                          : sns.diverging_palette(n=n, **kwargs),
                 }    
#Refer for details: https://xkcd.com/color/rgb/
all_colors    = sns.colors.xkcd_rgb

###############################################################################
#Import
###############################################################################
def import_trace(files, keys=[], **pd_args):
    data   = {}
    for i in range(len(files)):
        key       = keys[i+1] if keys else i+1
        data[key] = pd.read_csv(files[i],  **pd_args)
    return data    

###############################################################################
#Skewness and Kurtosis
###############################################################################
def check_skewness(traces, output='df'):
    return scipy_test(skewtest, traces, output='df')

def check_kurtosis(traces, output='df'):
    return scipy_test(kurtosistest, traces, output='df')

def scipy_test(test_func, traces, output='df'):
    result    = {}
    for label in traces:
        trace       = traces[label]
        test_result = test_func(trace, axis=0, nan_policy='omit')
        
        if output == 'df':
            variables     = trace.columns.to_list()
            df            = pd.DataFrame( test_result, columns=variables, index=('stats', 'pval'))
            result[label] = df
        else:
            result[label] = test_result
    
    return result
        
###############################################################################
#Wrapper Functions for Bivariate Plots
###############################################################################
def pairplot_steps(traces, pairs, figs=[], AX={}, gradient=5, palette={}, legend_args={}, plot_args={'marker': '+', 'linewidth':0}, palette_type='light'):
    return pairplot_wrapper('plot', traces=traces, pairs=pairs, figs=figs, AX=AX, palette=palette, gradient=gradient, palette_type=palette_type, legend_args=legend_args, plot_args=plot_args)

def pairplot_kde(traces, pairs, figs=[], AX={}, palette={}, legend_args={}, plot_args={}):
    return pairplot_wrapper('kde', traces=traces, pairs=pairs, figs=figs, AX=AX, palette=palette, gradient=1, palette_type='light', legend_args=legend_args, plot_args=plot_args)

def pairplot_wrapper(plot_func, traces, pairs, figs=[], AX={}, palette={}, gradient=1, palette_type='light', legend_args={}, plot_args={}):
    pairs1       = [tuple(pair) for pair in pairs]
    palette1     = make_palette(traces, pairs1, palette, gradient=gradient, palette_type=palette_type)
    figs1, AX1   = figs, AX
    
    for label in traces:
        figs1, AX1 = plot_helper(plot_func, label, traces[label], pairs1, figs=figs1, AX=AX1, palette=palette1[label], legend_args=legend_args, plot_args=plot_args)
    
    [fs(fig) for fig in figs1]
    
    return figs1, AX1
    
###############################################################################
#Wrapper Functions for Univariate Plots
###############################################################################    
def plot_steps(traces, skip=[], figs=[], AX={}, palette={}, legend_args={}, plot_args={'marker': '+', 'linewidth':0}):
    return singleplot_wrapper('plot', traces, skip=skip, figs=figs, AX=AX, palette=palette, legend_args=legend_args, plot_args=plot_args)
    
def plot_kde(traces, skip=[], figs=[], AX={}, palette={}, legend_args={}, plot_args={'linewidth': 3}):
    return singleplot_wrapper('kde', traces, skip=skip, figs=figs, AX=AX, palette=palette, legend_args=legend_args, plot_args=plot_args)
    
def plot_hist(traces, skip=[], figs=[], AX={}, palette={}, legend_args={}, plot_args={}):
    return singleplot_wrapper('hist', traces, skip=skip, figs=figs, AX=AX, palette=palette, legend_args=legend_args, plot_args=plot_args)
    
def singleplot_wrapper(plot_func, traces, skip=[], figs=[], AX={}, palette={}, legend_args={}, plot_args={}):
    figs1, AX1, variables, first_label = setup_singleplot(traces, skip, figs, AX)
    palette1                           = make_palette(traces, variables, palette)
    legend_args1                       = legend_args if AX else {'labels': []}
    
    for label in traces:
        figs1, AX1 = plot_helper(plot_func, label, traces[label], variables, figs=figs1, AX=AX1, palette=palette1[label], legend_args=legend_args1, plot_args=plot_args)
    
    [fs(fig) for fig in figs1]
    
    if not AX:
        AX1[next(iter(AX1))].legend(**legend_args)
    return figs1, AX1

###############################################################################
#Supporting Functions for Wrapping
###############################################################################
def setup_singleplot(traces, skip, figs, AX):
    first_label = next(iter(traces))
    variables   = [variable for variable in traces[first_label].columns.to_list() if variable not in skip]
    n           = len(variables)
    
    figs1 = figs if AX else [plt.figure()]
    if AX:
        AX1   = AX  
    else:
        AX1 = {variables[i]: figs1[0].add_subplot(n//2 + n%2, 2, i+1) for i in range(len(variables))}
    
    return figs1, AX1, variables, first_label

def make_palette(traces, variables, palette, gradient=1, palette_type='light'):
    global palette_types
    if palette:
        if type(palette[next(iter(palette))]) == dict:
            #Assume colors have been fully specified
            palette1 = palette
        else:
            #Assume colors for each trace has been specified
            palette1 = {}
            for label in palette:
                base_color = palette[label]
                colors     = palette_types[palette_type](gradient, base_color)
                palette1[label] = {variable: colors for variable in variables}
                
    else:
        base_colors = palette_types['color'](len(traces), 'muted')
    
        palette1 = {}
        labels   = list(traces.keys())
        for i in range(len(labels)):
            label           = labels[i] if type(labels[i]) != list else tuple(labels[i])
            base_color      = base_colors[i]
            colors          = palette_types[palette_type](gradient, base_color)
            palette1[label] = {variable: colors for variable in variables}
    
    return palette1

###############################################################################
#Main Plotting
###############################################################################
def plot_helper(plot_func, label, trace, variables, figs=[], AX={}, palette={}, legend_args={}, plot_args={}):
    n     = len(variables)    
    figs1 = figs if AX else [plt.figure()                              for i in range(n)]
    AX1   = AX   if AX else {variables[i]: figs1[i].add_subplot(1,1,1) for i in range(n)}

    lines = []
    for i in range(len(variables)):
        
        if type(variables[i]) == str:
            vx, vy = None, variables[i]
        else:
            vx, vy = variables[i]
            
        ax = AX1[variables[i]]
        ax.set(xlabel=vx, ylabel=vy)
        ax.ticklabel_format(style='sci', scilimits=(-2,3))
        
        colors = palette.get(variables[i], [all_colors['baby blue']])
        x      = np.array_split(trace[vx], len(colors)) if vx else [[]]*len(colors)
        y      = np.array_split(trace[vy], len(colors))

        mapped_lines   = [axis_plot(ax, plot_func, x=x[i], y=y[i], color=colors[i],  label=label if i==len(colors)-1 else '_nolabel',**plot_args) for i in range(len(colors))]

        lines.append(mapped_lines[-1])
    
    if legend_args: 
        try:
            if len(legend_args.get('labels', [])):
                legend_args['handles'] = lines
            for key in AX1:
                AX1[key].legend(**legend_args)
        except:
            pass
    return figs1, AX1

def axis_plot(ax, func, x, y, *args, **kwargs):
    if func == 'plot':      
        if len(x):
            ax.plot(x, y, *args, **kwargs)
        else:
            ax.plot(y, *args, **kwargs)
    elif func == 'hist':
        ax.hist(y, *args, **kwargs)
    elif func == 'kde':
        if len(x):
            sns.kdeplot(data=y, data2=x, *args, ax=ax, **kwargs)
        else:
            sns.kdeplot(y, *args, ax=ax, **kwargs)
    return

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