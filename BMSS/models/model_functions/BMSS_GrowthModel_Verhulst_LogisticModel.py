import numpy as np
from numba import jit

@jit(nopython=True)
def model_BMSS_GrowthModel_Verhulst_LogisticModel(y, t, params):
	OD = y[0]

	r       = params[0]
	N_asymp = params[1]

	dOD = (r) * (OD) * (1 - (OD / N_asymp))

	return np.array([dOD])