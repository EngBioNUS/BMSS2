from os.path import dirname, join

###############################################################################
#Globals
###############################################################################
model_functions_directory = join(dirname(__file__), 'model_functions')

###############################################################################
#Functions
###############################################################################
def model_to_code(core_model,  use_numba=True, local=False, mode='w'):
    header = 'import numpy as np\n'
    if use_numba:
        header += 'from numba import jit\n\n' + '@jit(nopython=True)\n'
    
    result  = header + 'def model_' + core_model['system_type'].replace(', ', '_') + '(y, t, params):\n' 
    
    states     = states_to_code(core_model['states'])
    params     = params_to_code(core_model['parameters'] + core_model['inputs'])
    equations  = equations_to_code(core_model['equations'], core_model['states'])
    result    += '\n\n'.join([states, params, equations])
    
    filename = core_model['system_type'].replace(', ', '_') + '.py'
    if mode == 'w' or mode == 'a':
        export_code(result, filename, local, mode)
    return result

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
    temp    = ['\t'*indent + params[i] + ' '*(longest - len(params[i]) + 1) + '= params[' + str(i) + ']' for i in range(len(params))]
    result  = '\n'.join(temp)
    
    return result

def equations_to_code(equations, states, indent=1):
    '''
    Excepts a list of strings corresponding to equations and formats them.
    Assumes the last block of strings contains the differentials.
    
    E.g. ["a=1","","ds=a**2","dx=a**3"]
    will return the following.
    "
    a = 1
    
    ds = a**2
    dx = a**3
    
    return np.array([ds, dx])
    "
    '''
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
    if diff:
        blocks.append([diff, expr])
                
    temp = []
    for block in blocks:
        if temp:
            temp.append('\t'*indent)
        temp.append(equations_to_code_helper(*block, indent=indent))
    
    return_value = '\t'*indent + 'return np.array([' + ', '.join(diff) +'])' 
    
    if len(diff) != len(states):
        message = ' '.join(['The final block of equations contains', 
                            str(len(diff)),
                            'equations. However, the model has', 
                            str(len(states)),
                            'states.'
                            ])
        raise Exception(message)
        
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
    
    export_models([__model__])