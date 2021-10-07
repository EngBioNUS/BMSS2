import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_Test_Model_Repressilator(y, t, params):
	PX = y[0]
	PY = y[1]
	PZ = y[2]
	X  = y[3]
	Y  = y[4]
	Z  = y[5]

	beta     = params[0]
	alpha0   = params[1]
	alpha    = params[2]
	eff      = params[3]
	n        = params[4]
	KM       = params[5]
	tau_mRNA = params[6]
	tau_prot = params[7]
	t_ave    = params[8]
	kd_mRNA  = params[9]
	kd_prot  = params[10]
	k_tl     = params[11]
	a_tr     = params[12]
	ps_a     = params[13]
	ps_0     = params[14]
	a0_tr    = params[15]

	beta  = tau_mRNA/tau_prot
	alpha0= a0_tr*eff*tau_prot/(ln(2)*KM)
	a0_tr = ps_0*60
	alpha = a_tr*eff*tau_prot/(ln(2)*KM)
	a_tr  = (ps_a - ps_0)*60
	t_ave = tau_mRNA/ln(2)
	kd_mRNA= ln(2)/tau_mRNA
	kd_prot= ln(2)/tau_prot
	k_tl  = eff/t_ave
	dPX   = +(k_tl*X) -(kd_prot*PX)
	dPY   = +(k_tl*Y) -(kd_prot*PY)
	dPZ   = +(k_tl*Z) -(kd_prot*PZ)
	dX    = +(a0_tr + a_tr*KM**n/(KM**n + PZ**n)) -(kd_mRNA*X)
	dY    = +(a0_tr + a_tr*KM**n/(KM**n + PX**n)) -(kd_mRNA*Y)
	dZ    = +(a0_tr + a_tr*KM**n/(KM**n + PY**n)) -(kd_mRNA*Z)

	return np.array([dPX, dPY, dPZ, dX, dY, dZ])