import numpy             as np
from numba               import jit
from pandas              import DataFrame
from scipy.stats         import norm
from scipy.integrate     import odeint

###############################################################################
#Sampler Algorithm
###############################################################################
def sampler(guess,     priors,    step_size, 
            trials=10000, skip=[], bounds={}, blocks=[], SA=True, 
            likelihood_function=None, 
            likelihood_args={}):
    
    accepted = []
    rejected = []
    
    temp               = convert_input(guess, priors, step_size, skip=skip, bounds=bounds, blocks=blocks) 
    blocks_dict        = temp['blocks_dict']
    bounds_dict        = temp['bounds_dict']
    params_array       = temp['params_array']
    param_names        = temp['param_names']
    prior_distribution = temp['prior_distribution']
    prior_index        = temp['prior_index']
    step_size_rvs      = temp['step_size_rvs']

    log_prior_curr      = None
    log_likelihood_curr = None
    p_curr              = None
    
    theta_curr  = params_array.copy()
    block_index = 0
    for i in range(trials):
        #Transition
        block            = blocks_dict[block_index]
        theta_new        = theta_curr.copy()
        theta_new[block] = transition(theta_curr[block], step_size_rvs[block])

        block_index += 1

        if block_index == len(blocks_dict):
            block_index  = 0
        
        #Check bounds
        skip = any(param < 0 for param in theta_new)
        
        for index in bounds_dict:
            lb, ub = bounds_dict[index]
            if theta_new[index] > ub or theta_new[index] < lb:
                skip = True
                break

        if skip:
            skip = False
            step = theta_new
            rejected.append(step)
            continue
        
        #Calculate posterior
        if log_prior_curr == None:
            p_curr, log_prior_curr, log_likelihood_curr = get_log_posterior(theta_curr, prior_index, prior_distribution, likelihood_function, likelihood_args)
        
        p_new, log_prior_new, log_likelihood_new = get_log_posterior(theta_new, prior_index, prior_distribution, likelihood_function, likelihood_args)
                
        #Calculate acceptance
        p_accept = get_exp_substract(p_new, p_curr) 
        
        #Compare with random number
        test   = np.random.rand()
        if SA == True:
            test = test**(1-1*i/trials)
        accept = p_accept > test
        
        #Collect sample
        if accept:
            theta_curr          = theta_new
            log_likelihood_curr = log_likelihood_new
            log_prior_curr      = log_prior_new
            p_curr              = p_new
            accepted.append(theta_new)
 
        else:
            rejected.append(theta_new)
    
    accepted = DataFrame(np.array(accepted), columns=param_names) if accepted else DataFrame(columns=param_names)
    rejected = DataFrame(np.array(rejected), columns=param_names) if rejected else DataFrame(columns=param_names)
    return {'a': accepted, 'r': rejected}

@jit(nopython=True)
def get_exp_substract(a, b):
    return np.exp(a-b)

###############################################################################
#Conversion
###############################################################################    
def check_input(guess, priors, step_size={}, skip=[], bounds={}, blocks=[]):
    if type(guess) == dict:
        guess_keys = guess.keys()
            
    elif type(guess) == DataFrame:
        guess_keys = guess.columns
    else:
        raise Exception('Guess is neither dictionary nor DataFrame.')
    
    if not all([type(key) == str for key in guess_keys]):
        raise Exception('Parameter names must be strings.')
        
    for key in step_size:
        if key not in guess_keys:
            raise Exception('Key ' + key + ' in step_size not in present in guess_keys.')
    
    for key in priors:
        if key not in guess_keys:
            raise Exception('Key ' + key + ' in priors not in present in guess_keys.')
    
    for key in skip:
        if key not in guess_keys:
            raise Exception('Key ' + key + ' in skip not in present in guess_keys.')
    
    for key in bounds:
        if key not in guess_keys:
            raise Exception('Key ' + key + ' in bounds not in present in guess_keys.')
        if len(bounds[key]) != 2:
            raise Exception('Bounds[' + key + '] must be of length 2: [lower_bound, upper_bound]')
        if bounds[key][0] > bounds[key][1]:
            raise Exception('Bounds[' + key + ']: lower_bound must be smaller than upper_bound.')
        if guess[key] < bounds[key][0] or guess[key] > bounds[key][1]:
            raise Exception('Value of guess outside bounds for key: ' + key)
            
    for block in blocks:
        for key in block:
            if key not in guess_keys:
                raise Exception('Key ' + key + ' in blocks not in present in guess_keys.')


