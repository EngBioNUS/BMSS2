import numpy as np
from numba import jit

@jit(nopython=True)
def model_BMSS_LogicGate_ANDgate(y, t, params):
	m1 = y[0]
	p1 = y[1]
	m2 = y[2]
	p2 = y[3]
	m3 = y[4]
	p3 = y[5]

	synm1  = params[0]
	degm   = params[1]
	synp   = params[2]
	degp   = params[3]
	synm2  = params[4]
	synm3  = params[5]
	p1_max = params[6]
	p2_max = params[7]
	state1 = params[8]
	state2 = params[9]

	dm1 = synm1*state1 - degm*m1
	dp1 = synp*m1 - degp*p1
	dm2 = synm2*state2 - degm*m2
	dp2 = synp*m2 - degp*p2
	dm3 = synm3*(p1/p1_max)*(p2/p2_max) - degm*m3
	dp3 = synp*m3 - degp*p3

	return np.array([dm1, dp1, dm2, dp2, dm3, dp3])