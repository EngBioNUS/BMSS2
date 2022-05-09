import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_Inducible_Double_Uptake(y, t, params):
	inde = y[0]
	indi = y[1]
	m    = y[2]
	p    = y[3]

	upind = params[0]
	k_ind = params[1]
	synm  = params[2]
	degm  = params[3]
	synp  = params[4]
	degp  = params[5]

	dinde= -upind*inde
	dindi= upind*inde
	dm = synm*indi/(indi + k_ind) - degm*m
	dp = synp*m - degp*p

	return np.array([dinde, dindi, dm, dp])