import numpy as np
from numba import jit

@jit(nopython=True)
def model_BMSS_DelayActivation_Inducible_ActiveTransport_InducerDegradation(y, t, params):
	inde = y[0]
	indi = y[1]
	m    = y[2]
	p    = y[3]

	vm      = params[0]
	n_trans = params[1]
	k_trans = params[2]
	degind  = params[3]
	n       = params[4]
	k_ind   = params[5]
	synm    = params[6]
	degm    = params[7]
	synp    = params[8]
	degp    = params[9]

	dinde= -vm*(inde**n_trans)/(inde**n_trans + k_trans**n_trans)
	dindi= vm*(inde**n_trans)/(inde**n_trans + k_trans**n_trans) - degind*indi
	dm = synm*(indi**n)/(indi**n + k_ind**n) - degm*m
	dp = synp*m - degp*p

	return np.array([dinde, dindi, dm, dp])