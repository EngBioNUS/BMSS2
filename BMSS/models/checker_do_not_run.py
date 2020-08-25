import numpy as np
def model_Bioconversion_Naringenin_Tyrosine_MalonicAcid_Combinatorial(y, t, params):
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

	Vm            = params[0]
	ntrans        = params[1]
	Ktrans        = params[2]
	n_ind         = params[3]
	K_ind         = params[4]
	syn_mRNA      = params[5]
	syn_Pep       = params[6]
	deg_Pep1      = params[7]
	deg_mRNA      = params[8]
	deg_Pep       = params[9]
	syn_mMCS      = params[10]
	syn_pMCS      = params[11]
	syn_mPAL      = params[12]
	syn_pPAL      = params[13]
	syn_mE4CL     = params[14]
	syn_pE4CL     = params[15]
	kcatTyr       = params[16]
	KmTyr         = params[17]
	kcatCouA      = params[18]
	KmCouA        = params[19]
	kcatMalA      = params[20]
	KmMalA        = params[21]
	kcatCouMalCoA = params[22]
	KmMalCoA      = params[23]
	KmCouCoA      = params[24]

	VTyr = kcatTyr*PAL*(Tyr/(KmTyr+Tyr))
	VCouA= kcatCouA*E4CL*(CouA/(KmCouA+CouA))
	VMalA= kcatMalA*MCS*(MalA/(KmMalA+MalA))
	VCouMalCoA= kcatCouMalCoA*OsCHS*(CouCoA*(MalCoA))/((KmMalCoA)*CouCoA + KmCouCoA*(MalCoA) + CouCoA*(MalCoA)+KmCouCoA*KmMalCoA)
	
	dInde = -Vm*((Inde**ntrans)/(Inde**ntrans+Ktrans**ntrans))
	dIndi = Vm*((Inde**ntrans)/(Inde**ntrans+Ktrans**ntrans))
	dmCHS = (syn_mRNA*((Indi**n_ind)/(Indi**n_ind+K_ind**n_ind)))-(deg_mRNA*mCHS)
	dOsCHS= (syn_Pep*mCHS)-(deg_Pep1*OsCHS)
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

Inde,Indi,mCHS,OsCHS,mMCS,MCS,mPAL,PAL,mE4CL,E4CL,Tyr,CouA,CouCoA,MalA,MalCoA,Nar,Vm,ntrans,Ktrans,n_ind,K_ind,syn_mRNA,syn_Pep,deg_Pep1,deg_mRNA,deg_Pep,syn_mMCS,syn_pMCS,syn_mPAL,syn_pPAL,syn_mE4CL,syn_pE4CL,kcatTyr,KmTyr,kcatCouA,KmCouA,kcatMalA,KmMalA,kcatCouMalCoA,KmMalCoA,KmCouCoA= np.random.rand(41)

Inde,Indi,mCHS,OsCHS,mMCS,MCS,mPAL,PAL,mE4CL,E4CL,Tyr,CouA,CouCoA,MalA,MalCoA,Nar,Vm,ntrans,Ktrans,n_ind,K_ind,syn_mRNA,syn_Pep,deg_Pep1,deg_mRNA,deg_Pep,syn_mMCS,syn_pMCS,syn_mPAL,syn_pPAL,syn_mE4CL,syn_pE4CL,kcatTyr,KmTyr,kcatCouA,KmCouA,kcatMalA,KmMalA,kcatCouMalCoA,KmMalCoA,KmCouCoA= list(map(float, [Inde,Indi,mCHS,OsCHS,mMCS,MCS,mPAL,PAL,mE4CL,E4CL,Tyr,CouA,CouCoA,MalA,MalCoA,Nar,Vm,ntrans,Ktrans,n_ind,K_ind,syn_mRNA,syn_Pep,deg_Pep1,deg_mRNA,deg_Pep,syn_mMCS,syn_pMCS,syn_mPAL,syn_pPAL,syn_mE4CL,syn_pE4CL,kcatTyr,KmTyr,kcatCouA,KmCouA,kcatMalA,KmMalA,kcatCouMalCoA,KmMalCoA,KmCouCoA]))

y = Inde,Indi,mCHS,OsCHS,mMCS,MCS,mPAL,PAL,mE4CL,E4CL,Tyr,CouA,CouCoA,MalA,MalCoA,Nar

t = 0
dt = 1e-3

params = Vm,ntrans,Ktrans,n_ind,K_ind,syn_mRNA,syn_Pep,deg_Pep1,deg_mRNA,deg_Pep,syn_mMCS,syn_pMCS,syn_mPAL,syn_pPAL,syn_mE4CL,syn_pE4CL,kcatTyr,KmTyr,kcatCouA,KmCouA,kcatMalA,KmMalA,kcatCouMalCoA,KmMalCoA,KmCouCoA

y = y + dt*model_Bioconversion_Naringenin_Tyrosine_MalonicAcid_Combinatorial(y, t, params)

y = y + dt*model_Bioconversion_Naringenin_Tyrosine_MalonicAcid_Combinatorial(y, t, params)