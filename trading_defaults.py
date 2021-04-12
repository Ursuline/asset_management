#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 15:56:37 2021

# Default variables for trading

@author: charles mégnin
"""
from datetime import datetime
from datetime import timedelta
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

#pd.options.display.float_format = '{:,.2f}'.format
pd.set_option("precision", 7)

SSL_PORT = 465
SMTP_SERVER = 'smtp.gmail.com'

STATS_LEVEL = .05 # p-value level

DATA_DIR  = 'data'
PLOT_DIR  = 'plots'
META_DIR  = 'meta'

HUGE       = 1000000
REACTIVITY = 1

POSITIONS = ['long', 'short', 'cash']
ACTIONS   = ['buy', 'sell', 'n/c']

DEFAULT_PERIOD = '5y'  # data download period

#Min & max rolling window spans
MIN_SPAN = 5
MAX_SPAN = 75
DEFAULT_SPAN = 20

# Min & max buffer around mean
MIN_BUFF  = 0.0
MAX_BUFF  = 0.035
DEFAULT_BUFFER = .01
N_BUFFERS = 51

INIT_WEALTH    = 100.0

N_MAXIMA_DISPLAY = 10 # number of maxima to display on contour plot

FEE_PCT        = .004  # broker's fee

#### PLOT DEFAULTS ####
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = 'STIXGeneral'

COLOR_SCHEME   = plt.rcParams['axes.prop_cycle'].by_key()['color']
MO_YR_FMT      = mdates.DateFormatter('%b-%y')
DAY_MO_YR_FMT  = mdates.DateFormatter('%d-%b-%y')
TITLE_SIZE     = 14
MAX_LABEL_SIZE = 8
VLINE_COLOR    = 'tomato'
GRID_COLOR     = '#ededed'
TITLE_COLOR    = 'dimgrey'

#Plot dimensions
CONTOUR_WIDTH  = 12
SURFACE_WIDTH  = 10
FIG_WIDTH      = 14
FIG_HEIGHT     = 8

# Contour plots
N_CONTOURS     = 10

# markers & their legends
ANNOTATE_COLOR = 'black'
MARKER_COLOR   = 'black'

# 3-D plots
SURFACE_COLOR_SCHEMES  = ['viridis', 'cividis', 'plasma', 'inferno', 'magma']
SURFACE_COLOR_SCHEMES += ['hot',  'afmhot']
SURFACE_COLOR_SCHEMES += ['PiYG', 'Spectral', 'bwr', 'seismic']
SURFACE_COLOR_SCHEMES += ['hsv']
SURFACE_COLOR_SCHEMES += ['jet', 'turbo', 'gist_rainbow', 'rainbow', 'nipy_spectral']

CONTOUR_COLOR_SCHEME = SURFACE_COLOR_SCHEMES[0]
SURFACE_COLOR_SCHEME  = SURFACE_COLOR_SCHEMES[12]

MIN_AZIMUTH   = 0
MAX_AZIMUTH   = 360
DELTA_AZIMUTH = 1

MIN_ELEVATION   = 5
MAX_ELEVATION   = 90
DELTA_ELEVATION = 1

MIN_DISTANCE   = 5
MAX_DISTANCE   = 20
DELTA_DISTANCE = 1

# default azimuth, elevation, distance
PERSPECTIVE = [315, 35, 10]

# Time constaants
TODAY     = datetime.strftime(datetime.now(), '%Y-%m-%d')
YESTERDAY = datetime.strftime(datetime.now() - timedelta(days = 1), '%Y-%m-%d')

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

def get_month_year_format():
    '''Return date format for axis'''
    return MO_YR_FMT

def get_day_month_year_format():
    '''Return date format for axis'''
    return DAY_MO_YR_FMT
