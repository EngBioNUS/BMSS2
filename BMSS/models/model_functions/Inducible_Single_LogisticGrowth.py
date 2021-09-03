import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_Inducible_Single_LogisticGrowth(y, t, params):
	x = y[0]
	p = y[1]

	mu_max = params[0]
	x_max  = params[1]
	k_ind  = params[2]
	synp   = params[3]
	n_ind  = params[4]
	ind    = params[5]

	mu = mu_max*(1 - x/x_max)
	dx = mu*x
	dp = synp *ind**n_ind/(ind**n_ind + k_ind**n_ind) -mu*p

	return np.array([dx, dp])