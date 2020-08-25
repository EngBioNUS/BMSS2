import configparser
import copy
import importlib
#import ast
import BMSS.models.model_handler as mh
from os.path import dirname, join, basename, splitext

###############################################################################
#Globals
###############################################################################
model_functions_directory = join(dirname(dirname(__file__)), 'models', 'model_functions')

def get_model_function(modelpath):
    filename_w_ext = basename(modelpath)
    filename, _ = splitext(filename_w_ext)
    
    if modelpath == filename_w_ext:
        module = importlib.import_module(filename)
        model_function = getattr(module, 'model_'+filename)
    else:
        module = importlib.import_module('.model_functions.'+ filename, 'BMSS.models')
        model_function = getattr(module, 'model_'+filename)
    print(filename)
    
    return model_function


###############################################################################
# Wrapper Functions
###############################################################################
def read_and_add_model_to_database(filenames):
    '''Wrapper function to read the configuration .ini file and add the
    model to the database.
    Return: the list of models in dict and list of stored models (w/o
    combinations info for more manipulation).
    '''
    model_list, model_stored_list, rowid_list = ([] for i in range(3))

    for filename in filenames:
        # read the configuration ini file and return a dict
        model = read_config(filename)
        model_list.append(model)
        
        model_stored = copy.deepcopy(model)
        
        # remove the key combinations for storage purpose
        model_stored.pop('combinations', None)
        
        # run through the model checker to ensure right model format to be stored
        model_stored = mh.make_core_model(**model_stored)
        
        model_stored_list.append(model_stored)
        
        # add model to database
        #rowid = mh.add_model_to_database(model_stored)
        rowid = mh.add_to_database(model_stored)
        rowid_list.append(rowid)
        print('row id: ', rowid_list)
        
        return model_list, model_stored_list


###############################################################################
#Create model in dict from configuration .ini file
###############################################################################
def read_config(filename):
    config = configparser.ConfigParser()
    model  = {'id'          : '',
              'system_type' : '',
              'states'      : [], 
              'parameters'  : [],
              'combinations': [],
              'inputs'      : [],
              'equations'   : [],
              'ia'          : ''
              }
    with open(filename, 'r') as file:
        config.read_file(file)
        
    for key in config.sections():
        if (key == 'ia') or (key == 'system_type'):
            line = config[key][key].strip()
        elif key == 'equations':
            line = config[key][key].replace('\n', ',').split(',')
            line = [s.strip() if s else '' for s in line]
            line = line if line[0] else line[1:]
        else:
            line = config[key][key].replace('\n', ',').split(',')
            line = [s.strip() for s in line if s]
        
        model[key] = line
        
    return model


###############################################################################
#Functions
###############################################################################
def model_to_code(model_dict,  use_numba=False, local=False, mode='w'):
    
    model_dict_copy = copy.copy(model_dict)
    
#    if isinstance(model_dict_copy['system_type'], str):
#        model_dict_copy['system_type'] = ast.literal_eval(model_dict_copy['system_type'])
    
    header = 'import numpy as np\n\n'
    if use_numba:
        header += 'from numba import jit\n\n' + '@jit(nopython=True)\n'
    
    result  = header + 'def model_' + '_'.join([k.strip() for k in model_dict_copy['system_type'].split(',')])+\
    '(t, y, params = [], comb = []):\n' 
    
    states     = states_to_code(model_dict_copy['states'])
    #params     = params_to_code(model_dict['parameters'] + model_dict['inputs'])
    params     = params_w_comb_to_code(model_dict_copy['parameters']\
                                       + model_dict_copy['inputs'],\
                                       model_dict_copy['combinations'])
    
    equations  = equations_to_code(model_dict_copy['equations'])
    result    += '\n\n'.join([states, params, equations])
    
    #filename = '_'.join(model_dict_copy['system_type']) + '.py'
    filename = '_'.join([k.strip() for k in model_dict_copy['system_type'].split(',')]) + '.py'

    if local:
        filepath = filename
        print(filename, 'has been created.')
    else:
        filepath = join(model_functions_directory, filename)
        print(filename, 'has been created at path', model_functions_directory)
    
    export_code(result, filename, local, mode)
    return result, filepath

