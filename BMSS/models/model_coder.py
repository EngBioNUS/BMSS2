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
#Supporting Functions
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
    Assumes the differentials are given by "d"+state_name.
    
    E.g. If the states are x1 and x2, the return value is np.array([x1, x2])
    
    '''
    result = ''
    blocks = []
    lhs    = []
    rhs    = []
    diff   = {'d'+state: False for state in states}
    for equation in equations:
        if equation.strip():
            lhs_, rhs_ = [s.strip() for s in equation.split('=')]
       
            lhs.append(lhs_)
            rhs.append(rhs_)
            
            if lhs_ in diff:
                diff[lhs_] = True
        else:
            if lhs:
                blocks.append([lhs.copy(), rhs.copy()])
                lhs = []
                rhs = []
            else:
                pass
    if lhs:
        blocks.append([lhs, rhs])
                
    temp = []
    for block in blocks:
        if temp:
            temp.append('\t'*indent)
        temp.append(equations_to_code_helper(*block, indent=indent))
    
    
    return_value = '\t'*indent + 'return np.array([' + ', '.join(diff.keys()) + '])'
    
    if not all(diff.values()):
        missing = [lhs_ for lhs_ in diff if not diff[lhs_]]
        message = 'The following differentials are missing: {missing}'.format(missing=missing)
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
    
    equations = __model__['equations']
    states    = __model__['states']
    
    equations = equations[::-1]
    
    print(equations_to_code(equations, states))
    
    