import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_BMSS_InducerDegradation_Inducible_SingleEquation(y, t, params):
	ind = y[0]
	p   = y[1]

	n      = params[0]
	degind = params[1]
	k_ind  = params[2]
	synp   = params[3]
	degp   = params[4]

	dind= -degind*ind
	dp = synp*(ind**n)/(ind**n + k_ind**n) - degp*p

	return np.array([dind, dp])