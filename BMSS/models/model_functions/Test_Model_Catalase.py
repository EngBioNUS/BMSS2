import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_Test_Model_Catalase(y, t, params):
	e  = y[0]
	x  = y[1]
	p  = y[2]
	p1 = y[3]
	a  = y[4]
	p2 = y[5]

	k1       = params[0]
	k2       = params[1]
	k4_prime = params[2]
	k4       = params[3]

	da = -(1*k4*p*a)
	de = +(1*k4*p*a) +(1*k4_prime*p*x) +(1*k4_prime*p*x) -(1*(k1*e*x - k2*p))
	dp = +(1*(k1*e*x - k2*p)) -(1*k4*p*a) -(1*k4*p*a) -(1*k4_prime*p*x)
	dp1= +(1*k4_prime*p*x)
	dp2= +(1*k4*p*a)
	dx = -(1*(k1*e*x - k2*p)) -(1*k4_prime*p*x)

	return np.array([de, dx, dp, dp1, da, dp2])