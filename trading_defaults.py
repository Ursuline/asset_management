#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 15:56:37 2021

# Default variables for trading

@author: charles mégnin
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

#pd.options.display.float_format = '{:,.2f}'.format
pd.set_option("precision", 7)

DATA_DIR  = 'data'
PLOT_DIR  = 'plots'

HUGE       = 1000000
REACTIVITY = 1

POSITIONS = ['long', 'short', 'n/c']
ACTIONS   = ['buy', 'sell', 'n/c']

DEFAULT_PERIOD = '5y'  # data download period

#Min & max rolling window spans
MIN_SPAN = 5
MAX_SPAN = 60

# Min & max buffer around mean
MIN_BUFF  = 0.0
MAX_BUFF  = 0.03
N_BUFFERS = 101

INIT_WEALTH    = 100.0

FEE_PCT        = .004  # broker's fee


#### PLOT DEFAULTS ####
COLOR_SCHEME   = plt.rcParams['axes.prop_cycle'].by_key()['color']
YEAR_MONTH_FMT = mdates.DateFormatter('%b-%y')
TITLE_SIZE     = 14
MAX_LABEL_SIZE = 8
VLINE_COLOR    = 'tomato'
GRID_COLOR     = '#ededed'
TITLE_COLOR    = 'dimgrey'
FIG_WIDTH      = 14
FIG_HEIGHT     = 8

def get_spans():
    '''returns max & min rolling window spans '''
    return [MIN_SPAN, MAX_SPAN]

def get_buffers():
    '''returns max, min buffers and increment '''
    return [MIN_BUFF, MAX_BUFF, N_BUFFERS]

def get_actions():
    '''returns actions '''
    return ACTIONS

def get_positions():
    '''return positions'''
    return POSITIONS

def get_color_scheme():
    '''Returrns default color scheme'''
    return COLOR_SCHEME

def get_year_month_format():
    '''Return date format for axis'''
    return YEAR_MONTH_FMT
