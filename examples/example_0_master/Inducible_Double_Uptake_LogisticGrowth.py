import numpy as np
from numba import jit

@jit(nopython=True)
def model_Inducible_Double_Uptake_LogisticGrowth(y, t, params):
	x    = y[0]
	inde = y[1]
	indi = y[2]
	m    = y[3]
	p    = y[4]

	mu_max = params[0]
	x_max  = params[1]
	upind  = params[2]
	k_ind  = params[3]
	synm   = params[4]
	degm   = params[5]
	synp   = params[6]
	n_ind  = params[7]

	mu = mu_max*(1 - x/x_max)
	
	dx = mu*x
	dinde= -upind*inde
	dindi= upind*inde
	dm = synm*indi**n_ind/(indi**n_ind + k_ind**n_ind) - degm*m
	dp = synp*m - mu*p

	return np.array([dx, dinde, dindi, dm, dp])