#!/usr/bin/env python
#
# Author: Qiming Sun <osirpt.sun@gmail.com>
#

'''
XC functional, the interface to libxc
(http://www.tddft.org/programs/octopus/wiki/index.php/Libxc)
'''

import copy
import ctypes
import numpy
import pyscf.lib

libdft = pyscf.lib.load_library('libdft')

# xc_code from libxc
XC_CODES = {
'XC_LDA_X'                :   1,  # Exchange
'XC_LDA_C_WIGNER'         :   2,  # Wigner parametrization
'XC_LDA_C_RPA'            :   3,  # Random Phase Approximation
'XC_LDA_C_HL'             :   4,  # Hedin & Lundqvist
'XC_LDA_C_GL'             :   5,  # Gunnarson & Lundqvist
'XC_LDA_C_XALPHA'         :   6,  # Slater Xalpha
'XC_LDA_C_VWN'            :   7,  # Vosko, Wilk, & Nussair
'XC_LDA_C_VWNRPA'         :   8,  # Vosko, Wilk, & Nussair (RPA)
'XC_LDA_C_PZ'             :   9,  # Perdew & Zunger
'XC_LDA_C_PZMOD'          :  10,  # Perdew & Zunger (Modified)
'XC_LDA_C_OBPZ'           :  11,  # Ortiz & Ballone (PZ)
'XC_LDA_C_PW'             :  12,  # Perdew & Wang
'XC_LDA_C_PWMOD'          :  13,  # Perdew & Wang (Modified)
'XC_LDA_C_OBPW'           :  14,  # Ortiz & Ballone (PW)
'XC_LDA_C_2DAMGB'         :  15,  # Attacalite et al
'XC_LDA_C_2DPRM'          :  16,  # Pittalis, Rasanen & Marques correlation in 2D
'XC_LDA_C_VBH'            :  17,  # von Barth & Hedin
'XC_LDA_C_1DCSC'          :  18,  # Casula, Sorella, and Senatore 1D correlation
'XC_LDA_X_2D'             :  19,  # Exchange in 2D
'XC_LDA_XC_TETER93'       :  20,  # Teter 93 parametrization
'XC_LDA_X_1D'             :  21,  # Exchange in 1D
'XC_LDA_C_ML1'            :  22,  # Modified LSD (version 1) of Proynov and Salahub
'XC_LDA_C_ML2'            :  23,  # Modified LSD (version 2) of Proynov and Salahub
'XC_LDA_C_GOMBAS'         :  24,  # Gombas parametrization
'XC_LDA_C_PWRPA'          :  25,  # Perdew & Wang fit of the RPA
'XC_LDA_C_1DLOOS'         :  26,  # P-F Loos correlation LDA
'XC_LDA_C_RC04'           :  27,  # Ragot-Cortona
'XC_LDA_C_VWN1'           :  28,  # Vosko, Wilk, & Nussair (1)
'XC_LDA_C_VWN2'           :  29,  # Vosko, Wilk, & Nussair (2)
'XC_LDA_C_VWN3'           :  30,  # Vosko, Wilk, & Nussair (3)
'XC_LDA_C_VWN4'           :  31,  # Vosko, Wilk, & Nussair (4)
'XC_LDA_K_TF'             :  50,  # Thomas-Fermi kinetic energy functional
'XC_LDA_K_LP'             :  51,  # Lee and Parr Gaussian ansatz
'XC_GGA_C_Q2D'            :  47,  # Chiodo et al
'XC_GGA_X_Q2D'            :  48,  # Chiodo et al
'XC_GGA_X_PBEMOL'         :  49,  # Del Campo, Gazquez, Trickey and Vela (PBE-like)
'XC_GGA_K_TFVW'           :  52,  # Thomas-Fermi plus von Weiszaecker correction
'XC_GGA_K_REVAPBEINT'     :  53,  # interpolated version of REVAPBE
'XC_GGA_K_APBEINT'        :  54,  # interpolated version of APBE
'XC_GGA_K_REVAPBE'        :  55,  # revised APBE
'XC_GGA_X_AK13'           :  56,  # Armiento & Kuemmel 2013
'XC_GGA_K_MEYER'          :  57,  # Meyer,  Wang, and Young
'XC_GGA_X_LVRPW86'        :  58,  # Berland and Hyldgaard
'XC_GGA_X_PBETCA'         :  59,  # PBE revised by Tognetti et al
'XC_GGA_X_PBEINT'         :  60,  # PBE for hybrid interfaces
'XC_GGA_C_ZPBEINT'        :  61,  # spin-dependent gradient correction to PBEint
'XC_GGA_C_PBEINT'         :  62,  # PBE for hybrid interfaces
'XC_GGA_C_ZPBESOL'        :  63,  # spin-dependent gradient correction to PBEsol
'XC_GGA_XC_OPBED'         :  65,  # oPBE_D functional of Goerigk and Grimme
'XC_GGA_XC_OPWLYPD'       :  66,  # oPWLYP-D functional of Goerigk and Grimme
'XC_GGA_XC_OBLYPD'        :  67,  # oBLYP-D functional of Goerigk and Grimme
'XC_GGA_X_VMT84GE'        :  68,  # VMT{8,4} with constraint satisfaction with mu = mu_GE
'XC_GGA_X_VMT84PBE'       :  69,  # VMT{8,4} with constraint satisfaction with mu = mu_PBE
'XC_GGA_X_VMTGE'          :  70,  # Vela, Medel, and Trickey with mu = mu_GE
'XC_GGA_X_VMTPBE'         :  71,  # Vela, Medel, and Trickey with mu = mu_PBE
'XC_GGA_C_N12SX'          :  79,  # N12-SX functional from Minnesota
'XC_GGA_C_N12'            :  80,  # N12 functional from Minnesota
'XC_GGA_X_N12'            :  82,  # N12 functional from Minnesota
'XC_GGA_C_VPBE'           :  83,  # variant PBE
'XC_GGA_C_OPXALPHA'       :  84,  # one-parameter progressive functional (XALPHA version)
'XC_GGA_C_OPG96'          :  85,  # one-parameter progressive functional (G96 version)
'XC_GGA_C_OPPBE'          :  86,  # one-parameter progressive functional (PBE version)
'XC_GGA_C_OPB88'          :  87,  # one-parameter progressive functional (B88 version)
'XC_GGA_C_FT97'           :  88,  # Filatov & Thiel correlation
'XC_GGA_C_SPBE'           :  89,  # PBE correlation to be used with the SSB exchange
'XC_GGA_X_SSBSW'          :  90,  # Swarta, Sola and Bickelhaupt correction to PBE
'XC_GGA_X_SSB'            :  91,  # Swarta, Sola and Bickelhaupt
'XC_GGA_X_SSBD'           :  92,  # Swarta, Sola and Bickelhaupt dispersion
'XC_GGA_XC_HCTH407P'      :  93,  # HCTH/407+
'XC_GGA_XC_HCTHP76'       :  94,  # HCTH p=7/6
'XC_GGA_XC_HCTHP14'       :  95,  # HCTH p=1/4
'XC_GGA_XC_B97GGA1'       :  96,  # Becke 97 GGA-1
'XC_GGA_XC_HCTHA'         :  97,  # HCTH-A
'XC_GGA_X_BPCCAC'         :  98,  # BPCCAC (GRAC for the energy)
'XC_GGA_C_REVTCA'         :  99,  # Tognetti, Cortona, Adamo (revised)
'XC_GGA_C_TCA'            : 100,  # Tognetti, Cortona, Adamo
'XC_GGA_X_PBE'            : 101,  # Perdew, Burke & Ernzerhof exchange
'XC_GGA_X_PBER'           : 102,  # Perdew, Burke & Ernzerhof exchange (revised)
'XC_GGA_X_B86'            : 103,  # Becke 86 Xalfa,beta,gamma
'XC_GGA_X_HERMAN'         : 104,  # Herman et al original GGA
'XC_GGA_X_B86MGC'         : 105,  # Becke 86 Xalfa,beta,gamma (with mod. grad. correction)
'XC_GGA_X_B88'            : 106,  # Becke 88
'XC_GGA_X_G96'            : 107,  # Gill 96
'XC_GGA_X_PW86'           : 108,  # Perdew & Wang 86
'XC_GGA_X_PW91'           : 109,  # Perdew & Wang 91
'XC_GGA_X_OPTX'           : 110,  # Handy & Cohen OPTX 01
'XC_GGA_X_DK87R1'         : 111,  # dePristo & Kress 87 (version R1)
'XC_GGA_X_DK87R2'         : 112,  # dePristo & Kress 87 (version R2)
'XC_GGA_X_LG93'           : 113,  # Lacks & Gordon 93
'XC_GGA_X_FT97A'          : 114,  # Filatov & Thiel 97 (version A)
'XC_GGA_X_FT97B'          : 115,  # Filatov & Thiel 97 (version B)
'XC_GGA_X_PBESOL'         : 116,  # Perdew, Burke & Ernzerhof exchange (solids)
'XC_GGA_X_RPBE'           : 117,  # Hammer, Hansen & Norskov (PBE-like)
'XC_GGA_X_WC'             : 118,  # Wu & Cohen
'XC_GGA_X_MPW91'          : 119,  # Modified form of PW91 by Adamo & Barone
'XC_GGA_X_AM05'           : 120,  # Armiento & Mattsson 05 exchange
'XC_GGA_X_PBEA'           : 121,  # Madsen (PBE-like)
'XC_GGA_X_MPBE'           : 122,  # Adamo & Barone modification to PBE
'XC_GGA_X_XPBE'           : 123,  # xPBE reparametrization by Xu & Goddard
'XC_GGA_X_2DB86MGC'       : 124,  # Becke 86 MGC for 2D systems
'XC_GGA_X_BAYESIAN'       : 125,  # Bayesian best fit for the enhancement factor
'XC_GGA_X_PBEJSJR'        : 126,  # JSJR reparametrization by Pedroza, Silva & Capelle
'XC_GGA_X_2DB88'          : 127,  # Becke 88 in 2D
'XC_GGA_X_2DB86'          : 128,  # Becke 86 Xalfa,beta,gamma
'XC_GGA_X_2DPBE'          : 129,  # Perdew, Burke & Ernzerhof exchange in 2D
'XC_GGA_C_PBE'            : 130,  # Perdew, Burke & Ernzerhof correlation
'XC_GGA_C_LYP'            : 131,  # Lee, Yang & Parr
'XC_GGA_C_P86'            : 132,  # Perdew 86
'XC_GGA_C_PBESOL'         : 133,  # Perdew, Burke & Ernzerhof correlation SOL
'XC_GGA_C_PW91'           : 134,  # Perdew & Wang 91
'XC_GGA_C_AM05'           : 135,  # Armiento & Mattsson 05 correlation
'XC_GGA_C_XPBE'           : 136,  # xPBE reparametrization by Xu & Goddard
'XC_GGA_C_LM'             : 137,  # Langreth and Mehl correlation
'XC_GGA_C_PBEJRGX'        : 138,  # JRGX reparametrization by Pedroza, Silva & Capelle
'XC_GGA_X_OPTB88VDW'      : 139,  # Becke 88 reoptimized to be used with vdW functional of Dion et al
'XC_GGA_X_PBEK1VDW'       : 140,  # PBE reparametrization for vdW
'XC_GGA_X_OPTPBEVDW'      : 141,  # PBE reparametrization for vdW
'XC_GGA_X_RGE2'           : 142,  # Regularized PBE
'XC_GGA_C_RGE2'           : 143,  # Regularized PBE
'XC_GGA_X_RPW86'          : 144,  # refitted Perdew & Wang 86
'XC_GGA_X_KT1'            : 145,  # Keal and Tozer version 1
'XC_GGA_XC_KT2'           : 146,  # Keal and Tozer version 2
'XC_GGA_C_WL'             : 147,  # Wilson & Levy
'XC_GGA_C_WI'             : 148,  # Wilson & Ivanov
'XC_GGA_X_MB88'           : 149,  # Modified Becke 88 for proton transfer
'XC_GGA_X_SOGGA'          : 150,  # Second-order generalized gradient approximation
'XC_GGA_X_SOGGA11'        : 151,  # Second-order generalized gradient approximation 2011
'XC_GGA_C_SOGGA11'        : 152,  # Second-order generalized gradient approximation 2011
'XC_GGA_C_WI0'            : 153,  # Wilson & Ivanov initial version
'XC_GGA_XC_TH1'           : 154,  # Tozer and Handy v. 1
'XC_GGA_XC_TH2'           : 155,  # Tozer and Handy v. 2
'XC_GGA_XC_TH3'           : 156,  # Tozer and Handy v. 3
'XC_GGA_XC_TH4'           : 157,  # Tozer and Handy v. 4
'XC_GGA_X_C09X'           : 158,  # C09x to be used with the VdW of Rutgers-Chalmers
'XC_GGA_C_SOGGA11X'       : 159,  # To be used with hyb_gga_x_SOGGA11-X
'XC_GGA_X_LB'             : 160,  # van Leeuwen & Baerends
'XC_GGA_XC_HCTH93'        : 161,  # HCTH functional fitted to  93 molecules
'XC_GGA_XC_HCTH120'       : 162,  # HCTH functional fitted to 120 molecules
'XC_GGA_XC_HCTH147'       : 163,  # HCTH functional fitted to 147 molecules
'XC_GGA_XC_HCTH407'       : 164,  # HCTH functional fitted to 407 molecules
'XC_GGA_XC_EDF1'          : 165,  # Empirical functionals from Adamson, Gill, and Pople
'XC_GGA_XC_XLYP'          : 166,  # XLYP functional
'XC_GGA_XC_B97'           : 167,  # Becke 97
'XC_GGA_XC_B971'          : 168,  # Becke 97-1
'XC_GGA_XC_B972'          : 169,  # Becke 97-2
'XC_GGA_XC_B97D'          : 170,  # Grimme functional to be used with C6 vdW term
'XC_GGA_XC_B97K'          : 171,  # Boese-Martin for Kinetics
'XC_GGA_XC_B973'          : 172,  # Becke 97-3
'XC_GGA_XC_PBE1W'         : 173,  # Functionals fitted for water
'XC_GGA_XC_MPWLYP1W'      : 174,  # Functionals fitted for water
'XC_GGA_XC_PBELYP1W'      : 175,  # Functionals fitted for water
'XC_GGA_XC_SB981A'        : 176,  # Schmider-Becke 98 parameterization 1a
'XC_GGA_XC_SB981B'        : 177,  # Schmider-Becke 98 parameterization 1b
'XC_GGA_XC_SB981C'        : 178,  # Schmider-Becke 98 parameterization 1c
'XC_GGA_XC_SB982A'        : 179,  # Schmider-Becke 98 parameterization 2a
'XC_GGA_XC_SB982B'        : 180,  # Schmider-Becke 98 parameterization 2b
'XC_GGA_XC_SB982C'        : 181,  # Schmider-Becke 98 parameterization 2c
'XC_GGA_X_LBM'            : 182,  # van Leeuwen & Baerends modified
'XC_GGA_X_OL2'            : 183,  # Exchange form based on Ou-Yang and Levy v.2
'XC_GGA_X_APBE'           : 184,  # mu fixed from the semiclassical neutral atom
'XC_GGA_K_APBE'           : 185,  # mu fixed from the semiclassical neutral atom
'XC_GGA_C_APBE'           : 186,  # mu fixed from the semiclassical neutral atom
'XC_GGA_K_TW1'            : 187,  # Tran and Wesolowski set 1 (Table II)
'XC_GGA_K_TW2'            : 188,  # Tran and Wesolowski set 2 (Table II)
'XC_GGA_K_TW3'            : 189,  # Tran and Wesolowski set 3 (Table II)
'XC_GGA_K_TW4'            : 190,  # Tran and Wesolowski set 4 (Table II)
'XC_GGA_X_HTBS'           : 191,  # Haas, Tran, Blaha, and Schwarz
'XC_GGA_X_AIRY'           : 192,  # Constantin et al based on the Airy gas
'XC_GGA_X_LAG'            : 193,  # Local Airy Gas
'XC_GGA_XC_MOHLYP'        : 194,  # Functional for organometallic chemistry
'XC_GGA_XC_MOHLYP2'       : 195,  # Functional for barrier heights
'XC_GGA_XC_THFL'          : 196,  # Tozer and Handy v. FL
'XC_GGA_XC_THFC'          : 197,  # Tozer and Handy v. FC
'XC_GGA_XC_THFCFO'        : 198,  # Tozer and Handy v. FCFO
'XC_GGA_XC_THFCO'         : 199,  # Tozer and Handy v. FCO
'XC_GGA_C_OPTC'           : 200,  # Optimized correlation functional of Cohen and Handy
'XC_GGA_K_VW'             : 500,  # von Weiszaecker functional
'XC_GGA_K_GE2'            : 501,  # Second-order gradient expansion (l = 1/9)
'XC_GGA_K_GOLDEN'         : 502,  # TF-lambda-vW form by Golden (l = 13/45)
'XC_GGA_K_YT65'           : 503,  # TF-lambda-vW form by Yonei and Tomishima (l = 1/5)
'XC_GGA_K_BALTIN'         : 504,  # TF-lambda-vW form by Baltin (l = 5/9)
'XC_GGA_K_LIEB'           : 505,  # TF-lambda-vW form by Lieb (l = 0.185909191)
'XC_GGA_K_ABSP1'          : 506,  # gamma-TFvW form by Acharya et al [g = 1 - 1.412/N^(1/3)]
'XC_GGA_K_ABSP2'          : 507,  # gamma-TFvW form by Acharya et al [g = 1 - 1.332/N^(1/3)]
'XC_GGA_K_GR'             : 508,  # gamma-TFvW form by Gazquez and Robles
'XC_GGA_K_LUDENA'         : 509,  # gamma-TFvW form by Ludena
'XC_GGA_K_GP85'           : 510,  # gamma-TFvW form by Ghosh and Parr
'XC_GGA_K_PEARSON'        : 511,  # Pearson
'XC_GGA_K_OL1'            : 512,  # Ou-Yang and Levy v.1
'XC_GGA_K_OL2'            : 513,  # Ou-Yang and Levy v.2
'XC_GGA_K_FRB88'          : 514,  # Fuentealba & Reyes (B88 version)
'XC_GGA_K_FRPW86'         : 515,  # Fuentealba & Reyes (PW86 version)
'XC_GGA_K_DK'             : 516,  # DePristo and Kress
'XC_GGA_K_PERDEW'         : 517,  # Perdew
'XC_GGA_K_VSK'            : 518,  # Vitos, Skriver, and Kollar
'XC_GGA_K_VJKS'           : 519,  # Vitos, Johansson, Kollar, and Skriver
'XC_GGA_K_ERNZERHOF'      : 520,  # Ernzerhof
'XC_GGA_K_LC94'           : 521,  # Lembarki & Chermette
'XC_GGA_K_LLP'            : 522,  # Lee, Lee & Parr
'XC_GGA_K_THAKKAR'        : 523,  # Thakkar 1992
'XC_GGA_X_WPBEH'          : 524,  # short-range version of the PBE
'XC_GGA_X_HJSPBE'         : 525,  # HJS screened exchange PBE version
'XC_GGA_X_HJSPBESOL'      : 526,  # HJS screened exchange PBE_SOL version
'XC_GGA_X_HJSB88'         : 527,  # HJS screened exchange B88 version
'XC_GGA_X_HJSB97X'        : 528,  # HJS screened exchange B97x version
'XC_GGA_X_ITYH'           : 529,  # short-range recipe for exchange GGA functionals
'XC_GGA_X_SFAT'           : 530,  # short-range recipe for exchange GGA functionals
'XC_HYB_GGA_X_N12SX'      :  81,  # N12-SX functional from Minnesota
'XC_HYB_GGA_XC_B3PW91'    : 401,  # The original hybrid proposed by Becke
'XC_HYB_GGA_XC_B3LYP'     : 402,  # The (in)famous B3LYP
'XC_HYB_GGA_XC_B3P86'     : 403,  # Perdew 86 hybrid similar to B3PW91
'XC_HYB_GGA_XC_O3LYP'     : 404,  # hybrid using the optx functional
'XC_HYB_GGA_XC_MPW1K'     : 405,  # mixture of mPW91 and PW91 optimized for kinetics
'XC_HYB_GGA_XC_PBEH'      : 406,  # aka PBE0 or PBE1PBE
'XC_HYB_GGA_XC_B97'       : 407,  # Becke 97
'XC_HYB_GGA_XC_B971'      : 408,  # Becke 97-1
'XC_HYB_GGA_XC_B972'      : 410,  # Becke 97-2
'XC_HYB_GGA_XC_X3LYP'     : 411,  # maybe the best hybrid
'XC_HYB_GGA_XC_B1WC'      : 412,  # Becke 1-parameter mixture of WC and PBE
'XC_HYB_GGA_XC_B97K'      : 413,  # Boese-Martin for Kinetics
'XC_HYB_GGA_XC_B973'      : 414,  # Becke 97-3
'XC_HYB_GGA_XC_MPW3PW'    : 415,  # mixture with the mPW functional
'XC_HYB_GGA_XC_B1LYP'     : 416,  # Becke 1-parameter mixture of B88 and LYP
'XC_HYB_GGA_XC_B1PW91'    : 417,  # Becke 1-parameter mixture of B88 and PW91
'XC_HYB_GGA_XC_MPW1PW'    : 418,  # Becke 1-parameter mixture of mPW91 and PW91
'XC_HYB_GGA_XC_MPW3LYP'   : 419,  # mixture of mPW and LYP
'XC_HYB_GGA_XC_SB981A'    : 420,  # Schmider-Becke 98 parameterization 1a
'XC_HYB_GGA_XC_SB981B'    : 421,  # Schmider-Becke 98 parameterization 1b
'XC_HYB_GGA_XC_SB981C'    : 422,  # Schmider-Becke 98 parameterization 1c
'XC_HYB_GGA_XC_SB982A'    : 423,  # Schmider-Becke 98 parameterization 2a
'XC_HYB_GGA_XC_SB982B'    : 424,  # Schmider-Becke 98 parameterization 2b
'XC_HYB_GGA_XC_SB982C'    : 425,  # Schmider-Becke 98 parameterization 2c
'XC_HYB_GGA_X_SOGGA11X'   : 426,  # Hybrid based on SOGGA11 form
'XC_HYB_GGA_XC_HSE03'     : 427,  # the 2003 version of the screened hybrid HSE
'XC_HYB_GGA_XC_HSE06'     : 428,  # the 2006 version of the screened hybrid HSE
'XC_HYB_GGA_XC_HJSPBE'    : 429,  # HJS hybrid screened exchange PBE version
'XC_HYB_GGA_XC_HJSPBESOL' : 430,  # HJS hybrid screened exchange PBE_SOL version
'XC_HYB_GGA_XC_HJSB88'    : 431,  # HJS hybrid screened exchange B88 version
'XC_HYB_GGA_XC_HJSB97X'   : 432,  # HJS hybrid screened exchange B97x version
'XC_HYB_GGA_XC_CAMB3LYP'  : 433,  # CAM version of B3LYP
'XC_HYB_GGA_XC_TUNEDCAMB3LYP': 434, # CAM version of B3LYP tunes for excitations
'XC_HYB_GGA_XC_BHANDH'    : 435,  # Becke half-and-half
'XC_HYB_GGA_XC_BHANDHLYP' : 436,  # Becke half-and-half with B88 exchange
'XC_HYB_GGA_XC_MB3LYPRC04': 437,  # B3LYP with RC04 LDA
'XC_HYB_GGA_XC_MPWLYP1M'  : 453,  # MPW with 1 par. for metals/LYP
'XC_HYB_GGA_XC_REVB3LYP'  : 454,  # Revised B3LYP
'XC_HYB_GGA_XC_CAMYBLYP'  : 455,  # BLYP with yukawa screening
'XC_HYB_GGA_XC_PBE013'    : 456,  # PBE0-1/3
'XC_MGGA_XC_OTPSSD'       :  64,  # oTPSS_D functional of Goerigk and Grimme
'XC_MGGA_C_CS'            :  72,  # Colle and Salvetti
'XC_MGGA_C_MN12SX'        :  73,  # MN12-SX functional of Minnesota
'XC_MGGA_C_MN12L'         :  74,  # MN12-L functional of Minnesota
'XC_MGGA_C_M11L'          :  75,  # M11-L functional of Minnesota
'XC_MGGA_C_M11'           :  76,  # M11 functional of Minnesota
'XC_MGGA_C_M08SO'         :  77,  # M08-SO functional of Minnesota
'XC_MGGA_C_M08HX'         :  78,  # M08-HX functional of Minnesota
'XC_MGGA_X_LTA'           : 201,  # Local tau approximation of Ernzerhof & Scuseria
'XC_MGGA_X_TPSS'          : 202,  # Perdew, Tao, Staroverov & Scuseria exchange
'XC_MGGA_X_M06L'          : 203,  # M06-Local functional of Minnesota
'XC_MGGA_X_GVT4'          : 204,  # GVT4 from Van Voorhis and Scuseria
'XC_MGGA_X_TAUHCTH'       : 205,  # tau-HCTH from Boese and Handy
'XC_MGGA_X_BR89'          : 206,  # Becke-Roussel 89
'XC_MGGA_X_BJ06'          : 207,  # Becke & Johnson correction to Becke-Roussel 89
'XC_MGGA_X_TB09'          : 208,  # Tran & Blaha correction to Becke & Johnson
'XC_MGGA_X_RPP09'         : 209,  # Rasanen, Pittalis, and Proetto correction to Becke & Johnson
'XC_MGGA_X_2DPRHG07'      : 210,  # Pittalis, Rasanen, Helbig, Gross Exchange Functional
'XC_MGGA_X_2DPRHG07PRP10' : 211,  # PRGH07 with PRP10 correction
'XC_MGGA_X_REVTPSS'       : 212,  # revised Perdew, Tao, Staroverov & Scuseria exchange
'XC_MGGA_X_PKZB'          : 213,  # Perdew, Kurth, Zupan, and Blaha
'XC_MGGA_X_M05'           : 214,  # M05 functional of Minnesota
'XC_MGGA_X_M052X'         : 215,  # M05-2X functional of Minnesota
'XC_MGGA_X_M06HF'         : 216,  # M06-HF functional of Minnesota
'XC_MGGA_X_M06'           : 217,  # M06 functional of Minnesota
'XC_MGGA_X_M062X'         : 218,  # M06-2X functional of Minnesota
'XC_MGGA_X_M08HX'         : 219,  # M08-HX functional of Minnesota
'XC_MGGA_X_M08SO'         : 220,  # M08-SO functional of Minnesota
'XC_MGGA_X_MS0'           : 221,  # MS exchange of Sun, Xiao, and Ruzsinszky
'XC_MGGA_X_MS1'           : 222,  # MS1 exchange of Sun, et al
'XC_MGGA_X_MS2'           : 223,  # MS2 exchange of Sun, et al
'XC_MGGA_X_MS2H'          : 224,  # MS2 hybrid exchange of Sun, et al
'XC_MGGA_X_M11L'          : 226,  # M11-L functional of Minnesota
'XC_MGGA_X_MN12L'         : 227,  # MN12-L functional from Minnesota
'XC_MGGA_X_MN12SX'        : 228,  # MN12-SX functional from Minnesota
'XC_MGGA_C_CC06'          : 229,  # Cancio and Chou 2006
'XC_MGGA_X_MK00'          : 230,  # Exchange for accurate virtual orbital energies
'XC_MGGA_C_TPSS'          : 231,  # Perdew, Tao, Staroverov & Scuseria correlation
'XC_MGGA_C_VSXC'          : 232,  # VSxc from Van Voorhis and Scuseria (correlation part)
'XC_MGGA_C_M06L'          : 233,  # M06-Local functional of Minnesota
'XC_MGGA_C_M06HF'         : 234,  # M06-HF functional of Minnesota
'XC_MGGA_C_M06'           : 235,  # M06 functional of Minnesota
'XC_MGGA_C_M062X'         : 236,  # M06-2X functional of Minnesota
'XC_MGGA_C_M05'           : 237,  # M05 functional of Minnesota
'XC_MGGA_C_M052X'         : 238,  # M05-2X functional of Minnesota
'XC_MGGA_C_PKZB'          : 239,  # Perdew, Kurth, Zupan, and Blaha
'XC_MGGA_C_BC95'          : 240,  # Becke correlation 95
'XC_MGGA_C_REVTPSS'       : 241,  # revised TPSS correlation
'XC_MGGA_XC_TPSSLYP1W'    : 242,  # Functionals fitted for water
'XC_MGGA_X_MK00B'         : 243,  # Exchange for accurate virtual orbital energies (v. B)
'XC_MGGA_X_BLOC'          : 244,  # functional with balanced localization
'XC_MGGA_X_MODTPSS'       : 245,  # Modified Perdew, Tao, Staroverov & Scuseria exchange
'XC_HYB_MGGA_X_M11'       : 225,  # M11 functional of Minnesota
'XC_HYB_MGGA_XC_M05'      : 438,  # M05 functional of Minnesota
'XC_HYB_MGGA_XC_M052X'    : 439,  # M05-2X functional of Minnesota
'XC_HYB_MGGA_XC_B88B95'   : 440,  # Mixture of B88 with BC95 (B1B95)
'XC_HYB_MGGA_XC_B86B95'   : 441,  # Mixture of B86 with BC95
'XC_HYB_MGGA_XC_PW86B95'  : 442,  # Mixture of PW86 with BC95
'XC_HYB_MGGA_XC_BB1K'     : 443,  # Mixture of B88 with BC95 from Zhao and Truhlar
'XC_HYB_MGGA_XC_M06HF'    : 444,  # M06-HF functional of Minnesota
'XC_HYB_MGGA_XC_MPW1B95'  : 445,  # Mixture of mPW91 with BC95 from Zhao and Truhlar
'XC_HYB_MGGA_XC_MPWB1K'   : 446,  # Mixture of mPW91 with BC95 for kinetics
'XC_HYB_MGGA_XC_X1B95'    : 447,  # Mixture of X with BC95
'XC_HYB_MGGA_XC_XB1K'     : 448,  # Mixture of X with BC95 for kinetics
'XC_HYB_MGGA_XC_M06'      : 449,  # M06 functional of Minnesota
'XC_HYB_MGGA_XC_M062X'    : 450,  # M06-2X functional of Minnesota
'XC_HYB_MGGA_XC_PW6B95'   : 451,  # Mixture of PW91 with BC95 from Zhao and Truhlar
'XC_HYB_MGGA_XC_PWB6K'    : 452,  # Mixture of PW91 with BC95 from Zhao and Truhlar for kinetics
'XC_HYB_MGGA_XC_TPSSH'    : 457,  #    TPSS hybrid
'XC_HYB_MGGA_XC_REVTPSSH' : 458,  # revTPSS hybrid
}


