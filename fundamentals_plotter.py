#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 12 14:59:53 2021

fundamentals_plotter.py

@author: charly
"""
import pandas as pd
import numpy as np
from bokeh.models import ColumnDataSource
import company as cny

class Fundamentals_plotter:
    '''Plotter for fundamentals plots'''
    def __init__(self, cie:cny.Company, time_series:pd.DataFrame):
        self._cie = cie
        self._time_series = time_series
        self._cds = None
        self._build_cds()

    def _build_cds(self):
        self.time_series.replace(np.inf, 0, inplace=True) # replace infinity values with 0
        self.time_series.index.name = 'year'
        self.time_series.index      = self.time_series.index.astype('string')
        self._cds                   = ColumnDataSource(data = self.time_series)


    def plot(self):
        #def fundamentals_plot(self, time_series:pd.DataFrame, plot_type:str, subtitle:str, filename:str):
        '''
        Generic time series bokeh plot for values (bars) and their growth (lines)
        plot_type: either of revenue, bs (balance sheet), dupont, wb ("warren buffet"), ...
        '''
        defaults = self.get_plot_defaults()


        if plot_type in ['wb', 'dupont', 'valuation', 'valuation2', 'dividend', 'debt', 'income2']:
            top_y_axis_label = 'ratio'
        else:
            top_y_axis_label = f'{self.get_currency().capitalize()}'
        cols = time_series.columns.tolist()
        metrics   = cols[0:int(len(cols)/2)]
        d_metrics = cols[int(len(cols)/2):]

        # Build a dictionary of metrics and their respective means
        means = dict(zip(metrics, time_series[metrics].mean().tolist()))

        panels = []
        for axis_type in ['linear', 'log']:
            # Initialize top plot (data / bars)
            min_y, max_y = self._get_minmax_y(ts_df     = time_series[metrics],
                                              axis_type = axis_type,
                                              plot_type = plot_type,
                                              defaults  = defaults,
                                              plot_position = 'top',
                                              )
            plot_top = self._initialize_plot(position  = 'top',
                                             min_y     = min_y,
                                             max_y     = max_y,
                                             axis_type = axis_type,
                                             defaults  = defaults,
                                             source    = cds,
                                             )
            # Initialize bottom plot (changes / lines)
            min_y, max_y = self._get_minmax_y(ts_df     = time_series[d_metrics],
                                              axis_type = axis_type,
                                              plot_type = plot_type,
                                              defaults  = defaults,
                                              plot_position = 'bottom',
                                              )
            plot_bottom = self._initialize_plot(position  = 'bottom',
                                                max_y     = max_y,
                                                min_y     = min_y,
                                                axis_type = 'linear',
                                                defaults  = defaults,
                                                source    = cds,
                                                linked_figure = plot_top
                                                )
            # Add title to top plot
            self._build_title_bokeh(fig      = plot_top,
                                    defaults = defaults,
                                    subtitle = subtitle,
                                    )
            # Add bars to top plot
            self._build_bar_plots(fig       = plot_top, # top blot is bar plot
                                  defaults  = defaults,
                                  years     = time_series.index.tolist(),
                                  metrics   = metrics,
                                  plot_type = plot_type,
                                  means     = means,
                                  source    = cds,
                                  )
            self._build_means_lines(fig       = plot_top,
                                    defaults  = defaults,
                                    means     = means,
                                    plot_type = plot_type,
                                    )
            # Add WB benchmarks to WB plots
            if plot_type == 'wb':
                self._build_wb_benchmarks(fig      = plot_top,
                                          defaults = defaults,
                                          )
            elif plot_type == 'valuation':
                self._build_valuation_benchmarks(fig      = plot_top,
                                                 defaults = defaults,
                                                 )
            # Add lines to bottom plot
            self._build_line_plots(fig       = plot_bottom, # bottom plot is line plot
                                   defaults  = defaults,
                                   metrics   = d_metrics,
                                   source    = cds,
                                   )
            # Format axes and legends on top & bottom plots
            for plot in [plot_top, plot_bottom]:
                if plot == plot_top:
                    position     = 'top'
                    y_axis_label, fmt = self._get_y_axis_format(plot_type=plot_type, position=position, axis_type=axis_type)
                else: #bottom plot
                    position = 'bottom'
                    y_axis_label, fmt = self._get_y_axis_format(plot_type=plot_type, position=position, axis_type='linear')
                self._build_axes(fig      = plot,
                                 position = position,
                                 defaults = defaults,
                                 y_axis_label = y_axis_label,
                                 axis_format  = fmt,
                                 )
                self._position_legend(fig      = plot,
                                      defaults = defaults,
                                      )
            # Merge top & bottom plots & captions into column
            caption_text =  self._build_caption_text(plot_type)
            plot         = column(plot_top,
                                  plot_bottom,
                                  caption_text,
                                  sizing_mode='stretch_width',
                                  )
            panel        = Panel(child=plot,
                                 title=axis_type,
                                 )
            panels.append(panel)
        tabs = Tabs(tabs=panels)
        show(tabs)
        # Save plot to file
        output_file(filename)
        save(tabs)
