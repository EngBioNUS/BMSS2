import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_Temporary(y, t, params):
	m = y[0]
	p = y[1]

	k_ind = params[0]
	synm  = params[1]
	degm  = params[2]
	synp  = params[3]
	degp  = params[4]
	ind   = params[5]

	dm = synm*ind/(ind + k_ind) - degm*m
	dp = synp*m - degp*p

	return np.array([dm, dp])