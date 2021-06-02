import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_BMSS_ConstitutivePromoter_DoubleEquation_MaturationTime(y, t, params):
	m     = y[0]
	p     = y[1]
	p_mat = y[2]

	synm  = params[0]
	degm  = params[1]
	synp  = params[2]
	degp  = params[3]
	k_mat = params[4]

	dm     = synm - degm*m
	dp     = synp*m - k_mat*p
	dp_mat = k_mat*p - degp*p_mat

	return np.array([dm, dp, dp_mat])