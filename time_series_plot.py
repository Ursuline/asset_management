#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 27 14:17:10 2021
time_series_plot.py

Bokeh time series plot

@author: charly
"""
from datetime import timedelta
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Title
from bokeh.models import HoverTool, ResetTool, CrosshairTool
from bokeh.models import WheelZoomTool, ZoomInTool, ZoomOutTool
from bokeh.layouts import gridplot
from bokeh.io import show, curdoc
import trading_defaults as dft

class TimeSeriesPlot():
    '''Bokeh time series plot'''
    W_PLOT   = 950
    H_PLOT_P = 600
    H_PLOT_V = 150
    curdoc().theme = 'dark_minimal'

    @classmethod
    def get_default_display_flags(cls):
        '''Returns default flags for display'''
        flags = {}
        flags['close']      = True
        flags['ema']        = True
        flags['ema_buffer'] = False
        flags['sma']        = False
        flags['sma_buffer'] = False
        flags['volume']     = True
        flags['arrows']     = True
        flags['statistics'] = False
        flags['save']       = True
        return flags

    def __init__(self, ticker_object, topomap, strat_pos, disp_dates, span, buffer, disp_flags):
        self._ticker_obj    = ticker_object
        self._topomap       = topomap
        self._strat_pos     = strat_pos
        self._display_dates = disp_dates
        self._span          = span
        self._buffer        = buffer
        self._fee           = None
        self._hold          = None
        self._ema           = None
        self._display_flags = disp_flags
        self.update()


    def update(self, disp_flags = None, disp_dates=None, span=None, buffer=None, fee=None):
        '''Global (re)-setter'''
        window_start = self._display_dates[0] - timedelta(days = self._span + 1)
        window_end   = self._display_dates[1]
        close        = self._ticker_obj.get_close()
        dfr          = self._topomap.build_strategy(close.loc[window_start:window_end, :].copy(),
                                                    self._span,
                                                    self._buffer,
                                                    )
        if disp_flags is not None:
            self._display_flags = disp_flags

        if disp_dates is not None:
            self._display_dates = disp_dates

        if span is not None:
            self._span = span

        if buffer is not None:
            self._buffer = buffer

        if fee is None:
            self._fee  = self._topomap.get_fee(dfr, dft.get_actions())
        else:
            self._fee = fee
        self._hold = self._topomap.get_cumret(dfr, 'hold')  # cumulative returns for hold
        self._ema  = self._topomap.get_cumret(dfr, 'ema', self._fee)  # cumulative returns for EMA


    def build_plot(self, source: ColumnDataSource):
        '''Plotting call'''
        plot_price = self._plot_price_window(source=source)
        plot_vol = self._plot_volume_window(source=source)
        show(gridplot([plot_price, plot_vol], ncols=1))


    def _build_title(self):
        ''' Build plot title '''
        dates         = self._display_dates
        ticker_name   = self._ticker_obj.get_name()
        ticker_symbol = self._ticker_obj.get_symbol()

        title  = f'{ticker_name} ({ticker_symbol}) | {self._strat_pos.capitalize()} position | '
        title += f'{dates[0].strftime("%d %b %Y")} - {dates[1].strftime("%d %b %Y")}'
        #title += f' | {buy_sell[0]} buys {buy_sell[1]} sells'

        return title


    def _build_subtitle(self):
        ''' Build plot subtitle '''
        title  = f'EMA max payoff={self._ema:.2%} (hold={self._hold:.2%}) | '
        title += f'{self._span:.0f}-day mean | '
        title += f'opt buffer={self._buffer:.2%}'

        return title

    @staticmethod
    def _add_tools(plot):
        '''Add tools tips'''
        tooltips=[("date", "$x{%d %b %Y}"),
                  ("close", "@Close{$0,0.00}"),
                  ("return", "@RET{%0,0.00}"),
                  ("volume", "@Volume{(0.00 a)}")
                  ]
        formatters = {'$x': 'datetime'}
        plot.add_tools(HoverTool(tooltips   = tooltips,
                                 formatters = formatters,
                                 # display a tooltip whenever the cursor is vertically in line with a glyph
                                 mode = 'vline',
                                 ),
                      )

        plot.add_tools(ResetTool())
        plot.add_tools(WheelZoomTool())
        plot.add_tools(ZoomInTool())
        plot.add_tools(ZoomOutTool())
        plot.add_tools(CrosshairTool(dimensions="both", line_color=dft.X_HAIR_COLOR))

        return plot


    def _plot_volume_window(self, source):
        plot = figure(x_axis_type      = "datetime",
                      plot_width       = self.W_PLOT,
                      plot_height      = self.H_PLOT_V,
                      y_axis_label     ='Volume',
                      toolbar_location = 'right',
                      toolbar_sticky   = False,
                      output_backend   = "webgl",
                     )
        plot.line(source=source,
                  x='Date',
                  y='Volume',
                  legend_label="Volume",
                  line_width=1,
                  line_color=dft.COLOR_SCHEME[2]
                 )
        return plot


    def _plot_price_window(self, source):
        '''Plots stock price ema etc
        source is a ColumnDataSource object
        '''

        title    = self._build_title()
        subtitle = self._build_subtitle()

        plot = figure(x_axis_type      = "datetime",
                      plot_width       = self.W_PLOT,
                      plot_height      = self.H_PLOT_P,
                      y_axis_label     ='Price',
                      toolbar_location = 'right',
                      toolbar_sticky   = False,
                      output_backend   = "webgl",
                     )
        plot.add_layout(Title(text=subtitle, text_font_style="italic"), 'above')
        plot.add_layout(Title(text=title, text_font_size="16pt"), 'above')

        # configure so that Bokeh chooses what (if any) scroll tool is active
        plot.toolbar.active_scroll = "auto"
        plot.toolbar.autohide = True

        plot.line(source=source,
                  x='Date',
                  y='Close',
                  legend_label="Close",
                  line_width=1,
                  line_color=dft.COLOR_SCHEME[1]
                 )
        plot = self._add_tools(plot)

        plot.legend.location = "top_left"
        plot.legend.border_line_alpha = .5
        plot.legend.background_fill_alpha = .5
        plot.legend.click_policy = "mute"

        return plot
