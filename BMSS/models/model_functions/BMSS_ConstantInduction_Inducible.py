import numpy as np
from numba import jit

@jit(nopython=True)
def model_BMSS_ConstantInduction_Inducible(y, t, params):
	m = y[0]
	p = y[1]

	n     = params[0]
	k_ind = params[1]
	synm  = params[2]
	degm  = params[3]
	synp  = params[4]
	degp  = params[5]
	ind   = params[6]

	dm = synm*(ind**n)/(ind**n + k_ind**n) - degm*m
	dp = synp*m - degp*p

	return np.array([dm, dp])