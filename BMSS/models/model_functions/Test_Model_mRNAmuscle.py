import numpy as np
from numpy import log   as ln
from numpy import log10 as log
from numpy import exp
from numba import jit

@jit(nopython=True)
def model_Test_Model_mRNAmuscle(y, t, params):
	FoxO3              = y[0]
	FoxO3_Sirt1        = y[1]
	HoxA11             = y[2]
	HoxA11_mRNA        = y[3]
	Mafbx              = y[4]
	miR181             = y[5]
	miR181_HoxA11_mRNA = y[6]
	miR181_Sirt1_mRNA  = y[7]
	miR181_gene        = y[8]
	MyoD               = y[9]
	MyoD_gene          = y[10]
	MyoD_gene_FoxO3    = y[11]
	MyoD_gene_HoxA11   = y[12]
	MyoD_mRNA          = y[13]
	Sirt1              = y[14]
	Sirt1_mRNA         = y[15]
	Sink               = y[16]
	Source             = y[17]

	kbinFoxO3Sirt1       = params[0]
	kbinmiR181Sirt1      = params[1]
	kbinmiR181HoxA11     = params[2]
	kbinMyoDgeneFoxO3    = params[3]
	kbinMyoDgeneHoxA11   = params[4]
	kdegFoxO3            = params[5]
	kdegFoxO3Sirt1       = params[6]
	kdegHoxA11           = params[7]
	kdegHoxA11mRNA       = params[8]
	kdegHoxA11mRNAmiR181 = params[9]
	kdegMafbx            = params[10]
	kdegmiR181           = params[11]
	kdegMyoD             = params[12]
	kdegMyoDmRNA         = params[13]
	kdegSirt1            = params[14]
	kdegSirt1mRNA        = params[15]
	kdegSirt1mRNAmiR181  = params[16]
	krelFoxO3Sirt1       = params[17]
	krelmiR181HoxA11     = params[18]
	krelmiR181Sirt1      = params[19]
	krelMyoDgeneFoxO3    = params[20]
	krelMyoDgeneHoxA11   = params[21]
	ksynFoxO3            = params[22]
	ksynHoxA11           = params[23]
	ksynHoxA11mRNA       = params[24]
	ksynMafbx            = params[25]
	ksynmiR181           = params[26]
	ksynMyoD             = params[27]
	ksynMyoDmRNA         = params[28]
	ksynSirt1            = params[29]
	ksynSirt1mRNA        = params[30]

	dFoxO3       = +(krelFoxO3Sirt1*FoxO3_Sirt1) +(krelMyoDgeneFoxO3*MyoD_gene_FoxO3) +(krelMyoDgeneFoxO3*MyoD_gene_FoxO3) +(ksynFoxO3*Source) +(krelMyoDgeneFoxO3*MyoD_gene_FoxO3) +(ksynFoxO3*Source) +(ksynFoxO3*Source) +(ksynMafbx*FoxO3) +(krelMyoDgeneFoxO3*MyoD_gene_FoxO3) +(ksynFoxO3*Source) +(ksynFoxO3*Source) +(ksynMafbx*FoxO3) +(ksynFoxO3*Source) +(ksynMafbx*FoxO3) +(ksynMafbx*FoxO3) -(kbinFoxO3Sirt1*FoxO3*Sirt1) +(krelMyoDgeneFoxO3*MyoD_gene_FoxO3) +(ksynFoxO3*Source) +(ksynFoxO3*Source) +(ksynMafbx*FoxO3) +(ksynFoxO3*Source) +(ksynMafbx*FoxO3) +(ksynMafbx*FoxO3) -(kbinFoxO3Sirt1*FoxO3*Sirt1) +(ksynFoxO3*Source) +(ksynMafbx*FoxO3) +(ksynMafbx*FoxO3) -(kbinFoxO3Sirt1*FoxO3*Sirt1) +(ksynMafbx*FoxO3) -(kbinFoxO3Sirt1*FoxO3*Sirt1) -(kbinFoxO3Sirt1*FoxO3*Sirt1) -(kbinMyoDgeneFoxO3*MyoD_gene*FoxO3) +(krelMyoDgeneFoxO3*MyoD_gene_FoxO3) +(ksynFoxO3*Source) +(ksynFoxO3*Source) +(ksynMafbx*FoxO3) +(ksynFoxO3*Source) +(ksynMafbx*FoxO3) +(ksynMafbx*FoxO3) -(kbinFoxO3Sirt1*FoxO3*Sirt1) +(ksynFoxO3*Source) +(ksynMafbx*FoxO3) +(ksynMafbx*FoxO3) -(kbinFoxO3Sirt1*FoxO3*Sirt1) +(ksynMafbx*FoxO3) -(kbinFoxO3Sirt1*FoxO3*Sirt1) -(kbinFoxO3Sirt1*FoxO3*Sirt1) -(kbinMyoDgeneFoxO3*MyoD_gene*FoxO3) +(ksynFoxO3*Source) +(ksynMafbx*FoxO3) +(ksynMafbx*FoxO3) -(kbinFoxO3Sirt1*FoxO3*Sirt1) +(ksynMafbx*FoxO3) -(kbinFoxO3Sirt1*FoxO3*Sirt1) -(kbinFoxO3Sirt1*FoxO3*Sirt1) -(kbinMyoDgeneFoxO3*MyoD_gene*FoxO3) +(ksynMafbx*FoxO3) -(kbinFoxO3Sirt1*FoxO3*Sirt1) -(kbinFoxO3Sirt1*FoxO3*Sirt1) -(kbinMyoDgeneFoxO3*MyoD_gene*FoxO3) -(kbinFoxO3Sirt1*FoxO3*Sirt1) -(kbinMyoDgeneFoxO3*MyoD_gene*FoxO3) -(kbinMyoDgeneFoxO3*MyoD_gene*FoxO3) -(kdegFoxO3*FoxO3) +(krelMyoDgeneFoxO3*MyoD_gene_FoxO3) +(ksynFoxO3*Source) +(ksynFoxO3*Source) +(ksynMafbx*FoxO3) +(ksynFoxO3*Source) +(ksynMafbx*FoxO3) +(ksynMafbx*FoxO3) -(kbinFoxO3Sirt1*FoxO3*Sirt1) +(ksynFoxO3*Source) +(ksynMafbx*FoxO3) +(ksynMafbx*FoxO3) -(kbinFoxO3Sirt1*FoxO3*Sirt1) +(ksynMafbx*FoxO3) -(kbinFoxO3Sirt1*FoxO3*Sirt1) -(kbinFoxO3Sirt1*FoxO3*Sirt1) -(kbinMyoDgeneFoxO3*MyoD_gene*FoxO3) +(ksynFoxO3*Source) +(ksynMafbx*FoxO3) +(ksynMafbx*FoxO3) -(kbinFoxO3Sirt1*FoxO3*Sirt1) +(ksynMafbx*FoxO3) -(kbinFoxO3Sirt1*FoxO3*Sirt1) -(kbinFoxO3Sirt1*FoxO3*Sirt1) -(kbinMyoDgeneFoxO3*MyoD_gene*FoxO3) +(ksynMafbx*FoxO3) -(kbinFoxO3Sirt1*FoxO3*Sirt1) -(kbinFoxO3Sirt1*FoxO3*Sirt1) -(kbinMyoDgeneFoxO3*MyoD_gene*FoxO3) -(kbinFoxO3Sirt1*FoxO3*Sirt1) -(kbinMyoDgeneFoxO3*MyoD_gene*FoxO3) -(kbinMyoDgeneFoxO3*MyoD_gene*FoxO3) -(kdegFoxO3*FoxO3) +(ksynFoxO3*Source) +(ksynMafbx*FoxO3) +(ksynMafbx*FoxO3) -(kbinFoxO3Sirt1*FoxO3*Sirt1) +(ksynMafbx*FoxO3) -(kbinFoxO3Sirt1*FoxO3*Sirt1) -(kbinFoxO3Sirt1*FoxO3*Sirt1) -(kbinMyoDgeneFoxO3*MyoD_gene*FoxO3) +(ksynMafbx*FoxO3) -(kbinFoxO3Sirt1*FoxO3*Sirt1) -(kbinFoxO3Sirt1*FoxO3*Sirt1) -(kbinMyoDgeneFoxO3*MyoD_gene*FoxO3) -(kbinFoxO3Sirt1*FoxO3*Sirt1) -(kbinMyoDgeneFoxO3*MyoD_gene*FoxO3) -(kbinMyoDgeneFoxO3*MyoD_gene*FoxO3) -(kdegFoxO3*FoxO3) +(ksynMafbx*FoxO3) -(kbinFoxO3Sirt1*FoxO3*Sirt1) -(kbinFoxO3Sirt1*FoxO3*Sirt1) -(kbinMyoDgeneFoxO3*MyoD_gene*FoxO3) -(kbinFoxO3Sirt1*FoxO3*Sirt1) -(kbinMyoDgeneFoxO3*MyoD_gene*FoxO3) -(kbinMyoDgeneFoxO3*MyoD_gene*FoxO3) -(kdegFoxO3*FoxO3) -(kbinFoxO3Sirt1*FoxO3*Sirt1) -(kbinMyoDgeneFoxO3*MyoD_gene*FoxO3) -(kbinMyoDgeneFoxO3*MyoD_gene*FoxO3) -(kdegFoxO3*FoxO3) -(kbinMyoDgeneFoxO3*MyoD_gene*FoxO3) -(kdegFoxO3*FoxO3) -(kdegFoxO3*FoxO3) -(ksynMafbx*FoxO3)
	dFoxO3_Sirt1 = +(kbinFoxO3Sirt1*FoxO3*Sirt1) -(kdegFoxO3Sirt1*FoxO3_Sirt1) -(kdegFoxO3Sirt1*FoxO3_Sirt1) -(krelFoxO3Sirt1*FoxO3_Sirt1)
	dHoxA11      = +(krelMyoDgeneHoxA11*MyoD_gene_HoxA11) +(ksynHoxA11*HoxA11_mRNA) +(ksynHoxA11*HoxA11_mRNA) -(kbinMyoDgeneHoxA11*HoxA11*MyoD_gene) +(ksynHoxA11*HoxA11_mRNA) -(kbinMyoDgeneHoxA11*HoxA11*MyoD_gene) -(kbinMyoDgeneHoxA11*HoxA11*MyoD_gene) -(kdegHoxA11*HoxA11)
	dHoxA11_mRNA = +(krelmiR181HoxA11*miR181_HoxA11_mRNA) +(ksynHoxA11*HoxA11_mRNA) +(ksynHoxA11*HoxA11_mRNA) +(ksynHoxA11mRNA*Source) +(ksynHoxA11*HoxA11_mRNA) +(ksynHoxA11mRNA*Source) +(ksynHoxA11mRNA*Source) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) +(ksynHoxA11*HoxA11_mRNA) +(ksynHoxA11mRNA*Source) +(ksynHoxA11mRNA*Source) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) +(ksynHoxA11mRNA*Source) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) -(kdegHoxA11mRNA*HoxA11_mRNA) +(ksynHoxA11*HoxA11_mRNA) +(ksynHoxA11mRNA*Source) +(ksynHoxA11mRNA*Source) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) +(ksynHoxA11mRNA*Source) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) -(kdegHoxA11mRNA*HoxA11_mRNA) +(ksynHoxA11mRNA*Source) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) -(kdegHoxA11mRNA*HoxA11_mRNA) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) -(kdegHoxA11mRNA*HoxA11_mRNA) -(kdegHoxA11mRNA*HoxA11_mRNA) -(ksynHoxA11*HoxA11_mRNA)
	dMafbx       = +(ksynMafbx*FoxO3) -(kdegMafbx*Mafbx)
	dMyoD        = +(ksynMyoD*MyoD_mRNA) -(kdegMyoD*MyoD)
	dMyoD_gene   = +(krelMyoDgeneFoxO3*MyoD_gene_FoxO3) +(krelMyoDgeneHoxA11*MyoD_gene_HoxA11) +(krelMyoDgeneHoxA11*MyoD_gene_HoxA11) -(kbinMyoDgeneFoxO3*MyoD_gene*FoxO3) +(krelMyoDgeneHoxA11*MyoD_gene_HoxA11) -(kbinMyoDgeneFoxO3*MyoD_gene*FoxO3) -(kbinMyoDgeneFoxO3*MyoD_gene*FoxO3) -(kbinMyoDgeneHoxA11*HoxA11*MyoD_gene)
	dMyoD_gene_FoxO3= +(kbinMyoDgeneFoxO3*MyoD_gene*FoxO3) +(ksynMyoDmRNA*MyoD_gene_FoxO3) +(ksynMyoDmRNA*MyoD_gene_FoxO3) -(krelMyoDgeneFoxO3*MyoD_gene_FoxO3) +(ksynMyoDmRNA*MyoD_gene_FoxO3) -(krelMyoDgeneFoxO3*MyoD_gene_FoxO3) -(krelMyoDgeneFoxO3*MyoD_gene_FoxO3) -(ksynMyoDmRNA*MyoD_gene_FoxO3)
	dMyoD_gene_HoxA11= +(kbinMyoDgeneHoxA11*HoxA11*MyoD_gene) -(krelMyoDgeneHoxA11*MyoD_gene_HoxA11)
	dMyoD_mRNA   = +(ksynMyoD*MyoD_mRNA) +(ksynMyoDmRNA*MyoD_gene_FoxO3) +(ksynMyoDmRNA*MyoD_gene_FoxO3) -(kdegMyoDmRNA*MyoD_mRNA) +(ksynMyoDmRNA*MyoD_gene_FoxO3) -(kdegMyoDmRNA*MyoD_mRNA) -(kdegMyoDmRNA*MyoD_mRNA) -(ksynMyoD*MyoD_mRNA)
	dSink        = +(kdegFoxO3*FoxO3) +(kdegHoxA11*HoxA11) +(kdegHoxA11*HoxA11) +(kdegHoxA11mRNA*HoxA11_mRNA) +(kdegHoxA11*HoxA11) +(kdegHoxA11mRNA*HoxA11_mRNA) +(kdegHoxA11mRNA*HoxA11_mRNA) +(kdegMafbx*Mafbx) +(kdegHoxA11*HoxA11) +(kdegHoxA11mRNA*HoxA11_mRNA) +(kdegHoxA11mRNA*HoxA11_mRNA) +(kdegMafbx*Mafbx) +(kdegHoxA11mRNA*HoxA11_mRNA) +(kdegMafbx*Mafbx) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegHoxA11*HoxA11) +(kdegHoxA11mRNA*HoxA11_mRNA) +(kdegHoxA11mRNA*HoxA11_mRNA) +(kdegMafbx*Mafbx) +(kdegHoxA11mRNA*HoxA11_mRNA) +(kdegMafbx*Mafbx) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegHoxA11mRNA*HoxA11_mRNA) +(kdegMafbx*Mafbx) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegHoxA11*HoxA11) +(kdegHoxA11mRNA*HoxA11_mRNA) +(kdegHoxA11mRNA*HoxA11_mRNA) +(kdegMafbx*Mafbx) +(kdegHoxA11mRNA*HoxA11_mRNA) +(kdegMafbx*Mafbx) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegHoxA11mRNA*HoxA11_mRNA) +(kdegMafbx*Mafbx) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegHoxA11mRNA*HoxA11_mRNA) +(kdegMafbx*Mafbx) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegSirt1*Sirt1) +(kdegHoxA11*HoxA11) +(kdegHoxA11mRNA*HoxA11_mRNA) +(kdegHoxA11mRNA*HoxA11_mRNA) +(kdegMafbx*Mafbx) +(kdegHoxA11mRNA*HoxA11_mRNA) +(kdegMafbx*Mafbx) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegHoxA11mRNA*HoxA11_mRNA) +(kdegMafbx*Mafbx) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegHoxA11mRNA*HoxA11_mRNA) +(kdegMafbx*Mafbx) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegSirt1*Sirt1) +(kdegHoxA11mRNA*HoxA11_mRNA) +(kdegMafbx*Mafbx) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegSirt1*Sirt1) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegSirt1*Sirt1) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegSirt1*Sirt1) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegSirt1*Sirt1) +(kdegSirt1*Sirt1) +(kdegSirt1mRNA*Sirt1_mRNA) +(kdegHoxA11*HoxA11) +(kdegHoxA11mRNA*HoxA11_mRNA) +(kdegHoxA11mRNA*HoxA11_mRNA) +(kdegMafbx*Mafbx) +(kdegHoxA11mRNA*HoxA11_mRNA) +(kdegMafbx*Mafbx) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegHoxA11mRNA*HoxA11_mRNA) +(kdegMafbx*Mafbx) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegHoxA11mRNA*HoxA11_mRNA) +(kdegMafbx*Mafbx) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegSirt1*Sirt1) +(kdegHoxA11mRNA*HoxA11_mRNA) +(kdegMafbx*Mafbx) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegSirt1*Sirt1) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegSirt1*Sirt1) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegSirt1*Sirt1) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegSirt1*Sirt1) +(kdegSirt1*Sirt1) +(kdegSirt1mRNA*Sirt1_mRNA) +(kdegHoxA11mRNA*HoxA11_mRNA) +(kdegMafbx*Mafbx) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegSirt1*Sirt1) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegSirt1*Sirt1) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegSirt1*Sirt1) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegSirt1*Sirt1) +(kdegSirt1*Sirt1) +(kdegSirt1mRNA*Sirt1_mRNA) +(kdegMafbx*Mafbx) +(kdegMyoD*MyoD) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegSirt1*Sirt1) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegSirt1*Sirt1) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegSirt1*Sirt1) +(kdegSirt1*Sirt1) +(kdegSirt1mRNA*Sirt1_mRNA) +(kdegMyoD*MyoD) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegSirt1*Sirt1) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegSirt1*Sirt1) +(kdegSirt1*Sirt1) +(kdegSirt1mRNA*Sirt1_mRNA) +(kdegMyoDmRNA*MyoD_mRNA) +(kdegSirt1*Sirt1) +(kdegSirt1*Sirt1) +(kdegSirt1mRNA*Sirt1_mRNA) +(kdegSirt1*Sirt1) +(kdegSirt1mRNA*Sirt1_mRNA) +(kdegSirt1mRNA*Sirt1_mRNA) +(kdegmiR181*miR181)
	dSirt1       = +(kdegFoxO3Sirt1*FoxO3_Sirt1) +(krelFoxO3Sirt1*FoxO3_Sirt1) +(krelFoxO3Sirt1*FoxO3_Sirt1) +(ksynSirt1*Sirt1_mRNA) +(krelFoxO3Sirt1*FoxO3_Sirt1) +(ksynSirt1*Sirt1_mRNA) +(ksynSirt1*Sirt1_mRNA) -(kbinFoxO3Sirt1*FoxO3*Sirt1) +(krelFoxO3Sirt1*FoxO3_Sirt1) +(ksynSirt1*Sirt1_mRNA) +(ksynSirt1*Sirt1_mRNA) -(kbinFoxO3Sirt1*FoxO3*Sirt1) +(ksynSirt1*Sirt1_mRNA) -(kbinFoxO3Sirt1*FoxO3*Sirt1) -(kbinFoxO3Sirt1*FoxO3*Sirt1) -(kdegSirt1*Sirt1)
	dSirt1_mRNA  = +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(ksynSirt1*Sirt1_mRNA) +(ksynSirt1*Sirt1_mRNA) +(ksynSirt1mRNA*Source) +(ksynSirt1*Sirt1_mRNA) +(ksynSirt1mRNA*Source) +(ksynSirt1mRNA*Source) -(kbinmiR181Sirt1*miR181*Sirt1_mRNA) +(ksynSirt1*Sirt1_mRNA) +(ksynSirt1mRNA*Source) +(ksynSirt1mRNA*Source) -(kbinmiR181Sirt1*miR181*Sirt1_mRNA) +(ksynSirt1mRNA*Source) -(kbinmiR181Sirt1*miR181*Sirt1_mRNA) -(kbinmiR181Sirt1*miR181*Sirt1_mRNA) -(kdegSirt1mRNA*Sirt1_mRNA) +(ksynSirt1*Sirt1_mRNA) +(ksynSirt1mRNA*Source) +(ksynSirt1mRNA*Source) -(kbinmiR181Sirt1*miR181*Sirt1_mRNA) +(ksynSirt1mRNA*Source) -(kbinmiR181Sirt1*miR181*Sirt1_mRNA) -(kbinmiR181Sirt1*miR181*Sirt1_mRNA) -(kdegSirt1mRNA*Sirt1_mRNA) +(ksynSirt1mRNA*Source) -(kbinmiR181Sirt1*miR181*Sirt1_mRNA) -(kbinmiR181Sirt1*miR181*Sirt1_mRNA) -(kdegSirt1mRNA*Sirt1_mRNA) -(kbinmiR181Sirt1*miR181*Sirt1_mRNA) -(kdegSirt1mRNA*Sirt1_mRNA) -(kdegSirt1mRNA*Sirt1_mRNA) -(ksynSirt1*Sirt1_mRNA)
	dSource      = -(ksynFoxO3*Source) -(ksynHoxA11mRNA*Source) -(ksynHoxA11mRNA*Source) -(ksynSirt1mRNA*Source)
	dmiR181      = +(kdegHoxA11mRNAmiR181*miR181_HoxA11_mRNA) +(kdegSirt1mRNAmiR181*miR181_Sirt1_mRNA) +(kdegSirt1mRNAmiR181*miR181_Sirt1_mRNA) +(krelmiR181HoxA11*miR181_HoxA11_mRNA) +(kdegSirt1mRNAmiR181*miR181_Sirt1_mRNA) +(krelmiR181HoxA11*miR181_HoxA11_mRNA) +(krelmiR181HoxA11*miR181_HoxA11_mRNA) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(kdegSirt1mRNAmiR181*miR181_Sirt1_mRNA) +(krelmiR181HoxA11*miR181_HoxA11_mRNA) +(krelmiR181HoxA11*miR181_HoxA11_mRNA) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(krelmiR181HoxA11*miR181_HoxA11_mRNA) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(ksynmiR181*miR181_gene) +(kdegSirt1mRNAmiR181*miR181_Sirt1_mRNA) +(krelmiR181HoxA11*miR181_HoxA11_mRNA) +(krelmiR181HoxA11*miR181_HoxA11_mRNA) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(krelmiR181HoxA11*miR181_HoxA11_mRNA) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(ksynmiR181*miR181_gene) +(krelmiR181HoxA11*miR181_HoxA11_mRNA) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(ksynmiR181*miR181_gene) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(ksynmiR181*miR181_gene) +(ksynmiR181*miR181_gene) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) +(kdegSirt1mRNAmiR181*miR181_Sirt1_mRNA) +(krelmiR181HoxA11*miR181_HoxA11_mRNA) +(krelmiR181HoxA11*miR181_HoxA11_mRNA) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(krelmiR181HoxA11*miR181_HoxA11_mRNA) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(ksynmiR181*miR181_gene) +(krelmiR181HoxA11*miR181_HoxA11_mRNA) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(ksynmiR181*miR181_gene) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(ksynmiR181*miR181_gene) +(ksynmiR181*miR181_gene) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) +(krelmiR181HoxA11*miR181_HoxA11_mRNA) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(ksynmiR181*miR181_gene) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(ksynmiR181*miR181_gene) +(ksynmiR181*miR181_gene) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(ksynmiR181*miR181_gene) +(ksynmiR181*miR181_gene) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) +(ksynmiR181*miR181_gene) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) -(kbinmiR181Sirt1*miR181*Sirt1_mRNA) +(kdegSirt1mRNAmiR181*miR181_Sirt1_mRNA) +(krelmiR181HoxA11*miR181_HoxA11_mRNA) +(krelmiR181HoxA11*miR181_HoxA11_mRNA) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(krelmiR181HoxA11*miR181_HoxA11_mRNA) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(ksynmiR181*miR181_gene) +(krelmiR181HoxA11*miR181_HoxA11_mRNA) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(ksynmiR181*miR181_gene) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(ksynmiR181*miR181_gene) +(ksynmiR181*miR181_gene) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) +(krelmiR181HoxA11*miR181_HoxA11_mRNA) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(ksynmiR181*miR181_gene) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(ksynmiR181*miR181_gene) +(ksynmiR181*miR181_gene) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(ksynmiR181*miR181_gene) +(ksynmiR181*miR181_gene) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) +(ksynmiR181*miR181_gene) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) -(kbinmiR181Sirt1*miR181*Sirt1_mRNA) +(krelmiR181HoxA11*miR181_HoxA11_mRNA) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(ksynmiR181*miR181_gene) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(ksynmiR181*miR181_gene) +(ksynmiR181*miR181_gene) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(ksynmiR181*miR181_gene) +(ksynmiR181*miR181_gene) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) +(ksynmiR181*miR181_gene) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) -(kbinmiR181Sirt1*miR181*Sirt1_mRNA) +(krelmiR181Sirt1*miR181_Sirt1_mRNA) +(ksynmiR181*miR181_gene) +(ksynmiR181*miR181_gene) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) +(ksynmiR181*miR181_gene) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) -(kbinmiR181Sirt1*miR181*Sirt1_mRNA) +(ksynmiR181*miR181_gene) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) -(kbinmiR181Sirt1*miR181*Sirt1_mRNA) -(kbinmiR181HoxA11*miR181*HoxA11_mRNA) -(kbinmiR181Sirt1*miR181*Sirt1_mRNA) -(kbinmiR181Sirt1*miR181*Sirt1_mRNA) -(kdegmiR181*miR181)
	dmiR181_HoxA11_mRNA= +(kbinmiR181HoxA11*miR181*HoxA11_mRNA) -(kdegHoxA11mRNAmiR181*miR181_HoxA11_mRNA) -(kdegHoxA11mRNAmiR181*miR181_HoxA11_mRNA) -(krelmiR181HoxA11*miR181_HoxA11_mRNA)
	dmiR181_Sirt1_mRNA= +(kbinmiR181Sirt1*miR181*Sirt1_mRNA) -(kdegSirt1mRNAmiR181*miR181_Sirt1_mRNA) -(kdegSirt1mRNAmiR181*miR181_Sirt1_mRNA) -(krelmiR181Sirt1*miR181_Sirt1_mRNA)
	dmiR181_gene = +(ksynmiR181*miR181_gene) -(ksynmiR181*miR181_gene)

	return np.array([dFoxO3, dFoxO3_Sirt1, dHoxA11, dHoxA11_mRNA, dMafbx, dmiR181, dmiR181_HoxA11_mRNA, dmiR181_Sirt1_mRNA, dmiR181_gene, dMyoD, dMyoD_gene, dMyoD_gene_FoxO3, dMyoD_gene_HoxA11, dMyoD_mRNA, dSirt1, dSirt1_mRNA, dSink, dSource])