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

pd.options.display.float_format = '{:,.2f}'.format

DATA_DIR  = 'data'
PLOT_DIR  = 'plots'

HUGE     = 1000000

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
color_scheme   = plt.rcParams['axes.prop_cycle'].by_key()['color']
year_month_fmt = mdates.DateFormatter('%b-%y')
title_size     = 14
max_label_size = 8
vline_color    = 'tomato'
gridcolor      = '#ededed'
title_color    = 'dimgrey'
fig_width      = 14
fig_height     = 8

def get_spans():
    '''returns max & min rolling window spans '''
    return [MIN_SPAN, MAX_SPAN]

def get_buffers():
    '''returns max, min buffers and increment '''
    return [MIN_BUFF, MAX_BUFF, N_BUFFERS]

def get_init_wealth():
    '''returns initial_wealth value (typically 100)'''
    return INIT_WEALTH

def get_fee_pct():
    """returns broker's fee"""
    return FEE_PCT

def get_actions():
    '''returns actions '''
    return ACTIONS

def get_positions():
    '''return positions'''
    return POSITIONS
