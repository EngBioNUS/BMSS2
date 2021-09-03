import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_SubModel2(y, t, params):
	x1 = y[0]

	g1 = params[0]

	dx1 = -g1*x1

	return np.array([dx1])