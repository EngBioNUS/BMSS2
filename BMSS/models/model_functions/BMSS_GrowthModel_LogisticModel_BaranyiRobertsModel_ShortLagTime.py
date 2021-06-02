import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_BMSS_GrowthModel_LogisticModel_BaranyiRobertsModel_ShortLagTime(y, t, params):
	OD = y[0]

	mu_max = params[0]
	N_max  = params[1]
	m      = params[2]
	q0     = params[3]
	t      = params[4]

	dOD = ((q0 * (2.7183**(mu_max * t))) / (1 + (q0 * (2.7183**(mu_max * t))))) * mu_max * OD * (1 - ((OD / N_max) ** m))

	return np.array([dOD])