import numpy as np
from numba import jit

@jit(nopython=True)
def model_BMSS_LogicGate_ORgate_DelayActivation(y, t, params):
	Inde  = y[0]
	Indi  = y[1]
	mRNA1 = y[2]
	Pep1  = y[3]
	mRNA2 = y[4]
	Pep2  = y[5]
	mRNA3 = y[6]
	Pep3  = y[7]

	syn_mRNA1 = params[0]
	syn_mRNA2 = params[1]
	syn_mRNA3 = params[2]
	deg_mRNA  = params[3]
	syn_Pep   = params[4]
	deg_Pep   = params[5]
	Pepmax    = params[6]
	Km        = params[7]
	state1    = params[8]
	state2    = params[9]

	dInde  = -(Inde/(Inde+Km))*Inde
	dIndi  = (Inde/(Inde+Km))*Inde
	dmRNA1 = syn_mRNA1*(Indi)*(state1) - (deg_mRNA *mRNA1)
	dPep1  = (syn_Pep*mRNA1) - (deg_Pep*Pep1)
	dmRNA2 = syn_mRNA2*(state2) - (deg_mRNA *mRNA2)
	dPep2  = (syn_Pep*mRNA2) - (deg_Pep*Pep2)
	dmRNA3 = (syn_mRNA3*((Pep1+Pep2)/Pepmax))-(deg_mRNA *mRNA3)
	dPep3  = (syn_Pep*mRNA3)-(deg_Pep*Pep3)

	return np.array([dInde, dIndi, dmRNA1, dPep1, dmRNA2, dPep2, dmRNA3, dPep3])