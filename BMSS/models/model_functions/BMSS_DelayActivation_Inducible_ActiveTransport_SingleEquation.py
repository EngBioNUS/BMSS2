import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_BMSS_DelayActivation_Inducible_ActiveTransport_SingleEquation(y, t, params):
	inde = y[0]
	indi = y[1]
	p    = y[2]

	vm      = params[0]
	n_trans = params[1]
	k_trans = params[2]
	n       = params[3]
	k_ind   = params[4]
	synp    = params[5]
	degp    = params[6]

	dinde= -vm*(inde**n_trans)/(inde**n_trans + k_trans**n_trans)
	dindi= vm*(inde**n_trans)/(inde**n_trans + k_trans**n_trans)
	dp = synp*(indi**n)/(indi**n + k_ind**n) - degp*p

	return np.array([dinde, dindi, dp])