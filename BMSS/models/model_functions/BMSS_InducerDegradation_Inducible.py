import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_BMSS_InducerDegradation_Inducible(y, t, params):
	ind = y[0]
	m   = y[1]
	p   = y[2]

	n      = params[0]
	degind = params[1]
	k_ind  = params[2]
	synm   = params[3]
	degm   = params[4]
	synp   = params[5]
	degp   = params[6]

	dind= -degind*ind
	dm = synm*(ind**n)/(ind**n + k_ind**n) - degm*m
	dp = synp*m - degp*p

	return np.array([dind, dm, dp])