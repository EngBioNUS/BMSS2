import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_BMSS_ConstantInduction_Inducible_SingleEquation(y, t, params):
	p = y[0]

	n     = params[0]
	k_ind = params[1]
	synp  = params[2]
	degp  = params[3]
	ind   = params[4]

	dp = synp*(ind**n)/(ind**n + k_ind**n) - degp*p

	return np.array([dp])