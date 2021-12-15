#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 12 14:59:53 2021

fundamentals_plotter.py

@author: charly
"""
import os
import math
import pandas as pd
import numpy as np
from bokeh.layouts import gridplot
from bokeh.transform import dodge
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.models import HoverTool, Title, Span, Label, NumeralTickFormatter
from bokeh.models.widgets import Tabs, Panel, Paragraph
from bokeh.plotting import figure, show, output_file, save
from bokeh.palettes import Dark2_8
from numerize import numerize
import company as cny
import metrics as mtr

# Utilities
def round_up(val:float, ndigits:int):
    '''round up utility'''
    return (math.ceil(val * math.pow(10, ndigits)) + 1) / math.pow(10, ndigits)


def round_down(val:float, ndigits:int):
    '''round down utility'''
    return (math.floor(val * math.pow(10, ndigits)) - 1) / math.pow(10, ndigits)


class FundamentalsPlotter:
    '''Plotter for fundamentals plots'''
    def __init__(self, cie:cny.Company, time_series:pd.DataFrame):
        self._cie = cie
        self._time_series = time_series
        self._cds = None
        self._build_cds()

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
                max_y = max(max_y, round_up(defaults['currentRatio_benchmark'], 1))
            max_y *= 1.05 # leave breathing room above
            if axis_type == 'linear':
                min_y = min(round_down(ts_df.min().min(), 1), 0)
                if plot_type == 'valuation':
                    min_y = 0
            else: # Log plot
                min_y = 1e-3
        else: #Bottom plot
            max_y = min(round_up(ts_df.max().max(), 1), 10)
            min_y = max(round_down(ts_df.min().min(), 1), -1)
        return (min_y, max_y)

    @staticmethod
    def _get_initial_x_offset(metrics):
        '''Returns initial bar offset for bar plot'''
        if len(metrics) == 1:
            return 0.
        if len(metrics) == 2:
            return 0.
        if len(metrics) == 3:
            return -.125
        if len(metrics) == 4:
            return -.375
        if len(metrics) == 5:
            return -.5
        print(f'_get_initial_x_offset: metrics length {len(metrics)} not handled')
        return 0

    @staticmethod
    def _get_bar_shift(metrics):
        '''Returns shift amount bw successive bars'''
        if len(metrics) == 1:
            return .5
        if len(metrics) == 2:
            return .35
        if len(metrics) == 3:
            return .75/3
        if len(metrics) == 4:
            return .8/4
        if len(metrics) == 5:
            return .75/5
        print(f'_get_bar_shift; metrics length {len(metrics)} not handled')
        return 0

    @staticmethod
    def _initialize_plot(position:str, axis_type:str, defaults:dict, source:ColumnDataSource, min_y:float, max_y:float, linked_figure=None):
        '''Initialize plot
           position = top or bottom (plot)
           axis_type = log or linear
           min_y, max_y : y axis bounds
        '''
        if position == 'top':
            plot_height = defaults['plot_height']
            x_range     = source.data['year']
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
        fig.xaxis.major_label_text_font_size = defaults['top_axis_label_text_font_size']
        fig.xaxis.axis_label_text_color      = defaults['axis_label_text_color']
        # Y axis
        fig.yaxis.axis_label_text_font_size  = defaults['top_axis_label_text_font_size']
        if position == 'top':
            fig.yaxis.major_label_text_font_size = defaults['top_axis_label_text_font_size']
        else:
            fig.yaxis.major_label_text_font_size = defaults['bottom_axis_label_text_font_size']
        fig.yaxis.axis_label_text_color      = defaults['axis_label_text_color']
        fig.yaxis.axis_label   = y_axis_label
        fig.yaxis[0].formatter = NumeralTickFormatter(format=axis_format)

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
    def _build_caption_text(plot_type):
        '''Builds caption nomenclature to be added to bottom part of plot'''
        if plot_type in ['dupont', 'wb', 'dividend', 'valuation', 'valuation2', 'debt', 'income2']:
            caption_text = Paragraph(text=mtr.metrics_captions[plot_type], align='center')
        else: # no caption
            caption_text = Paragraph(text='')
        return caption_text

    @staticmethod
    def _position_legend(fig, defaults):
        '''Must be set after legend defined'''
        fig.legend.location     = "top_left"
        fig.legend.click_policy = 'hide'
        fig.legend.orientation  = "vertical"
        fig.legend.label_text_font_size = defaults['legend_font_size']
        fig.add_layout(fig.legend[0], 'right')

# REFACTOR THIS METHOD
    def _map_item_to_name(self, item:str):
        '''Converts column name to readable metric (WIP)'''
        if item.startswith('d_'):
            return '\u0394 ' + self._map_item_to_name(item[2:])
        if item.lower() == 'assetturnover':           return 'Asset turnover'
        if item.lower() == 'croic':                   return 'Cash ROIC'
        if item.lower() == 'currentratio':            return 'Current ratio'
        if item.lower() == 'debttoassets':            return 'Debt-to-assets ratio'
        if item.lower() == 'debttoequity':            return 'Debt-to-equity ratio'
        if item.lower() == 'dividendyield':           return 'Dividend yield'
        if item.lower() == 'ebit':                    return 'EBIT'
        if item.lower() == 'ebitperrevenue':          return 'EBIT-to-revenue'
        if item.lower() == 'evtoebit':                return 'E.V.-to-ebit'
        if item.lower() == 'equitymultiplier':        return 'Equity multiplier'
        if item.lower() == 'grossprofitratio':        return 'Gross profit margin'
        if item.lower() == 'interestcoverage':        return 'Interest coverage'
        if item.lower() == 'freecashflow':            return 'FCF'
        if item.lower() == 'freecashflowtorevenue':   return 'FCF-to-revenue'
        if item.lower() == 'netdebttoebit':           return 'Net debt-to-ebit'
        if item.lower() == 'netprofitmargin':         return 'Net profit margin'
        if item.lower() == 'payoutratio':             return 'Payout ratio'
        if item.lower() == 'peg':                     return 'P/E-to-growth'
        if item.lower() == 'peratio':                 return 'P/E ratio'
        if item.lower() == 'pricetobookratio':        return 'Price-to-book ratio'
        if item.lower() == 'pricetosalesratio':       return 'Price-to-sales ratio'
        if item.lower() == 'returnonequity':          return 'ROE'
        if item.lower() == 'revenue':                 return 'Revenue'
        if item.lower() == 'shorttermcoverageratios': return 'Short term coverage ratio'
        if item.lower() == 'roic':                    return 'ROIC'
        if item.lower() == 'totalassets':             return 'Total assets'
        if item.lower() == 'totalliabilities':        return 'Total liabilities'
        if item.lower() == 'totalstockholdersequity': return 'Total stockholders equity'
        print(f'_map_item_to_name: unknown item {item}')
        return ''


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
        fig.add_layout(Title(text=f'{self._cie.get_company_name()} ({self._cie.get_ticker()})',
                             align='center',
                             text_font_size=defaults['title_font_size'],
                             text_color=defaults['title_color'],
                             text_font=defaults['text_font']),
                       'above',
                       )


    def _build_cds(self):
        '''Builds column data source corresponding to the time series'''
        self._time_series.replace(np.inf, 0, inplace=True) # replace infinity values with 0
        self._time_series.index.name = 'year'
        self._time_series.index      = self._time_series.index.astype('string')
        self._cds                   = ColumnDataSource(data = self._time_series)


    def _get_y_axis_format(self, plot_type:str, position:str, axis_type:str):
        '''Builds format for y axis'''
        if position == 'top':
            if plot_type in ['wb', 'dupont', 'valuation', 'valuation2', 'dividend', 'debt', 'income2']:
                y_axis_label = 'ratio'
            else:
                y_axis_label = f'{self._cie.get_currency().capitalize()}'
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


    def _build_bar_plots(self, fig, defaults:dict, years:list, metrics:list, plot_type:str, means:dict, source:ColumnDataSource):
        '''Builds bar plots (metrics) on primary axis'''
        x_pos = self._get_initial_x_offset(metrics)
        bar_shift = self._get_bar_shift(metrics)
        bar_width = defaults['bar_width_shift_ratio'] * bar_shift
        for i, metric in enumerate(metrics):
            vbar = fig.vbar(x      = dodge('year', x_pos, FactorRange(*years)),
                            bottom = 1e-6,
                            top    = metric,
                            width  = bar_width,
                            source = source,
                            color  = defaults['palette'][i],
                            legend_label = self._map_item_to_name(metric),
                            )
            self._build_bar_tooltip(fig=fig, barplot=vbar, means=means, metrics=metrics, plot_type=plot_type, defaults=defaults)
            x_pos += bar_shift


    def _build_line_plots(self, fig, defaults:dict, metrics:list, source:ColumnDataSource):
        '''Builds line plots (metrics change) on secondary axis'''
        for i, metric in enumerate(metrics):
            legend_label = self._map_item_to_name(metric)
            line = fig.line(x = 'year',
                            y = metric,
                            line_width = 1,
                            line_dash = defaults['line_dash'],
                            color = defaults['palette'][i],
                            legend_label = legend_label,
                            source = source,
                            )
            fig.circle(x='year',
                       y=metric,
                       color=defaults['palette'][i],
                       fill_color='white',
                       size=5,
                       legend_label=legend_label,
                       source = source,
                       )
            self._build_line_tooltips(fig, line, metrics)
        self._build_zero_growth_line(fig, defaults)


    def _build_line_tooltips(self, fig, line, metrics:list):
        '''Build tooltips for line plots'''
        tooltips = [('Growth','@year')]
        for metric in metrics:
            tooltips.append( (self._map_item_to_name(metric),
                              f'@{metric}'+"{0.0%}")
                            )
            hover_tool = HoverTool(tooltips   = tooltips,
                                   show_arrow = True,
                                   renderers  = [line],
                                   #mode       = 'vline',
                                   )
            fig.add_tools(hover_tool)


    def _build_means_lines(self, fig, defaults:dict, means:dict, plot_type:str):
        '''Plots means lines for each metric'''
        for idx, (metric, mean) in enumerate(means.items()):
            mean_line = Span(location   = mean,
                              dimension  ='width',
                              line_color = defaults['palette'][idx],
                              line_dash  = defaults['means_line_dash'],
                              line_width = defaults['means_line_thickness'],
                              )
            fig.add_layout(mean_line)
            #Add annotation
            text  = 'mean ' + self._map_item_to_name(metric).lower() + ': '
            if plot_type in ['bs', 'income']:
                text += f'{self._cie.get_currency_symbol()}'
            if plot_type in ['debt', 'dividend', 'income2']:
                text += f'{mean:.1%}'
            else:
                text += f'{numerize.numerize(mean)}'
            fig.add_layout(self._build_line_caption(text      = text,
                                                    x_value   = 2,
                                                    y_value   = mean,
                                                    x_units   = 'screen',
                                                    y_units   = 'data',
                                                    color     = 'dimgray',#defaults['palette'][idx],
                                                    font_size = defaults['means_font_size'],
                                                    )
                           )


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


    def _build_bar_tooltip(self, fig, barplot, means:dict, metrics:list, plot_type:str, defaults:dict):
        '''Build tooltips for bar plots'''
        tooltip = [('','@year')]
        for metric in metrics:
            prefix = ''
            if plot_type in ['wb', 'dupont', 'valuation', 'valuation2']:
                text  = f' (mean = {means[metric]:.1f})'
                if plot_type == 'wb':
                    bmark = defaults[f'{metric}_benchmark']
                    text  = f' (mean = {means[metric]:.1f} | benchmark = {bmark})'
                value = prefix + f'@{metric}' + "{0.0a}" + text
            elif plot_type in ['dividend', 'debt', 'income2']:
                text = f' (mean = {means[metric]:.1%})'
                value = prefix + f'@{metric}' + "{0.0%}" + text
            else:
                prefix = f'{self._cie.get_currency_symbol()}'
                text = f' (mean = {prefix}{numerize.numerize(means[metric], 1)})'
                value = prefix + f'@{metric}' + "{0.0a}" + text
            tooltip.append((self._map_item_to_name(metric), value))
        hover_tool = HoverTool(tooltips   = tooltip,
                               show_arrow = True,
                               renderers  = [barplot],
                               mode       = 'vline',
                               )
        fig.add_tools(hover_tool)


    def _build_wb_benchmarks(self, fig, defaults:dict):
        '''
        Plots horizontal lines corresponding to Buffet benchmarks for the
        3 ratios: roe, current ratio & debt to equity
        '''
        # Build line
        benchmarks = ['returnOnEquity_benchmark', 'debtToEquity_benchmark','currentRatio_benchmark']
        for idx, benchmark in enumerate(benchmarks):
            bmk = Span(location   = defaults[benchmark],
                       dimension  ='width',
                       line_color = defaults['palette'][idx],
                       line_dash  = defaults['benchmark_line_dash'],
                       line_width = defaults['benchmark_line_thickness'],
                       )
            fig.add_layout(bmk)
            #Add annotation
            text = benchmark.replace('_', ' ')
            text += f': {defaults[benchmark]}'
            fig.add_layout(self._build_line_caption(text      = text,
                                                    x_value   = 2,
                                                    y_value   = defaults[benchmark],
                                                    x_units   = 'screen',
                                                    y_units   = 'data',
                                                    color     = 'dimgray',#defaults['palette'][idx],
                                                    font_size = defaults['benchmark_font_size'],
                                                    )
                               )


    def _build_valuation_benchmarks(self, fig, defaults:dict):
        '''
        Plots horizontal lines corresponding to valuation benchmarks for the
        price-to-book ratio
        '''
        # Build line
        benchmarks = ['priceToBookRatio_benchmark', 'pegRatio_benchmark']
        for idx, benchmark in enumerate(benchmarks):
            bmk = Span(location   = defaults[benchmark],
                       dimension  ='width',
                       line_color = defaults['palette'][idx],
                       line_dash  = defaults['benchmark_line_dash'],
                       line_width = defaults['benchmark_line_thickness'],
                       )
            fig.add_layout(bmk)
            #Add annotation
            text = benchmark.replace('_', ' ')
            text += f': {defaults[benchmark]}'
            fig.add_layout(self._build_line_caption(text      = text,
                                                    x_value   = 2,
                                                    y_value   = defaults[benchmark],
                                                    x_units   = 'screen',
                                                    y_units   = 'data',
                                                    color     = 'dimgray',#defaults['palette'][idx],
                                                    font_size = defaults['benchmark_font_size'],
                                                    )
                               )


    def plot(self, plot_type:str, subtitle:str, filename:str):
        '''
        Generic time series bokeh plot for values (bars) and their growth (lines)
        plot_type: either of revenue, bs (balance sheet), dupont, wb ("warren buffet"), ...
        '''
        defaults = self.get_plot_defaults()

        cols = self._time_series.columns.tolist()
        metrics   = cols[0:int(len(cols)/2)]
        d_metrics = cols[int(len(cols)/2):]

        # Build a dictionary of metrics and their respective means
        means = dict(zip(metrics, self._time_series[metrics].mean().tolist()))

        panels = [] # 2 panels: linear and log plots
        for axis_type in ['linear', 'log']:
            min_y, max_y = self._get_minmax_y(ts_df     = self._time_series[metrics],
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
                                             source    = self._cds,
                                             )
            # Initialize bottom plot (changes / lines)
            min_y, max_y = self._get_minmax_y(ts_df     = self._time_series[d_metrics],
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
                                                source    = self._cds,
                                                linked_figure = plot_top
                                                )
            # Add title to top plot
            self._build_title(fig      = plot_top,
                              defaults = defaults,
                              subtitle = subtitle,
                              )
            # Add bars to top plot
            self._build_bar_plots(fig       = plot_top, # top blot is bar plot
                                  defaults  = defaults,
                                  years     = self._time_series.index.tolist(),
                                  metrics   = metrics,
                                  plot_type = plot_type,
                                  means     = means,
                                  source    = self._cds,
                                  )
            self._build_means_lines(fig       = plot_top,
                                    defaults  = defaults,
                                    means     = means,
                                    plot_type = plot_type,
                                    )
            if plot_type == 'wb': # Add benchmarks to WB plot
                self._build_wb_benchmarks(fig      = plot_top,
                                          defaults = defaults,
                                          )
            elif plot_type == 'valuation': # Add benchmarks to valuation plot
                self._build_valuation_benchmarks(fig      = plot_top,
                                                 defaults = defaults,
                                                 )
            # Add growth lines to bottom plot
            self._build_line_plots(fig       = plot_bottom, # bottom plot is line plot
                                   defaults  = defaults,
                                   metrics   = d_metrics,
                                   source    = self._cds,
                                   )
            # Format axes and legends on top & bottom plots
            for plot in [plot_top, plot_bottom]:
                if plot == plot_top: #top plot
                    position     = 'top'
                    y_axis_label, fmt = self._get_y_axis_format(plot_type=plot_type,
                                                                position=position,
                                                                axis_type=axis_type,
                                                                )
                else: #bottom plot
                    position = 'bottom'
                    y_axis_label, fmt = self._get_y_axis_format(plot_type=plot_type,
                                                                position=position,
                                                                axis_type='linear',
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
            plot         = gridplot(children = [plot_top,
                                                plot_bottom,
                                                caption_text,
                                                ],
                                    ncols    = 1,
                                    sizing_mode = 'stretch_width',
                                    )
            panel        = Panel(child=plot,
                                 title=axis_type,
                                 )
            panels.append(panel)
        tabs = Tabs(tabs=panels)
        show(tabs)
        # Save plot to file
        try:
            output_file(filename)
        except FileNotFoundError:
            print(f'creating data directory {os.path.dirname(filename)}')
            os.mkdir(os.path.dirname(filename))
            output_file(filename)
        save(tabs)
