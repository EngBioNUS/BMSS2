import numpy  as np
import pandas as pd
from   scipy.stats import norm

###############################################################################
#Non-Standard Imports
###############################################################################
try:
    from .       import curvefitting     as cf
    from .models import settings_handler as sh
except:
    import curvefitting as cf
    from models         import settings_handler as sh

###############################################################################
#AIC Calculation
###############################################################################    
def calculate_aic(data, models, params, priors={}):
    '''Calculates AIC of model calculating posterior and than applying AIC 
    formula. Returns a DataFrame of the AIC Values.

    Parameters
    ----------
    data : dict
        Curve-fitting data.
    models : dict
        The models used for curve-fitting.
    params : pandas.DataFrame
        The parameters with which to integrate the models with.
    priors : dict, optional
        Priors if any. The default is {}.

    Returns
    -------
    table : pandas.DataFrame
        A DataFrame with AIC values.
    '''
    aic = {}
    
    #Standardize format
    try:
        params1 = pd.DataFrame(params)
    except:
        params1 = pd.DataFrame([params])
        
    #Set up arguments
    posterior_args     = get_posterior_args(data, models, params1, priors)
    n_points, n_params = get_aic_args(data, models)
    
    aic = []  

    for name, row in params1.iterrows():
        log_posterior = get_posterior_for_each_model(params_series=row, **posterior_args) 
        model_aic     = n_points*np.log(-log_posterior/n_points) + 2*n_params
        
        aic.append(model_aic)
        

    aic = pd.DataFrame(aic, columns=models.keys(), index=params1.index)
    
    table         = pd.DataFrame(aic.stack().reset_index())
    table.columns = ['row', 'model_num', 'AIC Value']
    return table

def get_aic_args(data, models):
    '''
    Supporting function for calculate_aic. Do not run.
    
    :meta private:
    '''
    n_points = {}
    n_params = []
    for model_num in data:
        n_points[model_num] = 0
        n_params.append( len(models[model_num]['params']) )
        for state in data[model_num]:
            for scenario in data[model_num][state]:
                if scenario < 1:
                    continue
                else:
                    n_points[model_num] += len(data[model_num][state][scenario])
    
    return np.array(list(n_points.values())), np.array(n_params)

def get_posterior_args(data, models, params, priors):
    '''
    Supporting function for calculate_aic. Do not run.
    
    :meta private:
    '''
    t_indices    = cf.get_t_indices(data, models)

    prior_distribution = {model_num: np.array([priors[param] for param in models[model_num]['params'] if param in priors]) for model_num in models}
    prior_distribution = {model_num: norm(prior_distribution[model_num][:,0], prior_distribution[model_num][:,1]) for model_num in models if len(prior_distribution[model_num])}
    prior_index        = {model_num: [param for param in models[model_num]['params'] if param in priors] for model_num in models}
    
    result        =  {'data'               : data, 
                      'models'             : models, 
                      't_indices'          : t_indices, 
                      'prior_distribution' : prior_distribution,
                      'prior_index'        : prior_index
                      }
    return result        

def get_posterior_for_each_model(data, models, params_series, prior_distribution, prior_index, t_indices={}):
    '''
    Supporting function for calculate_aic. Do not run.
    
    :meta private:
    '''
    log_posterior = []
    for model_num in data:
        
        #Log likelihood
        #SSE negated due to definition of log likelihood
        params_          = params_series[models[model_num]['params']].values
        model_likelihood = -cf.get_SSE_dataset(model_num, data, models, params_, t_indices)
        
        #Log prior
        if len(prior_index[model_num]):
            params__    = params_series[prior_index[model_num]]
            model_prior = np.sum(prior_distribution[model_num].pdf(params__))
        else:
            model_prior = 0
        
        model_posterior = model_likelihood + model_prior
        
        log_posterior.append(model_posterior)
    return np.array(log_posterior)
    
    
def normalize_aic(aic_values):
    '''
    Accepts a list-like array of aic values and returns a normalized array 
    where the lowest value is zero.
    '''
    return np.array(aic_values) - np.min(aic_values)

###############################################################################
#AIC Tables/DataFrames
###############################################################################
def rank_aic(aic_dataframe, aic_column_name='AIC Value', inplace=True):
    '''
    Accepts a dataframe where each row corresponds to one model
    aic_dataframe cannot have any columns named 'Evidence'.
    '''
    daic     = normalize_aic(aic_dataframe[aic_column_name])
    evidence = ['Substantial support' if daic[i] < 2 else 'Weak support' if daic[i] < 10 else 'No support' for i in range(len(daic))] 
    
    loc  = len(aic_dataframe.columns) 
    
    
    ranked_table = aic_dataframe if inplace else aic_dataframe.copy()
    ranked_table.insert(loc    = loc,
                        column ='d(' + aic_column_name + ')',
                        value  = daic
                        ) 
    ranked_table.insert(loc    = loc,
                        column ='Evidence',
                        value  = evidence
                        ) 
    
    ranked_table = ranked_table.sort_values(aic_column_name)
    return ranked_table
    
