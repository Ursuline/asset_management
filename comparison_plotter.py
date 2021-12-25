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
import metrics as mtr


class ComparisonPlotter(pltr.Plotter):
    '''Plotter for fundamentals plots'''
    def __init__(self, base_cie:cny.Company, cie_data:pd.DataFrame, peer_names:list, year:str):
        super().__init__(base_cie=base_cie, cie_data=cie_data)
        self._peer_names = peer_names
        self._year       = year
        self._top_cds    = None # ColumnDataSource metrics
        self._bottom_cds = None # ColumnDataSource change in metrics


    def _build_top_cds(self, dataframe):
        '''Build ColumnDataSource for top plot (metrics)'''
        dataframe         = dataframe.transpose()
        for column in dataframe.columns:
            dataframe.rename(columns={column : mtr.map_item_to_name(column)}, inplace=True)
        dataframe         = dataframe.transpose()
        self._top_cds  = ColumnDataSource(data = dataframe)


    def _build_bottom_cds(self, dataframe):
        '''Build ColumnDataSource for bottom plot (changes in metrics)'''
        dataframe         = dataframe.transpose()
        dataframe.columns = dataframe.columns.str.replace('d_', '')
        for column in dataframe.columns:
            dataframe.rename(columns={column : mtr.map_item_to_name(column)}, inplace=True)
        dataframe         = dataframe.transpose()
        self._bottom_cds = ColumnDataSource(data = dataframe)


    def _build_cds(self):
        '''Builds 2 column data sources corresponding to the time series'''
        rows      = self._cie_data.index.tolist()
        metrics   = rows[0:int(len(rows)/2)]
        d_metrics = rows[int(len(rows)/2):]
        self._cie_data.replace(np.inf, 0, inplace=True) # replace infinity values with 0
        self._cie_data.index.name = 'metric'
        self._build_top_cds(self._cie_data.loc[metrics].copy())
        self._build_bottom_cds(self._cie_data.loc[d_metrics].copy())


    def _build_title(self, fig, subtitle:str):
        '''Build plot title and subtitle'''
        #subtitle
        fig.add_layout(Title(text  = subtitle,
                             align = 'center',
                             text_font_size = self._defaults['subtitle_font_size'],
                             text_color     = self._defaults['title_color'],
                             text_font      = self._defaults['text_font'],
                             ),
                       'above',
                       )
        #title
        text = f'{self._base_cie.get_company_name()} & peers ({self._year})'
        fig.add_layout(Title(text  = text,
                             align = 'center',
                             text_font_size = self._defaults['title_font_size'],
                             text_color     = self._defaults['title_color'],
                             text_font      = self._defaults['text_font'],
                             ),
                       'above',
                       )

    def _build_bar_plot(self, fig, companies:list, metrics:list, metric_set:str, position:str, source:ColumnDataSource):
        '''Builds bar plots (metrics) on primary axis'''
        x_pos     = self._get_initial_x_offset(companies)
        bar_shift = self._get_bar_shift(companies)
        bar_width = self._defaults['bar_width_shift_ratio'] * bar_shift
        for i, company in enumerate(companies):
            hatch_pattern = ' '
            if i == 0:
                hatch_pattern = '/'
            vbar = fig.vbar(x      = dodge('metric', x_pos, FactorRange(*metrics)),
                            bottom = 1e-6,
                            top    = company,
                            width  = bar_width,
                            source = source,
                            color  = self._defaults['palette'][i],
                            hatch_pattern = hatch_pattern,
                            hatch_color   = 'white',
                            hatch_alpha   = 95,
                            legend_label  = company,
                            )
            self._build_bar_tooltip(fig        = fig,
                                    barplot    = vbar,
                                    companies  = companies,
                                    metric_set = metric_set,
                                    position   = position,
                                    )
            x_pos += bar_shift
            if position == 'bottom':
                self._build_zero_growth_line(fig)


    def _build_bar_tooltip(self, fig, barplot, companies:list, metric_set:str, position:str):
        '''Build tooltips for bar plots'''
        fmt = mtr.get_tooltip_format(metric_set) # tooltip format
        #First row of tooltips is the metric name
        if position == 'top':
            tooltip = [('', '@metric')]
        else: #botom plot is change
            year = int(self._year)
            tooltip = [('', '\u0394 @metric'),
                       ('', f'({year-1}-{year})'),] #reference year in 2nd row

        for company in companies:
            prefix = ''
            if position == 'top': #tooltips for top plot
                if metric_set in ['income_metrics', 'bs_metrics']: # currency plots
                    prefix = f'{self._base_cie.get_currency_symbol()}'
                value = prefix + '@{' + company + '}' + f'{fmt}'

            else: #tooltips for bottom plot
                value = '@{' + company + '}{0.0%}' # change is always %
            tooltip.append((company, value))
        hover_tool = HoverTool(tooltips   = tooltip,
                               show_arrow = True,
                               renderers  = [barplot],
                               mode       = 'vline',
                               )
        fig.add_tools(hover_tool)


    def plot(self, metric_set:str, subtitle:str, filename:str):
        '''Generic time series bokeh plot for values (bars) and their growth (lines)
           plot_type: either of revenue, bs (balance sheet), dupont, wb ("warren buffet"), ...
           '''
        self._build_cds()

        rows      = self._cie_data.index.tolist()
        metrics   = rows[0:int(len(rows)/2)]
        d_metrics = rows[int(len(rows)/2):]

        panels = [] # 2 panels: linear and log plots
        for axis_type in ['linear', 'log']:
            min_y, max_y = self._get_minmax_y(ts_df      = self._cie_data.loc[metrics],
                                              axis_type  = axis_type,
                                              metric_set = metric_set,
                                              plot_position = 'top',
                                              )
            plot_top = self._initialize_plot(position  = 'top',
                                             min_y     = min_y,
                                             max_y     = max_y,
                                             axis_type = axis_type,
                                             source    = self._top_cds,
                                             x_range_name = 'metric',
                                             )
            # Initialize bottom plot (changes / lines)
            min_y, max_y = self._get_minmax_y(ts_df      = self._cie_data.loc[d_metrics],
                                              axis_type  = axis_type,
                                              metric_set = metric_set,
                                              plot_position = 'bottom',
                                              )
            plot_bottom = self._initialize_plot(position  = 'bottom',
                                                min_y     = min_y,
                                                max_y     = max_y,
                                                axis_type = 'linear',
                                                source    = self._bottom_cds,
                                                x_range_name  = 'metric',
                                                linked_figure = plot_top
                                                )
            # Add title to top plot
            self._build_title(fig      = plot_top,
                              subtitle = subtitle,
                              )
            # Add bars to top plot
            self._build_bar_plot(fig        = plot_top,
                                 companies  = self._peer_names,
                                 metrics    = mtr.map_items_to_names(metrics),
                                 metric_set = metric_set,
                                 source     = self._top_cds,
                                 position   = 'top',
                                 )
            # Add growth bars to bottom plot
            self._build_bar_plot(fig        = plot_bottom,
                                 companies  = self._peer_names,
                                 metrics    = mtr.map_items_to_names(metrics),
                                 source     = self._bottom_cds,
                                 metric_set = metric_set,
                                 position   = 'bottom',
                                 )
            # Format axes and legends on top & bottom plots
            for plot in [plot_top, plot_bottom]:
                if plot == plot_top: #top plot
                    position     = 'top'
                    y_axis_label, fmt = self._get_y_axis_format(metric_set = metric_set,
                                                                position   = position,
                                                                axis_type  = axis_type,
                                                                )
                else: #bottom plot
                    position = 'bottom'
                    y_axis_label, fmt = self._get_y_axis_format(metric_set = metric_set,
                                                                position   = position,
                                                                axis_type  ='linear',
                                                                )
                self._build_axes(fig      = plot,
                                 position = position,
                                 y_axis_label = y_axis_label,
                                 axis_format  = fmt,
                                 )
                self._position_legend(fig = plot)
            plot_bottom.legend.visible=False
            # Merge top & bottom plots & captions into a 1-column plot
            caption_text =  self._build_nomenclature_caption(metric_set = metric_set)
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
        self._commit(tabs=tabs, filename=filename)
