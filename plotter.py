#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 16 15:31:27 2021

plotter.py
superclass for fundamentals`Plotter and comparisonPlotter classes

@author: charly
"""
import math
import numpy as np
import pandas as pd
from bokeh.models import ColumnDataSource
from bokeh.palettes import Dark2_8
import company as cny


# Utilities
def round_up(val:float, ndigits:int):
    '''round up utility'''
    return (math.ceil(val * math.pow(10, ndigits)) + 1) / math.pow(10, ndigits)


def round_down(val:float, ndigits:int):
    '''round down utility'''
    return (math.floor(val * math.pow(10, ndigits)) - 1) / math.pow(10, ndigits)

class Plotter:
    '''Super class for plots'''
    def __init__(self, cie:cny.Company, time_series:pd.DataFrame):
        self._cie = cie
        self._time_series = time_series
        self._cds = None
        self._build_cds()

    def _build_cds(self):
        '''Builds column data source corresponding to the time series'''
        self._time_series.replace(np.inf, 0, inplace=True) # replace infinity values with 0
        self._time_series.index.name = 'year'
        self._time_series.index      = self._time_series.index.astype('string')
        self._cds                   = ColumnDataSource(data = self._time_series)

    def _map_item_to_name(self, item:str):
        '''Converts column name to readable metric (WIP)'''
        if item.startswith('d_'):
            return '\u0394 ' + self._map_item_to_name(item[2:])
        itemdict = {'assetturnover':           'Asset turnover',
                    'croic':                   'Cash ROIC',
                    'currentratio':            'Current ratio',
                    'debttoassets':            'Debt-to-assets ratio',
                    'debttoequity':            'Debt-to-equity ratio',
                    'dividendyield':           'Dividend yield',
                    'ebit':                    'EBIT',
                    'ebitperrevenue':          'EBIT-to-revenue',
                    'evtoebit':                'E.V.-to-ebit',
                    'equitymultiplier':        'Equity multiplier',
                    'freecashflow':            'FCF',
                    'grossprofitratio':        'Gross profit margin',
                    'interestcoverage':        'Interest coverage',
                    'freecashflowtorevenue':   'FCF-to-revenue',
                    'netdebttoebit':           'Net debt-to-ebit',
                    'netprofitmargin':         'Net profit margin',
                    'payoutratio':             'Payout ratio',
                    'peg':                     'P/E-to-growth',
                    'peratio':                 'P/E ratio',
                    'pricetobookratio':        'Price-to-book ratio',
                    'pricetosalesratio':       'Price-to-sales ratio',
                    'returnonequity':          'ROE',
                    'revenue':                 'Revenue',
                    'roic':                    'ROIC',
                    'shorttermcoverageratios': 'Short term coverage ratio',
                    'totalassets':             'Total assets',
                    'totalliabilities':        'Total liabilities',
                    'totalstockholdersequity': 'Total stockholders equity',
                    }
        try:
            return itemdict[item.lower()]
        except:
            print(f'_map_item_to_name(): No mapping for item "{item}"')
            return ''


    @staticmethod
    def get_plot_defaults():
        '''Returns default plot settings'''
        defaults = {}
        defaults['plot_width']  = 1200
        defaults['plot_height'] = 500
        defaults['plot_bottom_height'] = 200
        defaults['theme']     = 'light_minimal'
        defaults['palette']   = Dark2_8
        defaults['text_font'] = 'helvetica'
        # Title
        defaults['title_color']        = '#333333'
        defaults['title_font_size']    = '22pt'
        defaults['subtitle_font_size'] = '18pt'
        # Legend
        defaults['legend_font_size'] = '11pt'
        # Bars
        defaults['bar_width_shift_ratio'] = .9 # bar width/shift
        # Lines
        defaults['line_dash'] = ''
        defaults['zero_growth_line_color']     = 'red'
        defaults['zero_growth_line_thickness'] = .5
        defaults['zero_growth_line_dash']      = 'dotted'
        defaults['zero_growth_font_size']      = '8pt'
        defaults['zero_growth_font_color']     = 'dimgray'
        # WB Benchmarks:
        defaults['returnOnEquity_benchmark'] = .08
        defaults['debtToEquity_benchmark']   = .5
        defaults['currentRatio_benchmark']   = 1.5
        defaults['priceToBookRatio_benchmark'] = 1.0
        defaults['pegRatio_benchmark']        = 1.0
        defaults['benchmark_line_dash']      = 'dashed'
        defaults['benchmark_line_thickness'] = 2
        defaults['benchmark_font_size']      = '9pt'
        # Means
        defaults['means_line_dash']      = 'dotted'
        defaults['means_line_thickness'] = 1
        defaults['means_font_size']      = '9pt'

        defaults['label_alpha']     = .75
        defaults['label_font_size'] = '10pt'
        # Axes
        defaults['top_axis_label_text_font_size']    = '12pt'
        defaults['bottom_axis_label_text_font_size'] = '8pt'
        defaults['axis_label_text_color']            = 'dimgray'
        return defaults
