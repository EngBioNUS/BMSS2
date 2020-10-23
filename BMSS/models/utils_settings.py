import numpy  as np
import pandas as pd

###############################################################################
#Supporting Functions for Reading Strings into Python
###############################################################################    
def eval_init_string(string):
    try:
        result = string_to_array(string)
        result = {i+1: result[i] for i in range(len(result))}
    except:
        result        = string_to_dataframe(string)
        result.index += 1
        result        = result.T.to_dict('list')

    for key in result:
        if any([type(x) == str for x in result[key]]) == str:
            raise Exception('Error in reading initial values. There is likely a missing comma(s).')
        try:
            result[key] = np.array(result[key])
        except:
            raise Exception('Error in reading initial values. Ensure you input is list-like.')
    return result

def eval_tspan_string(string):
    if string:
        try:
            return string_to_linspace(string)
        except:
            return np.array(eval(string.replace('\n', '')))
    else:
        return [np.linspace(0, 600, 31)]

def eval_params_string(string):
    return string_to_dataframe(string)

def string_to_linspace(string):
    '''
    Use this when you expect arguments for numpy.linspace
    '''
    try:
        return [np.linspace(*segment) for segment in eval('[' + string +']')]
    except:
        try:
            return [np.linspace(*segment) for segment in eval(string)]
        except:
            return np.array(eval(string))

def string_to_list(string):
    '''
    Use this when you expect a list of numbers
    '''
    string1 = string.replace('\n', ',')
    lst     = [s.strip() for s in string1.split(',')]
    lst     = [s for s in lst if s]
    string1 = ', '.join(lst)

    try:
        return eval('[' + string1 +']')
    except:
        return eval(string1)

def string_to_list_string(string):
    '''
    Use this when you expect a list of strings
    '''
    string1 = string.replace('[', '').replace(']', '').replace('\n', ',')
    lst     = [s.strip() for s in string1.split(',')]
    lst     = [s for s in lst if s]

    return lst
    
def string_to_array(string):
    '''
    Use this when you expect a list that can be converted into a numpy array.
    '''
    return np.array(string_to_list(string))
        
def string_to_dict(string):
    '''
    Use this when you expect a dictionary
    '''
    result = [s.strip() for s in split_at_top_level(string)]
    result = [line.split('=') for line in result ]
    result = [[lst[0].strip(), '='.join(lst[1:]).strip()] for lst in result]
    
    result = {pair[0]: try_eval(pair[1]) for pair in result}    
    
    return result

def string_to_dict_array(string):
    '''
    Use this when you expect a dictionary and expect the values to be numpy arrays
    '''
    temp = string_to_dict(string)
    try:
        iter(temp[next(iter(temp))])
        return {key: np.array(temp[key])  for key in temp}
    except:
        return {key: np.array([temp[key]])  for key in temp}
    
def string_to_dataframe(string):
    '''
    Use this when you expect a dictionary and want to convert it into a DataFrame
    '''
    return pd.DataFrame(string_to_dict_array(string))
    
def split_at_top_level(string, delimiter=','):
    '''
    Use this for nested lists.
    This is also a helper function for string_to_dict.
    '''
    nested = []
    buffer = ''
    result = []
    matching_bracket = {'(':')', '[':']', '{':'}'}
    
    for char in string:
        if char in ['[', '(', '{']:
            nested.append(char)
            buffer += char
        
        elif char in [']', ')', '}']:
            if char == matching_bracket.get(nested[-1]):
                nested = nested[:-1]
                buffer += char
            else:
                raise Exception('Mismatched brackets.' )
        elif char == delimiter and not nested:
            if buffer:
                result.append(buffer)
                buffer = ''
        else:
            buffer += char
    if buffer:
        result.append(buffer)
    return result

def try_eval(x):
    '''
    Attempts to convert string to numbers.
    '''
    try:
        return eval(x)
    except:
        return x