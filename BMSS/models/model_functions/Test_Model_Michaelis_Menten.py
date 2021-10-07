import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_Test_Model_Michaelis_Menten(y, t, params):
	S  = y[0]
	E  = y[1]
	ES = y[2]
	P  = y[3]

	E0   = params[0]
	kf   = params[1]
	kr   = params[2]
	kcat = params[3]
	Vmax = params[4]
	Km   = params[5]
	R    = params[6]

	R  = Vmax*S/(S + Km)
	dE = +(kcat*ES) -(kf*S*E - kr*ES)
	dES= +(kf*S*E - kr*ES) -(kcat*ES)
	dP = +(kcat*ES)
	dS = -(kf*S*E - kr*ES)

	return np.array([dS, dE, dES, dP])