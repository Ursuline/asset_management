#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 16 15:31:27 2021

plotter.py
superclass for FundamentalsPlotter and ComparisonPlotter classes

@author: charly
"""
import os
import pandas as pd
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, NumeralTickFormatter, Span, Label
from bokeh.models.widgets import Paragraph
from bokeh.plotting import show, output_file, save
import utilities as util
import metrics as mtr
import company as cny


class Plotter:
    '''Super class for plots'''
    def __init__(self, base_cie:cny.Company, cie_data:pd.DataFrame):
        self._base_cie = base_cie
        self._cie_data = cie_data


    def _get_y_axis_format(self, plot_type:str, position:str, axis_type:str):
        '''Builds format for y axis'''
        if position == 'top':
            if plot_type in ['wb', 'dupont', 'valuation', 'valuation2', 'dividend', 'debt', 'income2']:
                y_axis_label = 'ratio'
            else:
                try:
                    y_axis_label = f'{self._cie.get_currency().capitalize()}'
                except AttributeError:
                    y_axis_label = 'currency'
            if axis_type == 'log':
                fmt = '0.000a'
            else:
                if plot_type in ['dividend', 'debt', 'income2']:
                    fmt = '0.%'
                elif plot_type in ['wb', 'dupont']:
                    fmt = '0.0a'
                else:
                    fmt = '0.a'
        else: #bottom plot
            y_axis_label = 'growth'
            fmt = '0.%'
        return y_axis_label, fmt

    @staticmethod
    def _initialize_plot(position:str, axis_type:str, defaults:dict, source:ColumnDataSource, x_range_name:str ,min_y:float, max_y:float, linked_figure=None):
        '''Initialize plot
           position = top or bottom (plot)
           axis_type = log or linear
           min_y, max_y : y axis bounds
        '''
        if position == 'top':
            plot_height = defaults['plot_height']
            x_range     = source.data[x_range_name]
        else:
            plot_height = defaults['plot_bottom_height']
            x_range     = linked_figure.x_range # connect bottom plot x-axis to top plot x-axis
        fig = figure(x_range     = x_range,
                     y_range     = [min_y, max_y],
                     plot_width  = defaults['plot_width'],
                     plot_height = plot_height,
                     tools       = 'pan, box_zoom, ywheel_zoom, reset, save',
                     y_axis_type = axis_type,
                     )
        fig.xgrid.grid_line_color = None
        # Configure toolbar & bokeh logo
        fig.toolbar.autohide = True
        fig.toolbar_location = 'right'
        fig.toolbar.logo     = None
        return fig

    @staticmethod
    def _build_axes(fig, position:str, defaults:dict, axis_format:str, y_axis_label:str):
        '''Sets various parameters for x & y axes'''
        # X axis
        fig.xaxis.major_label_text_font_size = defaults['top_axis_label_font_size']
        fig.xaxis.axis_label_text_color      = defaults['axis_label_color']
        # Y axis
        fig.yaxis.axis_label_text_font_size  = defaults['top_axis_label_font_size']
        if position == 'top':
            fig.yaxis.major_label_text_font_size = defaults['top_axis_label_font_size']
        else:
            fig.yaxis.major_label_text_font_size = defaults['bottom_axis_label_font_size']
        fig.yaxis.axis_label_text_color      = defaults['axis_label_color']
        fig.yaxis.axis_label   = y_axis_label
        fig.yaxis[0].formatter = NumeralTickFormatter(format=axis_format)


    def _build_zero_growth_line(self, fig, defaults:dict):
        '''Builds zero growth horizontal line on secondary axis'''
        # Build line
        zero_growth = Span(location   = 0.0,
                           dimension  ='width',
                           line_color = defaults['zero_growth_line_color'],
                           line_dash  = defaults['zero_growth_line_dash'],
                           line_width = defaults['zero_growth_line_thickness'],
                           )
        fig.add_layout(zero_growth)
        # Add annotation
        fig.add_layout(self._build_line_caption(text      = '',
                                                x_value   = 2,
                                                y_value   = 0,
                                                x_units   = 'screen',
                                                y_units   = 'data',
                                                color     = defaults['zero_growth_font_color'],
                                                font_size = defaults['zero_growth_font_size'],
                                                )
                        )

    @staticmethod
    def _get_minmax_y(ts_df:pd.DataFrame, axis_type:str, plot_type:str, plot_position:str, defaults:dict):
        '''
        Returns min & max values for top plot y axis
        axis_type: log or linear
        plot_type: bs, dupont, wb, etc
        plot_position: top or bottom
        '''
        if plot_position == 'top':
            max_y = ts_df.max().max()
            if plot_type == 'wb': # show benchmarks no matter what
                max_y = max(max_y, util.round_up(defaults['currentRatio_benchmark'], 1))
            max_y *= 1.05 # leave breathing room above
            if axis_type == 'linear':
                min_y = min(util.round_down(ts_df.min().min(), 1), 0)
                if plot_type == 'valuation':
                    min_y = 0
            else: # Log plot
                min_y = 1e-3
        else: #Bottom plot
            max_y = min(util.round_up(ts_df.max().max(), 1), 10)
            min_y = max(util.round_down(ts_df.min().min(), 1), -1)
        return (min_y, max_y)

    @staticmethod
    def _get_initial_x_offset(columns):
        '''Returns initial bar offset for bar plot'''
        offset = .1
        return - (len(columns) -1) * offset

    @staticmethod
    def _get_bar_shift(columns):
        '''Returns shift amount bw successive bars'''
        if len(columns) == 0:
            return 0
        return .75/len(columns)

    @staticmethod
    def _position_legend(fig, defaults):
        '''Must be set after legend defined'''
        fig.legend.location     = "top_left"
        fig.legend.click_policy = 'hide'
        fig.legend.orientation  = "vertical"
        fig.legend.label_text_font_size = defaults['legend_font_size']
        fig.add_layout(fig.legend[0], 'right')

    @staticmethod
    def _build_caption_text(plot_type):
        '''Builds caption nomenclature to be added to bottom part of plot'''
        if plot_type in ['dupont', 'wb', 'dividend', 'valuation', 'valuation2', 'debt', 'income2']:
            caption_text = Paragraph(text=mtr.metrics_captions[plot_type], align='center')
        else: # no caption
            caption_text = Paragraph(text='')
        return caption_text

    @staticmethod
    def _build_line_caption(text:str, x_value:float, y_value:float, x_units:str, y_units:str, color, font_size:int):
        return Label(x = x_value,
                     y = y_value,
                     x_units = x_units,
                     y_units = y_units,
                     text    = text,
                     text_color     = color,
                     text_font_size = font_size,
                     )

    @staticmethod
    def _commit(tabs, filename):
        # Make sure directory exists & save plot to file
        os.makedirs(os.path.dirname(filename),
                    exist_ok = True
                    )
        output_file(filename)
        save(tabs)
        show(tabs)
