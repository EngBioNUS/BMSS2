import numpy as np
def model_BMSS_ConstantInduction_Inducible_MaturationTime(y, t, params):
	m     = y[0]
	p     = y[1]
	p_mat = y[2]

	k_ind = params[0]
	synm  = params[1]
	degm  = params[2]
	synp  = params[3]
	degp  = params[4]
	k_mat = params[5]
	ind   = params[6]

	dm     = synm*ind/(ind + k_ind) - degm*m
	dp     = synp*m - k_mat*p
	dp_mat = k_mat*p - degp*p_mat

	return np.array([dm, dp, dp_mat])

m,p,p_mat,k_ind,synm,degm,synp,degp,k_mat,ind= np.random.rand(10)

m,p,p_mat,k_ind,synm,degm,synp,degp,k_mat,ind= list(map(float, [m,p,p_mat,k_ind,synm,degm,synp,degp,k_mat,ind]))

y = [m,p,p_mat]

t = 0
dt = 1e-3

params = k_ind,synm,degm,synp,degp,k_mat,ind

y = y + dt*model_BMSS_ConstantInduction_Inducible_MaturationTime(y, t, params)

y = y + dt*model_BMSS_ConstantInduction_Inducible_MaturationTime(y, t, params)