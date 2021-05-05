#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  5 16:39:18 2021

Run parameters

@author: charly
"""
import trading_portfolio as ptf
import trading_defaults as dft

# Skip these securities
REMOVE  = ['UL', 'FP.PA', 'ORA.PA', 'KC4.F', 'BNP.PA', 'KER.PA', 'SMC.PA']
REMOVE += ['FB', 'HO.PA', 'LHN.SW', 'SQ', 'BIDU', 'ARKQ', 'KORI.PA']
REMOVE += ['TRI.PA', 'HEXA.PA', 'CA.PA', 'ATO.PA', 'SNE']
FILTER  = True # Remove securities from REMOVE list

# RECOMMENDER SWITCHES
# Notifications defaults
SCREEN = True
EMAIL  = True
NOTIFY = True # item-per-item notification

# display time series in browser
DISPLAY = True

CLOUD = False # Cloud or local run

REFRESH_YAHOO = True # Download fresh Yahoo data
REFRESH_EMA   = True  # Recompute ema map

POSITIONS = ['long', 'short']

START_DATE = '2018-01-02'

TICKERS = ptf.CRYPTO
#TICKERS = ['POM.PA']

END_DATE   = '2021-05-04'
END_DATE   = dft.TODAY

DATE_RANGE = [START_DATE, END_DATE]
ZOOM_RANGE = [START_DATE, END_DATE]