import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_TestModel_Monod_Constitutive_Single_ProductInhibition(y, t, params):
	x = y[0]
	s = y[1]
	h = y[2]

	mu_max = params[0]
	Ks     = params[1]
	Kh     = params[2]
	Y      = params[3]
	synh   = params[4]

	mu = mu_max*s/(s+Ks)*Kh/(h+Kh)
	dx = x*mu
	ds = -dx/Y
	dh = synh -h*mu

	return np.array([dx, ds, dh])