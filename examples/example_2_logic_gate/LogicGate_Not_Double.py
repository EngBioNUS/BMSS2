import numpy as np
from numba import jit

@jit(nopython=True)
def model_LogicGate_Not_Double(y, t, params):
	m1 = y[0]
	m2 = y[1]
	p1 = y[2]
	p2 = y[3]

	synm1 = params[0]
	synm2 = params[1]
	degm  = params[2]
	kp1   = params[3]
	rep   = params[4]
	synp1 = params[5]
	synp2 = params[6]
	degp  = params[7]
	u1    = params[8]

	dm1 = synm1*u1                    -degm*m1
	dm2 = synm2*(kp1+rep*p1)/(kp1+p1) -degm*m2
	dp1 = synp1 *m1                   -degp*p1
	dp2 = synp2 *m2                   -degp*p2

	return np.array([dm1, dm2, dp1, dp2])