import numpy as np
from numba import jit

@jit(nopython=True)
def model_BMSS_InducerDegradation_Inducible_MaturationTime(y, t, params):
	ind   = y[0]
	m     = y[1]
	p     = y[2]
	p_mat = y[3]

	n      = params[0]
	degind = params[1]
	k_ind  = params[2]
	synm   = params[3]
	degm   = params[4]
	synp   = params[5]
	degp   = params[6]
	k_mat  = params[7]

	dind   = -degind*ind
	dm     = synm*(ind**n)/(ind**n + k_ind**n) - degm*m
	dp     = synp*m - k_mat*p
	dp_mat = k_mat*p - degp*p_mat

	return np.array([dind, dm, dp, dp_mat])