import numpy as np
from numba import jit

@jit(nopython=True)
def model_BMSS_ConstitutivePromoter_SingleEquation_MaturationTime(y, t, params):
	p     = y[0]
	p_mat = y[1]

	synp  = params[0]
	degp  = params[1]
	k_mat = params[2]

	dp     = synp - k_mat*p
	dp_mat = k_mat*p - degp*p_mat

	return np.array([dp, dp_mat])