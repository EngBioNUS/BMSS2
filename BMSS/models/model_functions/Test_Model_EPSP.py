import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_Test_Model_EPSP(y, t, params):
	BLL = y[0]
	IL  = y[1]
	AL  = y[2]
	A   = y[3]
	BL  = y[4]
	B   = y[5]
	DLL = y[6]
	D   = y[7]
	ILL = y[8]
	DL  = y[9]
	I   = y[10]
	ALL = y[11]

	kf_0  = params[0]
	kr_0  = params[1]
	kf_1  = params[2]
	kr_1  = params[3]
	kf_2  = params[4]
	kr_2  = params[5]
	kf_3  = params[6]
	kr_3  = params[7]
	kf_4  = params[8]
	kr_4  = params[9]
	kf_5  = params[10]
	kr_5  = params[11]
	kf_6  = params[12]
	kr_6  = params[13]
	kf_7  = params[14]
	kr_7  = params[15]
	kf_8  = params[16]
	kr_8  = params[17]
	kf_9  = params[18]
	kr_9  = params[19]
	kf_10 = params[20]
	kr_10 = params[21]
	kf_11 = params[22]
	kr_11 = params[23]
	kf_12 = params[24]
	kr_12 = params[25]
	kf_13 = params[26]
	kr_13 = params[27]
	kf_14 = params[28]
	kr_14 = params[29]
	kf_15 = params[30]
	kr_15 = params[31]
	kf_16 = params[32]
	kr_16 = params[33]
	t2    = params[34]

	dA   = +(1*(kf_5*B - kr_5*A)) -(1*(kf_3*A - kr_3*AL)) -(1*(kf_3*A - kr_3*AL)) -(1*(kf_9*A - kr_9*I))
	dAL  = +(1*(kf_3*A - kr_3*AL)) +(1*(kf_6*BL - kr_6*AL)) +(1*(kf_6*BL - kr_6*AL)) -(1*(kf_10*AL - kr_10*IL)) +(1*(kf_6*BL - kr_6*AL)) -(1*(kf_10*AL - kr_10*IL)) -(1*(kf_10*AL - kr_10*IL)) -(1*(kf_4*AL - kr_4*ALL))
	dALL = +(1*(kf_2*BLL - kr_2*ALL)) +(1*(kf_4*AL - kr_4*ALL)) +(1*(kf_4*AL - kr_4*ALL)) -(1*(kf_11*ALL - kr_11*ILL))
	dB   = -(1*(kf_0*B - kr_0*BL)) -(1*(kf_5*B - kr_5*A))
	dBL  = +(1*(kf_0*B - kr_0*BL)) -(1*(kf_1*BL - kr_1*BLL)) -(1*(kf_1*BL - kr_1*BLL)) -(1*(kf_6*BL - kr_6*AL))
	dBLL = +(1*(kf_1*BL - kr_1*BLL)) -(1*(kf_2*BLL - kr_2*ALL))
	dD   = +(1*(kf_14*I - kr_14*D)) -(1*(kf_12*D - kr_12*DL))
	dDL  = +(1*(kf_12*D - kr_12*DL)) +(1*(kf_15*IL - kr_15*DL)) +(1*(kf_15*IL - kr_15*DL)) -(1*(kf_13*DL - kr_13*DLL))
	dDLL = +(1*(kf_13*DL - kr_13*DLL)) +(1*(kf_16*ILL - kr_16*DLL))
	dI   = +(1*(kf_9*A - kr_9*I)) -(1*(kf_14*I - kr_14*D)) -(1*(kf_14*I - kr_14*D)) -(1*(kf_7*I - kr_7*IL))
	dIL  = +(1*(kf_10*AL - kr_10*IL)) +(1*(kf_7*I - kr_7*IL)) +(1*(kf_7*I - kr_7*IL)) -(1*(kf_15*IL - kr_15*DL)) +(1*(kf_7*I - kr_7*IL)) -(1*(kf_15*IL - kr_15*DL)) -(1*(kf_15*IL - kr_15*DL)) -(1*(kf_8*IL - kr_8*ILL))
	dILL = +(1*(kf_11*ALL - kr_11*ILL)) +(1*(kf_8*IL - kr_8*ILL)) +(1*(kf_8*IL - kr_8*ILL)) -(1*(kf_16*ILL - kr_16*DLL))

	return np.array([dBLL, dIL, dAL, dA, dBL, dB, dDLL, dD, dILL, dDL, dI, dALL])