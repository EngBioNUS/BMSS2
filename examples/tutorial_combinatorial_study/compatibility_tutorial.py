"""
@author: jingwui

This file exemplifies how we can set up the combinatorial model to ensure
compatibility and interoperability with other functions of the software. 
"""

import __init__
import os
import numpy as np
import matplotlib.pyplot as plt
import BMSS.combinatorial.model_coder_CA as mca 
import BMSS.combinatorial.combinatorial_run_modules as cm   
import BMSS.models.model_handler as mh
import BMSS.simulation as sim


plt.close('all')


def modify_init(init_values, params, model_num, scenario_num, segment):
    '''Modify states at certain time segments.'''
    #Always use a copy and not the original
    new_init = init_values.copy()
    
    print('Test segment', segment)
    
    #Change initial value of hm based on relative strength
    if segment == 0:
        #adding IPTG of 0.02e-3
        new_init[0] = 0.02e-3
    elif segment == 2:
        #adding substrates: Tyrosine (index -6) of 0.25e-3;
        #Malonic acid (index -3) of 1e-3
        new_init[-6] = 0.25e-3
        new_init[-3] = 1e-3
    else:
        pass
    
    return new_init


def modify_params(init_values, params, model_num, scenario_num, segment):
    '''Modify parameter 'syn_mRNA' at index 6 just as an example.'''
    #Always use a copy and not the original
    new_params = params.copy()
    
    if model_num == 1 and segment == 3:
        new_params[6] = 0e-8
    else:
        new_params[6] = 1e-8
    
    return new_params


if __name__ == '__main__':
    
    '''Read the configuration .ini file and add the model to database.
    Can also read multiple .ini files. Return the model in the form of
    a list of dictionaries.
    '''
    filenames = ['Combinatorial_Bioconversion_Naringenin_comb.ini']
    model, stored_model = mca.read_and_add_model_to_database(filenames)
    print('Model dict with combinations:\n', model[0]) # to view the model with combinations
    print('\nModel dict without combinations:\n', stored_model[0])
    
    
    '''First example on how to run the bioconversion model with parameters,
    and generate the full model dict in order to use functions from other modules.
    '''
    
