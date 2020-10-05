import importlib
import re
from   itertools import product
from   pandas    import DataFrame
from   textwrap  import dedent

###############################################################################
#Globals
###############################################################################
mod_prefix = 'BMSS'

###############################################################################
#Supporting Functions for Import
###############################################################################
def split_line(line, delimiter=','):
    result = []
    for x in line.split(delimiter):
        x1 = x.strip()
        if len(x1) > 0:
            result.append(x1)
    return result

def quote(line, quote_char=1):
    q = "'" if quote_char == 1 else '"'
    return [q+x+q for x in line]

###############################################################################
#Import
###############################################################################
def import_txt(filename):
    with open(filename+'.txt', 'r') as file:
        return load_model(file)

def load_model(filestream):
    content_type = ''
    content = {'states'     : {}, 
               'parameters' : [], 
               'inputs'     : {},
               'ics'        : {}, 
               'equations'  : [],
               'known'      : {}, 
               'measured'   : [],
               'decomp'     : []
               }
    filestream1 = filestream.split('\n') if type(filestream) == str else filestream
    for line in filestream1:
        if len(line.rstrip()) == 0:
            continue
        elif line[0] == '%':
            continue
        elif line[0] == '#':
            content_type = line[1:].strip()
        
        elif content_type == 'equations':
            content['equations'].append(line.strip())
        elif content_type in ['inputs', 'known', 'states']:
            line1 = [s.strip() for s in line.strip().split(',')]
            line1 = [s.split('=') for s in line1 if s]
            for pair in line1:
                key, value                 = pair[0].strip(), pair[1].strip()
                content[content_type][key] = eval(value)

        elif content_type == 'decomp':
            line1 = [s.strip() for s in line.strip().replace(']', '[').split('[')]
            line1 = [s.strip() for s in line1 if s and s.strip() != ',']
            line1 = [[ss.strip() for ss in s.split(',')] for s in line1]
            content[content_type].extend(line1)
        else:
            line1 = [s.strip() for s in line.strip().split(',')]
            line1 = [s for s in line1 if s]
            content[content_type].append(line1)
    
    content['ics']    = content['states'].copy()
    content['states'] = [list(content['states'].keys())]
    
    states             = [state for lst in content['states']     for state in lst]
    measured           = [state for lst in content['measured']   for state in lst]
    parameters         = [param for lst in content['parameters'] for param in lst]
    input_conditions   = content['inputs']
    measured_states    = [state for state in states if state in measured]
    unknown_parameters = [param for param in parameters if param not in content['known']]
    
    
    data = {'variables'          : content['states'] + content['parameters'] + list(content['inputs'].keys()),
            'equations'          : content['equations'],
            'measured_states'    : measured_states,
            'states'             : states,
            'unknown_parameters' : unknown_parameters,
            'input_conditions'   : input_conditions,
            'ics'                : content['ics'],
            'known_params'       : content['known'],
            'decomposition'      : content['decomp']
            }
        
    return data, content

###############################################################################
#Export as .py
###############################################################################    
def write_to_file(variables, equations, measured_states, states, unknown_parameters, input_conditions, ics, decomposition=[], known_params={}, filename=''):
    text     = '\n\n'.join([export_model(variables, equations),
                            export_args(measured_states, states, unknown_parameters, input_conditions, ics, decomposition, known_params),
                            export_run()])
    if len(filename) > 0:
        with open(filename, 'w') as file:
            file.write(text)
    return text

def export_model(variables, equations):
    global mod_prefix 
    
    header  = '###############################################################################\n#Model\n###############################################################################'
    mod     = mod_prefix + '.strike_goldd_simplified' if mod_prefix else 'strike_goldd_simplified'
    imports = 'from sympy import Matrix, Float, Symbol\nfrom ' + mod + ' import*'
    content = ''
    eq      = ''
    storage = 'variables = {' + ', '.join(["'" + v + "': " + v for group in variables for v in group]) + '}'
    
    ###############################################################################
    #Variables
    ###############################################################################   
    for line in variables:
        if len(line) > 1:
            lhs = ', '.join([x for x in line])
            rhs = '[Symbol(' + 'x' + ') for x in [' + ', '.join([x for x in quote(line)]) + ']]'
            content += lhs + ' = ' + rhs + '\n'
        elif len(line) == 1:
            lhs = line[0]
            rhs =  "Symbol('" + lhs + "')"
            content += lhs + ' = ' + rhs + '\n'
        else:
            continue

    ###############################################################################
    #Equations
    ############################################################################### 
    eq = '\n'.join([line for line in equations]) 

    result = '\n\n'.join([imports, header, content, eq, storage])
    return result

def export_args(measured_states, states, unknown_parameters, input_conditions, ics, decomposition, known_params):
    result  = '###############################################################################\n#Specify Input for IA\n###############################################################################\n'
    result += '#User makes changes here\n'
    
    def make_matrix(name, lst):
        return name + ' = Matrix([' + ', '.join(lst) + '])\n' 
    
    diff    = get_differential(states)
    result += make_matrix('measured_states   ', measured_states)
    result += make_matrix('states            ', states)
    result += make_matrix('unknown_parameters', unknown_parameters)
    result += make_matrix('diff              ', diff)
    result += get_input_conditions(input_conditions)
    result += get_ics(ics)
    result += get_decomposition(decomposition)
    
    ###############################################################################
    #Substitutions
    ###############################################################################
    if known_params:
        subs = get_substitution(known_params, unknown_parameters)
        subs += 'diff = diff.subs(known_parameters.items())'
        
        result += '\n\n' + subs
    
    return result

