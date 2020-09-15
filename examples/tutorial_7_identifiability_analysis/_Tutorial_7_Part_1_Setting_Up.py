import setup_bmss                   as lab
import BMSS.models.setup_sg         as ssg

import BMSS.models.model_handler as mh
'''
Tutorial 7 Part 1: Setting Up
- Create symbolic variables for using strike-goldd

'''

if __name__ == '__main__':
    '''
    A priori identifiability analysis allows you to determine whether or not the
    states or parameters of your model are identifiable based on which parameters
    are ficed beforehand and which states are measured during he experiment.
    
    Unlike numerical integration, this type of analysis requires symbolic algebra and 
    the model functions from other tutorials cannot be used. 
    '''
    
    '''
    Separating the settings/arguments for your analysis from your main code improves
    readability and convenience during reuse and modification. In addition, it also 
    prevents accidental modifications to your code when tweaking the settings/arguments.
    
    All BMSS analysis modules have an associated "setup"  module that can allows
    you to manage your settings/arguments via a .ini file. In each case, these 
    functionalities are available.
    
    1. Reading the .ini file into a dictionary.
    2. Compiling the arguments from the dictionary for use in BMSS analysis modules.
    3. Wrapping steps 1 and 2 into a single function when working with models in the database.
    4. Generation of a .ini template for use as a settings file.
    
    The steps automatically convert the information in the .ini files into arguments
    that can be fed directly into BMSS functions. The settings files for different types
    of analysis are all very similar. This allows you to copy and paste sections as 
    appropriate.
    '''
    
    '''
    1. Reading the Settings File
    '''
    filename    = 'settings_sg.ini' 
    config_data = ssg.from_config(filename)
    
    '''
    Note: In order to speed up calculations, provide parameter vaues for 
    fixed_parameters where possible.
    '''
    
    '''
    2. Compiling Arguments
    '''
    core_model = mh.from_config('Monod_Inducible.ini')
    
    user_core_models = {core_model['system_type']: core_model}
    
    sg_args, config_data, variables = ssg.get_strike_goldd_args(filename, 
                                                        user_core_models = user_core_models,
                                                        write_file       = False)
    
    print('Keys in sg_args[1]: ')
    print(sg_args[1].keys())
    print()
    
    '''
    sg_args is a dictionary in the form {model_num: model} where a model contains
    information on the system of equations, the number of unknown parameters and
    other arguments required for running the strike-goldd algorithm.
    
    The keys are as follows:
    'h'      : A 1 column Matrix of states that measured during the experiment.
    'x'      : A 1 column Matrix of states in for the model
    'p'      : A 1 column Matrix of unknown parameters.
    'f'      : A 1 column Matrix of differential equations for each state in order.
    'u'      : A dictionary where the keys are the inputs and the values are the number of non-zero derivatives.
                For an inducer/repressor system, use no. of inducer/repressor concentrations minus one.
    'ics'    : A dictionary where the keys are the states and the values are their initial conditions.
                Note that values are represented using sympy's Float class and not the python float.
    'decomp' : A list of lists of states that make up a submodel for analysis.
    
    On Decomposition
    Due to the computational cost of symbolic algebra, large models need to be broken down into 
    smaller submodels which can be analyzed more easily. For example, a model with states [x1, x2, x3]
    can be broken down  and analyzed in the order [[x1, x2], [x1, x3], [x2, x3], [x1, x2, x3]]. 
    During analysis of a submodel, less computation is used as compared to analyzing the full model. 
    When parameters/states have been found to be identifiable/observable, the number of unknown 
    parameters/states to check decreases, eventually allowing the full model to be analyzed.
    
    Note that a complicated model may still require too much computation even after decomposition.
    In such cases, consider simplification/reformulation that approximate the original model.
    
    variables is a nested fictionary in the form {model_num: {param_name: variable}} where variable
    is a sympy Symbol and allows you to manipulate the variables in sg_args.
    '''
    
    print('Differentials for model 1')
    print(sg_args[1]['f'])
    print()
    
    print('variables in variables[1]')
    print(variables[1])
    print()
    
    '''
    3. Wrapping for Models in Database
    
    For models already in the database, we can combine the above steps into a single 
    function call.
    '''
    sg_args, config_data, variables = ssg.get_strike_goldd_args(filename)
    
    '''
    4. Template Generation
    
    For models already in the database, templates can be generated. Open the output
    file and check its contents.
    '''
    system_types_settings_names = [('BMSS, Monod, Inducible', None),
                                    ]
    
    ssg.make_settings_template(system_types_settings_names, filename='settings_sg_template.ini')
    
    
    