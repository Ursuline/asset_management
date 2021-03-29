#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 23:12:46 2021

trading_portfolio.py

Lists of securities to be used by trading_driver.py

@author: charles mégnin
"""

INDICES    = ['^GSPC', '^DJI', '^IXIC', '^FCHI', '^N225', '^HSI', '^DJSH']
DEFENSE    = ['NOC' ,'HO.PA', 'BA', 'PLTR', 'RTX', 'LMT']
HEALTHCARE = ['TDOC', 'BLC.PA', 'PHA.PA', 'KORI.PA', 'ORP.PA']
LUXURY     = ['MC.PA', 'RMS.PA', 'OR.PA']
FRENCH     = ['SU.PA', 'FP.PA', 'STLA.PA', 'ELIS.PA', 'LHN.SW']
K_WOOD     = ['ARKF', 'ARKG', 'ARKK', 'ARKQ', 'ARKW']
TECH       = ['AAPL', 'TSLA', 'AMZN', 'MSFT', 'SPOT', 'SQ', 'SHOP', 'GOOGL']
TECH      += ['NVDA', 'HIPAY.PA']
CSR        = ['MSFT', 'DIS', 'GOOGL', 'BMW.DE', 'DAI.DE', 'SNE', 'INTC']
CSR       += ['VWAGY', 'AAPL', 'NSRGY', 'LEGO', 'CAJ', 'K', 'JNJ']
COMM       = ['ROKU', 'ZM', 'BIDU', 'NFLX']
CRYPTO     = ['BTC-USD', 'ETH-USD']
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
FUTURES     = ['SB=F', 'SG=F']
NEW = ['LHN.SW', 'HIPAY.PA']