import numpy             as np
from numba               import jit
from pandas              import DataFrame, Series
from scipy.optimize      import basinhopping           as sp_bh
from scipy.optimize      import differential_evolution as sp_de
from scipy.optimize      import dual_annealing         as sp_da
from scipy.stats         import norm

###############################################################################
#Sampler Algorithm
###############################################################################
def differential_evolution(guess, priors={}, skip=[], bounds={}, 
                           likelihood_function=None, 
                           likelihood_args={}, 
                           **scipy_args):
    
    '''
    Minimizes the negative of the posterior function with custom likelihood function.
    Bounds must be provided for ALL parameters
    '''

    accepted   = []
    full_trace = []
    
    temp               = convert_input(guess, priors=priors, skip=skip, bounds=bounds) 
    var_param_index    = temp['var_param_index']
    bounds_array       = temp['bounds_array']
    prior_distribution = temp['prior_distribution'] 
    prior_index        = temp['prior_index']        
    full_param_array   = temp['param_array']
    param_names        = list(guess)
    
    wrapped_posterior   = wrap_log_posterior(var_param_index, full_param_array, prior_index, prior_distribution, likelihood_function, likelihood_args, full_trace)
    wrapped_callback    = wrap_record_trace_de(var_param_index, full_param_array, accepted)
    
    res = sp_de(wrapped_posterior, bounds=bounds_array, callback=wrapped_callback, **scipy_args)
    
    accepted, full_trace = return_df(accepted, full_trace, columns=param_names)
    
    return {'a': accepted, 's': res, 'f': full_trace}
        
def basinhopping(guess, priors={}, skip=[], bounds={}, step_size=0.1, 
                 step_size_is_ratio=True,
                 likelihood_function=None, 
                 likelihood_args={}, 
                 **scipy_args):
    
    '''
    Minimizes the negative of the posterior function with custom likelihood function.
    '''
    
    accepted   = []
    rejected   = []
    full_trace = []

    temp               = convert_input(guess, priors=priors, skip=skip, bounds=bounds, step_size=step_size) 
    var_param_index    = temp['var_param_index']
    var_param_array    = temp['var_param_array']
    bounds_array       = temp['bounds_array']
    prior_distribution = temp['prior_distribution'] 
    prior_index        = temp['prior_index']        
    full_param_array   = temp['param_array']
    step_size_array    = temp['step_size_array']
    param_names        = list(guess)

    wrapped_posterior   = wrap_log_posterior(var_param_index, full_param_array, prior_index, prior_distribution, likelihood_function, likelihood_args, full_trace)
    wrapped_accept_test = wrap_bounds_test(bounds_array, *scipy_args.get('accept_test', []))
    wrapped_callback    = wrap_record_trace_bh(var_param_index, full_param_array, accepted, rejected)
    wrapped_transition  = wrap_transition(var_param_array, step_size=step_size_array, step_size_is_ratio=step_size_is_ratio)

    res = sp_bh(wrapped_posterior, x0=var_param_array, take_step=wrapped_transition, callback=wrapped_callback, accept_test=wrapped_accept_test, minimizer_kwargs={'method': 'trust-constr'}, **scipy_args)
    
    accepted, rejected, full_trace = return_df(accepted, rejected, full_trace, columns=param_names)
    
    return {'a': accepted, 'r': rejected, 's': res, 'f': full_trace}

def dual_annealing(guess,     priors={},  skip=[], bounds={},
                   likelihood_function=None, 
                   likelihood_args={}, 
                   **scipy_args):
    '''
    Minimizes the negative of the posterior function with custom likelihood function.
    '''
    accepted   = []
    contexts   = []
    full_trace = []

    temp               = convert_input(guess, priors=priors, skip=skip, bounds=bounds, bound_max=10) 
    var_param_index    = temp['var_param_index']
    var_param_array    = temp['var_param_array']
    bounds_array       = temp['bounds_array']
    prior_distribution = temp['prior_distribution'] 
    prior_index        = temp['prior_index']        
    full_param_array   = temp['param_array']
    param_names        = list(guess)
    
    wrapped_posterior   = wrap_log_posterior(var_param_index, full_param_array, prior_index, prior_distribution, likelihood_function, likelihood_args, full_trace)
    wrapped_callback    = wrap_record_trace_da(var_param_index, full_param_array, accepted, contexts)

    res = sp_da(wrapped_posterior, bounds=bounds_array, x0=var_param_array, callback=wrapped_callback, **scipy_args)
    
    accepted, full_trace = return_df(accepted, full_trace, columns=param_names)

    return {'a': accepted, 'c': contexts, 'f': full_trace, 's': res}

def return_df(*arrays, columns):
    result = []
    for array in arrays:
        if len(array):
            result.append( DataFrame(np.array(array), columns=columns) )
        else:
            result.append( DataFrame(columns=columns) )
    return result
            
