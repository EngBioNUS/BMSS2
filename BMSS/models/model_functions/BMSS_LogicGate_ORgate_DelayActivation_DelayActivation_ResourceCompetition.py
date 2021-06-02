import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_BMSS_LogicGate_ORgate_DelayActivation_DelayActivation_ResourceCompetition(y, t, params):
	Inde1 = y[0]
	Indi1 = y[1]
	Inde2 = y[2]
	Indi2 = y[3]
	mRNA1 = y[4]
	Pep1  = y[5]
	mRNA2 = y[6]
	Pep2  = y[7]
	mRNA3 = y[8]
	Pep3  = y[9]

	syn_mRNA1 = params[0]
	syn_mRNA2 = params[1]
	syn_mRNA3 = params[2]
	deg_mRNA  = params[3]
	syn_Pep   = params[4]
	deg_Pep   = params[5]
	Pepmax    = params[6]
	Km1       = params[7]
	Km2       = params[8]
	Ratio     = params[9]
	state1    = params[10]
	state2    = params[11]

	dInde1 = -(Inde1/(Inde1+Km1))*Inde1
	dIndi1 = (Inde1/(Inde1+Km1))*Inde1
	dInde2 = -(Inde2/(Inde2+Km2))*Inde2
	dIndi2 = (Inde2/(Inde2+Km2))*Inde2
	dmRNA1 = syn_mRNA1*(Indi1)*(state1) - (deg_mRNA *mRNA1)
	dPep1  = (syn_Pep*mRNA1) - (deg_Pep*Pep1)
	dmRNA2 = syn_mRNA2*(Indi2)*(state2) - (deg_mRNA *mRNA2)
	dPep2  = (syn_Pep*mRNA2) - (deg_Pep*Pep2)
	dmRNA3 = (syn_mRNA3*((Pep1+Pep2)/Pepmax))-(deg_mRNA *mRNA3)
	dPep3  = (syn_Pep*(1-state1*state2*Ratio)*mRNA3)-(deg_Pep*Pep3)

	return np.array([dInde1, dIndi1, dInde2, dIndi2, dmRNA1, dPep1, dmRNA2, dPep2, dmRNA3, dPep3])