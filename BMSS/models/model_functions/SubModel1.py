import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_SubModel1(y, t, params):
	x0 = y[0]

	g0 = params[0]

	dx0 = -g0*x0

	return np.array([dx0])