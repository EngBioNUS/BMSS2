import numpy  as np
import pandas as pd

###############################################################################
#Non-Standard Imports
###############################################################################
from . import mcmc         as mc
from . import curvefitting as cf
from .models import model_handler as mh
from .models import param_handler as ph

###############################################################################
#AIC Calculation
###############################################################################    
def calculate_aic(data, models, parameter_ensemble, priors={}):
    aic       = {}
    
    #Standardize format
    if type(parameter_ensemble) == dict:
        try:
            rows = pd.DataFrame(parameter_ensemble).to_dict('record')
        except:
            rows = [parameter_ensemble]
    else:
        rows = parameter_ensemble.to_dict('record')
    
    #Iterate across models
    for dataset_num in data:
        models_  = {dataset_num: models[dataset_num]}
        data_    = {dataset_num: data[dataset_num]}
        n_points = 0
        
        
        #Get number of data points
        for state in data_[dataset_num]:
            for scenario in data_[dataset_num][state]:
                if scenario < 1:
                    continue
                else:
                    n_points += len(data_[dataset_num][state][scenario])
        
        model_params = models[dataset_num]['params']
        model_priors = {p: priors[p] for p in priors if p in model_params}
        model_aic    = []
        
        #Iterate across ensemble
        for row in rows:
            #Set up prior
            prior_distribution = mc.get_prior_distribution(model_priors) if model_priors else None
            prior_index        = mc.get_prior_index(row, model_priors)   if model_priors else [] 

            #Set up likelihood
            likelihood_args     = cf.get_likelihood_args(data_, models_, row)
            likelihood_function = cf.get_SSE_data
    
            theta = np.array(list(row.values()))
            
            log_posterior, log_prior, log_likelihood = mc.get_log_posterior(theta, prior_index, prior_distribution, likelihood_function, likelihood_args)
            
            model_aic.append( n_points*np.log(-log_posterior/n_points) + 2*len(model_params) )

        aic[dataset_num]       = np.min(model_aic) 
        
    return aic

def normalize_aic(aic_values):
    '''
    Accepts a list-like array of aic values and returns a normalized array 
    where the lowest value is zero.
    '''
    return np.array(aic_values) - np.min(aic_values)
    
###############################################################################
#Param Ensemble Constructors
###############################################################################
def make_param_ensemble(trace, system_type, ensemble_name, units, init=[], priors={}, parameter_bounds={}, columns=[]):
    '''
    Creates parameter ensembles using the trace from the sampler results.
    '''
    core_model = mh.quick_search(system_type)
    columns1   = columns if columns else core_model['parameters']
    if type(trace) == pd.DataFrame:
        parameters         = trace[columns1]
        try:
            parameters.columns = core_model['parameters'] + core_model['inputs']
        except ValueError:
            raise Exception('Mismatched parameters. Parameters/inputs for system_type: ' + str(core_model['parameters']) + '\n trace columns: ' + str(columns1))
        except Exception as e:
            raise e
    else:
        parameters = {key: trace[key] for key in columns1}
    parameter_ensemble = ph.make_param_ensemble(system_type, ensemble_name, units, parameters=parameters, init=init, priors=priors, parameter_bounds=parameter_bounds)
    
    return parameter_ensemble

###############################################################################
#AIC Tables/DataFrames
###############################################################################
def aic_to_dataframe(system_types_ensemble_names, aic_values):
    '''
    Accepts a list of system_type, ensemble_name pairs and corresponding AIC values
    and returns a DataFrame
    '''
    system_types    = [s[0] for s in system_types_ensemble_names]
    ensemble_names  = [s[1] for s in system_types_ensemble_names]
    daic            = normalize_aic(list(aic_values))
    evidence        = ['Substantial support' if daic[i] < 2 else 'Weak support' if daic[i] < 10 else 'No support' for i in range(len(daic))] 
    aic             = pd.DataFrame(zip(system_types, ensemble_names, aic_values, daic, evidence), 
                                   columns=('system_type', 'ensemble_name', 'AIC Value', 'dAIC', 'Evidence'))
    
    aic             = aic.sort_values('AIC Value')
    return aic

###############################################################################
#Interfacing with Setup CF
###############################################################################    
def quick_rank_aic(trace, sampler_args, info, ensemble_names):
    '''
    A shortcut function to be used in tandem with BMSS.models.setup_cf
    Accepts the trace returned by the sampler, the sampler_args and info values 
    returned by BMSS.models.setup_cf.setup_sampler_args_sa and similar functions.
    '''
    param_ensembles = quick_make_param_ensembles(trace, sampler_args, info, ensemble_names, init={})    
    aic             = calculate_aic(sampler_args['data'], sampler_args['models'], trace, priors=sampler_args['priors'])
    aic             = aic_to_dataframe(param_ensembles.keys(), aic.values())

    return param_ensembles, aic

def quick_make_param_ensembles(trace, sampler_args, info, ensemble_names, init={}):
    '''
    Makes parameter ensembles iteratively. Accepts the trace returned by the sampler, the sampler_args and info values 
    returned by BMSS.models.setup_cf.setup_sampler_args_sa and similar functions.
    '''
    if type(ensemble_names) == str:
        keys            = list(info.keys())
        ensemble_names1 = {keys[i]: ensemble_names for i in range(len(keys))}
    elif type(ensemble_names) == dict:
        ensemble_names1 = ensemble_names
    else:
        ensemble_names1 = dict(zip(info.keys(), ensemble_names))
    
    result = {}
    
    for key in info:
        system_type      = info[key]['system_type']
        priors           = info[key]['priors']
        parameter_bounds = info[key]['bounds']
        units            = info[key]['units'] 
        ensemble_name    = ensemble_names1[key]
        columns          = sampler_args['models'][key]['params']
        init1            = init[key] if init else []

        pe = make_param_ensemble(trace, system_type, ensemble_name, units, init=init1, priors=priors, parameter_bounds=parameter_bounds, columns=columns)
    
    
        result[(system_type, ensemble_name)] = pe
    return result
