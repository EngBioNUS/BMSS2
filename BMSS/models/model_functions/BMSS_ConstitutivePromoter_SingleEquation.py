import numpy as np
from numba import jit

@jit(nopython=True)
def model_BMSS_ConstitutivePromoter_SingleEquation(y, t, params):
	p = y[0]

	synp = params[0]
	degp = params[1]

	dp = synp - degp*p

	return np.array([dp])