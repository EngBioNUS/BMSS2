import numpy as np
from numba import jit

@jit(nopython=True)
def model_BMSS_ConstantInduction_Inducible_Inhibition(y, t, params):
	m = y[0]
	p = y[1]

	k_leak   = params[0]
	synm     = params[1]
	degm     = params[2]
	n        = params[3]
	k_ind    = params[4]
	k_inhmax = params[5]
	n_inh    = params[6]
	k_inh    = params[7]
	synp     = params[8]
	degp     = params[9]
	inducer  = params[10]

	dm = k_leak + (synm*(inducer**n)/(inducer**n + k_ind**n))*(1 - k_inhmax*(inducer**n_inh)/(inducer**n_inh + k_inh**n_inh)) - degm*m
	dp = synp*m - degp*p

	return np.array([dm, dp])