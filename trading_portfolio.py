#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 23:12:46 2021

trading_portfolio.py

Lists of securities to be used by trading_driver.py

@author: charles mégnin
"""
AUTOMOBILE = ['VWAGY', 'BMW.DE', 'DAI.DE', 'STLA.PA', 'POM.PA']

CHEM       = ['AI.PA', 'SIKA.SW']

COMM       = ['ROKU', 'ZM', 'BIDU', 'NFLX', 'ORA.PA', 'XIL.PA']

CONSUMER   = ['NKE', 'MDM.PA']

DEFENSE    = ['NOC' ,'HO.PA', 'BA', 'PLTR', 'RTX', 'LMT']

FINANCIAL  = ['AMUN.PA', 'BNP.PA', 'GLE.PA', 'CS.PA']

FNB        = ['RI.PA', 'ABI.BR', 'BN.PA', 'BON.PA', 'K', 'HEIA.AS', 'DGE.PA']
FNB       += ['CPR.MI']

HEALTHCARE = ['TDOC', 'BLC.PA', 'PHA.PA', 'KORI.PA', 'ORP.PA', 'NOVN.SW', 'BOI.PA']

INDUSTRIAL  = ['SU.PA', 'G1A.DE', 'STF.PA', 'RXL.PA', 'VCT.PA', 'EN.PA', 'VIE.PA']
INDUSTRIAL += ['AIR.PA']

LUXURY     = ['MC.PA', 'RMS.PA', 'OR.PA']

MATERIALS  = ['MLM', 'LHN.SW']

NRJ        = ['FP.PA', 'EDPR.LS', 'NEOEN.PA', 'ABIO.PA']

TECH       = ['AAPL', 'TSLA', 'AMZN', 'MSFT', 'SPOT', 'SQ', 'SHOP', 'GOOGL']
TECH      += ['NVDA', 'HIPAY.PA', 'ATO.PA', 'BIG.PA', 'SOP.PA']


INDICES    = ['^GSPC', '^DJI', '^IXIC', '^FCHI', '^N225', '^HSI', '^DJSH']


SWISS      = ['LHN.SW', 'SIKA.SW']

FRENCH     = ['ELIS.PA', 'KER.PA', 'SMCP.PA', 'BEN.PA']

CRYPTO     = ['BTC-USD', 'ETH-USD']

CSR        = ['MSFT', 'DIS', 'GOOGL', 'BMW.DE', 'DAI.DE', 'SNE', 'INTC']
CSR       += ['VWAGY', 'AAPL', 'NSRGY', 'LEGO', 'CAJ', 'K', 'JNJ']

GAFAM       = ['GOOGL', 'AAPL', 'FB', 'AMZN', 'MSFT']

K_WOOD     = ['ARKF', 'ARKG', 'ARKK', 'ARKQ', 'ARKW']

FUTURES     = ['SB=F', 'GC=F']


ADRIEN     = ['ATO.PA', 'BN.PA', 'BON.PA', 'CA.PA', 'GLE.PA', 'HEXA.PA']
ADRIEN    += ['SPIE.PA', 'TRI.PA']

JACQUELINE  = ['BIG.PA', 'ATO.PA', 'BN.PA', 'BON.PA', 'CA.PA', 'FP.PA', 'KORI.PA']
JACQUELINE += ['ORA.PA', 'SPIE.PA']

JP          = ['ABI.BR', 'ATO.PA', 'BIG.PA', 'BN.PA', 'BNP.PA', 'CA.PA']
JP         += ['FP.PA', 'KORI.PA', 'ORA.PA', 'SAN.PA', 'SPIE.PA', 'XIL.PA']

PEA_MC      = ['BIG.PA', 'FP.PA', 'HO.PA', 'MEDCL.PA', 'NK.PA', 'ORA.PA']
PEA_MC     += ['SAN.PA', 'UFF.PA']

PEA         = ['UL', 'FP.PA', 'SW.PA', 'GLE.PA', 'SAN.PA', 'SGO.PA', 'RI.PA']
PEA        += ['ORA.PA' ,'MKGAF', 'MMT.SG', 'MC.PA', 'LR.PA', 'KC4.F']
PEA        += ['HEIA.AS', 'G1A.DE', 'EL.PA', 'CA.PA', 'BVI.PA', 'BNP.PA']
PEA        += ['CS.PA', 'AI.PA']

SAXO_CY     = ['ABI.BR', 'AI.PA', 'ALLDL.PA', 'BLC.PA', 'EDPR.LS', 'KORI.PA']
SAXO_CY    += ['ORP.PA', 'PHA.PA', 'SOP.PA', 'STLA.PA', 'WLN.PA']

PORTFOLIOS  = ADRIEN + JACQUELINE + JP + PEA_MC + PEA + SAXO_CY


WANTS       = ['RMS.PA', 'MC.PA', 'SU.PA', 'CPR.MI']

DIG         = ['NFLX', 'CAJ', 'MKGAF', 'BLC.PA', 'NVDA', 'ZM', 'MSFT']

STABLE      = ['AAPL', 'ABI.BR', 'RMS.PA', 'MC.PA', 'SIKA.SW', 'ALFA.ST']
STABLE     += ['HEIA.AS', 'EDPR.LS', 'NOC', 'BEN.PA']

ACTIVE  = ['ABI.BR', 'SAN.PA', 'SIKA.SW', 'ALFA.ST', 'BIG.PA', 'AI.PA', 'BEN.PA']
ACTIVE += ['BOI.PA', 'MLM', 'POM.PA', 'ORP.PA', 'NKE', 'STF.PA', 'RXL.PA', 'LHN.SW']
ACTIVE += ['VCT.PA', 'NEOEN.PA', 'ABIO.PA', 'EN.PA', 'VIE.PA', 'AIR.PA', 'MDM.PA']
ACTIVE += ['RBT.PA']
ACTIVE += CRYPTO + PORTFOLIOS

OBSERVE = ACTIVE + K_WOOD + GAFAM + CSR + INDICES + WANTS

ALL  = AUTOMOBILE + CHEM + COMM + CONSUMER + DEFENSE + FINANCIAL + FNB + HEALTHCARE
ALL += INDUSTRIAL + LUXURY + MATERIALS + NRJ + TECH + INDICES + SWISS + FRENCH
ALL += CRYPTO + CSR + GAFAM + K_WOOD + FUTURES