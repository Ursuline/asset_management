#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 22 18:19:25 2021

plotter_defaults.py

Handles default values for Plotter class

@author: charly
"""
import os
from bokeh.palettes import Dark2_8

ROOT       = '/Users/charly/Documents/projects/asset_management'
URL        = 'https://ml-finance.ams3.digitaloceanspaces.com/fundamentals'
FILE       = 'stocks.csv'
PLOT_DIR   = os.path.join(ROOT, 'plots')
DATA_DIR   = os.path.join(ROOT, 'data')
CLOUD_PATH = os.path.join(URL, FILE)
# URL (remote) or DIR (local)
METRICS_SOURCE = 'DIR'
# ----- Don't change the if/else
if METRICS_SOURCE == 'URL':
    METRIC_SETS_PATH = os.path.join(URL, 'metric_sets.yaml')
    METRICS_PATH = os.path.join(URL, 'metrics.yaml')
else:
    METRIC_SETS_PATH = os.path.join(DATA_DIR, 'metric_sets.yaml')
    METRICS_PATH = os.path.join(DATA_DIR, 'metrics.yaml')
# ----------
PERIOD     = 'annual'

# General
THEME = 'dark_minimal'
TEXT_FONT = 'helvetica'
PALETTE = Dark2_8

#Plot dimensions
PLOT_WIDTH = 1200
PLOT_TOP_HEIGHT = 525
PLOT_BOTTOM_HEIGHT = 150

# Axes
TOP_AXIS_LABEL_FONT_SIZE = '12pt'
BOTTOM_AXIS_LABEL_FONT_SIZE = '8pt'
AXIS_LABEL_COLOR = 'dimgrey'

# Title specs
TITLE_COLOR = '#333333'
TITLE_FONT_SIZE = '22pt'
SUBTITLE_FONT_SIZE = '18pt'

#Legend specs
LEGEND_FONT_SIZE = '11pt'

# Bar spacing
BAR_WIDTH_SHIFT_RATIO = .9 # bar width/shift

# Line plots
LINE_DASH = ''

# Zero growth line
ZERO_GROWTH_LINE_COLOR = 'red'
ZERO_GROWTH_LINE_THICKNESS = .5
ZERO_GROWTH_LINE_DASH = 'dashed'
ZERO_GROWTH_FONT_SIZE = '8pt'
ZERO_GROWTH_FONT_COLOR = 'dimgray'

# Means lines
MEANS_LINE_DASH = 'dotted'
MEANS_LINE_THICKNESS = 1
MEANS_FONT_SIZE = '9pt'
MEANS_FONT_COLOR = 'dimgray'

# Benchmarks
ROE_BENCHMARK = .08
DEBT_EQUITY_BENCHMARK = .5
CURRENT_RATIO_BENCHMARK = 1.5
PRICE_TO_BOOK_RATIO_BENCHMARK = 1.0
PEG_RATIO_BENCHMARK = 1.0
BENCHMARK_LINE_DASH = 'dashed'
BENCHMARK_LINE_THICKNESS = 2
BENCHMARK_FONT_SIZE = '9pt'
BENCHMARK_FONT_COLOR = 'dimgray'

#Labels
LABEL_ALPHA = .75
LABEL_FONT_SIZE = '10pt'

#Captions
CAPTION_COLOR = 'dimgray'

def get_data_directory():
    return DATA_DIR

def get_metric_sets_path():
    return METRIC_SETS_PATH

def get_metrics_path():
    return METRICS_PATH

def get_plot_directory():
    return PLOT_DIR

def get_cloud_path():
    return CLOUD_PATH

def get_plot_defaults():
    '''Returns a dictionary of default plot settings'''
    defaults = {}
    # Dimensions
    defaults['plot_width']  = PLOT_WIDTH
    defaults['plot_height'] = PLOT_TOP_HEIGHT
    defaults['plot_bottom_height'] = PLOT_BOTTOM_HEIGHT
    # General
    defaults['theme']     = THEME
    defaults['palette']   = PALETTE
    defaults['text_font'] = TEXT_FONT
    # Titles
    defaults['title_color']        = TITLE_COLOR
    defaults['title_font_size']    = TITLE_FONT_SIZE
    defaults['subtitle_font_size'] = SUBTITLE_FONT_SIZE
    # Legends
    defaults['legend_font_size'] = LEGEND_FONT_SIZE
    defaults['bar_width_shift_ratio'] = BAR_WIDTH_SHIFT_RATIO
    defaults['line_dash'] = LINE_DASH
    # Zero growth line
    defaults['zero_growth_line_color']     = ZERO_GROWTH_LINE_COLOR
    defaults['zero_growth_line_thickness'] = ZERO_GROWTH_LINE_THICKNESS
    defaults['zero_growth_line_dash']      = ZERO_GROWTH_LINE_DASH
    defaults['zero_growth_font_size']      = ZERO_GROWTH_FONT_SIZE
    defaults['zero_growth_font_color']     = ZERO_GROWTH_FONT_COLOR
    # WB Benchmarks:
    defaults['returnOnEquity_benchmark']   = ROE_BENCHMARK
    defaults['debtToEquity_benchmark']     = DEBT_EQUITY_BENCHMARK
    defaults['currentRatio_benchmark']     = CURRENT_RATIO_BENCHMARK
    defaults['priceToBookRatio_benchmark'] = PRICE_TO_BOOK_RATIO_BENCHMARK
    defaults['pegRatio_benchmark']         = PEG_RATIO_BENCHMARK
    defaults['benchmark_line_dash']        = BENCHMARK_LINE_DASH
    defaults['benchmark_line_thickness']   = BENCHMARK_LINE_THICKNESS
    defaults['benchmark_font_size']        = BENCHMARK_FONT_SIZE
    defaults['benchmark_font_color']       = BENCHMARK_FONT_COLOR
    # Means
    defaults['means_line_dash']      = MEANS_LINE_DASH
    defaults['means_line_thickness'] = MEANS_LINE_THICKNESS
    defaults['means_font_size']      = MEANS_FONT_SIZE
    defaults['means_font_color']     = MEANS_FONT_COLOR
    # Labels
    defaults['label_alpha']     = LABEL_ALPHA
    defaults['label_font_size'] = LABEL_FONT_SIZE
    # Axes
    defaults['top_axis_label_font_size']    = TOP_AXIS_LABEL_FONT_SIZE
    defaults['bottom_axis_label_font_size'] = BOTTOM_AXIS_LABEL_FONT_SIZE
    defaults['axis_label_color']            = AXIS_LABEL_COLOR
    # Captions
    defaults['caption_color'] = CAPTION_COLOR
    return defaults
