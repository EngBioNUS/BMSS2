import matplotlib.pyplot as plt
import numpy             as np
from   numba             import jit

import setup_bmss              as lab
import BMSS.curvefitting       as cf
import BMSS.models.setup_sim   as sm
import BMSS.models.model_handler as mh

plt.style.use(lab.styles['dark_style'])

##Reset Plots
plt.close('all')       

system_types   = []
#Create the simulation settings ONCE
sm.make_settings_template(system_types, filename='sim_settings.ini')

filename       = '.ini'
# models, params = sm.setup_models_and_params(filename)

# #Required Argument
# plot_index  = {1: [],
#                }

# #Optional Arguments
# titles      = {model_num: {state: state for state in plot_index[model_num]} for model_num in plot_index}
# labels      = {model_num: {scenario: str(scenario) for scenario in models[model_num]['init'].keys()} for model_num in plot_index}

# #Very Optional Arguments
# legend_args = {'fontsize': 16, 'loc': 'upper right'}
# line_args   = {'linewidth': 3}
# palette     =  {'palette_type': 'color',
#                 'palette'     : 'muted'
#                }

# figs = []
# AX   = {}
# figs, AX = cf.plot(posterior=params,              
#                    models=models, 
#                    plot_index=plot_index,  
#                    titles=titles,       
#                    labels=labels,     
#                    legend_args=legend_args,  
#                    figs=figs,             
#                    AX=AX,             
#                    palette=palette, 
#                    line_args=line_args)

