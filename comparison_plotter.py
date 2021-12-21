#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 16 15:41:32 2021

@author: charly
"""
import pandas as pd
import numpy as np
from bokeh.layouts import gridplot
from bokeh.transform import dodge
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.models import HoverTool, Title
from bokeh.models.widgets import Tabs, Panel
import plotter as pltr
import company as cny


class ComparisonPlotter(pltr.Plotter):
    '''Plotter for fundamentals plots'''
    def __init__(self, base_cie:cny.Company, cie_data:pd.DataFrame, year:str):
        self._base_cie = base_cie
        self._cie_data = cie_data
        self._year     = year
        self._top_cds    = None # metrics
        self._bottom_cds = None # change in metrics
        super().__init__()


    def _build_bottom_cds(self, dataframe):
        '''Build ColumnDataSource for bottom plot (changes in metrics)'''
        dataframe         = dataframe.transpose()
        dataframe.columns = dataframe.columns.str.replace('d_', '')
        dataframe         = dataframe.transpose()
        self._bottom_cds = ColumnDataSource(data = dataframe)


    def _build_cds(self):
        '''Builds column data source corresponding to the time series'''
        rows      = self._cie_data.index.tolist()
        metrics   = rows[0:int(len(rows)/2)]
        d_metrics = rows[int(len(rows)/2):]
        self._cie_data.replace(np.inf, 0, inplace=True) # replace infinity values with 0
        self._cie_data.index.name = 'metric'
        self._cie_data.columns = self._cie_data.columns.str.replace('.', '_')
        self._top_cds  = ColumnDataSource(data = self._cie_data.loc[metrics])
        self._build_bottom_cds(self._cie_data.loc[d_metrics].copy())


    def _build_title(self, fig, defaults:dict, subtitle:str):
        '''Build plot title and subtitle'''
        #subtitle
        fig.add_layout(Title(text=subtitle,
                             align='center',
                             text_font_size=defaults['subtitle_font_size'],
                             text_color=defaults['title_color'],
                             text_font=defaults['text_font']),
                       'above',
                       )
        #title
        fig.add_layout(Title(text=f'{self._base_cie.get_company_name()} & Peers {self._year}',
                             align='center',
                             text_font_size=defaults['title_font_size'],
                             text_color=defaults['title_color'],
                             text_font=defaults['text_font']),
                       'above',
                       )


    def _build_top_bar_plot(self, fig, defaults:dict, companies:list, metrics:list, plot_type:str, source:ColumnDataSource):
        '''Builds bar plots (metrics) on primary axis'''
        x_pos = self._get_initial_x_offset(companies)
        bar_shift = self._get_bar_shift(companies)
        bar_width = defaults['bar_width_shift_ratio'] * bar_shift

        for i, company in enumerate(companies):
            hatch_pattern = ' '
            if i == 0:
                hatch_pattern = '/'
            vbar = fig.vbar(x      = dodge('metric', x_pos, FactorRange(*metrics)),
                            bottom = 1e-6,
                            top    = company,
                            width  = bar_width,
                            source = source,
                            color  = defaults['palette'][i],
                            hatch_pattern = hatch_pattern,
                            hatch_color = 'white',
                            hatch_alpha = 95,
                            legend_label = company,
                            )
            self._build_bar_tooltip(fig=fig, barplot=vbar, companies=companies, plot_type=plot_type, defaults=defaults)
            x_pos += bar_shift


    def _build_bottom_bar_plot(self, fig, defaults:dict, companies:list, metrics:list, source:ColumnDataSource):
        ''''Builds bar plots (metrics) on primary axis'''
        x_pos = self._get_initial_x_offset(companies)
        bar_shift = self._get_bar_shift(companies)
        bar_width = defaults['bar_width_shift_ratio'] * bar_shift

        for i, company in enumerate(companies):
            hatch_pattern = ' '
            if i == 0:
                hatch_pattern = '/'
            vbar = fig.vbar(x      = dodge('metric', x_pos, FactorRange(*metrics)),
                            bottom = 1e-6,
                            top    = company,
                            width  = bar_width,
                            source = source,
                            color  = defaults['palette'][i],
                            hatch_pattern = hatch_pattern,
                            hatch_color = 'white',
                            hatch_alpha = 95,
                            legend_label = company,
                            )
            self._build_bar_tooltip(fig=fig, barplot=vbar, companies=companies, plot_type='', defaults=defaults)
            x_pos += bar_shift


    def _build_bar_tooltip(self, fig, barplot, companies:list, plot_type:str, defaults:dict):
        '''Build tooltips for bar plots'''
        tooltip = [('','@metric')]
        for company in companies:
            prefix = ''
            if plot_type in ['wb', 'dupont', 'valuation', 'valuation2']:
                value = prefix + f'@{company}' + "{0.0a}"
            else:
                prefix = f'{self._base_cie.get_currency_symbol()}'
                value =  prefix + f'@{company}' + '{0.0a}'
                #print(f'value={value}')
            tooltip.append((company, value))
        hover_tool = HoverTool(tooltips   = tooltip,
                               show_arrow = True,
                               renderers  = [barplot],
                               mode       = 'vline',
                               )
        fig.add_tools(hover_tool)


    def plot(self, plot_type:str, subtitle:str, filename:str):
        '''Generic time series bokeh plot for values (bars) and their growth (lines)
           plot_type: either of revenue, bs (balance sheet), dupont, wb ("warren buffet"), ...
           '''
        defaults = self.get_plot_defaults()
        rows     = self._cie_data.index.tolist()
        metrics   = rows[0:int(len(rows)/2)]
        d_metrics = rows[int(len(rows)/2):]

        print(self._cie_data.loc[metrics])
        print(self._cie_data.loc[d_metrics])
        print(self._cie_data.columns.tolist())

        panels = [] # 2 panels: linear and log plots
        for axis_type in ['linear', 'log']:
            min_y, max_y = self._get_minmax_y(ts_df = self._cie_data.loc[metrics],
                                              axis_type = axis_type,
                                              plot_type = plot_type,
                                              defaults  = defaults,
                                              plot_position = 'top',
                                              )
            # source_top = ColumnDataSource(data = self._cie_data.loc[metrics])
            plot_top = self._initialize_plot(position  = 'top',
                                             min_y     = min_y,
                                             max_y     = max_y,
                                             axis_type = axis_type,
                                             defaults  = defaults,
                                             source    = self._top_cds,
                                             x_range_name = 'metric',
                                             )
            # Initialize bottom plot (changes / lines)
            min_y, max_y = self._get_minmax_y(ts_df     = self._cie_data.loc[d_metrics],
                                              axis_type = axis_type,
                                              plot_type = plot_type,
                                              defaults  = defaults,
                                              plot_position = 'bottom',
                                              )
            # source_bottom = ColumnDataSource(data = self._cie_data.loc[d_metrics])
            # print(source_bottom.data)
            plot_bottom = self._initialize_plot(position  = 'bottom',
                                                min_y     = min_y,
                                                max_y     = max_y,
                                                axis_type = 'linear',
                                                defaults  = defaults,
                                                source    = self._bottom_cds,
                                                x_range_name = 'metric',
                                                linked_figure = plot_top
                                                )
            # Add title to top plot
            self._build_title(fig      = plot_top,
                              defaults = defaults,
                              subtitle = subtitle,
                              )
            # Add bars to top plot
            self._build_top_bar_plot(fig       = plot_top, # top blot is bar plot
                                     defaults  = defaults,
                                     companies = self._cie_data.columns.tolist(),
                                     metrics   = metrics,
                                     plot_type = plot_type,
                                     source    = self._top_cds,
                                     )
            # if plot_type == 'wb': # Add benchmarks to WB plot
            #     self._build_wb_benchmarks(fig      = plot_top,
            #                               defaults = defaults,
            #                               )
            # elif plot_type == 'valuation': # Add benchmarks to valuation plot
            #     self._build_valuation_benchmarks(fig      = plot_top,
            #                                      defaults = defaults,
            #                                      )
            # Add growth lines to bottom plot
            self._build_bottom_bar_plot(fig        = plot_bottom, # bottom plot is line plot
                                  defaults  = defaults,
                                  companies = self._cie_data.columns.tolist(),
                                  metrics   = metrics,
                                  source    = self._bottom_cds,
                                  )
            # Format axes and legends on top & bottom plots
            for plot in [plot_top, plot_bottom]:
                if plot == plot_top: #top plot
                    position     = 'top'
                    y_axis_label, fmt = self._get_y_axis_format(plot_type = plot_type,
                                                                position  = position,
                                                                axis_type = axis_type,
                                                                )
                else: #bottom plot
                    position = 'bottom'
                    y_axis_label, fmt = self._get_y_axis_format(plot_type = plot_type,
                                                                position  = position,
                                                                axis_type ='linear',
                                                                )
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
            plot  = gridplot(children = [plot_top,
                                         plot_bottom,
                                         caption_text,
                                         ],
                             ncols    = 1,
                             sizing_mode = 'stretch_width',
                             )
            panel = Panel(child=plot,
                          title=axis_type,
                          )
            panels.append(panel)
        tabs = Tabs(tabs=panels)
        self._commit(tabs, filename)
