import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_Test_Model_Cell_Cycle(y, t, params):
	EmptySet = y[0]
	u        = y[1]
	z        = y[2]
	v        = y[3]

	kappa   = params[0]
	k6      = params[1]
	k4      = params[2]
	k4prime = params[3]
	alpha   = params[4]

	alpha= k4prime/k4
	z = v - u
	du= k4*(v - u)*(alpha + u**2) - k6*u
	dv= kappa - k6*u
	dEmptySet= +(k6*u) -(kappa)
	du= +(k4*z*(k4prime/k4 + u**2)) -(k6*u)
	dz= +(kappa) -(k4*z*(k4prime/k4 + u**2))

	return np.array([dEmptySet, du, dz, dv])