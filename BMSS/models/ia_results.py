import os
import pandas  as     pd
import yaml    as     ya
from   io      import StringIO
from   pathlib import Path

###############################################################################
#Non-Standard Imports
###############################################################################
try:
    from . import model_handler as mh
except:
    import model_handler as mh

###############################################################################
#Globals
###############################################################################
ia_results_folder = Path(os.path.dirname(__file__)) / 'ia_results'

###############################################################################
#IA Result Handling
###############################################################################
def export_sg_results(sg_results, variables, config_data, user_core_models={}, filename='sg_results.yaml'):
    '''
    Exports the results as a human-readable .yaml file
    '''
    yaml_dict = {}
    
    for key in sg_results:
        system_type = config_data[key].get('system_type')
        core_model  = user_core_models.get(system_type)

        if not core_model:
            core_model = mh.quick_search(system_type)
            
        fixed_parameters = list(config_data[key]['parameter_values'].keys())
        
        nested_dict = make_new_nested_dict(sg_result        = sg_results[key],
                                           model_variables  = variables[key],
                                           core_model       = core_model,
                                           fixed_parameters = fixed_parameters,
                                           **config_data[key]
                                           )
        nested_dict    = {**{'system_type' : system_type}, **nested_dict}
        yaml_dict[key] = nested_dict
    
    outfile = filename if filename[-5:] == '.yaml' else filename + '.yaml'
    
    
    try:
        with open(outfile, 'w') as file:
            ya.dump(yaml_dict, file, sort_keys=False)
    except FileNotFoundError:#user wants to use relative path
        cwd        = Path(os.getcwd())
        rel_path   = Path(outfile)
        folder     = rel_path.parent
        stem       = rel_path.stem 
        ext        = rel_path.suffix
        outfile    = stem + ext if ext == '.yaml' else stem + ext + '.yaml'
        
        os.mkdir(folder)
        
        full_path = cwd / folder / outfile
        
        with open(full_path, 'w') as file:
            ya.dump(yaml_dict, file, sort_keys=False)
        
    except Exception as e:
        raise e
        
    return yaml_dict
    
def dump_sg_results(sg_results, variables, config_data, user_core_models={}, save=False):
    '''
    Adds sg_results for each core_model to the csv file indexed under core_model['ia']
    where the system_type of each core_model is specified in config_data.
    
    If the core_model is not in the database, you must provide your own core_model 
    in user_core_models and index it under its system_type.
    '''
    new_rows = {}
    for key in sg_results:
        system_type = config_data[key].get('system_type')
        core_model  = user_core_models.get(system_type)

        if not core_model:
            core_model = mh.quick_search(system_type)
        
        fixed_parameters = list(config_data[key]['parameter_values'].keys())
        
        new_row = update_core_model(sg_result        = sg_results[key],
                                    model_variables  = variables[key],
                                    core_model       = core_model,
                                    save             = save,
                                    fixed_parameters = fixed_parameters,
                                    **config_data[key]
                                    )
        
        new_rows[key] = new_row
    
    return new_rows

###############################################################################
#Row Generation
###############################################################################
def write_new_row_to_file(sg_result, model_variables, init, input_conditions, fixed_parameters,  measured_states, system_type, core_model, pd_args={}, local=False, **kwargs):
    '''
    Generates a new row by calling make_new_row and updates the file indexed 
    under core_model['ia'] with replacement to prevent duplication. 
    
    The file will be created if it does not exist. model_handler.quick_search 
    is called if the core_model is not provided. 
    '''
    global ia_results_folder
        
    new_row = make_new_row(sg_result, model_variables, init, input_conditions, fixed_parameters,  measured_states, core_model, **kwargs)
    
    
    filename = core_model['ia']
    

    if filename:
        location  = os.getcwd() if local else ia_results_folder
        directory = filename    if local else ia_results_folder / filename 
        
        if filename in os.listdir(location):
            if 'header' not in pd_args:
                pd_args['header'] = [0, 1]
                
            df = pd.read_csv(directory, **pd_args)
            s  = pd.Series(new_row)
            
            if not all(df.columns == s.index):
                raise Exception('Keys in new row do not match csv headers. csv headers: ' + str(df.columns) )
            if len(df.columns) != len(s.index):
                raise Exception('Keys in new row do not match csv headers. csv headers: ' + str(df.columns) )
                
            #Check if inputs are duplicated
            try:
                row_num          = df['known'][s['known'] == df['known']].index[0]
                df.iloc[row_num] = s
                print('Updated row ' + str(row_num) + ' in ' + filename)
            except:
                df = df.append(s, ignore_index=True)
                print('Added row to ' + filename)
        
        else:
            df = pd.DataFrame([new_row], columns=pd.MultiIndex.from_tuples(new_row.keys()))
            df.to_csv(directory, index=False)
            print('Created ' + str(directory) + ' to store strike-goldd results.')
        
    else:
        print('No filename in core_model["ia"]. No files were written.')
    return new_row

