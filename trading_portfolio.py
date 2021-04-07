#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 23:12:46 2021

trading_portfolio.py

Lists of securities to be used by trading_driver.py

@author: charles mégnin
"""
AUTOMOBILE = ['VWAGY', 'BMW.DE', 'DAI.DE', 'STLA.PA']

CHEM       = ['AI.PA', 'SIKA.SW']

COMM       = ['ROKU', 'ZM', 'BIDU', 'NFLX', 'ORA.PA', 'XIL.PA']

DEFENSE    = ['NOC' ,'HO.PA', 'BA', 'PLTR', 'RTX', 'LMT']

FINANCIAL  = ['AMUN.PA', 'BNP.PA', 'GLE.PA', 'CS.PA']

FNB        = ['RI.PA', 'ABI.BR', 'BN.PA', 'BON.PA', 'K', 'HEIA.AS', 'DGE.PA']
FNB       += ['CPR.MI']

HEALTHCARE = ['TDOC', 'BLC.PA', 'PHA.PA', 'KORI.PA', 'ORP.PA', 'NOVN.SW']

INDUSTRIAL = ['SU.PA', 'G1A.DE']

LUXURY     = ['MC.PA', 'RMS.PA', 'OR.PA']

NRJ        = ['FP.PA', 'EDPR.LS']

TECH       = ['AAPL', 'TSLA', 'AMZN', 'MSFT', 'SPOT', 'SQ', 'SHOP', 'GOOGL']
TECH      += ['NVDA', 'HIPAY.PA', 'ATO.PA', 'BIG.PA']


INDICES    = ['^GSPC', '^DJI', '^IXIC', '^FCHI', '^N225', '^HSI', '^DJSH']


SWISS      = ['LHN.SW', 'SIKA.SW']

FRENCH     = ['ELIS.PA', 'KER.PA', 'SMCP.PA', 'BEN.PA']

CRYPTO     = ['BTC-USD', 'ETH-USD']

CSR        = ['MSFT', 'DIS', 'GOOGL', 'BMW.DE', 'DAI.DE', 'SNE', 'INTC']
CSR       += ['VWAGY', 'AAPL', 'NSRGY', 'LEGO', 'CAJ', 'K', 'JNJ']

GAFAM       = ['GOOGL', 'AAPL', 'FB', 'AMZN', 'MSFT']

K_WOOD     = ['ARKF', 'ARKG', 'ARKK', 'ARKQ', 'ARKW']


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

FUTURES     = ['SB=F', 'GC=F']

PORTFOLIOS  = ADRIEN + JACQUELINE + JP + PEA_MC + PEA + SAXO_CY

WANTS       = ['RMS.PA', 'MC.PA', 'SU.PA', 'CPR.MI']

CHECKS      = ['NSN.SW', 'OR.PA', 'DGE.PA', 'CPR.MI', 'RI.PA', 'AI.PA', 'UL']

DIG         = ['NFLX', 'CAJ', 'MKGAF', 'BLC.PA', 'NVDA', 'ZM', 'MSFT']

STABLE      = ['AAPL', 'ABI.BR', 'RMS.PA', 'MC.PA', 'SIKA.SW', 'ALFA.ST']
STABLE     += ['HEIA.AS', 'EDPR.LS', 'NOC', 'BEN.PA']

ACTIVE  = ['ABI.BR', 'SAN.PA', 'SIKA.SW', 'ALFA.ST', 'BIG.PA', 'AI.PA', 'BEN.PA']
ACTIVE += CRYPTO + PORTFOLIOS

OBSERVE = ACTIVE + K_WOOD + GAFAM + CSR + INDICES + WANTS

ALL  = AUTOMOBILE + CHEM + COMM + DEFENSE + FINANCIAL + FNB + HEALTHCARE
ALL += INDUSTRIAL + LUXURY + NRJ + TECH + INDICES + SWISS + FRENCH + CRYPTO
ALL += CSR + GAFAM + K_WOOD + FUTURES