LDA_IDS = set((1,  2,  3,  4,  5,  6,  7,  8,  9, 10,
               11, 12, 13, 14, 15, 16, 17, 17, 18, 19,
               20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
               30, 31, 50, 51,))

def is_lda(xc_code):
    if isinstance(xc_code, (tuple, list)):
        xc_code = is_lda(xc_code[0]) and is_lda(xc_code[1])
    else:
        xc_code = _format_code(xc_code)
    if isinstance(xc_code, int):
        if xc_code in LDA_IDS:
            return xc_code
    elif x_code == 'LDA':
        return 1
    elif 'XC_LDA_X_'+x_code in XC_CODES:
        return XC_CODES['XC_LDA_X_'+x_code]
    elif 'XC_LDA_C_'+x_code in XC_CODES:
        return XC_CODES['XC_LDA_C_'+x_code]
    elif 'XC_LDA_XC_'+x_code in XC_CODES:
        return XC_CODES['XC_LDA_XC_'+x_code]
    elif 'XC_LDA_K_'+x_code in XC_CODES:
        return XC_CODES['XC_LDA_K_'+x_code]

    return None


HYB_IDS = set((401, 402, 403, 404, 405, 406, 407, 408, 410, 411,
               412, 413, 414, 415, 416, 417, 418, 419, 420, 421,
               422, 423, 424, 425, 427, 428, 429, 430, 431, 432,
               433, 433, 433, 434, 435, 436, 437, 453, 454, 455,
               456,
               438, 439, 440, 441, 442, 443, 444, 445, 446, 447,
               448, 449, 450, 451, 452, 457, 458,))

