import numpy as np
from numba import jit

@jit(nopython=True)
def model_BMSS_TestModel_Naringenin_RBSStrength_PromoterStrength(y, t, params):
	Inde   = y[0]
	Indi   = y[1]
	mCHS   = y[2]
	OsCHS  = y[3]
	mMCS   = y[4]
	MCS    = y[5]
	mPAL   = y[6]
	PAL    = y[7]
	mE4CL  = y[8]
	E4CL   = y[9]
	Tyr    = y[10]
	CouA   = y[11]
	CouCoA = y[12]
	MalA   = y[13]
	MalCoA = y[14]
	Nar    = y[15]

	proMCS  = params[0]
	rbsMCS  = params[1]
	proPAL  = params[2]
	rbsPAL  = params[3]
	proE4CL = params[4]
	rbsE4CL = params[5]
	rbsCHS  = params[6]

	plasmidcopy_fold = 5
	
	Vm       = 6.1743e-05
	ntrans   = 0.9416
	Ktrans   = 0.0448
	n        = 5.4162
	K_ind    = 2.0583e-05
	syn_mRNA = 8.6567e-08 *plasmidcopy_fold
	syn_Pep  = 0.01931 *0.9504 *rbsCHS
	deg_Pep  = 0.0010
	deg_mRNA = 0.1386
	
	deg_Pep = 0.007397
	
	syn_mMCS = 2.2953e-07 *proMCS*plasmidcopy_fold
	syn_pMCS = 0.01931 *rbsMCS *0.9218
	
	syn_mPAL = 2.2953e-07 *proPAL*plasmidcopy_fold
	syn_pPAL = 0.01931 *rbsPAL *0.8684
	
	syn_mE4CL = 2.2953e-07 *proE4CL*plasmidcopy_fold
	syn_pE4CL = 0.01931 *rbsE4CL *0.9119
	
	kcatTyr = 61.2
	KmTyr   = 0.195e-3
	
	kcatCouA = 16.92
	KmCouA   = 0.246e-3
	
	kcatMalA = 0.15e-3/MCS
	KmMalA   = 529.4e-6
	
	kcatCouMalCoA = 0.0517
	KmMalCoA      = 47.42e-6
	KmCouCoA      = 45.44e-6
	
	VTyr = kcatTyr*PAL*(Tyr/(KmTyr+Tyr))
	VCouA= kcatCouA*E4CL*(CouA/(KmCouA+CouA))
	VMalA= kcatMalA*MCS*(MalA/(KmMalA+MalA))
	VCouMalCoA= kcatCouMalCoA*OsCHS*(CouCoA*(MalCoA))/((KmMalCoA)*CouCoA + KmCouCoA*(MalCoA) + CouCoA*(MalCoA)+KmCouCoA*KmMalCoA)
	
	dInde = -Vm*((Inde**ntrans)/(Inde**ntrans+Ktrans**ntrans))
	dIndi = Vm*((Inde**ntrans)/(Inde**ntrans+Ktrans**ntrans))
	dmCHS = (syn_mRNA*((Indi**n)/(Indi**n+K_ind**n)))-(deg_mRNA*mCHS)
	dOsCHS= (syn_Pep*mCHS)-(deg_Pep*OsCHS)
	dmMCS = (syn_mMCS)-(deg_mRNA * mMCS)
	dMCS  = (syn_pMCS*mMCS)-(deg_Pep*MCS)
	dmPAL = (syn_mPAL)-(deg_mRNA * mPAL)
	dPAL  = (syn_pPAL*mPAL)-(deg_Pep*PAL)
	dmE4CL= (syn_mE4CL)-(deg_mRNA * mE4CL)
	dE4CL = (syn_pE4CL*mE4CL)-(deg_Pep*E4CL)
	dTyr  = -VTyr
	dCouA = VTyr -VCouA
	dCouCoA= VCouA -VCouMalCoA
	dMalA = -VMalA
	dMalCoA= VMalA -3*VCouMalCoA
	dNar  = 1*VCouMalCoA

	return np.array([dInde, dIndi, dmCHS, dOsCHS, dmMCS, dMCS, dmPAL, dPAL, dmE4CL, dE4CL, dTyr, dCouA, dCouCoA, dMalA, dMalCoA, dNar])