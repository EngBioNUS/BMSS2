import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_BMSS_NOTgate_SingleEquation(y, t, params):
	m1 = y[0]
	p1 = y[1]

	synm     = params[0]
	degm     = params[1]
	synp     = params[2]
	degp     = params[3]
	k_maxrep = params[4]
	state    = params[5]

	dm1 = synm*(1-(k_maxrep*state)) - degm*m1
	dp1 = synp*m1 - degp*p1

	return np.array([dm1, dp1])