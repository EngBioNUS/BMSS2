import numpy as np
from numba import jit

@jit(nopython=True)
def model_BMSS_ConstantInduction_Inducible_MaturationTime(y, t, params):
	m     = y[0]
	p     = y[1]
	p_mat = y[2]

	k_ind = params[0]
	synm  = params[1]
	degm  = params[2]
	synp  = params[3]
	degp  = params[4]
	k_mat = params[5]
	ind   = params[6]

	dm     = synm*ind/(ind + k_ind) - degm*m
	dp     = synp*m - k_mat*p
	dp_mat = k_mat*p - degp*p_mat

	return np.array([dm, dp, dp_mat])