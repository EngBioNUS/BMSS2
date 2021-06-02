import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_BMSS_Multiple_ConstitutivePromoter_DoubleEquation_FixedPromoter_DifferentRBS_MaturationTime1(y, t, params):
	mx     = y[0]
	px     = y[1]
	px_mat = y[2]

	synm  = params[0]
	degm  = params[1]
	synpx = params[2]
	degp  = params[3]
	k_mat = params[4]

	dmx     = synm - degm*mx
	dpx     = synpx*mx - k_mat*px
	dpx_mat = k_mat*px - degp*px_mat

	return np.array([dmx, dpx, dpx_mat])