import numpy as np
from numba import jit

@jit(nopython=True)
def model_BMSS_Multiple_ConstitutivePromoter_SingleEquation_FixedRBS_MaturationTime(y, t, params):
	px     = y[0]
	px_mat = y[1]

	synpx = params[0]
	degp  = params[1]
	k_mat = params[2]

	dpx     = synpx - k_mat*px
	dpx_mat = k_mat*px - degp*px_mat

	return np.array([dpx, dpx_mat])