def is_hybrid_xc(xc_code):
    if isinstance(xc_code, (tuple, list)):
        xc_code = _format_code(xc_code[0])
    else:
        xc_code = _format_code(xc_code)
    if isinstance(xc_code, int):
        if xc_code in HYB_IDS:
            return xc_code
    else:
        if ',' in xc_code:
            xc_code = xc_code.split(',')[0]

        if 'XC_HYB_GGA_XC_'+xc_code in XC_CODES:
            return XC_CODES['XC_HYB_GGA_XC_'+xc_code]
        elif 'XC_HYB_MGGA_XC_'+xc_code in XC_CODES:
            return XC_CODES['XC_HYB_MGGA_XC_'+xc_code]
        elif 'XC_HYB_GGA_X_'+xc_code in XC_CODES:
            return XC_CODES['XC_HYB_GGA_X_'+xc_code]
        elif 'XC_HYB_MGGA_X_'+xc_code in XC_CODES:
            return XC_CODES['XC_HYB_MGGA_X_'+xc_code]
    return None


MGGA_IDS = set(( 64,  72, 73,  74,  75,  76,  77,  78,  201, 202,
                203, 204, 205, 206, 207, 208, 209, 210, 211, 212,
                213, 214, 215, 216, 217, 218, 219, 220, 221, 222,
                223, 224, 226, 227, 228, 229, 230, 231, 232, 233,
                234, 235, 236, 237, 238, 239, 240, 241, 242, 243,
                244, 245, 225, 438, 439, 440, 441, 442, 443, 444,
                445, 446, 447, 448, 449, 450, 451, 452, 457, 458,))

