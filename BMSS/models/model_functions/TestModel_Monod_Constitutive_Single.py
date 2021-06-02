import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_TestModel_Monod_Constitutive_Single(y, t, params):
	x = y[0]
	s = y[1]
	h = y[2]

	mu_max = params[0]
	Ks     = params[1]
	Y      = params[2]
	synh   = params[3]

	mu = mu_max*s/(s+Ks)
	
	dx = x*mu
	ds = -dx/Y
	dh = synh -h*mu

	return np.array([dx, ds, dh])