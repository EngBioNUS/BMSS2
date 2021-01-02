import keyword
import string
from   pathlib import Path
from   runpy   import run_path

###############################################################################
#Non-Standard Imports
###############################################################################
try:
    from .model_coder import equations_to_code, model_to_code
except:
    from model_coder import equations_to_code, model_to_code
    
punctuation = string.punctuation.replace('_', '')

def check_model_terms(model):
    states    = model['states']
    params    = model['parameters']
    inputs    = model.get('inputs', [])
    equations = model['equations']
    
    states_set = set(states)
    params_set = set(params)
    inputs_set = set(inputs)
    if len(states_set) != len(states):
       return False, 'Multiple occurence of certain states in states.'
    if len(params_set) != len(params):
        return False, 'Multiple occurence of certain parameters in parmeters.'
    if len(inputs_set) != len(inputs):
        return False, 'Multiple occurence of certain inputs in inputs.'
    
    shared = states_set.intersection(params_set, inputs_set)
    if shared:
        return False, 'Found ' + str(shared) + ' in both states, parameters and/or inputs.'
    
    terms    = list(map(get_terms, equations))
    lhs, rhs = [set().union(*s) for s in zip(*terms)]
    
    check_illegal_terms(terms)
    
    defined = lhs.union(states_set, params_set, inputs_set)
    
    undefined = [term for term in rhs if term not in defined]
    
    if undefined:
        return False, 'Undefined terms ' + str(undefined)
    
    unused = [term for term in inputs+params if term not in rhs and '_init' not in term]
    
    if unused:
        return False, 'Unused terms ' + str(unused)
    
    else:
        temp    = states+params+inputs
        var     = ','.join(temp) + '= np.random.rand(' + str(len(temp)) + ')*10'
        conv    = ','.join(temp) + '= list(map(float, [' + ','.join(temp) + ']))'
        y_test  = 'y = [' + ','.join(states) + ']'
        t_test  = 't = 0\ndt = 1e-3'
        p_test  = 'params = ' + ','.join(params+inputs)
        call    = 'y = y + dt*model_' + model['system_type'].replace(', ', '_') + '(y, t, params)'
        
        try:
            eq     = model_to_code(model, use_numba=False, mode=None)
        except Exception as e:
            return False, str(e.args[0])
        
        test_string = '\n\n'.join([eq, var, conv, y_test, t_test, p_test, call, call])
        
        filename    = Path(__file__).parent/ 'checker_do_not_run.py'
        for i in range(10):
            try:
                
                with open(filename, 'w') as file:
                    file.write(test_string)
                run_path(filename)
                
            except ZeroDivisionError:
                if i < 9:
                    pass
                else:
                    return False, 'Division by zero detected.'
            except IndexError:
                return False, 'Length of return value is not equal to length of states.'
            except Exception as e:
                return False, str(e.args[0])
            else:
                break
            
    return True, ''

def get_terms(f):
    '''
    Supporting function for make_group. Extracts all terms in an expression.
    '''
    global punctuation
    
    fs = f.strip()
    fs = f.split('#')[0]
    
    if not fs:
        return set(), set()
    
    eq = [s.strip() for s in  fs.split('=', 1)]
    
    if len(eq) < 2:
        raise Exception('Line is not an equation: ' + f)

    if any(list(map(illegal_equal, eq))):
        raise Exception('Syntax error. Illegal use of "=" symbol in line: '+ f)
    
    tr = str.maketrans(punctuation, ','*len(punctuation))
    eq = [set([i for i in s.replace(' ', '').translate(tr).split(',') if i and not isnum(i)]) for s in eq]
    
    return eq

def isnum(x):
    try:
        float(x)
        return True
    except:
        pass
    try:
        float(x+'0')
        return True
    except:
        return False

def illegal_equal(x):
    S = x.split('==')
    if S[0] == '' or S[-1]=='':
        return True
    
    for i in range(len(S)):
        s = S[i].split('=')

        if len(s) > 1:
            return True
    return False

def check_illegal_terms(terms):
    for term in terms:
        for illegal_term in ['np']:
            if term == illegal_term:
                raise Exception('Illegal term detected: ' + term)
        
        for illegal_term in keyword.kwlist:
            if term == illegal_term:
                raise Exception('Illegal term detected: ' + term)
                
    return
    
if __name__ == '__main__':
    __model__ = {'id'          : 'bmss01001',
                 'system_type' : 'Inducible, ConstInd',
                 'states'      : ['mRNA', 'Pep'], 
                 'parameters'  : ['syn_mRNA', 'deg_mRNA', 'syn_Pep', 'deg_Pep', 'Ki'],
                 'inputs'      : ['Ind'],
                 'equations'   : ['dmRNA = syn_mRNA*Ind/(Ind + Ki) - deg_mRNA*mRNA',
                                  '',
                                  'dPep  = syn_Pep*mRNA - 1/(deg_Pep)'
                                  ],
                 'ia'          : ''
                 
                 }
    
    __model__ = {'id'          : 'bmss01002',
                  'system_type' : 'BMSS, GrowthModel, MortalityPhase',
                  'states'      : ['OD'], 
                  'parameters'  : ['N0', 'm1', 'm2', 'tc1', 'tc2'],
                  'inputs'      : ['t'],
                  'equations'   : ['a = 1 / (tc1 ** m1)',
                                  'b = 1 / (tc2 ** m2)',
                                  '',
                                  'dOD = N0 * (a * m1 * (t ** (m1-1)) - b * m2 * (t ** (m2-1))) * (2.7183**(a * (t ** m1) - b * (t ** m2)))',
                                  ],
                  'ia'          : ''
                 
                  }
    
    r = check_model_terms(__model__)
    print(r)