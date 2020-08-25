"""
Created on 2020

@author: jingwui

This module contains all the functions for running combinatorial study. 
"""

import os
import copy
import numpy as np
import itertools
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import inspect
from scipy.integrate import odeint, ode
from SALib.analyze import sobol, fast, rbd_fast, delta
from SALib.sample import saltelli, fast_sampler, latin

#from access_pubchem import access_pubchem
try:
    from .plotfig import plotfig, heatmap, S2heatmap
except:
    from plotfig import plotfig, heatmap, S2heatmap 

plt.close('all')

matplotlib.use("Qt5Agg")


def convert_dfstrtovalue(dfstr, optiondict):
    '''convert the dataframe in string to their relative strength values.'''
    dfstrtmp = dfstr.copy()
    dfstrtmp = dfstrtmp.replace(optiondict)
    
    return dfstrtmp


def mergedicts(dictlist):
    '''Merge list of dictionaries.'''
    outputdict = {}
    for i in dictlist:
        outputdict.update(i)
        
    return outputdict


def search_matchcolumns(df, columnlist, valuelist):
    '''return the df rows that match the list of columns with the list of
    values.'''
    listtmp = [c + '==' + "'" +valuelist[i]+"'" for i, c in enumerate(columnlist)]
    querystr = ' & '.join(listtmp)
    print(querystr)
    
    dfoutput = df.query(querystr)
    
    return dfoutput
        

def plot_relative_strength(partdict_dict, filepath, **kwargs):
    '''Plot the heatmaps of multiple input relative stength in list,
    and export as png.'''
    figsize = (5,4)
    font_scale = 1.4
    
    if 'figsize' in kwargs:
        figsize = kwargs.get('figsize')
    if 'font_scale' in kwargs:
        font_scale = kwargs.get('font_scale')
    
    xylabels = ['','']
    
    for o, p in partdict_dict.items():
        heatmap([], np.array(list(p.values())).reshape(-1,1), xylabels,\
                xyticklabels = ['', list(p.keys())], \
                savefig = os.path.join(filepath, o+'_RelativeStrength.png'),\
                figsize = figsize, font_scale=font_scale)


def retrieve_name(var):
    '''Return the name of variable as string.'''
    callers_local_vars = inspect.currentframe().f_back.f_locals.items()
    varlist = [var_name for var_name, var_val in callers_local_vars if var_val is var]
    
    return varlist[0]  

    
def run_sensitivity_analysis(problem, odefun, y0, tspan, params,\
                             stateevent = {}, paramevent = {},\
                             method = 'sobol', **kwargs):
    '''Run sensitivity analysis and plot the heatmaps based on the solutions.
        problem: problem definitions
            example: problem = {
                        'num_vars': 3,
                        'names':['x1', 'x2', 'x3'],
                        'bounds': [[0, 1], [0, 10], [5, 100]]
                    }
        odefun: ODE function
        y0: list of initial values for states for solving the ODEs
        tspan: an array of time points for solving the ODEs
        stateevent: dict specifying the state events for solving ODEs
            key: Time, State
            value: list of time points, list of dicts containing state's index
            and the corresponding value.
        method: 'sobol', 'fast', 'RBD-FAST', 'delta'
    '''
    sampling = 1000
    
    cmap = 'Greens' #'Reds'
    
    if 'sampling' in kwargs:
        sampling = kwargs.get('sampling')
        
    if 'cmap' in kwargs:
        cmap = kwargs.get('cmap')
    
    SAmethod = {
            'sobol':
                {'sample': lambda problem, sampling: saltelli.sample(problem, sampling),\
                 'analyze': lambda problem, Y, print_to_console: sobol.analyze(problem, Y, print_to_console=True),
                 'plot': {'S1': ['S1', 'S1_conf', 'ST', 'ST_conf'], 'S2': ['S2', 'S2_conf']}},
            'fast':
                {'sample': lambda problem, sampling: fast_sampler.sample(problem, sampling),\
                 'analyze': lambda problem, Y, print_to_console: fast.analyze(problem, Y, print_to_console=True),
                 'plot': {'S1': ['S1', 'ST']}},
            'RBD-FAST':
                {'sample': lambda problem, sampling: latin.sample(problem, sampling),\
                 'analyze': lambda problem, param_values, Y, print_to_console: rbd_fast.analyze(problem, param_values, Y, print_to_console=False),
                 'plot': {'S1': ['S1']}},
            'delta':
                {'sample': lambda problem, sampling: latin.sample(problem, sampling),\
                 'analyze': lambda problem, param_values, Y, print_to_console: delta.analyze(problem, param_values, Y, print_to_console=False),
                 'plot': {'S1': ['delta', 'delta_conf', 'S1', 'S1_conf']}}}
    
    if method in SAmethod:
        param_values = SAmethod[method]['sample'](problem, sampling)
    
        Y = np.zeros((param_values.shape[0]))
        
        for i, x in enumerate(param_values):
            #sol = solveODE(odefun, y0, tspan, args = (x, ))
            sol = solveODE_event(odefun, y0, tspan, args = (params, x),\
                                 stateevent = stateevent, paramevent = paramevent)
            Y[i] = sol[-1,-1]
        
        if (method == 'RBD-FAST') or (method == 'delta'):
            Si = SAmethod[method]['analyze'](problem, param_values, Y, print_to_console=True)
        else:
            Si = SAmethod[method]['analyze'](problem, Y, print_to_console=True)
    
    S1 = []
    for i in SAmethod[method]['plot']['S1']:
        S1.append(Si[i])
        
    S1 = np.array(S1).T
    
    xlabels = SAmethod[method]['plot']['S1']
    ylabels = problem['names']
    
    # plot the first-order sensitivities
    heatmap([], S1, ['Sensitivity Analysis','Parameter'], [xlabels, ylabels],\
            cmap = cmap, figsize = (10, 6))
    
    if 'S2' in SAmethod[method]['plot']:
        S2data = Si['S2']
        S2CIdata = Si['S2_conf']
        xylabels = ['Parameter', 'Parameter']
        
        # plot the second-order sensitivities
        S2heatmap([], S2data, S2CIdata, xylabels, ylabels)
    
    return Si


