import numpy as np
from numba import jit

@jit(nopython=True)
def model_BMSS_NOTgate_DoubleEquation_MaturationTime(y, t, params):
	m1     = y[0]
	p1     = y[1]
	m2     = y[2]
	p2     = y[3]
	p2_mat = y[4]

	synm1    = params[0]
	degm     = params[1]
	synp     = params[2]
	degp     = params[3]
	synm2    = params[4]
	k_maxrep = params[5]
	p_max    = params[6]
	k_mat    = params[7]
	state    = params[8]

	dm1     = synm1*state - degm*m1
	dp1     = synp*m1 - degp*p1
	dm2     = synm2*(1 - k_maxrep*(p1/p_max)) - degm*m2
	dp2     = synp*m2 - k_mat*p2
	dp2_mat = k_mat*p2 - degp*p2_mat

	return np.array([dm1, dp1, dm2, dp2, dp2_mat])