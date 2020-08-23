import numpy as np
from numba import jit

@jit(nopython=True)
def model_BMSS_Monod_Inducible_Bioconversion_ProductInhibition(y, t, params):
	x  = y[0]
	s  = y[1]
	h  = y[2]
	c1 = y[3]
	c2 = y[4]

	mu_max = params[0]
	Ks     = params[1]
	Kh     = params[2]
	Y      = params[3]
	synh   = params[4]
	Kind   = params[5]
	rxn0   = params[6]
	k0     = params[7]
	v1     = params[8]
	Kc1    = params[9]
	Ind    = params[10]

	mu   = mu_max*s/(s+Ks)*Kh/(h+Kh)
	rxn1 = h*v1*c1/(c1+Kc1)
	
	dx = x*mu
	ds = -dx/Y
	dh = synh*Ind/(Ind+Kind) -h*mu
	dc1= -rxn1 +rxn0 -k0*c1
	dc2= rxn1 -mu*c2

	return np.array([dx, ds, dh, dc1, dc2])