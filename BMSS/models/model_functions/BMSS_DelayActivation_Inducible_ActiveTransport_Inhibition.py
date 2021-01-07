import numpy as np
from numba import jit

@jit(nopython=True)
def model_BMSS_DelayActivation_Inducible_ActiveTransport_Inhibition(y, t, params):
	inde = y[0]
	indi = y[1]
	m    = y[2]
	p    = y[3]

	vm       = params[0]
	n_trans  = params[1]
	k_trans  = params[2]
	k_leak   = params[3]
	n        = params[4]
	k_ind    = params[5]
	synm     = params[6]
	degm     = params[7]
	k_inhmax = params[8]
	n_inh    = params[9]
	k_inh    = params[10]
	synp     = params[11]
	degp     = params[12]

	dinde= -vm*(inde**n_trans)/(inde**n_trans + k_trans**n_trans)
	dindi= vm*(inde**n_trans)/(inde**n_trans + k_trans**n_trans)
	dm = k_leak + (synm*(indi**n)/(indi**n + k_ind**n))*(1 - k_inhmax*(inde**n_inh)/(inde**n_inh + k_inh**n_inh)) - degm*m
	dp = synp*m - degp*p

	return np.array([dinde, dindi, dm, dp])