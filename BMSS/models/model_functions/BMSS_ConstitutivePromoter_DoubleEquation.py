import numpy as np
from numba import jit

@jit(nopython=True)
def model_BMSS_ConstitutivePromoter_DoubleEquation(y, t, params):
	m = y[0]
	p = y[1]

	synm = params[0]
	degm = params[1]
	synp = params[2]
	degp = params[3]

	dm = synm - degm*m
	dp = synp*m - degp*p

	return np.array([dm, dp])