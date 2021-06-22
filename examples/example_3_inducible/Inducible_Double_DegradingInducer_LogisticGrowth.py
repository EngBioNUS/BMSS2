import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_Inducible_Double_DegradingInducer_LogisticGrowth(y, t, params):
	x   = y[0]
	ind = y[1]
	m   = y[2]
	p   = y[3]

	mu_max = params[0]
	x_max  = params[1]
	degind = params[2]
	k_ind  = params[3]
	synm   = params[4]
	degm   = params[5]
	synp   = params[6]
	n_ind  = params[7]

	mu = mu_max*(1 - x/x_max)
	
	dx = mu*x
	dind= -degind*ind
	dm = synm*ind**n_ind/(ind**n_ind + k_ind**n_ind) - degm*m
	dp = synp*m - mu*p

	return np.array([dx, dind, dm, dp])