def is_meta_gga(xc_code):
    if isinstance(xc_code, (tuple, list)):
        xc_code = is_meta_gga(xc_code[0]) or is_meta_gga(xc_code[1])
    else:
        xc_code = _format_code(xc_code)
    if isinstance(xc_code, int):
        if xc_code in MGGA_IDS:
            return xc_code
    else:
        if 'XC_MGGA_X_'+xc_code in XC_CODES:
            return XC_CODES['XC_MGGA_X_'+xc_code]
        elif 'XC_MGGA_C_'+xc_code in XC_CODES:
            return XC_CODES['XC_MGGA_C_'+xc_code]
        elif 'XC_HYB_MGGA_XC_'+xc_code in XC_CODES:
            return XC_CODES['XC_HYB_MGGA_XC_'+xc_code]
        elif 'XC_MGGA_XC_'+xc_code in XC_CODES:
            return XC_CODES['XC_MGGA_XC_'+xc_code]
        elif 'XC_HYB_MGGA_X_'+xc_code in XC_CODES:
            return XC_CODES['XC_HYB_MGGA_X_'+xc_code]
    return None

GGA_IDS = set(( 47,  48,  49,  52,  53,  54,  55,  56,  57,  58,
                59,  60,  61,  62,  63,  65,  66,  67,  68,  69,
                70,  71,  79,  80,  82,  83,  84,  85,  86,  87,
                88,  89,  90,  91,  92,  93,  94,  95,  96,  97,
                98,  99, 100, 101, 102, 103, 104, 105, 106, 107,
               108, 109, 110, 111, 112, 113, 114, 115, 116, 117,
               118, 119, 120, 121, 122, 123, 124, 125, 126, 127,
               128, 129, 130, 131, 132, 133, 134, 135, 136, 137,
               138, 139, 140, 141, 142, 143, 144, 145, 146, 147,
               148, 149, 150, 151, 152, 153, 154, 155, 156, 157,
               158, 159, 160, 161, 162, 163, 164, 165, 166, 167,
               168, 169, 170, 171, 172, 173, 174, 175, 176, 177,
               178, 179, 180, 181, 182, 183, 184, 185, 186, 187,
               188, 189, 190, 191, 192, 193, 194, 195, 196, 197,
               198, 199, 200, 500, 501, 502, 503, 504, 505, 506,
               507, 508, 509, 510, 511, 512, 513, 514, 515, 516,
               517, 518, 519, 520, 521, 522, 523, 524, 525, 526,
               527, 528, 529, 530,
                81, 401, 402, 403, 404, 405, 406, 407, 408, 410,
               411, 412, 413, 414, 415, 416, 417, 418, 419, 420,
               421, 422, 423, 424, 425, 426, 427, 428, 429, 430,
               431, 432, 433, 434, 435, 436, 437, 453, 454, 455,
               456,))

