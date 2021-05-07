import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_TestModel_CellModel_CellularResources_ProteomeAllocation_RibosomeLimitation(y, t, params):
	rmt = y[0]
	rmm = y[1]
	rmq = y[2]
	rmr = y[3]
	rmp = y[4]
	pt  = y[5]
	pm  = y[6]
	mt  = y[7]
	mm  = y[8]
	mq  = y[9]
	mr  = y[10]
	mp  = y[11]
	si  = y[12]
	a   = y[13]
	q   = y[14]
	r   = y[15]
	p   = y[16]
	N   = y[17]
	s0  = y[18]

	M      = params[0]
	gmax   = params[1]
	Kgamma = params[2]
	thetat = params[3]
	thetam = params[4]
	thetaq = params[5]
	thetar = params[6]
	thetap = params[7]
	wt     = params[8]
	wm     = params[9]
	wq     = params[10]
	wr     = params[11]
	wp     = params[12]
	nt     = params[13]
	nm     = params[14]
	nq     = params[15]
	nr     = params[16]
	np_    = params[17]
	hq     = params[18]
	Kt     = params[19]
	vt     = params[20]
	Kq     = params[21]
	vm     = params[22]
	Km     = params[23]
	ns     = params[24]
	dm     = params[25]
	kb     = params[26]
	ku     = params[27]
	RegN   = params[28]
	Regs0  = params[29]
	gamma  = params[30]
	ttrate = params[31]
	lam    = params[32]
	nucat  = params[33]

	gamma  = gmax*a/(Kgamma+a)
	ttrate = (rmq+rmr+rmp+rmt+rmm)*gamma
	lam    = ttrate/M
	nucat  = pm*vm*si/(Km+si)
	
	drmt= (+kb*r*mt-ku*rmt-gamma/nt*rmt-lam*rmt)
	drmm= (+kb*r*mm-ku*rmm-gamma/nm*rmm-lam*rmm)
	drmq= (+kb*r*mq-ku*rmq-gamma/nq*rmq-lam*rmq)
	drmr= (+kb*r*mr-ku*rmr-gamma/nr*rmr-lam*rmr)
	drmp= (+kb*r*mp-ku*rmp-gamma/np_*rmp-lam*rmp)
	dpt = (+gamma/nt*rmt-lam*pt)
	dpm = (+gamma/nm*rmm-lam*pm)
	dmt = (+(wt*a/(thetat + a))+ku*rmt+gamma/nt*rmt-kb*r*mt-dm*mt-lam*mt)
	dmm = (+(wm*a/(thetam + a))+ku*rmm+gamma/nm*rmm-kb*r*mm-dm*mm-lam*mm)
	dmq = (+(wq*a/(thetaq + a)/(1 + (q/Kq)**hq))+ku*rmq+gamma/nq*rmq-kb*r*mq-dm*mq-lam*mq)
	dmr = (+(wr*a/(thetar + a))+ku*rmr+gamma/nr*rmr-kb*r*mr-dm*mr-lam*mr)
	dmp = (+(wp*a/(thetap + a))+ku*rmp+gamma/np_*rmp-kb*r*mp-dm*mp-lam*mp)
	dsi = (+pt*vt*(s0/(Kt + s0)) -nucat-lam*si)
	da  = (+ns*nucat-ttrate-lam*a)
	dq  = (+gamma/nq*rmq-lam*q)
	dr  = (+ku*rmr+ku*rmt+ku*rmm+ku*rmp+ku*rmq+gamma/nr*rmr+gamma/nr*rmr+gamma/nt*rmt+gamma/nm*rmm+gamma/np_*rmp+gamma/nq*rmq-kb*r*mr-kb*r*mt-kb*r*mm-kb*r*mp-kb*r*mq-lam*r)
	dp  = (+gamma/np_*rmp-lam*p)
	dN  = RegN*(lam*N)
	ds0 = Regs0*(-(pt*vt*(s0/(Kt + s0))*N))

	return np.array([drmt, drmm, drmq, drmr, drmp, dpt, dpm, dmt, dmm, dmq, dmr, dmp, dsi, da, dq, dr, dp, dN, ds0])