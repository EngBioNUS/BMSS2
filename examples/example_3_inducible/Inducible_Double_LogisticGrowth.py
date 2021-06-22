import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_Inducible_Double_LogisticGrowth(y, t, params):
	x = y[0]
	m = y[1]
	p = y[2]

	mu_max = params[0]
	x_max  = params[1]
	k_ind  = params[2]
	synm   = params[3]
	degm   = params[4]
	synp   = params[5]
	n_ind  = params[6]
	ind    = params[7]

	mu = mu_max*(1 - x/x_max)
	
	dx = mu*x
	dm = synm*ind**n_ind/(ind**n_ind + k_ind**n_ind) - degm*m
	dp = synp*m - mu*p

	return np.array([dx, dm, dp])