def is_gga(xc_code):
    if isinstance(xc_code, (tuple, list)):
        xc_code = _format_code(xc_code[0])
    else:
        xc_code = _format_code(xc_code)
    if isinstance(xc_code, int):
        if xc_code in GGA_IDS:
            return xc_code
    else:
        if 'XC_GGA_X_'+xc_code in XC_CODES:
            return XC_CODES['XC_GGA_X_'+xc_code]
        elif 'XC_GGA_C_'+xc_code in XC_CODES:
            return XC_CODES['XC_GGA_C_'+xc_code]
        elif 'XC_HYB_GGA_XC_'+xc_code in XC_CODES:
            return XC_CODES['XC_HYB_GGA_XC_'+xc_code]
        elif 'XC_GGA_XC_'+xc_code in XC_CODES:
            return XC_CODES['XC_GGA_XC_'+xc_code]
        elif 'XC_HYB_GGA_X_'+xc_code in XC_CODES:
            return XC_CODES['XC_HYB_GGA_X_'+xc_code]
        elif 'XC_GGA_K_'+xc_code in XC_CODES:
            return XC_CODES['XC_GGA_K_'+xc_code]
    return None

X_AND_C_IDS = set(( 20,  65,  66,  67,  93,  94,  95,  96,  97, 146,
                   154, 155, 156, 157, 161, 162, 163, 164, 165, 166,
                   167, 168, 169, 170, 171, 172, 173, 174, 175, 176,
                   177, 178, 179, 180, 181, 194, 195, 196, 197, 198,
                   199, 401, 402, 403, 404, 405, 406, 407, 408, 410,
                   411, 412, 413, 414, 415, 416, 417, 418, 419, 420,
                   421, 422, 423, 424, 425, 427, 428, 429, 430, 431,
                   432, 433, 434, 435, 436, 437, 453, 454, 455, 456,
                    64, 242, 438, 439, 440, 441, 442, 443, 444, 445,
                   446, 447, 448, 449, 450, 451, 452, 457, 458,))

def is_x_and_c(xc_code):
    if isinstance(xc_code, (tuple, list)):
        xc_code = _format_code(xc_code[0])
    else:
        xc_code = _format_code(xc_code)
    if isinstance(xc_code, int):
        if xc_code in X_AND_C_IDS:
            return xc_code
    else:
        if 'HYB' in xc_code:
            return XC_CODES[xc_code]
        elif 'XC_HYB_GGA_XC_'+xc_code in XC_CODES:
            return XC_CODES['XC_HYB_GGA_XC_'+xc_code]
        elif 'XC_HYB_MGGA_XC_'+xc_code in XC_CODES:
            return XC_CODES['XC_HYB_MGGA_XC_'+xc_code]
        elif 'XC_LDA_XC_'+xc_code in XC_CODES:
            return XC_CODES['XC_LDA_XC_'+xc_code]
        elif 'XC_GGA_XC_'+xc_code in XC_CODES:
            return XC_CODES['XC_GGA_XC_'+xc_code]
        elif 'XC_MGGA_XC_'+xc_code in XC_CODES:
            return XC_CODES['XC_MGGA_XC_'+xc_code]
    return None


def _format_code(xc_code):
    if isinstance(xc_code, str):
        xc_code = xc_code.replace(' ','').replace('-','').replace('_','')
        if xc_code.isdigit():
            xc_code = int(xc_code)
        else:
            xc_code = xc_code.upper()
    return xc_code


# parse xc_code
def parse_xc_name(xc_name='LDA,VWN'):
    '''Convert the XC functional name to libxc library internal ID.
    '''
    if isinstance(xc_name, str):
        if ',' in xc_name:
            x_code, c_code = xc_name.split(',')
            x_code = _format_code(x_code)
            c_code = _format_code(c_code)
        else:
            x_code = _format_code(xc_name)
            c_code = 0
    elif isinstance(xc_name, int):
        x_code, c_code = xc_name, 0
    else:
        x_code, c_code = xc_name

    if isinstance(x_code, str):
        try:
            x_code = convert_x_code(x_code)
        except KeyError:
            return convert_xc_code(x_code), 0

    if isinstance(c_code, str):
        c_code = convert_c_code(c_code)

    return x_code, c_code

