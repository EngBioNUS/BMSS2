import numpy as np
from numba import jit

@jit(nopython=True)
def model_BMSS_Multiple_ConstitutivePromoter_DoubleEquation_FixedRBS(y, t, params):
	mx = y[0]
	px = y[1]

	synmx = params[0]
	degm  = params[1]
	synp  = params[2]
	degp  = params[3]

	dmx = synmx - degm*mx
	dpx = synp*mx - degp*px

	return np.array([dmx, dpx])