import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_BMSS_NOTgate_SingleEquation_MaturationTime(y, t, params):
	m1     = y[0]
	p1     = y[1]
	p1_mat = y[2]

	synm     = params[0]
	degm     = params[1]
	synp     = params[2]
	degp     = params[3]
	k_maxrep = params[4]
	k_mat    = params[5]
	state    = params[6]

	dm1     = synm*(1-(k_maxrep*state)) - degm*m1
	dp1     = synp*m1 - k_mat*p1
	dp1_mat = k_mat*p1 - degp*p1_mat

	return np.array([dm1, dp1, dp1_mat])