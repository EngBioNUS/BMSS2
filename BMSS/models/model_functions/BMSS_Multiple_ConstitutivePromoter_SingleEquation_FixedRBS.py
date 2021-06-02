import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_BMSS_Multiple_ConstitutivePromoter_SingleEquation_FixedRBS(y, t, params):
	px = y[0]

	synpx = params[0]
	degp  = params[1]

	dpx = synpx - degp*px

	return np.array([dpx])