def convert_input(guess, priors, step_size, skip=[], bounds={}, blocks=[]):
    
    check_input(guess, priors, step_size, skip=skip, bounds=bounds, blocks=blocks)
    
    guess_dict         = params_to_dict(guess)
    params_array       = params_to_array(guess_dict)[0]
    prior_distribution = get_prior_distribution(priors) if priors else None
    prior_index        = get_prior_index(guess, priors) if priors else []
    param_names        = list(guess_dict.keys())
    name_to_num        = {name: num for num, name in enumerate(param_names)}
    skip_index         = [name_to_num[name] for name in skip]
    blocks_array       = [[name_to_num[name] for name in block ] for block in blocks ]
    blocks_dict        = {}
    bounds_dict        = {name_to_num[name]: bounds[name] for name in bounds}
    step_size1         = {key: step_size[key] if key in step_size else guess[key]/15 if 'n' != key[0] else guess[key]/10 for key in guess_dict}
    step_size_rvs      = np.array([norm(0, step_size1[key]).rvs for key in step_size1])
    
    n = 0
    for i in range(len(guess)):
        if i in skip_index:
            continue
        
        in_block = False
        for block in blocks_array:
            if i in block:
                blocks_dict[n] = block
                in_block       = True
                break
        if not in_block:
            blocks_dict[n] = [i]
        n += 1
    
    result = {'blocks_array'      : blocks_array,
              'blocks_dict'       : blocks_dict,
              'bounds_dict'       : bounds_dict,
              'params_array'      : params_array,
              'param_names'       : param_names,
              'prior_distribution': prior_distribution,
              'prior_index'       : prior_index,
              'skip_index'        : skip_index,
              'step_size_rvs'     : step_size_rvs,
              }
    return result

def get_default_step_size(guess):
    if type(guess) == dict:
        return {key: guess[key]/15 if 'n' != key[0] else guess[key]/10 for key in guess}
    else:
        raise Exception('Guess is not a dict.')

def params_to_dict(params):
    if type(params) == dict:
        return params
    if type(params) == DataFrame:
        params_dict = params.to_dict('list')
        #Ensure that values are not enclosed in lists
        for key in params_dict:
            if type(params_dict[key]) == list:
                params_dict[key] = params_dict[key][0] 
        return params_dict
    else:
        raise Exception('Params must be a dict or DataFrame.')
        
def params_to_array(params):
    if type(params) == np.ndarray:
        return params
    elif type(params) == dict:
        result = np.array([row for row in params.values()])
        if type(result[0]) == np.ndarray:
            return result.T
        else:
            return np.array([result])
    elif type(params) == DataFrame:
        return params.to_numpy()
    else:
        raise Exception('Params is neither np.ndarry, dict nor DataFrame.')
 
###############################################################################
#Transition
###############################################################################
def transition(theta, step_size_rvs):
    delta = np.array([rvs() for rvs in step_size_rvs])
    return theta + delta

###############################################################################
#Posterior Calculation and Acceptance
###############################################################################
def get_log_posterior(theta, prior_index, prior_distribution, likelihood_function, likelihood_args):
    log_prior      = get_log_prior(theta[prior_index], prior_distribution)
    log_likelihood = get_log_likelihood(theta, likelihood_function=likelihood_function, likelihood_args=likelihood_args)
    
    log_posterior  = log_prior + log_likelihood

    return log_posterior, log_prior, log_likelihood

###############################################################################
#Likelihood and Prior Calculation
###############################################################################
def get_log_likelihood(params_array, likelihood_function=None, likelihood_args={}):
    return likelihood_function(params_array=params_array, **likelihood_args)

def get_log_prior(params={}, priors={}):
    '''
    Pass in a dicts of params and priors OR np.arrays of params and priors
    '''
    if not priors:

        return 0
    
    elif type(priors) == dict:  
        if type( priors[next(iter(priors))] ) == list:
            prior_distribution = get_prior_distribution(priors)
            params_array       = np.array([params[key] for key in priors.keys()])
            return get_log_sum(prior_distribution.pdf(params_array))
        else:
            return get_log_sum(np.array([priors[key].pdf([params[key]]) for key in priors]))
        
    else: 
        #Assumes params is already an array and has been sliced appropriately
        #Assumes priors is already a ditribution
        return get_log_sum(priors.pdf(params))

def get_prior_index(params, priors):
    return np.array([pair[0] for pair in enumerate(params) if priors.get(pair[1], False)])

def get_prior_distribution(priors):  
    values      = np.array(list(priors.values()))   
    return norm(values[:,0], values[:,1])

@jit(nopython=True)
def get_log_sum(a):
    return np.log(a).sum()