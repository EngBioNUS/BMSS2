import numpy as np
from numba import jit

@jit(nopython=True)
def model_BMSS_Multiple_ConstitutivePromoter_DoubleEquation_FixedPromoter_DifferentRBS1(y, t, params):
	mx = y[0]
	px = y[1]

	synm  = params[0]
	degm  = params[1]
	synpx = params[2]
	degp  = params[3]

	dmx = synm - degm*mx
	dpx = synpx*mx - degp*px

	return np.array([dmx, dpx])