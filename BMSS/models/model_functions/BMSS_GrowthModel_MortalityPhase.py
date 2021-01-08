import numpy as np
from numba import jit

@jit(nopython=True)
def model_BMSS_GrowthModel_MortalityPhase(y, t, params):
	OD = y[0]

	N0  = params[0]
	m1  = params[1]
	m2  = params[2]
	tc1 = params[3]
	tc2 = params[4]
	a   = params[5]
	b   = params[6]
	t   = params[7]

	a = 1 / (tc1 ** m1)
	b = 1 / (tc2 ** m2)
	
	dOD = N0 * (a * m1 * (t ** (m1-1)) - b * m2 * (t ** (m2-1))) * (2.7183**(a * (t ** m1) - b * (t ** m2)))

	return np.array([dOD])