def get_differential(states):
    return ['d' + state for state in states]

def get_ics(ics):
    temp    = []
    for state in ics:
        value = str(state) + ': Float(' + str(ics[state]) + ', 3)'
        temp.append(value)

    return 'init_conditions    = {' + ', '.join(temp) + '}\n'

def get_input_conditions(input_conditions):
    temp    = []
    for state in input_conditions:
        value = str(state) + ': ' + str(input_conditions[state])
        temp.append(value)
           
    return 'input_conditions   = {' + ', '.join(temp) + '}\n'

def get_decomposition(decomposition):
    d = 'decomposition      = ['
    j = ',\n' + ' '* (len(d))
    c = '\n' + ' '* (len(d)) + ']\n'
    return d + j.join([ '[' + ', '.join(group) + ']' for group in decomposition]) + c

def get_substitution(known_params, unknown_parameters):
    temp    = []
    for param in known_params:
        if param in unknown_parameters:
            continue
        
        value = str(param) + ' : ' + str(known_params[param])
        temp.append(value)

    return 'known_parameters = {' + ', '.join(temp) + '}\n'
    
def export_run():
    
    s = '''
    ###############################################################################
    #Call Strike-Goldd
    ###############################################################################
    def run_strike_goldd():
        start_time = time()
        x_aug_dict = strike_goldd(measured_states, 
                                  states, 
                                  unknown_parameters, 
                                  input_conditions, 
                                  diff, 
                                  init_conditions, 
                                  decomposition)
        print("Total time: ",time()-start_time)
        print(x_aug_dict)
        return x_aug_dict
    
    if __name__ == '__main__':
        pass
    '''
    return dedent(s)

###############################################################################
#Permutational IA
###############################################################################
def permutational_IA(data):
    '''
    Takes in an imported model and returns a DataFrame of IA results for all possible combinations of observed variables/known parameters.
    '''
    param_perms  = permute_list(data['params'])
    output_perms = permute_list(data['outputs'])

    template = {**{key+'_Known':1 for key in data['params']},
                **{key+'_Known':0 for key in data['states']},
                **{key+'_Identifiable':1 for key in data['params']},
                **{key+'_Identifiable':0 for key in data['states']}
                }

    first       = True
    result_list = []

    for i in range(len(param_perms)):
        for ii in range(len(output_perms)):

            unknown_params   = param_perms[i]
            observed_outputs = output_perms[ii]
            print('unknown_params', unknown_params)
            print('observed_outputs', observed_outputs)

            IA_result = template.copy()
            for key in unknown_params:
                IA_result[key+'_Known'] = 0
            for key in observed_outputs:
                IA_result[key+'_Known'] = 1
            
            write_to_file(data, 'dummy.py', params=unknown_params, outputs=observed_outputs)

            if first:
                d     = importlib.import_module('dummy')
                first = False
            else:
                importlib.reload(d)
                
            try:
                result = d.runIA()
                
            except ZeroDivisionError:
                print('Skipping due to ZeroDivisionError')
                print('############################################')
                for key in IA_result:
                    IA_result[key] = -1
            else:
                print('############################################')
                for key in result:
                    IA_result[str(key) + '_Identifiable'] = int(result[key])

            
                result_list.append(list(IA_result.values()))

    result_dataframe = DataFrame(data=result_list, columns=list(template.keys()))
    
    return result_dataframe

def permute_list(x):
    '''
    First return value is all the combinations and permutations of the list x.
    '''
    result = []
    perms  = permute_true_false(len(x))
    for p in perms:
        temp = tuple([x[i] for i in range(len(p)) if p[i]])
        if temp:
            result.append(temp)

    return result
    
def permute_true_false(n):
    result = list(product([0, 1], repeat=n))
    
    return result

###############################################################################
#Interconversion with ConfigParser
###############################################################################
def txt_to_configparser(data, filename):
    try:
        configparser = importlib.import_module('configparser')
    except:
        pass
    config       = configparser.ConfigParser()

    for key in data:
        config[key] = {key: data[key]}
        
    with open(filename, 'w') as configfile:
        config.write(configfile)

s = '''

#parameters
vm,
synm1, synp1, 
degm, degp

#inputs
u = 1

#measured
Inde,
m1, p1

#known
degm  = 0.15,
synm1 = 1e-6,
synp1 = 0.01

#equations
dInde = -vm*Inde + u
dIndi =  vm*Inde
dm1 = synm1*Indi - degm*m1
dp1 = synp1*m1 - degp*p1

#states
Inde = 1,
Indi = 1,
m1   = 1, 
p1   = 1

#decomp
[Inde, Indi],
[m1, p1],
[Inde, Indi, m1, p1]
'''

if __name__ == '__main__':
    from   io import StringIO
    
    data, content = load_model(StringIO(s))
    
    model_name = 'inducible_with_input'
    filename    = model_name + '.py'
    
    code = write_to_file(**data, filename= model_name + '.py')    
    mod  = importlib.import_module( model_name)
    
    result = mod.run_strike_goldd()