#    '''Add model to database.'''
#    rowid = mh.add_to_database(stored_model[0])
#    print('\nrowid for the added model:\n', rowid)
#    
#    
#    '''Generate the model function .py file in the form of modelfun(y, t, params).'''
#    model_codefile = mh.model_to_code(stored_model[0], local = False)
#    
#    
#    '''Get the model ODE function from the generated .py file,
#    in the form of modelfun(y, t, params). This function only works when the
#    model function file is located at model_functions folder under BMSS.models'''
#    model_function = mh.get_model_function(stored_model[0]['system_type'])
#    print(model_function)
#    
#    
#    '''Define the initial conditions for states in dict format for ease of manipulation.'''
#    y0dict = {'Inde':0.0e-3, 'Indi': 0, 'mCHS':0, 'OsCHS':0, \
#    'mMCS':0, 'MCS':1E-06, \
#    'mPAL':0, 'PAL':1E-06, \
#    'mE4CL':0, 'E4CL': 1E-06, \
#    'Tyr':0, 'CouA':0, 'CouCoA':0, 'MalA':0, 'MalCoA':0, 'Nar':0}
#    
#    # Get the y0 in list for ODE solving
#    y0 = np.array(list(y0dict.values()))
#    
#    
#    '''Define the Time segments needed to run piecewise integrator, with
#    inducer IPTG of 0.02 is added at the first time segment (segment[0]),
#    and the substrates Tyrosine of 0.25e-3 and Malonic acid of 1e-3 are added
#    at the third time segment (segment[2]). If there is no compound addition,
#    just define the duration of simulation, e.g. Time = [np.linspace(0, (18+24)*60)].
#    '''
#    Time = [np.linspace(0, 1), np.linspace(1, 18*60),\
#            np.linspace(18*60, 18*60+1), np.linspace(18*60+1, (18+24)*60)]
#    
#    
#    '''Define the models dict which is the standard format used as input argument
#    for other functions in other modules. '''
#    models = {1: {'function' : model_function,
#              'init'     : {1: y0
#                            },
#              'states'   : stored_model[0]['states'],            
#              'params'   : stored_model[0]['parameters'],
#              'tspan'    : Time,
#              'int_args' : {'modify_init'   : modify_init,
#                            'modify_params' : modify_params,
#                            'solver_args'   : {'rtol'   : 1.49012e-8,
#                                               'atol'   : 1.49012e-8,
#                                               'tcrit'  : np.array([]),
#                                               'h0'     : 0.0,
#                                               'hmax'   : 0.0,
#                                               'hmin'   : 0.0,
#                                               'mxstep' : 0,
#                                               'tfirst' : False,
#                                               },
#                            }
#              },
#          }
#    #print(models)
#    
#    plot_index  = {1: ['OsCHS', 'Nar']
#                    }
#    titles      = {1: {'OsCHS': 'OsCHS Expression', 'Nar':'Naringenin Output'}
#                   }
#    labels      = {1: {1:'label1', 2:'label2'},
#                   }
#    palette     =  {'palette_type': 'color', 
#                    'palette'     : 'muted'
#                    }
#                
#    legend_args = {'fontsize': 16, 'loc': 'upper right'}
#    line_args   = {'linewidth': 3}  
#    
#    
#    '''Define the parameters in dict format for ease of manipulation.'''
#    paramsdict = {'Vm': 6.1743e-05, 'ntrans': 0.9416,\
#                  'Ktrans': 0.0448, 'n_ind': 5.4162, 'K_ind': 2.0583e-05,\
#                  'syn_mRNA': 8.6567e-08, 'syn_Pep': 0.01931 *0.9504,\
#                  'deg_Pep1': 0.0010, 'deg_mRNA': 0.1386, 'deg_Pep': 0.007397,\
#                  'syn_mMCS': 2.2953e-07, 'syn_pMCS': 0.01931 *0.9218,\
#                  'syn_mPAL': 2.2953e-07, 'syn_pPAL': 0.01931 *0.8684,\
#                  'syn_mE4CL': 2.2953e-07, 'syn_pE4CL': 0.01931 *0.9119,\
#                  'kcatTyr': 61.2 , 'KmTyr': 0.195e-3, 'kcatCouA': 16.92,\
#                  'KmCouA': 0.246e-3, 'kcatMalA': 150, 'KmMalA': 529.4e-6,\
#                  'kcatCouMalCoA': 0.0517, 'KmMalCoA': 47.42e-6,\
#                  'KmCouCoA': 45.44e-6}
##    # to convert the parameters values into np.array
##    params = {}
##    for k, v in paramsdict.items():
##        params[k] = np.array([v])
#        
#    '''Integrate the models with the parameters.'''
#    ym, em = sim.integrate_models(models, paramsdict)
#    #ym, em = sim.integrate_models(models, params, args = (comb, ))
#    print('ym shape: ', ym[1][1][0].shape) #(200, 16)
#    print('em shape: ', em)
#    
#    
#    '''Plot the model simulation results.'''
#    figs, AX = sim.plot_model(plot_index, ym, em, titles=titles, labels=labels,\
#                              figs=[], AX={}, palette=palette,\
#                              line_args=line_args, legend_args=legend_args)
#    print('\nModel figure axis:\n', AX)
#    #set the y axis ticklabel to be in scientific notation using the figure axis
#    AX[1]['OsCHS'].ticklabel_format(style='sci', axis='y', scilimits=(-2, 1))              
#    AX[1]['Nar'].ticklabel_format(style='sci', axis='y', scilimits=(-2, 1))  
#    
    
    
    '''Second example on how to run the bioconversion model with parameters and
    combinations, then generate the full model dict in order to use functions
    from other modules.
    '''
    
    
    '''To generate the model function file for the combinatorial model from .ini.'''
    model2 = model.copy() # generate a copy of model generated from .ini file
    modelstr, modelpath = mca.model_to_code(model2[0], local=True) 
    print('\nModel in string format:\n', modelstr)
    print('\nModel path:\n', modelpath)
    
    '''Get the model ODE function from the generated .py file.'''
    model_function2 = mca.get_model_function(modelpath)
    print('called model function from the generated .py file:\n', model_function2)
    
    
    '''Or retrieve the base model without the combinations from database, and
    then add the combinations into the model dict.'''
