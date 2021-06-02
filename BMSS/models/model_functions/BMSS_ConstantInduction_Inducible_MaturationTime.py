import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_BMSS_ConstantInduction_Inducible_MaturationTime(y, t, params):
	m     = y[0]
	p     = y[1]
	p_mat = y[2]

	n     = params[0]
	k_ind = params[1]
	synm  = params[2]
	degm  = params[3]
	synp  = params[4]
	degp  = params[5]
	k_mat = params[6]
	ind   = params[7]

	dm     = synm*(ind**n)/(ind**n + k_ind**n) - degm*m
	dp     = synp*m - k_mat*p
	dp_mat = k_mat*p - degp*p_mat

	return np.array([dm, dp, dp_mat])