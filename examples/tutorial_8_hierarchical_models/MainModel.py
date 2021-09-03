import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_MainModel(y, t, params):
	x0 = y[0]
	x1 = y[1]

	p0 = params[0]
	p1 = params[1]
	g0 = params[2]
	g1 = params[3]

	dx0 = model_SubModel1(np.array([x0]), t, np.array([g0])) +p0
	dx1 = model_SubModel2(np.array([x1]), t, np.array([g1])) +p1

	return np.array([dx0, dx1])