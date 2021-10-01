#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 5 16:39:18 2021

Parameter set for sync_tickers.py

@author: charles mégnin
"""
from charting import trading_defaults as dft

# RECOMMENDER SWITCHES
# Notifications defaults
SCREEN = True
EMAIL  = True
NOTIFY = True # item-per-item notification

# html display plots in browser
DISPLAY_TIME_SERIES  = False
DISPLAY_SURFACE_PLOT = True
DISPLAY_CONTOUR_PLOT = True
CTR_SFC_PLOT_FORMATS = 'html' # html or png

REMOTE = False # Cloud or local run

REFRESH_YAHOO = False # Download fresh Yahoo data
REFRESH_EMA   = False  # Recompute ema map

# Cloud server
PORTFOLIO_URL  = 'https://ml-finance.ams3.digitaloceanspaces.com'
PORTFOLIO_PATH = 'charting/portfolios'
PORTFOLIO_DIR  = f'{PORTFOLIO_URL}/{PORTFOLIO_PATH}/'

# Indices
PORTFOLIO_FILES  = ['indices_long.csv', 'indices_short.csv']
# Holdings
PORTFOLIO_FILES += ['charly_crypto.csv', 'charly_crypto_short.csv']
PORTFOLIO_FILES = ['charly_saxo.csv']
PORTFOLIO_FILES += ['saxo_cycliques.csv']
PORTFOLIO_FILES += ['pea_mc.csv', 'adrien.csv']
PORTFOLIO_FILES += ['pea_pme.csv', 'abs.csv']
# Prospective
PORTFOLIO_FILES += ['watchlist_long.csv', 'watchlist_ark.csv', 'watchlist_gafam.csv', 'futures.csv']

#PORTFOLIO_FILES = ['charly_crypto.csv']

START_DATE = '2018-01-02'
END_DATE   = dft.TODAY
#END_DATE = '2021-09-12'

DATE_RANGE = [START_DATE, END_DATE]
ZOOM_RANGE = [START_DATE, END_DATE]
