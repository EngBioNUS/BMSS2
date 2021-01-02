import numpy as np
def model_BMSS_GrowthModel_MortalityPhase(y, t, params):
	OD = y[0]

	N0  = params[0]
	m1  = params[1]
	m2  = params[2]
	tc1 = params[3]
	tc2 = params[4]
	t   = params[5]

	a = 1 / (tc1 ** m1)
	b = 1 / (tc2 ** m2)
	
	dOD = N0 * (a * m1 * (t ** (m1-1)) - b * m2 * (t ** (m2-1))) * (2.7183**(a * (t ** m1) - b * (t ** m2)))

	return np.array([dOD])

OD,N0,m1,m2,tc1,tc2,t= np.random.rand(7)*10

OD,N0,m1,m2,tc1,tc2,t= list(map(float, [OD,N0,m1,m2,tc1,tc2,t]))

y = [OD]

t = 0
dt = 1e-3

params = N0,m1,m2,tc1,tc2,t

y = y + dt*model_BMSS_GrowthModel_MortalityPhase(y, t, params)

y = y + dt*model_BMSS_GrowthModel_MortalityPhase(y, t, params)