def convert_xc_code(x_code):
    if 'XC_HYB_GGA_XC_'+x_code in XC_CODES:
        return XC_CODES['XC_HYB_GGA_XC_'+x_code]
    elif 'XC_HYB_MGGA_XC_'+x_code in XC_CODES:
        return XC_CODES['XC_HYB_MGGA_XC_'+x_code]

    elif 'XC_LDA_XC_'+x_code in XC_CODES:
        return XC_CODES['XC_LDA_XC_'+x_code]
    elif 'XC_GGA_XC_'+x_code in XC_CODES:
        return XC_CODES['XC_GGA_XC_'+x_code]
    elif 'XC_MGGA_XC_'+x_code in XC_CODES:
        return XC_CODES['XC_MGGA_XC_'+x_code]
    else:
        raise KeyError('Unknown exchange functional %s' % x_code)

def convert_x_code(x_code):
    if x_code == 'LDA':
        x_code = 1

    elif 'XC_LDA_X_'+x_code in XC_CODES:
        x_code = XC_CODES['XC_LDA_X_'+x_code]
#    elif 'XC_LDA_K_'+x_code in XC_CODES:
#        x_code = XC_CODES['XC_LDA_K_'+x_code]

    elif 'XC_GGA_X_'+x_code in XC_CODES:
        x_code = XC_CODES['XC_GGA_X_'+x_code]
#    elif 'XC_GGA_K_'+x_code in XC_CODES:
#        x_code = XC_CODES['XC_GGA_K_'+x_code]

    elif 'XC_MGGA_X_'+x_code in XC_CODES:
        x_code = XC_CODES['XC_MGGA_X_'+x_code]

    elif 'XC_HYB_GGA_X_'+x_code in XC_CODES:
        x_code = XC_CODES['XC_HYB_GGA_X_'+x_code]
    elif 'XC_HYB_MGGA_X_'+x_code in XC_CODES:
        x_code = XC_CODES['XC_HYB_MGGA_X_'+x_code]

    else:
        raise KeyError('Unknown exchange functional %s' % x_code)

    return x_code

def convert_c_code(c_code):
    if 'XC_LDA_C_'+c_code in XC_CODES:
        c_code = XC_CODES['XC_LDA_C_'+c_code]

    elif 'XC_GGA_C_'+c_code in XC_CODES:
        c_code = XC_CODES['XC_GGA_C_'+c_code]

    elif 'XC_MGGA_C_'+c_code in XC_CODES:
        c_code = XC_CODES['XC_MGGA_C_'+c_code]

    else:
        raise KeyError('Unknown correlation functional %s' % c_code)

    return c_code


def hybrid_coeff(xc_code, spin=1):
    x_code = is_hybrid_xc(xc_code)
    if x_code is not None:
        libdft.VXChybrid_coeff.restype = ctypes.c_double
        return libdft.VXChybrid_coeff(ctypes.c_int(x_code), ctypes.c_int(spin))
    else:
        return 0

def eval_x(x_id, rho, spin=0, relativity=0, deriv=1, verbose=None,
           _driver='VXCnr_eval_x'):
    r'''Interface to call libxc library to evaluate exchange functional,
    potential and functional derivatives.
    
    See also eval_xc function.
    '''
    if spin == 0:
        rho_u = numpy.asarray(rho, order='C')
        prho_u = rho_u.ctypes.data_as(ctypes.c_void_p)
        prho_d = pyscf.lib.c_null_ptr()
    else:
        rho_u = numpy.asarray(rho[0], order='C')
        rho_d = numpy.asarray(rho[1], order='C')
        prho_u = rho_u.ctypes.data_as(ctypes.c_void_p)
        prho_d = rho_d.ctypes.data_as(ctypes.c_void_p)

    mgga = is_meta_gga(x_id)

    if rho_u.ndim == 2:
        ngrids = rho_u.shape[1]
    else:
        ngrids = len(rho_u)

    if spin == 0:
        nspin = 1
        exc = numpy.empty(ngrids)
        vxc = vrho = vsigma = vlapl = vtau = None
        if deriv > 0:
            if mgga:
                vxc = numpy.zeros(4*ngrids)
                vrho   = vxc[        :ngrids  ]
                vsigma = vxc[ngrids  :ngrids*2]
                vlapl  = vxc[ngrids*2:ngrids*3]
                vtau   = vxc[ngrids*3:        ]
            else:
                vxc = numpy.zeros(2*ngrids)
                vrho   = vxc[      :ngrids]
                vsigma = vxc[ngrids:      ]
            pvxc = vxc.ctypes.data_as(ctypes.c_void_p)
        else:
            pvxc = pyscf.lib.c_null_ptr()
        if deriv > 1:
            if mgga:
                fxc = numpy.zeros(10*ngrids)
                v2rho2      = fxc[        :ngrids  ]
                v2rhosigma  = fxc[ngrids  :ngrids*2]
                v2sigma2    = fxc[ngrids*2:ngrids*3]
                v2lapl2     = fxc[ngrids*3:ngrids*4]
                vtau2       = fxc[ngrids*4:ngrids*5]
                v2rholapl   = fxc[ngrids*5:ngrids*6]
                v2rhotau    = fxc[ngrids*6:ngrids*7]
                v2lapltau   = fxc[ngrids*7:ngrids*8]
                v2sigmalapl = fxc[ngrids*8:ngrids*9]
                v2sigmatau  = fxc[ngrids*9:        ]
            else:
                fxc = numpy.zeros(3*ngrids)
                v2rho2      = fxc[        :ngrids  ]
                v2rhosigma  = fxc[ngrids  :ngrids*2]
                v2sigma2    = fxc[ngrids*2:        ]
                v2lapl2   = vtau2       = v2rholapl  = v2rhotau = \
                v2lapltau = v2sigmalapl = v2sigmatau = None
            pfxc = fxc.ctypes.data_as(ctypes.c_void_p)
            fxc = (v2rho2   , v2rhosigma , v2sigma2  ,
                   v2lapl2  , vtau2      , v2rholapl , v2rhotau,
                   v2lapltau, v2sigmalapl, v2sigmatau,)
        else:
            fxc = None
            pfxc = pyscf.lib.c_null_ptr()
        if deriv > 2:
            kxc = numpy.zeros(4*ngrids)
            v3rho3      = kxc[        :ngrids  ]
            v3rho2sigma = kxc[ngrids  :ngrids*2]
            v3rhosigma2 = kxc[ngrids*2:ngrids*3]
            v3sigma     = kxc[ngrids*3:        ]
            pkxc = kxc.ctypes.data_as(ctypes.c_void_p)
            kxc = (v3rho3, v3rho2sigma, v3rhosigma2, v3sigma)
        else:
            kxc = None
            pkxc = pyscf.lib.c_null_ptr()
    else:
        nspin = 2
        exc = numpy.zeros(ngrids)
        vxc = vrho = vsigma = vlapl = vtau = None
        if deriv > 0:
            if mgga:
                vxc = numpy.zeros(9*ngrids)
                vrho   = vxc[        :ngrids*2].reshape(ngrids,2)
                vsigma = vxc[ngrids*2:ngrids*5].reshape(ngrids,3)
                vlapl  = vxc[ngrids*5:ngrids*7].reshape(ngrids,2)
                vtau   = vxc[ngrids*7:        ].reshape(ngrids,2)
            else:
                vxc = numpy.zeros(5*ngrids)
                vrho   = vxc[        :ngrids*2].reshape(ngrids,2)
                vsigma = vxc[ngrids*2:        ].reshape(ngrids,3)
            pvxc = vxc.ctypes.data_as(ctypes.c_void_p)
        else:
            vxc = vrho = vsigma = vlapl = vtau = None
            pvxc = pyscf.lib.c_null_ptr()
        if deriv > 1:
            if mgga:
                fxc = numpy.zeros(45*ngrids)
                v2rho2      = fxc[         :ngrids* 3].reshape(ngrids,3)
                v2rhosigma  = fxc[ngrids* 3:ngrids* 9].reshape(ngrids,6)
                v2sigma2    = fxc[ngrids* 9:ngrids*15].reshape(ngrids,6)
                v2lapl2     = fxc[ngrids*15:ngrids*18].reshape(ngrids,3)
                vtau2       = fxc[ngrids*18:ngrids*21].reshape(ngrids,3)
                v2rholapl   = fxc[ngrids*21:ngrids*25].reshape(ngrids,4)
                v2rhotau    = fxc[ngrids*25:ngrids*29].reshape(ngrids,4)
                v2lapltau   = fxc[ngrids*29:ngrids*33].reshape(ngrids,4)
                v2sigmalapl = fxc[ngrids*33:ngrids*39].reshape(ngrids,6)
                v2sigmatau  = fxc[ngrids*39:         ].reshape(ngrids,6)
            else:
                fxc = numpy.zeros(15*ngrids)
                v2rho2      = fxc[        :ngrids*3].reshape(ngrids,3)
                v2rhosigma  = fxc[ngrids*3:ngrids*9].reshape(ngrids,6)
                v2sigma2    = fxc[ngrids*9:        ].reshape(ngrids,6)
                v2lapl2   = vtau2       = v2rholapl  = v2rhotau = \
                v2lapltau = v2sigmalapl = v2sigmatau = None
            pfxc = fxc.ctypes.data_as(ctypes.c_void_p)
            fxc = (v2rho2   , v2rhosigma , v2sigma2  ,
                   v2lapl2  , vtau2      , v2rholapl , v2rhotau,
                   v2lapltau, v2sigmalapl, v2sigmatau,)
        else:
            fxc = None
            pfxc = pyscf.lib.c_null_ptr()
        if deriv > 2:
            kxc = numpy.zeros(35*ngrids)
            v3rho3      = kxc[         :ngrids* 4].reshape(ngrids,4 )
            v3rho2sigma = kxc[ngrids* 4:ngrids*13].reshape(ngrids,9 )
            v3rhosigma2 = kxc[ngrids*13:ngrids*25].reshape(ngrids,12)
            v3sigma     = kxc[ngrids*25:         ].reshape(ngrids,10)
            pkxc = kxc.ctypes.data_as(ctypes.c_void_p)
            kxc = (v3rho3, v3rho2sigma, v3rhosigma2, v3sigma)
        else:
            kxc = None
            pkxc = pyscf.lib.c_null_ptr()
    drv = getattr(libdft, _driver)
    drv(ctypes.c_int(x_id), ctypes.c_int(nspin),
        ctypes.c_int(relativity), ctypes.c_int(ngrids),
        prho_u, prho_d,
        exc.ctypes.data_as(ctypes.c_void_p), pvxc, pfxc, pkxc)
    return exc, (vrho, vsigma, vlapl, vtau), fxc, kxc