###############################################################################
#Preprocessing
###############################################################################
def convert_input(guess, skip, bounds={}, priors={}, step_size=0.1, bound_max='inf'):
    
    check_input(guess, priors, step_size, skip, bounds)
    print('guess', guess)
    result             = {}
    param_array        = params_to_array(guess)
    print('param_array', param_array)
    param_names        = list(guess) if type(guess) == dict else list(guess.columns)
    name_to_num        = {name: num for num, name in enumerate(param_names)}
    print('n2n', name_to_num)
    var_param_index    = np.array([name_to_num[name] for name in guess if name not in skip])
    print('var_param_index', var_param_index)
    var_param_array    = param_array[var_param_index]
    max_val            = {name: np.inf for name in param_names} if bound_max == 'inf' else {pair[0]:max(pair[1], 1e-7) for pair in zip([name for name in guess if name not in skip], bound_max*var_param_array)}
    bounds_array       = np.array([bounds.get(name, [0, max_val[name]]) for name in guess if name not in skip])
    prior_distribution = get_prior_distribution(priors) if priors else None
    prior_index        = get_prior_index(guess, priors) if priors else []

    if type(step_size) == dict:
        step_size1      = {}
        for key in guess:
            if key in skip:
                continue
            elif key in step_size:
                step_size1[key] = step_size[key] 
            elif 'n' != key[0]:
                step_size1[key] = guess[key]/15 
            else:
                step_size1[key] = guess[key]/10 
        step_size_array = np.array(list(step_size1.values()))
    else:
        step_size_array = step_size 

    result['param_array']        = param_array
    result['var_param_index']    = var_param_index
    result['var_param_array']    = var_param_array
    result['bounds_array']       = bounds_array
    result['prior_distribution'] = prior_distribution
    result['prior_index']        = prior_index  
    result['step_size_array']    = step_size_array
    
    return result

def params_to_array(params):
    if type(params) == np.ndarray:
        return params
    elif type(params) == dict:
        try:
            temp = params[next(iter(params))]
            next(iter(temp))
            raise Exception('Only one value of params allowed!')
        except:
            result = np.array(list(params.values()))
        
            return np.array(result)
    elif type(params) == DataFrame:
        if params.shape[0] > 1:
            raise Exception('Only one value of params allowed!')
        return params.to_numpy()
    elif type(params)  == Series:
        return params.values
    else:
        raise Exception('Params is neither np.ndarry, dict nor DataFrame.')
        
def get_prior_index(params, priors):
    return np.array([pair[0] for pair in enumerate(params) if priors.get(pair[1], False)])

def get_prior_distribution(priors):  
    values      = np.array(list(priors.values()))   
    return norm(values[:,0], values[:,1])

def check_input(guess, priors, step_size={}, skip=[], bounds={}):
    if type(guess) != dict and type(guess) != Series: 
        raise Exception('Guess is neither dictionary nor Series.')
    
    guess_keys = guess.keys() if type(guess) == dict else list(guess.index)
    
    if type(step_size) == dict:
        for key in step_size:
            if key not in guess_keys:
                raise Exception('Key ' + key + ' in step_size not in present in guess_keys.')
    else:
        try:
            len(step_size)
        except:
            pass
        else:
            raise Exception('step_size must be dict or number.')
        
    for key in priors:
        if key not in guess_keys:
            raise Exception('Key ' + key + ' in priors not in present in guess_keys.')
    
    for key in bounds:
        if key not in guess_keys:
            raise Exception('Key ' + key + ' in bounds not in present in guess_keys.')
        if len(bounds[key]) != 2:
            raise Exception('Bounds[' + key + '] must be of length 2: [lower_bound, upper_bound]')
        if bounds[key][0] > bounds[key][1]:
            raise Exception('Bounds[' + key + ']: lower_bound must be smaller than upper_bound.')
        if guess[key] < bounds[key][0] or guess[key] > bounds[key][1]:
            raise Exception('Value of guess outside bounds for key: ' + key)
            
###############################################################################
#Posterior Calculation and Acceptance
###############################################################################
def wrap_log_posterior(var_param_index, full_params_array, prior_index, prior_distribution, likelihood_function, likelihood_args, trace=[]):
    def helper(var_param_array):
        log_posterior, log_prior, log_likelihood = get_negative_log_posterior(var_param_array, var_param_index, full_params_array, prior_index, prior_distribution, likelihood_function, likelihood_args, trace)
        return log_posterior
    return helper

def get_negative_log_posterior(var_param_array, var_param_index, full_params_array, prior_index, prior_distribution, likelihood_function, likelihood_args, trace=[]):
    params_array   = reconstruct_params(var_param_array, var_param_index, full_params_array)
    log_prior      = get_log_prior(params_array[prior_index], prior_distribution)
    log_likelihood = get_log_likelihood(params_array, likelihood_function=likelihood_function, likelihood_args=likelihood_args)
    log_posterior  = -(log_prior + log_likelihood) 
    
    trace.append(params_array)
    
    return log_posterior, log_prior, log_likelihood

