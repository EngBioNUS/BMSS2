import numpy as np
from numba import jit

@jit(nopython=True)
def model_BMSS_DelayActivation_Inducible_ActiveTransport(y, t, params):
	inde = y[0]
	indi = y[1]
	m    = y[2]
	p    = y[3]

	vm      = params[0]
	n_trans = params[1]
	k_trans = params[2]
	n       = params[3]
	k_ind   = params[4]
	synm    = params[5]
	degm    = params[6]
	synp    = params[7]
	degp    = params[8]

	dinde= -vm*(inde**n_trans)/(inde**n_trans + k_trans**n_trans)
	dindi= vm*(inde**n_trans)/(inde**n_trans + k_trans**n_trans)
	dm = synm*(indi**n)/(indi**n + k_ind**n) - degm*m
	dp = synp*m - degp*p

	return np.array([dinde, dindi, dm, dp])