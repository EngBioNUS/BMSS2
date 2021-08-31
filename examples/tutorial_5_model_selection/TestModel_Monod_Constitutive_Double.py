import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_TestModel_Monod_Constitutive_Double(y, t, params):
	x  = y[0]
	s  = y[1]
	mh = y[2]
	h  = y[3]

	mu_max = params[0]
	Ks     = params[1]
	Y      = params[2]
	synm   = params[3]
	degm   = params[4]
	synh   = params[5]

	mu = mu_max*s/(s+Ks)
	
	dx = x*mu
	ds = -dx/Y
	dmh= synm    -mh*degm
	dh = synh*mh -h *mu

	return np.array([dx, ds, dmh, dh])