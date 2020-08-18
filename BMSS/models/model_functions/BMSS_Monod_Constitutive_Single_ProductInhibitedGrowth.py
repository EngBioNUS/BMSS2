import numpy as np
from numba import jit

@jit(nopython=True)
def model_BMSS_Monod_Constitutive_Single_ProductInhibitedGrowth(y, t, params):
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