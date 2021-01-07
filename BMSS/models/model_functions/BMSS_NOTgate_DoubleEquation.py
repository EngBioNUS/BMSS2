import numpy as np
from numba import jit

@jit(nopython=True)
def model_BMSS_NOTgate_DoubleEquation(y, t, params):
	m1 = y[0]
	p1 = y[1]
	m2 = y[2]
	p2 = y[3]

	synm1    = params[0]
	degm     = params[1]
	synp     = params[2]
	degp     = params[3]
	synm2    = params[4]
	k_maxrep = params[5]
	p_max    = params[6]
	state    = params[7]

	dm1 = synm1*state - degm*m1
	dp1 = synp*m1 - degp*p1
	dm2 = synm2*(1 - k_maxrep*(p1/p_max)) - degm*m2
	dp2 = synp*m2 - degp*p2

	return np.array([dm1, dp1, dm2, dp2])