#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 22 18:19:25 2021

plotter_defaults.py

Handles default values for Plotter class

@author: charly
"""
from bokeh.palettes import Dark2_8

# General
THEME = 'light_minimal'
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
ZERO_GROWTH_FONT_COLOR = 'dimgrey'

# Means lines
MEANS_LINE_DASH = 'dotted'
MEANS_LINE_THICKNESS = 1
MEANS_FONT_SIZE = '9pt'

# Benchmarks
ROE_BENCHMARK = .08
DEBT_EQUITY_BENCHMARK = .5
CURRENT_RATIO_BENCHMARK = 1.5
PRICE_TO_BOOK_RATIO_BENCHMARK = 1.0
PEG_RATIO_BENCHMARK = 1.0
BENCHMARK_LINE_DASH = 'dashed'
BENCHMARK_LINE_THICKNESS = 2
BENCHMARK_FONT_SIZE = '9pt'

#Labels
LABEL_ALPHA = .75
LABEL_FONT_SIZE = '10pt'

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
    # Ttiles
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
    # Means
    defaults['means_line_dash']      = MEANS_LINE_DASH
    defaults['means_line_thickness'] = MEANS_LINE_THICKNESS
    defaults['means_font_size']      = MEANS_FONT_SIZE
    # Labels
    defaults['label_alpha']     = LABEL_ALPHA
    defaults['label_font_size'] = LABEL_FONT_SIZE
    # Axes
    defaults['top_axis_label_font_size']    = TOP_AXIS_LABEL_FONT_SIZE
    defaults['bottom_axis_label_font_size'] = BOTTOM_AXIS_LABEL_FONT_SIZE
    defaults['axis_label_color']       = AXIS_LABEL_COLOR
    return defaults