###############################################################################
#Export
###############################################################################
def export_code(code, filename='code1.py', local=False, mode='w'):
    global model_functions_directory
    filename1 = filename if local else join(model_functions_directory, filename)
    with open(filename1, mode) as file:
        file.write(code)
    return
    

###############################################################################
#Supportying Functions
############################################################################### 
def states_to_code(states, indent=1):
    longest = len(max(states, key=len))
    temp    = ['\t'*indent + states[i] + ' '*(longest - len(states[i]) + 1) + '= y[' + str(i) + ']' for i in range(len(states))]
    result  = '\n'.join(temp)
    
    return result
    
def params_to_code(params, indent=1):
    longest = len(max(params, key=len))
    
    print(longest)
    temp    = ['\t'*indent + params[i] + ' '*(longest - len(params[i]) + 1) + '= params[' + str(i) + ']' for i in range(len(params))]
    print(temp)
    result  = '\n'.join(temp)
    
    return result

def params_w_comb_to_code(params, combinations, indent=1):
    '''Function to multiple the combinatorial variables to the params.
    Return the params in strings.
    ''' 
    longest = len(max(params, key=len))
    temp = []
    for i, p in enumerate(params):
        strtmp = '\t'*indent + p + ' '*(longest - len(p) + 1) + '= params[' + str(i) + ']'
        for j, c in enumerate(combinations):
            if c == p:
                strtmp += '*'+ 'comb[' + str(j) + ']'
            else:
                pass
        temp.append(strtmp)
    result = '\n'.join(temp)
        
    return result

def add_comb_to_model(model_dict, comb_list):
    '''Add the list of combinatorial parameters' names to be changed into the
    model dictionary.
    '''
    comb_dict = {'combinations':comb_list}
    new_model_dict = copy.deepcopy(model_dict)
    new_model_dict.update(comb_dict)
            
    return new_model_dict
    

def equations_to_code(equations, indent=1):
    result = ''
    blocks = []
    diff = []
    expr = []
    for equation in equations:
        if equation.strip():
            diff_, expr_ = [s.strip() for s in equation.split('=')]
       
            diff.append(diff_)
            expr.append(expr_)
        else:
            if diff:
                blocks.append([diff.copy(), expr.copy()])
                diff = []
                expr = []
            else:
                pass
				
    #print(blocks)
    if diff:
        blocks.append([diff, expr])
                
    temp = []
    for block in blocks:
        if temp:
            temp.append('\t'*indent)
        temp.append(equations_to_code_helper(*block, indent=indent))
    
    return_value = '\t'*indent + 'return np.array([' + ', '.join(diff) +'])' 
    
    result  = '\n'.join(temp) + '\n\n' + return_value
    return result 

def equations_to_code_helper(diff, expr, indent=1):       
    longest = len(max(diff)) 
    temp    = ['\t'*indent + diff[i] + ' '*(longest - len(diff[i]) + 1) + '= ' + expr[i] for i in range(len(diff))]
    result  = '\n'.join(temp)
    return result
    
    


if __name__ == '__main__':
    __model__ = {'system_type' : ['Inducible', 'ConstInd'],    
                 'variables'   : ['Ind', 'mRNA', 'Pep', 'syn_mRNA', 'deg_mRNA', 'syn_Pep', 'deg_Pep', 'Ki'],
                 'states'      : ['mRNA', 'Pep'], 
                 'parameters'  : ['syn_mRNA', 'deg_mRNA', 'syn_Pep', 'deg_Pep', 'Ki'],
                 'inputs'      : ['Ind'],
                 'equations'   : ['dmRNA  = syn_mRNA*Ind/(Ind + Ki)     - deg_mRNA*mRNA',
                                  'dPep   = syn_Pep*mRNA - deg_Pep'
                                  ]
                 }
    
#    code = model_to_code(__model__)
#    export_code(code)