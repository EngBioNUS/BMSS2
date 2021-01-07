import numpy as np
from numba import jit

@jit(nopython=True)
def model_BMSS_Multiple_ConstitutivePromoter_SingleEquation_FixedRBS(y, t, params):
	px = y[0]

	synpx = params[0]
	degp  = params[1]

	dpx = synpx - degp*px

	return np.array([dpx])