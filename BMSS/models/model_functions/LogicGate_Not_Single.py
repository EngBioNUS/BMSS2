import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_LogicGate_Not_Single(y, t, params):
	p1 = y[0]
	p2 = y[1]

	kp1   = params[0]
	synp1 = params[1]
	synp2 = params[2]
	rep   = params[3]
	degp  = params[4]
	u1    = params[5]

	dp1 = synp1 *u1                    -degp*p1
	dp2 = synp2 *(kp1+rep*p1)/(kp1+p1) -degp*p2

	return np.array([dp1, dp2])