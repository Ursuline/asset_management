#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 12 14:59:53 2021

fundamentals_plotter.py

@author: charly
"""
import pandas as pd
import numpy as np
from bokeh.layouts import gridplot
from bokeh.transform import dodge
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.models import HoverTool, Title, Span
from bokeh.models.widgets import Tabs, Panel
from numerize import numerize
import plotter as pltr
import company as cny
import metrics as mtr


class FundamentalsPlotter(pltr.Plotter):
    '''Plotter for fundamentals plots'''
    def __init__(self, cie:cny.Company, cie_data:pd.DataFrame):
        super().__init__(base_cie=cie, cie_data=cie_data)
        self._cds = None


    def _build_cds(self):
        '''Builds column data source corresponding to the time series'''
        self._cie_data.replace(np.inf, 0, inplace=True) # replace infinity values with 0
        self._cie_data.index.name = 'year'
        self._cie_data.index      = self._cie_data.index.astype('string')
        self._cds                   = ColumnDataSource(data = self._cie_data)


    def _build_title(self, fig, subtitle:str):
        '''Build plot title and subtitle'''
        #subtitle
        fig.add_layout(Title(text=subtitle,
                             align='center',
                             text_font_size = self._defaults['subtitle_font_size'],
                             text_color     = self._defaults['title_color'],
                             text_font      = self._defaults['text_font']),
                       'above',
                       )
        #title
        fig.add_layout(Title(text=f'{self._base_cie.get_company_name()} ({self._base_cie.get_ticker()})',
                             align='center',
                             text_font_size = self._defaults['title_font_size'],
                             text_color     = self._defaults['title_color'],
                             text_font      = self._defaults['text_font']),
                       'above',
                       )


    def _get_y_axis_format(self, metric_set:str, position:str, axis_type:str):
        '''Builds format for y axis'''
        if position == 'top':
            if metric_set in ['bs_metrics', 'income_metrics']:
                y_axis_label = f'{self._base_cie.get_currency().capitalize()}'
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


    def _build_bar_plots(self, fig, years:list, metrics:list, metric_set:str, means:dict, source:ColumnDataSource):
        '''Builds bar plots (metrics) on primary axis'''
        x_pos = self._get_initial_x_offset(metrics)
        bar_shift = self._get_bar_shift(metrics)
        bar_width = self._defaults['bar_width_shift_ratio'] * bar_shift
        for i, metric in enumerate(metrics):
            vbar = fig.vbar(x      = dodge('year', x_pos, FactorRange(*years)),
                            bottom = 1e-6,
                            top    = metric,
                            width  = bar_width,
                            source = source,
                            color  = self._defaults['palette'][i],
                            legend_label = mtr.map_metric_to_name(metric),
                            )
            self._build_bar_tooltip(fig=fig, barplot=vbar, means=means, metrics=metrics, metric_set=metric_set)
            x_pos += bar_shift


    def _build_line_plots(self, fig, metrics:list, source:ColumnDataSource):
        '''Builds line plots (metrics change) on secondary axis'''
        for i, metric in enumerate(metrics):
            legend_label = mtr.map_metric_to_name(metric)
            line = fig.line(x = 'year',
                            y = metric,
                            line_width = 1,
                            line_dash = self._defaults['line_dash'],
                            color = self._defaults['palette'][i],
                            legend_label = legend_label,
                            source = source,
                            )
            fig.circle(x='year',
                       y=metric,
                       color=self._defaults['palette'][i],
                       fill_color='white',
                       size=5,
                       legend_label=legend_label,
                       source = source,
                       )
            self._build_line_tooltips(fig, line, metrics)
        self._build_zero_growth_line(fig)


    def _build_line_tooltips(self, fig, line, metrics:list):
        '''Build tooltips for line plots'''
        tooltips = [('Growth','@year')]
        for metric in metrics:
            tooltips.append( (mtr.map_metric_to_name(metric),
                              f'@{metric}'+"{0.0%}")
                            )
            hover_tool = HoverTool(tooltips   = tooltips,
                                   show_arrow = True,
                                   renderers  = [line],
                                   mode       = 'mouse',
                                   )
            fig.add_tools(hover_tool)


    def _build_means_lines(self, fig, means:dict, metric_set:str):
        '''Plots means lines for each metric'''
        for idx, (metric, mean) in enumerate(means.items()):
            mean_line = Span(location    = mean,
                              dimension  ='width',
                              line_color = self._defaults['palette'][idx],
                              line_dash  = self._defaults['means_line_dash'],
                              line_width = self._defaults['means_line_thickness'],
                              )
            fig.add_layout(mean_line)
            #Add annotation
            text  = 'mean ' + mtr.map_metric_to_name(metric).lower() + ': '
            if metric_set in ['bs_metrics', 'income_metrics']:
                text += f'{self._base_cie.get_currency_symbol()}'
            if metric_set in ['debt_metrics', 'dividend_metrics', 'income2_metrics']:
                text += f'{mean:.1%}'
            else:
                text += f'{numerize.numerize(mean)}'
            fig.add_layout(self._build_line_caption(text      = text,
                                                    x_value   = 2,
                                                    y_value   = mean,
                                                    x_units   = 'screen',
                                                    y_units   = 'data',
                                                    color     = self._defaults['means_font_color'],
                                                    font_size = self._defaults['means_font_size'],
                                                    )
                           )


    def _build_bar_tooltip(self, fig, barplot, means:dict, metrics:list, metric_set:str):
        '''Build tooltips for bar plots'''
        fmt = mtr.get_tooltip_format(metric_set) # tooltip format
        tooltip = [('','@year')]
        for metric in metrics:
            prefix = ''
            if metric_set in ['wb_metrics', 'dupont_metrics', 'valuation_metrics', 'valuation2_metrics']:
                text  = f' (mean = {means[metric]:.1f})'
                if metric_set == 'wb_metrics':
                    bmark = self._defaults[f'{metric}_benchmark']
                    text  = f' (mean = {means[metric]:.1f} | benchmark = {bmark})'
                value = prefix + f'@{metric}' + f'{fmt}' + text
            elif metric_set in ['dividend_metrics', 'debt_metrics', 'income2_metrics']:
                text = f' (mean = {means[metric]:.1%})'
                value = prefix + f'@{metric}' + f'{fmt}' + text
            else:
                prefix = f'{self._base_cie.get_currency_symbol()}'
                text = f' (mean = {prefix}{numerize.numerize(means[metric], 1)})'
                value = prefix + f'@{metric}' + f'{fmt}' + text
            tooltip.append((mtr.map_metric_to_name(metric), value))
        hover_tool = HoverTool(tooltips   = tooltip,
                               show_arrow = True,
                               renderers  = [barplot],
                               mode       = 'vline',
                               )
        fig.add_tools(hover_tool)


    def _build_wb_benchmarks(self, fig):
        '''
        Plots horizontal lines corresponding to Buffet benchmarks for the
        3 ratios: roe, current ratio & debt to equity
        '''
        # Build line
        benchmarks = ['returnOnEquity_benchmark', 'debtToEquity_benchmark','currentRatio_benchmark']
        for idx, benchmark in enumerate(benchmarks):
            bmk = Span(location   = self._defaults[benchmark],
                       dimension  ='width',
                       line_color = self._defaults['palette'][idx],
                       line_dash  = self._defaults['benchmark_line_dash'],
                       line_width = self._defaults['benchmark_line_thickness'],
                       )
            fig.add_layout(bmk)
            #Add annotation
            text = benchmark.replace('_', ' ')
            text += f': {self._defaults[benchmark]}'
            fig.add_layout(self._build_line_caption(text      = text,
                                                    x_value   = 2,
                                                    y_value   = self._defaults[benchmark],
                                                    x_units   = 'screen',
                                                    y_units   = 'data',
                                                    color     = self._defaults['benchmark_font_color'],
                                                    font_size = self._defaults['benchmark_font_size'],
                                                    )
                               )


    def _build_valuation_benchmarks(self, fig):
        '''
        Plots horizontal lines corresponding to valuation benchmarks for the
        price-to-book ratio
        '''
        # Build line
        benchmarks = ['priceToBookRatio_benchmark', 'pegRatio_benchmark']
        for idx, benchmark in enumerate(benchmarks):
            bmk = Span(location   = self._defaults[benchmark],
                       dimension  ='width',
                       line_color = self._defaults['palette'][idx],
                       line_dash  = self._defaults['benchmark_line_dash'],
                       line_width = self._defaults['benchmark_line_thickness'],
                       )
            fig.add_layout(bmk)
            #Add annotation
            text = benchmark.replace('_', ' ')
            text += f': {self._defaults[benchmark]}'
            fig.add_layout(self._build_line_caption(text      = text,
                                                    x_value   = 2,
                                                    y_value   = self._defaults[benchmark],
                                                    x_units   = 'screen',
                                                    y_units   = 'data',
                                                    color     = self._defaults['benchmark_font_color'],
                                                    font_size = self._defaults['benchmark_font_size'],
                                                    )
                               )


    def plot(self, metric_set:str, subtitle:str, filename:str):
        '''
        Generic time series bokeh plot for values (bars) and their growth (lines)
        '''
        cols     = self._cie_data.columns.tolist()
        metrics   = cols[0:int(len(cols)/2)]
        d_metrics = cols[int(len(cols)/2):]
        self._build_cds()

        # Build a dictionary of metrics and their respective means
        means = dict(zip(metrics, self._cie_data[metrics].mean().tolist()))

        panels = [] # 2 panels: linear and log plots
        for axis_type in ['linear', 'log']:
            # Initialize top plot (metrics / bars)
            min_y, max_y = self._get_minmax_y(ts_df     = self._cie_data[metrics],
                                              axis_type = axis_type,
                                              metric_set = metric_set,
                                              plot_position = 'top',
                                              )
            plot_top = self._initialize_plot(position  = 'top',
                                             min_y     = min_y,
                                             max_y     = max_y,
                                             axis_type = axis_type,
                                             source    = self._cds,
                                             x_range_name = 'year',
                                             )
            # Initialize bottom plot (changes / lines)
            min_y, max_y = self._get_minmax_y(ts_df      = self._cie_data[d_metrics],
                                              axis_type  = axis_type,
                                              metric_set = metric_set,
                                              plot_position = 'bottom',
                                              )
            plot_bottom = self._initialize_plot(position  = 'bottom',
                                                max_y     = max_y,
                                                min_y     = min_y,
                                                axis_type = 'linear',
                                                source    = self._cds,
                                                x_range_name = 'year',
                                                linked_figure = plot_top,
                                                )
            # Add title to top plot
            self._build_title(fig      = plot_top,
                              subtitle = subtitle,
                              )
            # Add bars to top plot
            self._build_bar_plots(fig        = plot_top, # top blot is bar plot
                                  years      = self._cie_data.index.tolist(),
                                  metrics    = metrics,
                                  metric_set = metric_set,
                                  means      = means,
                                  source     = self._cds,
                                  )
            self._build_means_lines(fig        = plot_top,
                                    means      = means,
                                    metric_set = metric_set,
                                    )
            if metric_set == 'wb_metrics': # Add benchmarks to WB plot
                self._build_wb_benchmarks(fig = plot_top)
            elif metric_set == 'valuation_metrics': # Add benchmarks to valuation plot
                self._build_valuation_benchmarks(fig = plot_top)
            # Add growth lines to bottom plot
            self._build_line_plots(fig       = plot_bottom, # bottom plot is line plot
                                   metrics   = d_metrics,
                                   source    = self._cds,
                                   )
            # Format axes and legends on top & bottom plots
            for plot in [plot_top, plot_bottom]:
                if plot == plot_top: #top plot
                    position     = 'top'
                    y_axis_label, fmt = self._get_y_axis_format(metric_set = metric_set,
                                                                position  = position,
                                                                axis_type = axis_type,
                                                                )
                else: #bottom plot
                    position = 'bottom'
                    y_axis_label, fmt = self._get_y_axis_format(metric_set = metric_set,
                                                                position  = position,
                                                                axis_type ='linear',
                                                                )
                self._build_axes(fig      = plot,
                                 position = position,
                                 y_axis_label = y_axis_label,
                                 axis_format  = fmt,
                                 )
                self._position_legend(fig = plot)
            # Merge top & bottom plots & captions into column
            caption_text =  self._build_nomenclature_caption(metric_set)
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
