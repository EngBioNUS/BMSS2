import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_TestModel_Logistic_Inducible(y, t, params):
	x = y[0]
	h = y[1]

	mu_max = params[0]
	synh   = params[1]
	Kind   = params[2]
	x_max  = params[3]
	Ind    = params[4]

	mu = mu_max*(1 - x/x_max)
	dx = x*mu
	dh = synh*Ind/(Ind+Kind) -h*mu

	return np.array([dx, dh])