def eval_c(c_id, rho, spin=0, relativity=0, deriv=1, verbose=None):
    r'''Interface to call libxc library to evaluate correlation functional,
    potential and functional derivatives.
    
    See also eval_xc function.
    '''
    return eval_x(c_id, rho, spin, relativity, deriv, verbose, 'VXCnr_eval_c')

def eval_xc(x_id, c_id, rho, spin=0, relativity=0, deriv=1, verbose=None):
    r'''Interface to call libxc library to evaluate XC functional, potential
    and functional derivatives.

    Args:
        x_id, c_id : int
            Exchange/Correlation functional ID used by libxc library.
            See pyscf/dft/vxc.py for more details.
        rho : ndarray
            Shape of ((*,N)) for electron density (and derivatives) if spin = 0;
            Shape of ((*,N),(*,N)) for alpha/beta electron density (and derivatives) if spin > 0;
            where N is number of grids.
            rho (*,N) are ordered as (den,grad_x,grad_y,grad_z,laplacian,tau)
            where grad_x = d/dx den, laplacian = \nabla^2 den, tau = 1/2(\nabla f)^2
            In spin unrestricted case,
            rho is ((den_u,grad_xu,grad_yu,grad_zu,laplacian_u,tau_u)
                    (den_d,grad_xd,grad_yd,grad_zd,laplacian_d,tau_d))

    Kwargs:
        spin : int
            spin polarized if spin > 0
        relativity : int
            No effects.
        verbose : int or object of :class:`Logger`
            No effects.

    Returns:
        ex, vxc, fxc, kxc

        where

        * vxc = (vrho, vsigma, vlapl, vtau) for unrestricted case
        vrho[*,2]   = (u, d)
        vsigma[*,3] = (uu, ud, dd)
        vlapl[*,2]  = (u, d)
        vtau[*,2]   = (u, d)

        * vxc = (vrho[*], vsigma[*], vlapl[*], vtau[*]) for restricted case

        * fxc(N*45) for unrestricted case:
        | v2rho2[*,3]     = (u_u, u_d, d_d)
        | v2rhosigma[*,6] = (u_uu, u_ud, u_dd, d_uu, d_ud, d_dd)
        | v2sigma2[*,6]   = (uu_uu, uu_ud, uu_dd, ud_ud, ud_dd, dd_dd)
        | v2lapl2[*,3]
        | vtau2[*,3]
        | v2rholapl[*,4]
        | v2rhotau[*,4]
        | v2lapltau[*,4]
        | v2sigmalapl[*,6]
        | v2sigmatau[*,6]

        * fxc(N*10) for restricted case:
        (v2rho2, v2rhosigma, v2sigma2, v2lapl2, vtau2, v2rholapl, v2rhotau, v2lapltau, v2sigmalapl, v2sigmatau)

        * kxc(N*35) for unrestricted case:
        | v3rho3[*,4]       = (u_u_u, u_u_d, u_d_d, d_d_d)
        | v3rho2sigma[*,9]  = (u_u_uu, u_u_ud, u_u_dd, u_d_uu, u_d_ud, u_d_dd, d_d_uu, d_d_ud, d_d_dd)
        | v3rhosigma2[*,12] = (u_uu_uu, u_uu_ud, u_uu_dd, u_ud_ud, u_ud_dd, u_dd_dd, d_uu_uu, d_uu_ud, d_uu_dd, d_ud_ud, d_ud_dd, d_dd_dd)
        | v3sigma[*,10]     = (uu_uu_uu, uu_uu_ud, uu_uu_dd, uu_ud_ud, uu_ud_dd, uu_dd_dd, ud_ud_ud, ud_ud_dd, ud_dd_dd, dd_dd_dd)

        * kxc(N*4) for restricted case:
        (v3rho3, v3rho2sigma, v3rhosigma2, v3sigma)

        see also libxc_itrf.c
    '''
    if 0 and (c_id == 131 or x_id in (402, 404, 411, 416, 419)):
        # second derivative of LYP functional in libxc library diverge
        if spin == 0:
            if rho.ndim == 2:
                idx = rho[0] > 4.57e-11
                ngrids = rho.shape[1]
                rho = rho[:,idx]
            else:
                idx = rho > 4.57e-11
                ngrids = len(rho)
                rho = rho[idx]
        else:
            if rho[0].ndim == 2:
                idx = (rho[0][0] > 4.57e-11) & (rho[1][0] > 4.57e-11)
                ngrids = rho[0].shape[1]
                rho = (rho[0][:,idx], rho[1][:,idx])
            else:
                idx = (rho[0] > 4.57e-11) & (rho[1] > 4.57e-11)
                ngrids = len(rho[0])
                rho = (rho[0][idx], rho[1][idx])

        exc, (vrho, vsigma, vlapl, vtau), fxc, kxc = \
                eval_x(x_id, rho, spin, relativity, deriv, verbose)
        if c_id > 0:
            ec, (vrhoc, vsigmac, vlaplc, vtauc), fc, kc = \
                    eval_c(c_id, rho, spin, relativity, deriv, verbose)
            exc += ec
            if vrho   is not None: vrho   += vrhoc
            if vsigma is not None: vsigma += vsigmac
            if vlapl  is not None: vlapl  += vlaplc
            if vtau   is not None: vtau   += vtauc
            if fxc is not None: # Note: inplace updates for fxc, kxc
                for i, fxci in enumerate(fxc):
                    if fxci is not None:
                        fxci += fc[i]
            if kxc is not None:
                for i, kxci in enumerate(kxc):
                    if kxci is not None:
                        kxci += kc[i]
        def take(v):
            if v is None:
                return None
            elif v.ndim == 1:
                v1 = numpy.zeros(ngrids)
            else:
                v1 = numpy.zeros((ngrids,v.shape[1]))
            v1[idx] = v
            return v1
        exc    = take(exc)
        vrho   = take(vrho)
        vsigma = take(vsigma)
        vlapl  = take(vlapl)
        vtau   = take(vtau)
        if fxc is not None: fxc = [take(v) for v in fxc]
        if kxc is not None: kxc = [take(v) for v in kxc]

    else:

        exc, (vrho, vsigma, vlapl, vtau), fxc, kxc = \
                eval_x(x_id, rho, spin, relativity, deriv, verbose)
        if c_id > 0:
            ec, (vrhoc, vsigmac, vlaplc, vtauc), fc, kc = \
                    eval_c(c_id, rho, spin, relativity, deriv, verbose)
            exc += ec
            if vrho   is not None: vrho   += vrhoc
            if vsigma is not None: vsigma += vsigmac
            if vlapl  is not None: vlapl  += vlaplc
            if vtau   is not None: vtau   += vtauc
            if fxc is not None: # Note: inplace updates for fxc, kxc
                for i, fxci in enumerate(fxc):
                    if fxci is not None:
                        fxci += fc[i]
            if kxc is not None:
                for i, kxci in enumerate(kxc):
                    if kxci is not None:
                        kxci += kc[i]
    return exc, (vrho, vsigma, vlapl, vtau), fxc, kxc


