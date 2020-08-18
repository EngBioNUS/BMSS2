import matplotlib.pyplot as plt
from   numba             import jit

import setup_bmss            as lab
import BMSS.models.setup_sim as sm
import BMSS.simulation       as sim

'''
Tutorial 2 Part 2: Advanced Simulation of Models
- Make use of piecewise integration
- Modify the initial values and params
- Use piecewise integration 
- Control the labels and colors
'''

plt.style.use(lab.styles['dark_style'])
plt.close('all')

if __name__ == '__main__':
    filename = 'settings_sim_2.ini'
    
    models, params, config_data = sm.get_models_and_params(filename)
    
    '''
    If we want to the params according to the scenario, we can write an additional function
    and add it to the models dict. Suppose in this instance we want to change the inducer
    based on the scenario.
    '''
    
    def change_inducer_by_scenario(init_values, params, model_num, scenario_num, segment):
        '''
        Modifies the the current array of params based on model_num, scenario, segment and init_values.
        For safety, do not modify in place.
        '''
        inducer_conc = {1: 0, 2: 0.03, 3: 0.05, 4:0.15}
        
        new_params   = params.copy()
        if model_num == 1:
            new_params[-1] = inducer_conc[scenario_num]

        return new_params
     
    @jit(nopython=True)
    def synthesis_p(y, t, params):
        
        m = y[:,0]
        
        synp = params[3]
        
        synthesis_rate = synp*m
        
        return synthesis_rate, t, '-'
    
    #Modify models accordingly
    models[1]['int_args']['modify_params'] = change_inducer_by_scenario  
    
    #Integrate
    ym, em = sim.integrate_models(models, params, synthesis_p)
    
    '''
    em is a nested dictinary in the form em[function][model_num][scenario_num][row]
    '''
    
    #Modify the plot settings accordingly
    plot_index  = {1: ['p', synthesis_p],
                   }
    titles      = {1: {'p': 'Model 1 Protein', synthesis_p: 'Rate of Protein Synthesis'},
                   }
    labels      = {1: {1: 'Ind 0', 2: 'Ind 0.01', 3: 'Ind 0.05', 4: 'Ind 0.15'}
                   }
    
    figs, AX = sim.plot_model(plot_index, ym, e=em, titles=titles, labels=labels) 
    
    '''
    Supposed we have two segments to the experiment and that the inducer is removed in the second half.
    '''
    
    def change_inducer_by_scenario_and_segment(init_values, params, model_num, scenario_num, segment):
        '''
        Modifies the the current array of params based on model_num, scenario, segment and init_values.
        For safety, do not modify in place.
        '''
        inducer_conc = {1: 0, 2: 0.03, 3: 0.05, 4:0.15}
        
        new_params   = params.copy()
        if model_num == 1 and segment == 0:
            new_params[-1] = inducer_conc[scenario_num]
        elif model_num == 1 and segment == 1:
            new_params[-1] = 0

        return new_params
    
    filename = 'settings_sim_3.ini'
    
    models, params, config_data = sm.get_models_and_params(filename)
    
    #Print tspan
    print('Tspan for two-segment experiment')
    print(models[1]['tspan'])
    
    #Modify models accordingly
    models[1]['int_args']['modify_params'] = change_inducer_by_scenario_and_segment
    
    #Integrate
    ym, em = sim.integrate_models(models, params, synthesis_p)
    
    figs, AX = sim.plot_model(plot_index, ym, e=em, titles=titles, labels=labels) 
    
    '''
    Note that the initial values can also be modified in a similar manner. Write your own function
    and place it under models[model_num]['int_args']['modify_init'] instead.
    '''
    
    #Labeling by row
    '''
    Suppose we want labels not only for each scenario but also each row of params.
    We can then created dict for labels with one extra layer of nesting with each key 
    corresponding to the row index.
    '''
    labels      = {1: {1: {0: 'Ind 0, k_ind 0.01',
                           1: 'Ind 0, k_ind 0.05 '},
                       2: {0: 'Ind 0.01, k_ind 0.01',
                           1: 'Ind 0.01, k_ind 0.05'}, 
                       3: {0: 'Ind 0.05, k_ind 0.01',
                           1: 'Ind 0.05, k_ind 0.05'}, 
                       4: {0: 'Ind 0.15, k_ind 0.01',
                           1: 'Ind 0.15, k_ind 0.05'},
                       }
                   }
    # figs, AX = sim.plot_model(plot_index, ym, e=em, titles=titles, labels=labels) 
    
    #Controlling the palette
    '''
    Fine control of the palette can be achieved by using a nested dictionary similar to labels.
    In this example, the lines are colored according to scenario.
    '''
    palette     = {1: {1: sim.all_colors['baby blue'], 
                       2: sim.all_colors['goldenrod'],
                       3: sim.all_colors['coral'],
                       4: sim.all_colors['ocean'],
                       },
                   }
    '''
    In this example, one more layer of nesting is added to control the color for each row of params.
    '''
    palette     = {1: {1: {0: sim.all_colors['baby blue'],
                           1: sim.all_colors['cobalt']},
                       2: {0: sim.all_colors['marigold'],
                           1: sim.all_colors['goldenrod']}, 
                       3: {0: sim.all_colors['coral'],
                           1: sim.all_colors['crimson']}, 
                       4: {0: sim.all_colors['lime'],
                           1: sim.all_colors['ocean']},
                       }
                   }
    figs, AX = sim.plot_model(plot_index, ym, e=em, titles=titles, labels=labels, palette=palette) 
    
    '''
    Other formats for the palette are allowed too for the sake of convenience.
    This example makes use of seaborn's color palette and colors each line by scenario.
    '''
    palette = {'palette_type': 'color'}
    
    '''
    This one makes use of seaborn's dark_palette. Not recommended for plots when params contains multiple rows.
    '''
    palette = {'palette_type': 'dark',
               'color'       : sim.all_colors['red']}
    '''
    This one makes use of seaborn's light_palette. Not recommended for plots when 
    params contains multiple rows. Other options include dark, cubehelix and diverging.
    '''
    palette = {'palette_type': 'light',
               'color'       : sim.all_colors['ocean']}
    '''
    This one makes use of seaborn's light_palette. Not recommended for plots when 
    params contains multiple rows. Other options include dark, cubehelix and diverging.
    '''
    labels      = {1: {1: 'Ind 0', 2: 'Ind 0.01', 3: 'Ind 0.05', 4: 'Ind 0.15'}
                   }
    figs, AX = sim.plot_model(plot_index, ym, e=em, titles=titles, labels=labels, palette=palette) 
    
    