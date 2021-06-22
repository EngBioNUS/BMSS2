import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_Inducible_Double_DegradingInducer(y, t, params):
	ind = y[0]
	m   = y[1]
	p   = y[2]

	degind = params[0]
	k_ind  = params[1]
	synm   = params[2]
	degm   = params[3]
	synp   = params[4]
	degp   = params[5]

	dind= -degind*ind
	dm = synm*ind/(ind + k_ind) - degm*m
	dp = synp*m - degp*p

	return np.array([dind, dm, dp])