def create_jointplot(df, y, kind = 'reg', savefig = False, filepath = '',\
                     color = "skyblue"):
    '''Create joint plot for each column of dataframe as x-axis,
    and same y for the y-axis in separate figures.
    kind = 'reg': regression and kernel density fits
           'kde': density estimates.
    '''
    #sns.set(rc={'figure.figsize':(6.0, 8.0)})
    for p in list(df):
        try:
            jp = sns.jointplot(x=df[p], y=y, kind='reg',\
                               color=color, ratio = 2)
        except np.linalg.LinAlgError as err:
            if 'Singular matrix' in str(err):
                print('Warning:', p, 'is singular matrix')
                pass
        if savefig:
            jp.savefig(os.path.join(filepath, 'jointplot_'+p+'_scat.jpg'))


def plot_compounds(Time, soldict, indexlist, compoundlist, xylabels,\
                   figureopt = 'per_index', ax = None, **kwargs):
    '''Plot the time-response profiles of compounds in the form of either
    all compound profiles based on index or the profiles for all indexes
    based on compound, in separate figures. The interested lists of indexes and
    compounds are to be provided as input arguments.'''
    
    ax = ax.flatten() if not ax is None else None
    
    if figureopt == 'per_index':
        for m, i in enumerate(indexlist):
            axs = ax[m] if not ax is None else None
            yarray = np.array([soldict[i][compound] for compound in compoundlist]).T
            plotfig('index '+str(i)+str([f[0] for f in compoundlist]), Time,\
                    yarray, xylabels, compoundlist, ax = axs, **kwargs)
        
    elif figureopt == 'per_compound':
        for n, c in enumerate(compoundlist):
            axs = ax[n] if not ax is None else None
            yarray = np.array([soldict[i][c] for i in indexlist]).T
            plotfig(c, Time, yarray, xylabels, indexlist, ax = axs, **kwargs)
    
    else:
        raise Exception('Please enter the correct figure option.')


def get_combinations(optionsdict):
    '''Return two dataframes: one contains the different combinations based on
    part names, the other contains the different combinations with their relative
    strengths.'''
    optiondicttemp = {}
    # to convert the nested dict to list for generating combinations
    for key, value in optionsdict.items():
        optiondicttemp[key] = list(value.keys())
    
    # generate combinations based on the names
    keys, values = zip(*optiondicttemp.items())
    combinations_str = [dict(zip(keys, combination)) for combination in itertools.product(*values)]
    
    # convert the list of dicts to dataframe
    column = list(combinations_str[0].keys())
    dfcombinations_str = pd.DataFrame(data=combinations_str, columns = column)
    
    # generate combinations based on the values for simulations
    combinations_val = {}
    #for index, row in dfcombinations_str.head().iterrows():
    for index, row in dfcombinations_str.iterrows():
        templist = []
        for k, v in optionsdict.items():
            templist.append(v.get(row[k]))
            combinations_val[index] = templist
            
    # convert the dict of lists to dataframe
    dfcombinations_val = pd.DataFrame.from_dict(combinations_val,\
                                                orient = 'index',\
                                                columns = column)

    return dfcombinations_str, dfcombinations_val


