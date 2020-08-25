"""
@author: jingwui

This file exemplifies how we can perform combinatorial study analysis in more 
detail using the model input file provided by users in the form of 
configuration .ini format.

Requirements:
    pip install SALib
    pip install dnaplotlib
    
Type %reset at the IPython console to remove all variables on Variable explorer
"""

import __init__
import os
import copy
import numpy as np
import matplotlib.pyplot as plt
import BMSS.models.model_handler as mh
import BMSS.combinatorial.model_coder_CA as mca  
import BMSS.combinatorial.combinatorial_run_modules as cm    
import BMSS.combinatorial.plotfig as pf

from BMSS.combinatorial.simplednaplot import SimpleDNAplot


plt.close('all')

'''Save all the output figures to the 'Outputs' folder.'''
path0 = os.path.abspath(os.path.dirname(__file__))
print(path0)
outputpath = os.path.join(path0, 'Outputs')
print(outputpath)

        
if __name__ == '__main__':

    '''Plot the gene circuit diagram.'''
    simplot = SimpleDNAplot()
    partstr = 'p.pLac r.rbsD c.blue.OsCHS t p r c.purple.MCS t p r c.orange.PAL t p r c.red.4CL t o.pRFS101'
    regulations = 'p0->p0.Activation'
    circuitfigpath = os.path.join(outputpath, 'Circuitfigure.tiff')
    _, fig = simplot.plot_circuit(partstr, regulations, savefig = circuitfigpath)
    fig.show()
    
    
    filenames = ['Combinatorial_Bioconversion_Naringenin_comb.ini']
    
    '''Read the configuration .ini file and return a model dict.'''
    model = mca.read_config(filenames[0])
    print('\nmodel dictionary:\n', model)
    
    '''Remove the key 'combinations' for adding the model to database.'''
    model_stored = copy.deepcopy(model)
    model_stored.pop('combinations', None)
    print('\nmodel to be stored into database:\n', model_stored)
    
    '''Run through model checker to ensure proper model format to be stored.'''
    model_stored = mh.make_core_model(**model_stored)
    print('\nchecked model to be stored:\n', model_stored)
    
    '''Add model to database.'''
    rowid = mh.add_to_database(model_stored)
    print('\nrowid for the added model:\n', rowid)
    
    '''Create the model function .py file in the local repository
    and return the model in string for checking.'''
    modelstr, modelpath = mca.model_to_code(model, local=True)
    print('\nmodel in string format:\n', modelstr)
    
    
    '''Can also retrieve/search the model dict from the database based on keyword.'''   
    model = mh.search_database(keyword = 'naringenin')
    print('\nThe searched model from database:\n', model)
    print(len(model))  
    
    '''Customize the list of parameters to be modified in the combinatorial
    simulations using the default model from database.'''
    # list of parameters to be modified in the combinatorial study
    combinations_list = ['syn_mMCS', 'syn_pMCS', 'syn_mPAL', 'syn_pPAL',\
                         'syn_mE4CL', 'syn_pE4CL', 'syn_Pep']
    model_w_comb = mca.add_comb_to_model(model[-1], combinations_list)
    
    print(model_w_comb)
    
    '''Create the new model function .py file in the local repository
    and return the model in string for checking.'''
    new_modelstr, new_modelpath = mca.model_to_code(model_w_comb, local=False)
    print('\nModel in string format:\n', new_modelstr)
    print('\nModel path:\n', new_modelpath)
    
    
    '''Get the model ODE function from the generated .py file.'''
    modelfun = mca.get_model_function(new_modelpath) # or (new_modelpath)
    print('\nCalled model function from .py:\n', modelfun)
    
    
    '''Define the initial conditions for states in dict format for ease of manipulation.'''
    y0dict = {'Inde':0, 'Indi': 0, 'mCHS':0, 'OsCHS':0, \
    'mMCS':0, 'MCS':1E-06, \
    'mPAL':0, 'PAL':1E-06, \
    'mE4CL':0, 'E4CL': 1E-06, \
    'Tyr':0, 'CouA':0, 'CouCoA':0, 'MalA':0, 'MalCoA':0, 'Nar':0}
    
    # Get the y0 in list for ODE solving
    y0 = list(y0dict.values())
    
    
    '''Define the parameters in dict format for ease of manipulation.'''
    paramsdict = {'Vm': 6.1743e-05, 'ntrans': 0.9416, 'Ktrans': 0.0448,\
                  'n_ind': 5.4162, 'K_ind': 2.0583e-05, 'syn_mRNA': 8.6567e-08,\
                  'syn_Pep': 0.01931 *0.9504, 'deg_Pep1': 0.0010,\
                  'deg_mRNA': 0.1386, 'deg_Pep': 0.007397, 'syn_mMCS': 2.2953e-07,\
                  'syn_pMCS': 0.01931 *0.9218, 'syn_mPAL': 2.2953e-07,\
                  'syn_pPAL': 0.01931 *0.8684, 'syn_mE4CL': 2.2953e-07,\
                  'syn_pE4CL': 0.01931 *0.9119, 'kcatTyr': 61.2 , 'KmTyr': 0.195e-3,\
                  'kcatCouA': 16.92, 'KmCouA': 0.246e-3, 'kcatMalA': 150,\
                  'KmMalA': 529.4e-6, 'kcatCouMalCoA': 0.0517, 'KmMalCoA': 47.42e-6,\
                  'KmCouCoA': 45.44e-6}
    
    plasmidcopy_fold = 5
    
    # multiple some parameters with the plasmidcopy_fold
    modified_keylist = ['syn_mRNA', 'syn_mMCS', 'syn_mPAL', 'syn_mE4CL']
    new_paramsdict = cm.multiply_dictkey_byvalue(paramsdict, modified_keylist,\
                                                 plasmidcopy_fold)
    print('\nnew parameter dictionary:\n', new_paramsdict)
    
    # Get the parameters' values in list for ODE solving
    params = list(new_paramsdict.values())
    print("\nparameters' values:\n", params)
    
    # Define the time points for simulation
    Time = cm.set_time(0, (18+24)*60) # in min
    print('\nTime points:\n', Time)
    
    
    '''Define the Relative Strengths for Promoters and RBSs'''
    # Define RBS Relative Strengths in dict
    RBSdict = {'rbsD': 1.0, 'rbs32': 0.1855}
    
    # Define Promoter Relative Strengths wrt J23102 in dict
    Promoterdict = {'J23101': 0.909, 'J23106': 0.3636}
    
    '''Plot the relative strength partdict as heatmap and export the figure.''' 
    cm.plot_relative_strength({'PromoterOpt1':Promoterdict, 'RBSOpt1':RBSdict},
                              outputpath)


    '''Get all the combinations.'''
    Optiondict = {'pMCS': Promoterdict, 'rbsMCS': RBSdict,
                  'pPAL': Promoterdict, 'rbsPAL': RBSdict, 
                  'p4CL': Promoterdict, 'rbs4CL': RBSdict,
                  'rbsOsCHS': RBSdict}
    dfcombs_str, dfcombs_val = cm.get_combinations(Optiondict)
    print(dfcombs_str.head())
    print(dfcombs_val.head())
    
    
    '''Solve the ODE model.
    (define the stateevent and paramevent for simulations).
    '''
    stateevent = {'Time':[1, 18*60], 'State':[{0: 0.02e-3}, {-6: 0.25e-3, -3: 1e-3}]}
    #paramevent = {'Time':[18*60, 24*60], 'Param':[{6: 1e-08}, {11: 1.2953e-07, 13: 0.2953e-07}]}
    paramevent = {}
        
    
    '''Solve the model with a single combination.'''
    comb = [1, 0.5, 0.3, 1, 0.8, 0.4, 0.9]
    # Normally this represents the relative strength, but can be used to insert other values as well.
    print('\nCombinations: ', comb) 
    y = cm.solveODE_event(modelfun, y0, Time, args = (params, comb),\
                          stateevent = stateevent, paramevent = paramevent)

    # Use same figure number to overlap multiple lines in the same figure
    pf.plotfig(10, Time, y[:,-1], ['Time (min)', 'Concentration (Molar)'], ['Nar'])
    pf.plotfig(11, Time, y[:,-6], ['Time (min)', 'Concentration (Molar)'], ['Tyr'])
    pf.plotfig(12, Time, y[:,3], ['Time (min)', 'Concentration (Molar)'], ['OsCHS'])
    pf.plotfig(12, Time, y[:,5], [], ['MCS'])
    pf.plotfig(12, Time, y[:,7], [], ['PAL'], SetYlim = [0, 2.5e-5])
    
    # or column stack the 1D array into 2D array for non-sequential column data plotting in a same figure 
    AllEnzymes = np.column_stack((y[:,3], y[:,5], y[:,7], y[:,9]))
    
    pf.plotfig(13, Time, AllEnzymes, ['Time (min)', 'Concentration (Molar)'],\
                                      ['OsCHS', 'MCS', 'PAL', '4CL'])
    
    
    '''Solve the model for all combinations.'''
    states = list(y0dict.keys())
    soldict = cm.solve_combinations(dfcombs_val, modelfun, states, y0,\
                                    Time, params, stateevent = stateevent,\
                                    paramevent = {})
    print(soldict)
    
    
    '''Extract the time response data as array for different components in the form
    of dictionary.'''
    compdict = cm.get_component(soldict, ['CouA', 'Nar'])
    print(compdict) #(['Nar'][:,-1])
    
    '''Rank the combinatorial configurations based on [Nar] in the descending order.'''
    index, comparray, dfcombs_val_Output, dfcombs_str_Output = \
    cm.rank_combinations(dfcombs_val, dfcombs_str, compdict, 'Nar', 'descending')
    
    #get the top 10 index
    Top10index = index[:10]
    print('\nThe Top 10 indexes:\n', Top10index)
    
    
    '''Export all configurations with output to csv file.'''
    dfcombs_val_Output.to_csv(os.path.join(outputpath, 'Allcombsval_wOutput.csv'))
    dfcombs_str_Output.to_csv(os.path.join(outputpath, 'Allcombsstr_wOutput.csv'))


    '''Plot the heatmap showing the part strength values of the Top 10 configurations.'''
    xtlabels = list(dfcombs_val.columns)
    ytlabels = Top10index
    pf.heatmap(20, dfcombs_val.loc[Top10index], ['','Construct ID'],\
               [xtlabels, ytlabels],\
               savefig = os.path.join(outputpath,'Top10_constr_val.png'))
    
    '''Plot the heatmap showing the part names of the Top 10 configurations.'''
    pf.heatmap(21, dfcombs_val.loc[Top10index], ['','Construct ID'],\
               [xtlabels, ytlabels], annot = dfcombs_str.loc[Top10index],\
               savefig = os.path.join(outputpath,'Top10_constr_str.png'))
    
    
    '''Plot the heatmap of Top 10 configurations with their output performance.'''
    data1 = dfcombs_val_Output.iloc[:10,:-1]
    # can insert more than one column for data2 such as CouA and Nar 
    data2 = dfcombs_val_Output.iloc[:10,-1]*1e3 # Nar convert from M to mM
    xylabels = ['Parts', 'Construct index']
    
    pf.Biheatmap(22, data1, data2, xylabels, font_scale = 1)
    pf.Biheatmap(23, data1, data2, xylabels, annot = dfcombs_str_Output.iloc[:10,:-1])


    '''Plot the Top 10 final output expression in bar chart.'''
    pf.plotbar(24, comparray[-1, :10], ['Index', 'Naringenin (Molar)'], [], alpha=1,\
            set_xticklabels = index, Autolabel=True) #, set_xticklabelsoffset = 0)


    '''Plot multiple time-response figures based on list of index or list of compounds.'''   
    compoundlist1 = ['Tyr', 'CouA', 'CouCoA', 'MalA', 'MalCoA', 'Nar']
    compoundlist2 = ['Tyr', 'CouA', 'Nar']
    enzymelist = ['OsCHS', 'MCS', 'PAL', 'E4CL']
    xylabels = ['Time (min)', 'Concentration (Molar)']
    cm.plot_compounds(Time, soldict, Top10index[:3], compoundlist1,\
                      xylabels = xylabels, figureopt = 'per_index',\
                      SetYlim = [0, 1.4e-3])
    cm.plot_compounds(Time, soldict, Top10index, compoundlist2,\
                      xylabels = xylabels, figureopt = 'per_compound')
    cm.plot_compounds(Time, soldict, Top10index[:3], enzymelist,\
                      xylabels = xylabels, figureopt = 'per_index')
    
    
    '''Solve the ODE model based on user's defined combinations.'''
    defined_dict = {'pMCS':['J23101','J23106','J23106','J23106','J23106'],\
                    'rbsMCS':['rbsD','rbs32','rbsD','rbs32','rbs32'],\
                    'pPAL':['J23101','J23106','J23106','J23106','J23106'],\
                    'rbsPAL':['rbsD','rbs32','rbs32','rbsD','rbs32'],\
                    'p4CL':['J23101','J23106','J23106','J23106','J23106'],\
                    'rbs4CL':['rbsD','rbs32','rbs32','rbs32','rbsD'],\
                    'rbsOsCHS':['rbsD', 'rbsD', 'rbsD', 'rbsD','rbsD']}
    
    # merge the two dictionaries into one
    partdict = cm.mergedicts([Promoterdict, RBSdict])
    
    
    '''Run the defined combinations and update the dataframe with the
    compoundlist results.'''
    compoundlist = ['MalCoA', 'Nar']
    dfcombs_val_Output1, dfcombs_str_Output1, soldict =\
    cm.run_defined_combinations(defined_dict, partdict, compoundlist, modelfun,\
                                states, y0, Time, params, stateevent, paramevent)
    
    '''Plot the heatmap of the defined configurations with their output performance.'''
    data1 = dfcombs_val_Output1.iloc[:,:-2]
    # data2: MalCoA and Nar 
    data2 = dfcombs_val_Output1.iloc[:,-2:]*1e3 # convert from M to mM
    xylabels = ['Parts', 'Construct index']
    
    pf.Biheatmap([], data1, data2, xylabels, font_scale = 1)
    pf.Biheatmap([], data1, data2, xylabels, font_scale = 0.9,\
                 annot = dfcombs_str_Output1.iloc[:,:-2])
    
    
    '''Rank the defined combinations.'''
    rankedcompound = 'Nar' # state's name 
    sorted_dfcombs_val_Output1, sorted_dfcombs_str_Output1 =\
    cm.rank_defined_combinations(dfcombs_val_Output1, dfcombs_str_Output1,\
                                 rankedcompound, order = 'descending')
    
    '''Plot the ranked heatmap of the defined configurations with their performances.'''
    data1 = sorted_dfcombs_val_Output1.iloc[:,:-2]
    # data2: MalCoA and Nar 
    data2 = sorted_dfcombs_val_Output1.iloc[:,-1]*1e3 # convert from M to mM
    xylabels = ['Parts', 'Construct index']
    
    pf.Biheatmap([], data1, data2, xylabels, font_scale = 1)
    pf.Biheatmap([], data1, data2, xylabels, font_scale = 0.9,\
                 annot = sorted_dfcombs_str_Output1.iloc[:,:-2])
    
    
    '''Create jointplot for each of the columns vs Naringenin.'''
    cm.create_jointplot(dfcombs_val_Output.iloc[:,:-1],\
                     y = dfcombs_val_Output['Nar'], kind = 'reg',\
                     savefig = True, filepath = outputpath)
    
    
    '''Run sensitivity analysis and auto plot the heatmap'''
    xtlabels = list(Optiondict.keys())
    problem = {
            'num_vars': 7,
            'names': xtlabels,
            'bounds': [[0, 1]]*7
            }
    
    Si = cm.run_sensitivity_analysis(problem, modelfun, y0, Time, params,\
                             stateevent = stateevent, paramevent = {},\
                             method = 'sobol', sampling = 100)
    print('\nSensitivity Analysis Results:\n', Si)
    
    
    '''Auxiliary functionality (to ensure compatibility with other modules)
    To use the stored Naringenin's model from database to run simulations or
    curve-fitting as provided in other modules.'''
    
    '''retrieve/search the model dict from the database based on keyword.'''   
    model = mh.search_database(keyword = 'naringenin')
    print('\nThe searched model from database:\n', model)
    print(len(model)) 
    
    '''Use the model_to_code function from mh instead of mca to generate the
    compatible model function .py file.'''
    mh.model_to_code(model[-1], local = False)

    