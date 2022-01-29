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
from bokeh.io import curdoc
import utilities as util
import metrics as mtr
import company as cny
import plotter_defaults as dft


class Plotter:
    '''Super class for FundamentalsPlot & ComparisonPlot plots'''
    def __init__(self, base_cie:cny.Company, cie_data:pd.DataFrame):
        self._base_cie = base_cie
        self._cie_data = cie_data
        self._defaults  = dft.get_plot_defaults()


    def _get_y_axis_format(self, metric_set:str, position:str, axis_type:str):
        '''Builds format for y axis'''
        if position == 'top':
            if metric_set in ['bs_metrics', 'income_metrics']:
                try:
                    y_axis_label = f'{self._cie.get_currency().capitalize()}'
                except AttributeError:
                    y_axis_label = 'currency'
            else:
                y_axis_label = 'ratio'
            if axis_type == 'log':
                fmt = '0.000a'
            else:
                if metric_set in ['dividend_metrics', 'debt_metrics', 'income2_metrics']:
                    fmt = '0.%'
                elif metric_set in ['wb_metrics', 'dupont_metrics']:
                    fmt = '0.0a'
                else:
                    fmt = '0.a'
        else: #bottom plot
            y_axis_label = 'growth'
            fmt = '0.%'
        return y_axis_label, fmt


    def _initialize_plot(self, position:str, axis_type:str, source:ColumnDataSource, x_range_name:str ,min_y:float, max_y:float, linked_figure=None):
        '''Initialize plot
           position = top or bottom (plot)
           axis_type = log or linear
           min_y, max_y : y axis bounds
        '''
        if position == 'top':
            plot_height = self._defaults['plot_height']
            x_range     = source.data[x_range_name]
        else:
            plot_height = self._defaults['plot_bottom_height']
            x_range     = linked_figure.x_range # connect bottom plot x-axis to top plot x-axis
        fig = figure(x_range     = x_range,
                     y_range     = [min_y, max_y],
                     plot_width  = self._defaults['plot_width'],
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


    def _build_axes(self, fig, position:str, axis_format:str, y_axis_label:str):
        '''Sets various parameters for x & y axes'''
        # X axis
        fig.xaxis.major_label_text_font_size = self._defaults['top_axis_label_font_size']
        fig.xaxis.axis_label_text_color      = self._defaults['axis_label_color']
        # Y axis
        fig.yaxis.axis_label_text_font_size  = self._defaults['top_axis_label_font_size']
        if position == 'top':
            fig.yaxis.major_label_text_font_size = self._defaults['top_axis_label_font_size']
        else:
            fig.yaxis.major_label_text_font_size = self._defaults['bottom_axis_label_font_size']
        fig.yaxis.axis_label_text_color          = self._defaults['axis_label_color']
        fig.yaxis.axis_label   = y_axis_label
        fig.yaxis[0].formatter = NumeralTickFormatter(format=axis_format)


    def _build_zero_growth_line(self, fig):
        '''Builds zero growth horizontal line on secondary axis'''
        # Build line
        zero_growth = Span(location   = 0.0,
                           dimension  ='width',
                           line_color = self._defaults['zero_growth_line_color'],
                           line_dash  = self._defaults['zero_growth_line_dash'],
                           line_width = self._defaults['zero_growth_line_thickness'],
                           )
        fig.add_layout(zero_growth)
        # Add annotation
        fig.add_layout(self._build_line_caption(text      = '',
                                                x_value   = 2,
                                                y_value   = 0,
                                                x_units   = 'screen',
                                                y_units   = 'data',
                                                color     = self._defaults['zero_growth_font_color'],
                                                font_size = self._defaults['zero_growth_font_size'],
                                                )
                        )


    def _get_minmax_y(self, ts_df:pd.DataFrame, axis_type:str, metric_set:str, plot_position:str):
        '''
        Returns min & max values for top plot y axis
        axis_type: log or linear
        plot_type: bs, dupont, wb, etc
        plot_position: top or bottom
        '''
        if plot_position == 'top':
            max_y = ts_df.max().max()
            if metric_set == 'wb_metrics': # show benchmarks no matter what
                max_y = max(max_y, util.round_up(self._defaults['currentRatio_benchmark'], 1))
            max_y *= 1.05 # leave breathing room above
            if axis_type == 'linear':
                min_y = min(util.round_down(ts_df.min().min(), 1), 0)
                if metric_set == 'valuation_metrics':
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


    def _position_legend(self, fig):
        '''Must be set after legend defined'''
        fig.legend.location     = "top_left"
        fig.legend.click_policy = 'hide'
        fig.legend.orientation  = "vertical"
        fig.legend.label_text_font_size = self._defaults['legend_font_size']
        fig.add_layout(fig.legend[0], 'right')

    @staticmethod
    def _build_nomenclature_caption(metric_set:str):
        '''Builds caption nomenclature to be added to bottom part of plot'''
        return Paragraph(text  = mtr.get_metrics_set_caption(metric_set),
                         align = 'start',
                         )

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


    def _commit(self, tabs, filename:str):
        '''Displays plot, checks output directory exists & saves plot to file'''
        curdoc().theme = self._defaults['theme']
        os.makedirs(os.path.dirname(filename),
                    exist_ok = True,
                    )
        output_file(filename)
        show(tabs)
        save(tabs)
