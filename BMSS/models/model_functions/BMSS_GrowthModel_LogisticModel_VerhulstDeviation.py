import numpy as np
from numba import jit

@jit(nopython=True)
def model_BMSS_GrowthModel_LogisticModel_VerhulstDeviation(y, t, params):
	OD = y[0]

	r      = params[0]
	N_max  = params[1]
	N_mini = params[2]
	n      = params[3]

	dOD = (r) * (OD) * (1 - (OD / N_max)) * ((1 - (N_mini / OD)) ** (n))

	return np.array([dOD])