#    model2 = mh.search_database(keyword = 'naringenin')
#    print('\nTotal models found:\n', len(model2))
#    print('\nSearched model from database:\n', model2[-1]) #get the last one
#    
#    
#    '''Add combinations to the model dict.'''
#    combinations_list = ['syn_mMCS', 'syn_pMCS', 'syn_mPAL', 'syn_pPAL',\
#                         'syn_mE4CL', 'syn_pE4CL', 'syn_Pep']
#    model_w_comb = mca.add_comb_to_model(model2[-1], combinations_list)
#    
#    
#    '''Create the new model function .py file in the local repository
#    and return the model in string for checking.'''
#    new_modelstr, new_modelpath = mca.model_to_code(model_w_comb, local=True)
#    
#    
#    '''Get the model ODE function from the generated .py file, 
#    in the form of modelfun(t, y, params = [], comb = []).'''
#    model_function2 = mca.get_model_function(new_modelpath)
  
    
    '''Define the initial conditions for states in dict format for ease of manipulation.'''
    y0dict = {'Inde':0.0e-3, 'Indi': 0, 'mCHS':0, 'OsCHS':0, \
    'mMCS':0, 'MCS':1E-06, \
    'mPAL':0, 'PAL':1E-06, \
    'mE4CL':0, 'E4CL': 1E-06, \
    'Tyr':0, 'CouA':0, 'CouCoA':0, 'MalA':0, 'MalCoA':0, 'Nar':0}
    
    # Get the y0 in list for ODE solving
    y0 = np.array(list(y0dict.values()))
    
    
    '''Define the Time segments needed to run piecewise integrator, with
    inducer IPTG of 0.02 is added at the first time segment (segment[0]),
    and the substrates Tyrosine of 0.25e-3 and Malonic acid of 1e-3 are added
    at the third time segment (segment[2]). If there is no compound addition,
    just define the duration of simulation, e.g. Time = [np.linspace(0, (18+24)*60)].
    '''
    Time = [np.linspace(0, 1), np.linspace(1, 18*60),\
            np.linspace(18*60, 18*60+1), np.linspace(18*60+1, (18+24)*60)]
    
    
    '''Define the models dict which is the standard format used as input argument
    for other functions in other modules. To solve modelfun(t, y, params = [], comb = []),
    just set solver_args['tfirst'] to True.'''
    models = {1: {'function' : model_function2,
              'init'     : {1: y0
                            },
              'states'   : model2[0]['states'],            
              'params'   : model2[0]['parameters'],
              'tspan'    : Time,
              'int_args' : {'modify_init'   : modify_init,
                            'modify_params' : None,
                            'solver_args'   : {'rtol'   : 1.49012e-8,
                                               'atol'   : 1.49012e-8,
                                               'tcrit'  : np.array([]),
                                               'h0'     : 0.0,
                                               'hmax'   : 0.0,
                                               'hmin'   : 0.0,
                                               'mxstep' : 0,
                                               'tfirst' : True,
                                               },
                            }
              },
          }
    print('\nFull Model info:\n', models)
    
    plot_index  = {1: ['OsCHS', 'Nar']
                    }
    titles      = {1: {'OsCHS': 'OsCHS Expression', 'Nar':'Nar Output'}
                   }
    labels      = {1: {1: 'OsCHS'}
                   }
    palette     =  {'palette_type': 'color', 
                    'palette'     : 'muted'
                    }
                
    legend_args = {'fontsize': 16, 'loc': 'upper right'}
    line_args   = {'linewidth': 3}  
    
    
    '''Define the parameters in dict format for ease of manipulation.'''
    paramsdict = {'Vm': 6.1743e-05, 'ntrans': 0.9416,\
                  'Ktrans': 0.0448, 'n_ind': 5.4162, 'K_ind': 2.0583e-05,\
                  'syn_mRNA': 8.6567e-08, 'syn_Pep': 0.01931 *0.9504,\
                  'deg_Pep1': 0.0010, 'deg_mRNA': 0.1386, 'deg_Pep': 0.007397,\
                  'syn_mMCS': 2.2953e-07, 'syn_pMCS': 0.01931 *0.9218,\
                  'syn_mPAL': 2.2953e-07, 'syn_pPAL': 0.01931 *0.8684,\
                  'syn_mE4CL': 2.2953e-07, 'syn_pE4CL': 0.01931 *0.9119,\
                  'kcatTyr': 61.2 , 'KmTyr': 0.195e-3, 'kcatCouA': 16.92,\
                  'KmCouA': 0.246e-3, 'kcatMalA': 150, 'KmMalA': 529.4e-6,\
                  'kcatCouMalCoA': 0.0517, 'KmMalCoA': 47.42e-6,\
                  'KmCouCoA': 45.44e-6}

        
    '''Integrate the models with the parameters and the combinations inserted
    as an extra argument.'''
    comb = np.array([1,1,1,1,1,1,0.1])
    
    ym, em = sim.integrate_models(models, paramsdict, args = (comb, ))
    print('ym shape: ', ym[1][1][0].shape)
    print('em shape: ', em)
    
    
    '''Plot the model simulation results.'''
    figs, AX = sim.plot_model(plot_index, ym, em, titles=titles, labels=labels,\
                              figs=[], AX={}, palette=palette,\
                              line_args=line_args, legend_args=legend_args)
    print('\nModel figure axis:\n', AX)
    #set the y axis ticklabel to be in scientific notation using the figure axis
    AX[1]['OsCHS'].ticklabel_format(style='sci', axis='y', scilimits=(-2, 1))              
    AX[1]['Nar'].ticklabel_format(style='sci', axis='y', scilimits=(-2, 1)) 
    AX[1]['Nar'].legend(['Nar']) 

