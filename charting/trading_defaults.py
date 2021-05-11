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

DATA_DIR  = 'charting/data'
PLOT_DIR  = 'charting/plots'
META_DIR  = 'meta'

HUGE       = 1000000

STRATEGIES = ['long', 'short']
POSITIONS  = ['long', 'short', 'cash']
ACTIONS    = ['buy', 'sell', 'n/c']

# Time constants
TODAY     = datetime.strftime(datetime.now(), '%Y-%m-%d')
YESTERDAY = datetime.strftime(datetime.now() - timedelta(days = 1), '%Y-%m-%d')
DEFAULT_PERIOD = '5y'  # data download period

# days after closing. Next day = 1, omniscient = 0
LAG = 1 # Don't change this

#Min & max rolling window spans
MIN_SPAN = 5
MAX_SPAN = 120
DEFAULT_SPAN = 20
SPAN_DIC = dict({'min': MIN_SPAN,
                 'max': MAX_SPAN,
                 'default': DEFAULT_SPAN,
                 })

# Min & max buffer around mean
MIN_BUFF  = 0.0
MAX_BUFF  = 0.08
DEFAULT_BUFFER = .01
N_BUFFERS = 41
BUFFER_DIC = dict({'min': MIN_BUFF,
                   'max': MAX_BUFF,
                   'number': N_BUFFERS,
                   'default': DEFAULT_BUFFER,
                   })

INIT_WEALTH   = 100.0 # index value at time t0

N_MAXIMA_SAVE = 20 # number of maxima to save to file

FEE_PCT        = .004  # broker's fee

#### PLOT DEFAULTS ####
# Bokeh Time series
PLOT_WIDTH   = 1500
PLOT_HDIM_TOP = 600
PLOT_HDIM_BOT = 250
BK_THEMES = ['dark_minimal', 'light_minimal', 'night_sky', 'contrast', 'caliber']

def get_x_hair_color(theme):
    if theme in [BK_THEMES[1], BK_THEMES[4]]:
        return 'black'
    return 'white'

DPI = 360
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

# Plot dimensions
CONTOUR_WIDTH  = 12
SURFACE_WIDTH  = 10
FIG_WIDTH      = 14
FIG_HEIGHT     = 8

# Contour plots
N_CONTOURS     = 10
N_MAXIMA_DISPLAY = 10 # number of maxima to display on contour plot


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
DEFAULT_AZIMUTH = 315

MIN_ELEVATION   = 5
MAX_ELEVATION   = 90
DELTA_ELEVATION = 1
DEFAULT_ELEVATION = 35

MIN_DISTANCE   = 5
MAX_DISTANCE   = 20
DELTA_DISTANCE = 1
DEFAULT_DISTANCE = 10

# default azimuth, elevation, distance
PERSPECTIVE = dict({'azimuth':DEFAULT_AZIMUTH,
                    'elevation': DEFAULT_ELEVATION,
                    'distance': DEFAULT_DISTANCE
                    }
                   )

def get_spans():
    '''returns max & min rolling window spans '''
    return SPAN_DIC

def get_buffers():
    '''returns max, min buffers and increment '''
    return BUFFER_DIC

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
