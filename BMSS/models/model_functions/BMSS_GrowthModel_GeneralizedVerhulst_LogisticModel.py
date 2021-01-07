import numpy as np
from numba import jit

@jit(nopython=True)
def model_BMSS_GrowthModel_GeneralizedVerhulst_LogisticModel(y, t, params):
	OD = y[0]

	r       = params[0]
	N_asymp = params[1]
	alpha   = params[2]
	beta    = params[3]

	dOD = (r) * ((OD) ** alpha) * ((1 - (OD / N_asymp)) ** (beta))

	return np.array([dOD])