def solve_combinations(dfcombinations_val, ODEfun, states, y0, tspan, params,\
                       stateevent = {}, paramevent={}):
    '''Return a nested dict with combinational indexes as keys, the names of compounds
    as subkeys, and their corresponding time-response data as values'''
    comb = []
    for row in dfcombinations_val.itertuples():
        comb.append(list(row))
    combarray = np.array(comb)
    
    soldict = {}
    
    print('Solve ODE for combination: ')
    for i, c in enumerate(combarray[:,:]):
        print(i)
        #sol = solveODE(ODEfun, y0, tspan, args=(c[1:], ))
        sol = solveODE_event(ODEfun, y0, tspan, args=(params, c[1:]),\
                             stateevent = stateevent, paramevent = paramevent)
        soldict[c[0]] = {}
        for ind, s in enumerate(states):
            soldict[c[0]][s] = sol[:,ind]
        
    return soldict

def get_component(solutiondict, compoundlist):
    '''Return a dict with key containing the compound name, and value containing
    the 2D array of time-response data for all combinations.'''
    compdict = {}
    compdict['index'] = np.array(list(solutiondict.keys()))
    for c in compoundlist:
        sollist = []
        for k, v in solutiondict.items():
            sollist.append(v[c])
        compdict[c]  = np.array(sollist).T
        
    return compdict


def rank_combinations(dfcombinations_val, dfcombinations_str, compounddict, compound, order = 'descending'):
    '''Rank the combinations.
    dfcombinations_val: dataframe with the relative strength values for each part
    compounddict: dictionary containing compound names as keys and 2D array
            time-response results for all combinations as values.
    compound: compound name as str for evaluation
    order: rank in descending or ascending order
        
    Return:
        index: a list of index of the position after ranking, also refer to the
                construct number in this case
        comparray: 2D array of the evaluated compound after arranged based
                on the index
        dfcombinations_val_Output: updated dataframe with new column containing
                the corresponding output result.
    '''
    if compound in compounddict.keys():
        compend = compounddict[compound][-1,:]
        if order == 'descending': 
            index = np.argsort(-compend)
        else:
            index = np.argsort(compend)
        
        # rearrange the array based on index
        comparray = compounddict[compound][:, index]
        
        # store as new column into df
        dfcombinations_val_Output = dfcombinations_val.loc[index]
        dfcombinations_val_Output[compound] = comparray[-1,:]
        dfcombinations_str_Output = dfcombinations_str.loc[index]
        dfcombinations_str_Output[compound] = comparray[-1,:]
    else:
        print('No compound found in the dictionary')
        
    return index, comparray, dfcombinations_val_Output, dfcombinations_str_Output
    

def set_time(tstart, tend):
    '''Return the Time points for simulation.'''
    Time = np.linspace(tstart, tend, tend+1)
    
    return Time


def multiply_dictkey_byvalue(paramsdict, modified_keylist, factor):
    '''Multiply the values of params dictionary by a factor based on the keys
    in modified_keylist.
    '''
    new_paramsdict = copy.deepcopy(paramsdict)
    new_paramsdict.update({n: factor * new_paramsdict[n] for n in modified_keylist})
    
    return new_paramsdict


def solveODE(ODEfun, y0, tspan, args):
    '''Solve the ODE.'''
    sol = odeint(ODEfun, y0, tspan, args)
    
    return sol


def solveODE_event(ODEfun, y0, tspan, args, stateevent = {}, paramevent={}):
    '''Solve ODEs with triggers/events.'''
    sol = np.zeros((len(tspan), len(y0)))

    r = ode(ODEfun)
    r.set_initial_value(y0, tspan[0])
    
    params = copy.deepcopy(args[0])
    r.set_f_params(params, args[1])

    for ts in range(1, len(tspan)):
        sol[ts, :] = r.integrate(tspan[ts])
        if stateevent:
            for i, t in enumerate(stateevent['Time']):
                if ts == t:
                    for k,v in stateevent['State'][i].items():
                        y0tmp = sol[ts,:]
                        y0tmp[k] = v
                    r.set_initial_value(y0tmp, ts)
                    
        if paramevent:
            for i, t in enumerate(paramevent['Time']):
                if ts == t:
                    for k,v in paramevent['Param'][i].items():
                        params[k] = v
                    r.set_f_params(params, args[1])
                    
    return sol
  
    