@jit(nopython=True)
def reconstruct_params(variable_params, variable_param_index, params_array):
    params_array1 = params_array.copy()
    
    params_array1[variable_param_index] = variable_params
    
    return params_array1

###############################################################################
#Likelihood and Prior Calculation
###############################################################################
def get_log_likelihood(params_array, likelihood_function, likelihood_args={}):
    return likelihood_function(params_array=params_array, **likelihood_args)

def get_log_prior(params={}, priors={}):
    '''
    Pass in a dicts of params and priors OR np.arrays of params and priors
    '''
    if not priors:
        return 0
    
    elif type(priors) == dict: 
        #For testing purposes
        prior_distribution = get_prior_distribution(priors)
        params_array       = np.array([params[key] for key in priors.keys()])
        return get_log_sum(prior_distribution.pdf(params_array))
        
    else: 
        #Assumes params is already an array and has been sliced appropriately
        #Assumes priors is already a ditribution
        return get_log_sum(priors.pdf(params))

@jit(nopython=True)
def get_log_sum(a):
    return np.log(a).sum()

###############################################################################
#Transition
###############################################################################
def wrap_transition(guess_array, step_size=0.1, step_size_is_ratio=True):
    '''
    Generates a scipy.norm object for generating random variables.
    Wraps the transition step into a function that accepts the current array and returns the transitioned one.
    Use the get_step argument to return the norm object instead.
    If size_type_is_ratio is True, the sd equal to guess*step.
    If False, the sd equal to step.
    '''
    if step_size_is_ratio:
        step = norm([0]*len(guess_array), guess_array*step_size)
    else:
        step = norm([0]*len(guess_array), step_size)
        
    def helper(var_param_array, get_step=False):
        if not get_step:
            delta     = step.rvs()
            new_array = var_param_array + delta
            return new_array
        else:
            return step
    return helper

###############################################################################
#Tracing
###############################################################################
def wrap_record_trace_bh(var_param_index, params_array, accepted, rejected):
    def helper(x, f, accept):
        if accept:
            record_trace(x, var_param_index, params_array, accepted)
        else:
            record_trace(x, var_param_index, params_array, rejected)
        return
    return helper

def wrap_record_trace_da(var_param_index, params_array, accepted, contexts):
    def helper(x, f, context):
        
        record_trace(x, var_param_index, params_array, accepted)
        contexts.append(context)
        return
    return helper

def wrap_record_trace_de(var_param_index, params_array, trace):
    def helper(xk, convergence):
        record_trace(xk, var_param_index, params_array, trace)
        return
    return helper
               
def record_trace(var_param_array, var_param_index, params_array, trace):
    full_params_array = reconstruct_params(var_param_array, var_param_index, params_array)
    
    return trace.append(full_params_array)

###############################################################################
#Enforcing Bounds
###############################################################################    
def wrap_bounds_test(bounds_array, *funcs):
    '''
    Wraps bounds_test as well as any custom functions.
    '''
    def helper(f_new, x_new, f_old, x_old):
        var_param_array = x_new

        if not bounds_test(var_param_array, bounds_array):
            return False
        else:
            for func in funcs:
                if not func(f_new, x_new, f_old, x_old):
                    return False
            return True
    return helper

def bounds_test(var_param_array, bounds_array):
    if not np.all(var_param_array >= bounds_array[:,0]):
        return False
    elif not np.all(var_param_array <= bounds_array[:,1]):
        return False
    else:
        return True
    

def dummy(params_array, **kwargs):
    result = np.sum((50-params_array)**2)
    return result

if __name__ == '__main__':
    guess = {'p'+str(i):100 for i in range(21)}
    skip  = []
    
    priors = {}
    likelihood_function = dummy
    likelihood_args = {}
    scipy_args = {'niter':100}
    
    accepted = []
    rejected = []

    temp               = convert_input(guess, priors=priors, skip=skip, bounds={}) 
    var_param_index    = temp['var_param_index']
    var_param_array    = temp['var_param_array']
    bounds_array       = temp['bounds_array']
    prior_distribution = temp['prior_distribution'] 
    prior_index        = temp['prior_index']        
    full_param_array   = temp['param_array']
    param_names        = list(guess)
    
    wrapped_posterior   = wrap_log_posterior(var_param_index, full_param_array, prior_index, prior_distribution, likelihood_function, likelihood_args)
    
    wrapped_accept_test = wrap_bounds_test(bounds_array, *scipy_args.get('accept_test', []))
    
    wrapped_callback    = wrap_record_trace_de(var_param_index, full_param_array, accepted, rejected)
    
    wrapped_transition  = wrap_transition(var_param_array, step_size=10, step_size_is_ratio=False)
    