def define_xc(ni, description):
    '''Define the XC functional for numeric integration.  Rules to input
    functional description:

    * The given functional description must be a one-line string.
    * The functional description is case-insensitive.
    * The functional description string has two parts, separated by ",".  The
      first part describes the exchange functional, the second is the correlation
      functional.  If "," not appeared in string, entire string is considered as
      X functional.  There is no way to neglect X functional (just apply C
      functional)
    * The functional name can be placed in arbitrary order.  Two name needs to
      be separated by operations + or -.  Blank spaces are ignored.
      NOTE the parser only reads operators + - *.  / is not in support.
    * A functional name is associated with one factor.  If the factor is not
      given, it is assumed equaling 1.
    * String "HF" stands for exact exchange (HF K matrix).  It is allowed to
      put in C functional part.
    * Be careful with the libxc convention on GGA functional, in which the LDA
      contribution is included.

    Args:
        ni : an instance of :class:`_NumInt`

        description : str
            A string to describe the linear combination of different XC functionals.
            The X and C functional are separated by comma like '.8*LDA+.2*B86,VWN'.
            If "HF" was appeared in the string, it stands for the exact exchange.

    Examples:

    >>> mol = gto.M(atom='O 0 0 0; H 0 0 1; H 0 1 0', basis='ccpvdz')
    >>> mf = dft.RKS(mol)
    >>> mf._numint = define_xc(mf._numint, '.2*HF + .08*LDA + .72*B88, .81*LYP + .19*VWN')
    >>> mf.kernel()
    -76.3783361189611
    '''
    return define_xc_(copy.copy(ni), description)

def define_xc_(ni, description):
    '''Define the XC functional for numeric integration.  Rules to input
    functional description:

    * The given functional description must be a one-line string.
    * The functional description is case-insensitive.
    * The functional description string has two parts, separated by ",".  The
      first part describes the exchange functional, the second is the correlation
      functional.  If "," not appeared in string, entire string is considered as
      X functional.  There is no way to neglect X functional (just apply C
      functional)
    * The functional name can be placed in arbitrary order.  Two name needs to
      be separated by operations + or -.  Blank spaces are ignored.
      NOTE the parser only reads operators + - *.  / is not in support.
    * A functional name is associated with one factor.  If the factor is not
      given, it is assumed equaling 1.
    * String "HF" stands for exact exchange (HF K matrix).  It is allowed to
      put in C functional part.
    * Be careful with the libxc convention on GGA functional, in which the LDA
      contribution is included.

    Args:
        ni : an instance of :class:`_NumInt`

        description : str
            A string to describe the linear combination of different XC functionals.
            The X and C functional are separated by comma like '.8*LDA+.2*B86,VWN'.
            If "HF" was appeared in the string, it stands for the exact exchange.

    Examples:

    >>> mol = gto.M(atom='O 0 0 0; H 0 0 1; H 0 1 0', basis='ccpvdz')
    >>> mf = dft.RKS(mol)
    >>> define_xc_(mf._numint, '.2*HF + .08*LDA + .72*B88, .81*LYP + .19*VWN')
    >>> mf.kernel()
    -76.3783361189611
    >>> define_xc_(mf._numint, 'LDA*.08 + .72*B88 + .2*HF, .81*LYP + .19*VWN')
    >>> mf.kernel()
    -76.3783361189611
    '''
    if ',' in description:
        x_code, c_code = description.replace(' ','').upper().split(',')
    else:
        x_code, c_code = description.replace(' ','').upper(), ''

    hyb = 0
    acc = []
# Split to terms for additions
    tokens = [x for x in x_code.replace('-', '+-').split('+') if x]
    for t in tokens:
        if '*' in t:
            fac, key = t.split('*')
            if fac[0].isalpha():
                fac, key = key, fac
            fac = float(fac)
        else:
            fac, key = 1, t
        if key == 'HF':
            hyb = fac
        else:
            x_id = is_x_and_c(key)
            if x_id is None:
                x_id = convert_x_code(key)
            acc.append((fac, eval_x, x_id))

    tokens = [x for x in c_code.replace('-', '+-').split('+') if x]
    for t in tokens:
        if '*' in t:
            fac, key = t.split('*')
            if fac[0].isalpha():
                fac, key = key, fac
            fac = float(fac)
        else:
            fac, key = 1, t
        c_id = convert_c_code(key)
        acc.append((fac, eval_c, c_id))

    # search for the highest XC funcitonal type
    xctype = 'LDA'
    for x in acc:
        if is_lda(x[2]):
            pass
        elif is_meta_gga(x[2]):
            xctype = 'MGGA'
            raise NotImplementedError('meta-GGA')
            break
        else:
            xctype = 'GGA'
            break

    def eval_xc(x_id, c_id, rho, spin=0, relativity=0, deriv=1, verbose=None):
        fac, fn, xcid = acc[0]
        exc, (vrho, vsigma, vlapl, vtau), fxc, kxc = \
                fn(xcid, rho, spin, relativity, deriv, verbose)
        exc *= fac
        if vrho   is not None: vrho   *= fac
        if vsigma is not None: vsigma *= fac
        if vlapl  is not None: vlapl  *= fac
        if vtau   is not None: vtau   *= fac
        if fxc is not None:
            for i, fxci in enumerate(fxc):
                if fxci is not None:
                    fxci *= fac
        if kxc is not None:
            for i, kxci in enumerate(kxc):
                if kxci is not None:
                    kxci *= fac

        for fac, fn, xcid in acc[1:]:
            ec, (vrhoc, vsigmac, vlaplc, vtauc), fc, kc = \
                    fn(xcid, rho, spin, relativity, deriv, verbose)
            exc += fac*ec
            if vrho   is not None: vrho   += fac*vrhoc
            if vsigma is not None: vsigma += fac*vsigmac
            if vlapl  is not None: vlapl  += fac*vlaplc
            if vtau   is not None: vtau   += fac*vtauc
            if fxc is not None: # Note: inplace updates for fxc, kxc
                for i, fxci in enumerate(fxc):
                    if fxci is not None:
                        fxci += fac*fc[i]
            if kxc is not None:
                for i, kxci in enumerate(kxc):
                    if kxci is not None:
                        kxci += fac*kc[i]

        return exc, (vrho, vsigma, vlapl, vtau), fxc, kxc

    ni.eval_xc = eval_xc
    ni.hybrid_coeff = lambda *args, **kwargs: hyb
    ni._xc_type = lambda *args: xctype
    return ni

B3LYP5 = '.2*HF + .08*LDA + .72*B88, .81*LYP + .19*VWN'
BLYP = 'B88,LYP'




if __name__ == '__main__':
    from pyscf import gto, dft
    mol = gto.M(
        atom = [
        ["O" , (0. , 0.     , 0.)],
        [1   , (0. , -0.757 , 0.587)],
        [1   , (0. , 0.757  , 0.587)] ],
        basis = '6311g*',)
    mf = dft.RKS(mol)
    mf.xc = 'b88,lyp'
    eref = mf.kernel()

    mf = dft.RKS(mol)
    mf._numint = define_xc(mf._numint, BLYP)
    e1 = mf.kernel()
    print(e1 - eref)

    mf = dft.RKS(mol)
    mf._numint = define_xc(mf._numint, B3LYP5)
    e1 = mf.kernel()
    print(e1 - -76.4102717186263)
