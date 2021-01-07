import numpy as np
from numba import jit

@jit(nopython=True)
def model_BMSS_Multiple_ConstitutivePromoter_DoubleEquation_FixedRBS_MaturationTime(y, t, params):
	mx     = y[0]
	px     = y[1]
	px_mat = y[2]

	synmx = params[0]
	degm  = params[1]
	synp  = params[2]
	degp  = params[3]
	k_mat = params[4]

	dmx     = synmx - degm*mx
	dpx     = synp*mx - k_mat*px
	dpx_mat = k_mat*px - degp*px_mat

	return np.array([dmx, dpx, dpx_mat])