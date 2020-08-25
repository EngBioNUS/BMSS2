"""
@author: jingwui

This file exemplifies how we can perform combinatorial study analysis using
the model input file provided by users in the form of configuration .ini format.
More helper functions are used in this file to simplify the process.

Requirements:
    pip install SALib
    pip install dnaplotlib
    
Type %reset at the IPython console to remove all variables on Variable explorer
"""


import __init__
import os
import numpy as np
import matplotlib.pyplot as plt
import BMSS.combinatorial.model_coder_CA as mca
import BMSS.combinatorial.simplednaplot as pc   
import BMSS.combinatorial.combinatorial_run_modules as cm    
import BMSS.combinatorial.plotfig as pf


plt.close('all')

'''Save all the output figures to the 'Outputs' folder.'''
path0 = os.path.abspath(os.path.dirname(__file__))
print(path0)
outputpath = os.path.join(path0, 'Outputs')
print(outputpath)


if __name__ == '__main__':
    
    '''Plot the gene circuit diagram.'''
    partstr = 'p.pLac r.rbsD c.blue.OsCHS t p r c.purple.MCS t p r c.orange.PAL t p r c.red.4CL t o.pRFS101'
    regulations = 'p0->p0.Activation'
    circuitfigpath = os.path.join(outputpath, 'Circuitfigure.tiff')
    fig = pc.plot_circuit_config(partstr, regulations, savefig = circuitfigpath)
    fig.show()
    
    
    '''Read the configuration .ini file and add the model to database.
    Can also read multiple .ini files. Return the model in the form of
    a list of dictionaries.
    '''
    filenames = ['Combinatorial_Bioconversion_Naringenin_comb.ini']
    model, stored_model = mca.read_and_add_model_to_database(filenames)
    print(model[0]) # to view the model
    print(model[0].get('parameters')) # to check the parameters of the model
    
    
    '''To generate the model function for combinatorial simulations.
    Set local = True to generate the .py in the same repository, else the file
    will be generated in BMSS/models/model_functions folder.
    '''
    modelstr, modelpath = mca.model_to_code(model[0], local=False) 
    print('\nModel in string format:\n', modelstr)
    print('\nModel path:\n', modelpath)
    
    '''Get the model ODE function from the generated .py file.'''
    modelfun = mca.get_model_function(modelpath)
    print('called model function from the generated .py file:\n', modelfun)
    
    
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
    
    print(new_paramsdict)
    
    # Get the parameters' values in list for ODE solving
    params = list(new_paramsdict.values())
    print("\nparameters' values:\n", params)
    
    # Define the time points for simulation
    Time = cm.set_time(0, (18+24)*60) # in min
    print(Time)
    
    
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
    y = cm.solveODE_event(modelfun, y0, Time, args = (params, [1]*7),\
                          stateevent = stateevent, paramevent = paramevent)

    pf.plotfig(10, Time, y[:,-1], ['Time (min)', 'Concentration (Molar)'], ['Nar'])
    pf.plotfig(11, Time, y[:,-6], ['Time (min)', 'Concentration (Molar)'], ['Tyr'])
    pf.plotfig(12, Time, y[:,3], ['Time (min)', 'Concentration (Molar)'], ['OsCHS'], SetYlim=[0, 2.5e-5])
    pf.plotfig(12, Time, y[:,5], [], ['MCS'])
    pf.plotfig(12, Time, y[:,7], [], ['PAL'])
    
    '''Plot figures in subplots by controlling the axis input argument (ax).'''
    fig, axs = plt.subplots(2,2, num=13, figsize = (8,6))
    print('axs', axs)
    pf.plotfig([], Time, y[:,-1], ['Time (min)', 'Concentration (Molar)'], ['Nar'], ax=axs[0,0])
    pf.plotfig([],Time, y[:,-6], ['Time (min)', 'Concentration (Molar)'], ['Tyr'], ax=axs[0,1], SetYlim=[0, 3e-5])
    pf.plotfig([],Time, y[:,3], ['Time (min)', 'Concentration \n (Molar)'], ['OsCHS'], ax=axs[1,0], SetYlim=[0, 3e-5])
    pf.plotfig([],Time, y[:,5], [], ['MCS'], ax=axs[1,0])
    pf.plotfig([],Time, y[:,7], [], ['PAL'], ax=axs[1,0])
    pf.plotfig([],Time, y[:,9], [], ['4CL'], ax=axs[1,0])

    '''An example to plot errorbar using plotfig Errorbarstd in the same subplots figure.'''
    xe = np.array([1,2,3,4,5])
    ye = np.array([[3,5,2,4,6], [7,3,5,10,8]]).T
    yerr = np.array([[0.5, 0.7, 0.1, 0.3, 1], [0.7, 0.3, 0.5, 0.3, 2]]).T
    pf.plotfig([],xe, ye, ['Time (min)', 'Concentration \n (Molar)'],\
               ['Exp1', 'Exp2'], ax=axs[1,1], Errorbarstd = yerr,\
               SetYlim=[0, 20], SetYtick=[0, 20, 5])
    pf.plotfig([],xe, ye, ['Time (min)', 'Concentration \n (Molar)'],\
               ['Line1', 'Line2'], ax=axs[1,1], Errorbarstd = [])
    fig.tight_layout() #(pad = 0)
    
    
    '''Solve the model for all combinations. dataframe.iloc is to control the
    rows of combination to be solved, e.g: iloc[:15] means solving the first
    15 combinations.
    '''
    states = list(y0dict.keys())
    soldict = cm.solve_combinations(dfcombs_val.iloc[:], modelfun, states, y0,\
                                    Time, params, stateevent = stateevent,\
                                    paramevent = {})
    print(soldict)
    
    index, comparray, dfcombs_val_Output, dfcombs_str_Output =\
    cm.rank_combinations_helper(dfcombs_val.iloc[:], dfcombs_str.iloc[:], soldict,\
                                'Nar', order = 'descending')
    
    #get the top 10 index
    Top10index = index[:10]
    print(Top10index)
    
    
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
               savefig = os.path.join(outputpath,'Top10_constr_str.png'),\
               font_scale = 0.9)
    
    '''Plot both the heatmaps in the form of subplots.'''
    fig, axs = plt.subplots(1,2, num=22, figsize = (20,6))
    pf.heatmap([], dfcombs_val.loc[Top10index], ['','Construct ID'],\
               [xtlabels, ytlabels], ax=axs[0])
    pf.heatmap([], dfcombs_val.loc[Top10index], ['','Construct ID'],\
               [xtlabels, ytlabels], annot = dfcombs_str.loc[Top10index],\
               font_scale = 0.9, ax=axs[1])
    
    
    '''Plot the heatmap of Top 10 configurations with their output performance.'''
    data1 = dfcombs_val_Output.iloc[:10,:-1]
    # can insert more than one column for data2 such as CouA and Nar 
    data2 = dfcombs_val_Output.iloc[:10,-1]*1e3 # Nar convert from M to mM
    xylabels = ['Parts', 'Construct index']
    
    pf.Biheatmap(23, data1, data2, xylabels, font_scale = 1)
    pf.Biheatmap(24, data1, data2, xylabels, font_scale = 0.9,\
                 annot = dfcombs_str_Output.iloc[:10,:-1])
    
    '''Plot the Biheatmap in the form of subplots.'''
    fig = plt.figure(25, figsize = (20,6))
    gs = fig.add_gridspec(1, 2, hspace=0.4,wspace=0.1)
    pf.Biheatmap([], data1, data2, xylabels, font_scale = 1, ax=gs[0])
    pf.Biheatmap([], data1, data2, xylabels, font_scale = 0.9, ax=gs[1],\
                 annot = dfcombs_str_Output.iloc[:10,:-1])
    

    '''Plot the Top 10 final output expression in bar chart.'''
    pf.plotbar(26, comparray[-1, :10], ['Index', 'Naringenin (Molar)'], [], alpha=1,\
            set_xticklabels = index, Autolabel=True) #, set_xticklabelsoffset = 5)
    
    '''Plot the bar chart in subplots.'''
    fig, axs = plt.subplots(2, 1, num=27, figsize = (8,8))
    pf.plotbar([], comparray[-1, :10], ['Index', 'Naringenin (Molar)'], [], alpha=1,\
            set_xticklabels = index, Autolabel=False, ax=axs[0])
    pf.plotbar([], comparray[-1, :10], ['Index', 'Naringenin (Molar)'], [], alpha=1,\
            set_xticklabels = index, Autolabel=True, ax=axs[1]) #, set_xticklabelsoffset = 5)
    fig.tight_layout(pad = 1)


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
    
    '''Plot the compoundlist1 for all Top10index in the form of subplots.'''
    fig, axs = plt.subplots(2,5, num=40, figsize = (20,6))
    cm.plot_compounds(Time, soldict, Top10index[:], compoundlist1,\
                      xylabels = xylabels, figureopt = 'per_index',\
                      ax = axs, SetYlim = [0, 1.8e-3])
    fig.tight_layout() #(pad = 1) # can use pad to increase the spacing bet subplots
    
    
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
    
    rankedcompound = 'Nar' # state's name 
    
    index, comparray, dfcombs_val_Output1, dfcombs_str_Output1 =\
    cm.run_defined_combinations_and_rank(defined_dict, partdict,\
                                         rankedcompound, modelfun,\
                                         states, y0, Time, params,\
                                         stateevent, paramevent)
    
    '''Plot the heatmap of the defined configurations with their output performance.'''
    data1 = dfcombs_val_Output1.iloc[:,:-1]
    # can insert more than one column for data2 such as CouA and Nar 
    data2 = dfcombs_val_Output1.iloc[:,-1]*1e3 # Nar convert from M to mM
    xylabels = ['Parts', 'Construct index']
    
    pf.Biheatmap([], data1, data2, xylabels, font_scale = 1)
    pf.Biheatmap([], data1, data2, xylabels, font_scale = 0.9,\
                 annot = dfcombs_str_Output1.iloc[:,:-1])
    
    
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

    