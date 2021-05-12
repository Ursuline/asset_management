#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  5 16:39:18 2021

Run parameters

@author: charly
"""
from charting import trading_portfolio as ptf
from charting import trading_defaults as dft

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

# html display plots in browser
DISPLAY_TIME_SERIES  = True
DISPLAY_SURFACE_PLOT = True
DISPLAY_CONTOUR_PLOT = True

REMOTE = False # Cloud or local run

REFRESH_YAHOO = False # Download fresh Yahoo data
REFRESH_EMA   = False  # Recompute ema map

POSITIONS = ['long']

START_DATE = '2018-01-02'

TICKERS = ptf.K_WOOD
TICKERS = ['ARKK']

#END_DATE   = '2021-05-04'
END_DATE   = dft.YESTERDAY

DATE_RANGE = [START_DATE, END_DATE]
ZOOM_RANGE = [START_DATE, END_DATE]