def get_combinationslists(optionslist):
    '''Get the optionslist and return All combinations as 2D array
    Example:
        J23119 = 0.3984
        J23101 = 0.909 
        J23100 = 0.8181
        J23106 = 0.3636
        
        rbsD = 1.0
        rbs34 = 0.764
        rbs33 = 0.0061
        rbs32 = 0.1855
        
        PromoterList = [J23119, J23101, J23100, J23106]
        RBSList = [rbsD, rbs34, rbs33, rbs32] 
        optionslist = [PromoterList, RBSList, PromoterList, RBSList, PromoterList, RBSList]
        Allcombinations = get_combinationslists(optionslist)
    '''
    
    Listcombinations = list(itertools.product(*optionslist))
    
    return np.array(Listcombinations)


def rank_combinations_helper(dfcombinations_val, dfcombinations_str, soldict,\
                             compound, order = 'descending'):
    '''Helper function to run the rank combinations.'''
    # Get the time response data as array for different components in the form
    # of dictionary.
    compdict = get_component(soldict, [compound])
    
    # Rank the combinatorial configurations based on [Nar] in the descending order.'''
    index, comparray, dfcombinations_val_Output, dfcombinations_str_Output =\
    rank_combinations(dfcombinations_val, dfcombinations_str, compdict,\
                      compound, order)
    
    return index, comparray, dfcombinations_val_Output, dfcombinations_str_Output


def rank_defined_combinations(dfcombinations_val_Output, dfcombinations_str_Output,\
                              compound, order = 'descending'):
    '''Rank the compound stored in the dataframe and update both dataframes in 
    values and string (parts' names).
    '''
    if compound in dfcombinations_val_Output.columns:
        if order == 'descending':
            sorted_df_val = dfcombinations_val_Output.sort_values(compound,\
                                                                  ascending = False)
            sortedindex = list(sorted_df_val.index.values)
            sorted_df_str = dfcombinations_str_Output.loc[sortedindex]
        else:
            sorted_df_val = dfcombinations_val_Output.sort_values(compound)
            sortedindex = list(sorted_df_val.index.values)
            sorted_df_str = dfcombinations_str_Output.loc[sortedindex]
            
    return sorted_df_val, sorted_df_str
         

def run_defined_combinations(defined_dict, partdict, compoundlist, ODEfun,\
                             states, y0, tspan, params, stateevent = {}, paramevent={}):
    '''Helper function to run users' defined combinations.'''
    dfcombinations_str = pd.DataFrame(defined_dict)
    dfcombinations_val = convert_dfstrtovalue(dfcombinations_str, partdict)
    
    soldict = solve_combinations(dfcombinations_val, ODEfun, states, y0, tspan,\
                                 params, stateevent, paramevent)
    
    # Get the time response data as array for different components in the form
    # of dictionary.
    compdict = get_component(soldict, compoundlist)
    
    dfcombinations_val_Output = copy.deepcopy(dfcombinations_val)
    dfcombinations_str_Output = copy.deepcopy(dfcombinations_str)
    
    for compound in compoundlist:
        if compound in compdict.keys():
            compend = compdict[compound][-1,:]
            # store the compound result as new column into df
            dfcombinations_val_Output[compound] = compend
            dfcombinations_str_Output[compound] = compend
    
    return dfcombinations_val_Output, dfcombinations_str_Output, soldict


def run_defined_combinations_and_rank(defined_dict, partdict, rankedcompound, ODEfun,\
                             states, y0, tspan, params, stateevent = {}, paramevent={}):
    '''Helper function to run users' defined combinations
    and rank the combinations.
    '''
    dfcombinations_str = pd.DataFrame(defined_dict)
    dfcombinations_val = convert_dfstrtovalue(dfcombinations_str, partdict)
    
    soldict = solve_combinations(dfcombinations_val, ODEfun, states, y0, tspan,\
                                 params, stateevent, paramevent)
    
    # Get the time response data as array for different components in the form
    # of dictionary.
    compdict = get_component(soldict, [rankedcompound])
    
    # Rank the combinatorial configurations based on [Nar] in the descending order.'''
    index, comparray, dfcombinations_val_Output, dfcombinations_str_Output =\
    rank_combinations(dfcombinations_val, dfcombinations_str, compdict,\
                      rankedcompound, 'descending')
    
    return index, comparray, dfcombinations_val_Output, dfcombinations_str_Output


 