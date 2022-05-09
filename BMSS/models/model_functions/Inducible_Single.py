import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_Inducible_Single(y, t, params):
	p = y[0]

	k_ind = params[0]
	synp  = params[1]
	degp  = params[2]
	ind   = params[3]

	dp = synp *ind/(ind + k_ind) -degp*p

	return np.array([dp])