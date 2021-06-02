import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_BMSS_LogicGate_ANDgate_BasalLeakinessP1_BasalLeakinessP3_MaturationTime(y, t, params):
	m1     = y[0]
	p1     = y[1]
	m2     = y[2]
	p2     = y[3]
	m3     = y[4]
	p3     = y[5]
	p3_mat = y[6]

	k_leak1 = params[0]
	k_leak  = params[1]
	synm1   = params[2]
	degm    = params[3]
	synp    = params[4]
	degp    = params[5]
	synm2   = params[6]
	synm3   = params[7]
	p1_max  = params[8]
	p2_max  = params[9]
	k_mat   = params[10]
	state1  = params[11]
	state2  = params[12]

	dm1     = k_leak1 + synm1*state1 - degm*m1
	dp1     = synp*m1 - degp*p1
	dm2     = synm2*state2 - degm*m2
	dp2     = synp*m2 - degp*p2
	dm3     = k_leak + synm3*(p1/p1_max)*(p2/p2_max) - degm*m3
	dp3     = synp*m3 - k_mat*p3
	dp3_mat = k_mat*m3 - degp*p3_mat

	return np.array([dm1, dp1, dm2, dp2, dm3, dp3, dp3_mat])