def update_core_model(sg_result, model_variables, init, input_conditions, fixed_parameters,  measured_states, system_type, core_model, pd_args={}, save=False, **kwargs):
    '''
    Generates a new row by calling make_new_row and updates the database with replacement 
    if save is True. 
    '''
        
    new_row = make_new_row(sg_result, model_variables, init, input_conditions, fixed_parameters,  measured_states, core_model, **kwargs)
    mh.update_ia(core_model, new_row, save=save)
    
    return new_row

def make_new_row(sg_result, model_variables, init, input_conditions, fixed_parameters,  measured_states, core_model, **kwargs):
    '''
    Generates a row in dictionary form that can be appended to a DataFrame. Each 
    column is a tuple where the first value is "known" or "unknown" and the second
    value is a string variable that corresponds to a state, parameter of input in a
    core_model. Ignores kwargs.
    '''
    new_row = make_new_row_template(core_model, init, input_conditions, fixed_parameters,  measured_states, **kwargs)
    new_row = update_row_with_sg_result(new_row, sg_result, model_variables)
    
    return new_row

def make_new_nested_dict(sg_result, model_variables, init, input_conditions, fixed_parameters,  measured_states, core_model, **kwargs):
    '''
    Generates a nested dict from the return value of make_new_row
    '''
    new_row = make_new_row(sg_result, model_variables, init, input_conditions, fixed_parameters,  measured_states, core_model, **kwargs)
    
    nested_dict = {}
    
    for key, value in new_row.items():
        k1, k2                             = key
        nested_dict.setdefault(k1, {})[k2] = value
    
    return nested_dict

###############################################################################
#Supporting Functions
###############################################################################
def update_row_with_sg_result(row, sg_result, model_variables):
    '''
    Updates the row with information from sg_result and model_variables where
    sg_result is the output from the function strike_goldd and model_variables
    is a dict that maps a str variable in row to a symbolic variable in sg_result.
    '''
    for variable, symbolic in model_variables.items():
        column = 'output', variable
        
        if symbolic in sg_result:
            row[column] = int(sg_result[symbolic])

    return row

def make_new_row_template(core_model, init, input_conditions, fixed_parameters,  measured_states, **kwargs):
    '''
    Creates a dictionary that can be used as a template.
    '''
    new_row    = {}
    states     = core_model['states']
    parameters = core_model['parameters']
    inputs     = core_model['inputs']
    init_      = dict(zip(states, init[1]))

    for column in make_columns(core_model):
        group, variable = column
        
        if group == 'input':
            if check_in_lists(variable, states, measured_states):
                new_row[column] = 1
            elif check_in_lists(variable, parameters, fixed_parameters):
                new_row[column] = 1
            elif variable in inputs:
                new_row[column] = input_conditions[variable]
            else:
                new_row[column] = 0
        elif group == 'init':
            new_row[column] = float(init_[variable])
        else:
            new_row[column] = 1

    return new_row

def check_in_lists(variable, lst1, lst2, negate=False):
    '''
    Supporting function for make_new_row. Do not run.
    
    :meta private:
    '''
    if negate:
        return variable in lst1 and variable not in lst2
    else:
        return variable in lst1 and variable in lst2
    
def make_columns(core_model):
    '''
    Generates column tuples using states and parameters. Inputs are not included
    since 
    '''
    
    second = core_model['states'] + core_model['parameters'] 
    
    left  = [('init', s) for s in core_model['states']] + [('input', s) for s in second + core_model['inputs']]
    right = [('output', s) for s in second]
    return left + right


