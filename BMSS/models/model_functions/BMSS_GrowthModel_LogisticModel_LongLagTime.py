import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_BMSS_GrowthModel_LogisticModel_LongLagTime(y, t, params):
	OD = y[0]

	r       = params[0]
	N_asymp = params[1]
	t_lag   = params[2]
	a       = params[3]
	t       = params[4]

	dOD = (r * OD * (1 - (OD / N_asymp))) / (1 + (2.7183**(a * (t_lag - t))))

	return np.array([dOD])