import numpy as np
from numba import jit

@jit(nopython=True)
def model_LogicGate_OR_Double_Degrade_Delay(y, t, params):
	Inde  = y[0]
	Indi  = y[1]
	Ind   = y[2]
	mRNA1 = y[3]
	Pep1  = y[4]
	mRNA2 = y[5]
	Pep2  = y[6]
	mRNA3 = y[7]
	Pep3  = y[8]

	syn_mRNA1 = params[0]
	syn_mRNA2 = params[1]
	syn_mRNA3 = params[2]
	deg_mRNA  = params[3]
	syn_Pep   = params[4]
	deg_Pep   = params[5]
	Pepmax    = params[6]
	Km        = params[7]
	deg_Ind   = params[8]
	state1    = params[9]
	state2    = params[10]

	dInde_dt  = -(Inde/(Inde+Km))*Inde
	dIndi_dt  = (Inde/(Inde+Km))*Inde
	dInd_dt   = -deg_Ind*Ind
	dmRNA1_dt = syn_mRNA1*(Ind)*(state1) - (deg_mRNA *mRNA1)
	dPep1_dt  = (syn_Pep*mRNA1) - (deg_Pep*Pep1)
	dmRNA2_dt = syn_mRNA2*Indi*(state2) - (deg_mRNA *mRNA2)
	dPep2_dt  = (syn_Pep*mRNA2) - (deg_Pep*Pep2)
	dmRNA3_dt = (syn_mRNA3*((Pep1+Pep2)/Pepmax))-(deg_mRNA *mRNA3)
	dPep3_dt  = (syn_Pep*mRNA3)-(deg_Pep*Pep3)

	return np.array([dInde_dt, dIndi_dt, dInd_dt, dmRNA1_dt, dPep1_dt, dmRNA2_dt, dPep2_dt, dmRNA3_dt, dPep3_dt])