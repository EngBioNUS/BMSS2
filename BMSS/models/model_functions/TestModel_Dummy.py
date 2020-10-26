import numpy as np
from numba import jit

@jit(nopython=True)
def model_TestModel_Dummy(y, t, params):
	mRNA = y[0]
	Pep  = y[1]

	syn_mRNA = params[0]
	deg_mRNA = params[1]
	syn_Pep  = params[2]
	deg_Pep  = params[3]
	Ki       = params[4]
	Ind      = params[5]

	dmRNA = syn_mRNA*Ind/(Ind + Ki) - deg_mRNA*mRNA
	dPep  = syn_Pep*mRNA - deg_Pep

	return np.array([dmRNA, dPep])