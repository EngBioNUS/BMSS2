import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
def model_TestModel_Dummy(y, t, params):
	m = y[0]
	p = y[1]

	k_ind = params[0]
	synm  = params[1]
	degm  = params[2]
	synp  = params[3]
	degp  = params[4]
	ind   = params[5]

	dm = synm*ind/(ind + k_ind) - degm*m
	dp = synp*m - degp*p

	return np.array([dm, dp])

m,p,k_ind,synm,degm,synp,degp,ind= np.random.rand(8)*10

m,p,k_ind,synm,degm,synp,degp,ind= list(map(float, [m,p,k_ind,synm,degm,synp,degp,ind]))

y = [m,p]

t = 0
dt = 1e-3

params = k_ind,synm,degm,synp,degp,ind

y = y + dt*model_TestModel_Dummy(y, t, params)

y = y + dt*model_TestModel_Dummy(y, t, params)