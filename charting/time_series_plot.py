#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 27 14:17:10 2021
time_series_plot.py

Bokeh time series plot

@author: charly
"""
import os
from datetime import timedelta
import pandas as pd
from bokeh.plotting import figure, output_file, save
from bokeh.models import ColumnDataSource, Title, BooleanFilter, CDSView, Scatter
from bokeh.models import HoverTool, ResetTool, CrosshairTool
from bokeh.models import WheelZoomTool, ZoomInTool, ZoomOutTool, WheelPanTool
from bokeh.models import NumeralTickFormatter
from bokeh.io import output_notebook, export_png
from bokeh.layouts import gridplot
from bokeh.io import show, curdoc

from charting import trading_defaults as dft
from finance import utilities as util


class TimeSeriesPlot():
    '''Bokeh time series plot'''
    curdoc().theme = dft.BK_THEMES[0]

    @classmethod
    def get_default_display_flags(cls):
        '''Returns default flags for display'''
        flags = {}
        flags['close']      = True
        flags['ema']        = True
        flags['ema_buffer'] = True
        flags['sma']        = True
        flags['sma_buffer'] = False
        flags['arrows']     = True
        flags['statistics'] = False
        return flags

    def __init__(self, ticker_object, topomap, strat_pos, disp_dates, span, buffer, disp_flags):
        self._ticker_obj    = ticker_object
        self._topomap       = topomap
        self._strat_pos     = strat_pos
        self._display_dates = disp_dates
        self._trading_days  = None
        self._span          = span
        self._buffer        = buffer
        self._fee           = None
        self._hold          = None
        self._ema           = None
        self._strategy      = None
        self._plot          = None
        self._buy_sell      = None
        self._pathname      = None
        self._display_flags = disp_flags
        self.update()


    def update(self, disp_flags = None, disp_dates=None, span=None, buffer=None, fee=None):
        '''Global (re)-setter'''
        window_start   = self._display_dates[0] - timedelta(days = self._span + 1)
        window_end     = self._display_dates[1]
        volume         = self._ticker_obj.get_volume()
        close          = self._ticker_obj.get_close()
        self._strategy = self._topomap.build_strategy(close.loc[window_start:window_end, :].copy(),
                                                      self._span,
                                                      self._buffer,
                                                      )
        self._strategy.RET = self._strategy.RET - 1
        # Merge with Volume
        self._strategy = pd.DataFrame(pd.merge(self._strategy, volume, left_index=True, right_index=True))

        self._trading_days = volume.shape[0]

        if disp_flags is not None:
            self._display_flags = disp_flags

        if disp_dates is not None:
            self._display_dates = disp_dates

        if span is not None:
            self._span = span

        if buffer is not None:
            self._buffer = buffer

        if fee is None:
            self._fee  = self._topomap.get_fee(self._strategy, dft.get_actions())
        else:
            self._fee = fee

        self._hold = self._topomap.get_cumret(self._strategy, 'hold')  # cumulative returns for hold
        self._ema  = self._topomap.get_cumret(self._strategy, 'ema', self._fee)  # cumulative returns for EMA


    def build_plot(self, dataframe:pd.DataFrame, notebook:bool, display:bool, remote:bool):
        '''Plotting call'''
        source     = ColumnDataSource(dataframe)
        upper_pane = self._build_upper_pane(source = source)
        lower_pane = self._build_lower_pane(source = source,
                                              upper_pane = upper_pane,
                                              )

        # Link the CrossHairTools together
        crosshair = CrosshairTool(dimensions = "both",
                                  line_color = dft.get_x_hair_color(curdoc().theme),
                                  line_width = 1,
                                  line_alpha = .5,
                                  )
        upper_pane.add_tools(crosshair)
        lower_pane.add_tools(crosshair)

        self._plot = gridplot(children = [upper_pane, lower_pane],
                              ncols    = 1,
                              )
        self._show(notebook, display, remote)


    def _build_pathname(self, extension):
        '''Build html file path name'''
        directory = self._get_directory()
        filename  = f'{self._ticker_obj.get_symbol()}_'
        filename += f'{self._display_dates[0].date()}-{self._display_dates[1].date()}_'
        filename += f'{self._strat_pos}_tmseries.'
        filename += f'{extension}'
        self._pathname = os.path.join(directory, filename)


    def get_pathname(self):
        '''Getter for html file path name'''
        return self._pathname


    def _get_directory(self):
        '''Getter for html file directory'''
        symbol = self._ticker_obj.get_symbol()
        directory = os.path.join(dft.PLOT_DIR, symbol)
        return directory


    def get_strategy(self):
        '''Getter for strategy'''
        return self._strategy


    def _build_title(self, plot):
        ''' Build plot title '''
        dates         = self._display_dates
        ticker_name   = self._ticker_obj.get_name()
        ticker_symbol = self._ticker_obj.get_symbol()

        title  = f'{ticker_name} ({ticker_symbol}) | '
        title += f'{dates[0].strftime("%d %b %Y")} - {dates[1].strftime("%d %b %Y")}'
        if self._buy_sell is not None:
            title += f' | {self._buy_sell[0]} buys {self._buy_sell[1]} sells '

        plot.add_layout(Title(text=title,
                              text_font_style="bold",
                              text_font_size="16pt",
                              align="center"),
                        'above')

        return plot


    def _build_subtitle(self, plot):
        ''' Build plot subtitle '''
        title  = f'{self._strat_pos.capitalize()} position | '
        title += f'EMA max payoff={self._ema:.1%} (hold={self._hold:.1%}) | '
        title += f'{self._span:.0f}-day mean | '
        title += f'opt buffer={self._buffer:.2%}'
        if self._buy_sell is not None:
            denom = self._buy_sell[0] + self._buy_sell[1]
            if denom > 0:
                turnover = self._trading_days / denom
                title += f' | tx turnover: {turnover:.0f} days'

        plot.add_layout(Title(text=title,
                              text_font_style="normal",
                              align="center"),
                        'above')
        return plot


    def _build_lower_pane(self, source, upper_pane):
        pane = figure(x_axis_type      = "datetime",
                      plot_width       = dft.PLOT_WIDTH,
                      plot_height      = dft.PLOT_HDIM_BOT,
                      y_axis_label     ='Volume',
                      x_range          = upper_pane.x_range,
                      output_backend   = "webgl",
                     )

        booleans = [True if ret >= 0 else False for ret in source.data['RET']]
        view = CDSView(source=source, filters=[BooleanFilter(booleans)])
        pane.vbar(x='Date',
                  top='Volume',
                  source=source,
                  view = view,
                  legend_label="Volume+",
                  fill_color = 'lime',
                  line_color = 'lime')

        booleans = [True if ret < 0 else False for ret in source.data['RET']]
        view = CDSView(source=source, filters=[BooleanFilter(booleans)])
        pane.vbar(x='Date',
                  top='Volume',
                  source=source,
                  view = view,
                  legend_label="Volume-",
                  fill_color = 'tomato',
                  line_color = 'tomato')

        pane = self._customize_legend(pane,'')
        # format axes ticks
        pane.yaxis[0].formatter = NumeralTickFormatter(format="0a")

        pane.ygrid.band_fill_color="grey"
        pane.ygrid.band_fill_alpha = 0.1
        pane = self._add_tools(pane, 'bottom')
        return pane


    def _build_upper_pane(self, source):
        '''Plots stock price ema etc
        source is a ColumnDataSource object
        '''
        y_label = f'Price ({self._ticker_obj.get_currency_symbol()})'
        pane = figure(x_axis_type      = "datetime",
                      plot_width       = dft.PLOT_WIDTH,
                      plot_height      = dft.PLOT_HDIM_TOP,
                      y_axis_label     = y_label,
                      toolbar_location = 'right',
                      toolbar_sticky   = False,
                      output_backend   = "webgl",
                     )

        # configure so that Bokeh chooses what (if any) scroll tool is active
        pane.toolbar.active_scroll = "auto"
        pane.toolbar.autohide = True

        pane.ygrid.band_fill_color="grey"
        pane.ygrid.band_fill_alpha = 0.1

        source=ColumnDataSource(self._strategy)

        if self._display_flags['close']:
            pane = self._display_value(pane, source, 'close')
            pane = self._customize_legend(pane)

        if self._display_flags['ema']:
            pane = self._display_value(pane, source, 'ema')

        if self._display_flags['ema_buffer']:
            pane = self._display_value(pane, source, 'ema_buffer')

        if self._display_flags['sma']:
            pane = self._display_value(pane, source, 'sma')

        if self._display_flags['sma_buffer']:
            pane = self._display_value(pane, source, 'sma_buffer')
        #text = self._build_statistics_box()

        if self._display_flags['arrows']:
            pane = self._display_arrows(pane, source)

        # Build title & subtitle
        pane = self._build_subtitle(pane)
        pane = self._build_title(pane)

        pane = self._add_tools(pane, 'top')

        return pane


    def _display_arrows(self, plot, source):
        '''Adds buy/sell arrows to plot'''
        actions  = dft.get_actions()
        # Plot buys
        booleans = [True if act == 'buy' else False for act in self._strategy['ACTION']]
        view = CDSView(source=source, filters=[BooleanFilter(booleans)])
        glyph = Scatter(x="Date", y="Close", size=10, fill_color="lime", marker="inverted_triangle")
        plot.add_glyph(source, glyph, view=view)

        # Plot sells
        booleans = [True if act == 'sell' else False for act in self._strategy['ACTION']]
        view = CDSView(source=source, filters=[BooleanFilter(booleans)])
        glyph = Scatter(x="Date", y="Close", size=10, fill_color="tomato", marker="triangle")
        plot.add_glyph(source, glyph, view=view)

        # Compute the number of buy/sell movements
        n_buys   = self._strategy.loc[self._display_dates[0]:self._display_dates[1],
                                      'ACTION'].str.count(actions[0]).sum()
        n_sells  = self._strategy.loc[self._display_dates[0]:self._display_dates[1],
                                      'ACTION'].str.count(actions[1]).sum()
        self._buy_sell = [n_buys, n_sells]

        return plot


    def _display_value(self, plot, source, axis:str):
        '''
        Adds moving average and their buffers to plot
        '''
        line_dash = "0" # solid line by default

        if axis.lower() == 'close':
            y_axis       = 'Close'
            legend_label = 'Close'
            line_color   = dft.COLOR_SCHEME[1]

        elif axis.lower() == 'ema':
            y_axis       = 'EMA'
            legend_label = 'EMA'
            line_color   = dft.COLOR_SCHEME[2]

        elif axis.lower() == 'ema_buffer':
            label  = u'EMA \u00b1 '
            label += f'{self._buffer:.2%}'
            y_axis       = 'EMA_PLUS'
            legend_label = label
            line_dash="2 4"
            line_color   = dft.COLOR_SCHEME[2]

        elif axis.lower() == 'sma':
            y_axis       = 'SMA'
            legend_label = 'SMA'
            line_color   = dft.COLOR_SCHEME[3]

        elif axis.lower() == 'sma_buffer':
            label  = u'SMA \u00b1 '
            label += f'{self._buffer:.2%}'
            y_axis       = 'SMA_PLUS'
            legend_label = label
            line_dash="2 4"
            line_color   = dft.COLOR_SCHEME[3]
        else:
            msg = f'TimeSeriesPlot._display_value: unknown axis value {axis}'
            raise ValueError(msg)

        plot.line(source=source,
                  x='Date',
                  y=y_axis,
                  legend_label=legend_label,
                  line_width=1,
                  line_color=line_color,
                  line_dash=line_dash,
                 )

        # Add lower buffer
        if axis.lower() == 'ema_buffer':
            y_axis       = 'EMA_MINUS'
            line_color   = dft.COLOR_SCHEME[2]

        elif axis.lower() == 'sma_buffer':
            y_axis       = 'SMA_MINUS'
            line_color   = dft.COLOR_SCHEME[3]

        plot.line(source=source,
                  x='Date',
                  y=y_axis,
                  line_width=1,
                  line_dash="2 4",
                  line_color=line_color,
                 )
        return plot


    @staticmethod
    def _customize_legend(plot, legend_title=None):
        '''customize legend appearance'''

        if legend_title is not None:
            plot.legend.title = legend_title

        plot.legend.label_text_font       = "helvetica"

        plot.legend.location              = "top_left"

        plot.legend.background_fill_alpha = .4
        plot.legend.background_fill_color = "white"
        plot.legend.border_line_alpha     = .0
        plot.legend.border_line_width     = 1
        plot.legend.border_line_color     = "pink"
        plot.legend.click_policy          = "mute"
        return plot


    def _build_statistics_box(self):
        '''
        Place a text box with signal statistics
        '''
        summary_stats = util.get_summary_stats(self._strategy.loc[self._display_dates[0]:self._display_dates[1], :],
                                               dft.STATS_LEVEL,
                                               'RET')
        text  = 'Daily returns:\n'
        text += u'\u03bc='
        text += f'{summary_stats["mean"]:.2%}\n'
        text += u'\u03c3='
        text += f'{summary_stats["std"]:.2%}\n'
        text += f'Skewness={summary_stats["skewness"]:.2g}\n'
        text += f'Kurtosis={summary_stats["kurtosis"]:.2g}\n'
        text += f'Gaussian: {summary_stats["jb"]["gaussian"]}\n'
        text += f'({1-summary_stats["jb"]["level"]:.0%} '
        text += f'p-value={summary_stats["jb"]["gaussian"]:.3g})\n'
        return text


    def _add_tools(self, plot, panel):
        '''Add tools tips'''
        formatters = {'$x': 'datetime'}
        tooltips = [("", "$x{%d %b %Y}")]
        if panel == 'top':
            if self._display_flags['close']:
                tooltips.append(("Close", "@Close{$0,0.00}"))
            if self._display_flags['ema']:
                tooltips.append(("EMA", "@EMA{$0,0.00}"))
            if self._display_flags['sma']:
                tooltips.append(("SMA", "@SMA{$0,0.00}"))

            tooltips.append(("Return", "@RET{%0,0.00}"))
            tooltips.append(("Volume", "@Volume{(0.00 a)}"))
            plot.add_tools(HoverTool(tooltips   = tooltips,
                                     formatters = formatters,
                                     ),
                          )
            plot.add_tools(ResetTool())
            #plot.add_tools(WheelZoomTool())
            #plot.add_tools(ZoomInTool())
            #plot.add_tools(ZoomOutTool())
            #plot.add_tools(WheelPanTool())
        else:
            tooltips.append(("volume", "@Volume{(0.00 a)}"))

            plot.add_tools(HoverTool(tooltips   = tooltips,
                                     formatters = formatters,
                                     #mode       = 'vline',
                                     ),
                          )
        return plot


    def _show(self, notebook:bool, display:bool, remote:bool):
        '''Screen display & save'''
        if notebook:
            output_notebook()
        else:
            self._build_pathname('html')
            output_file(self._pathname)

        if display and not remote: # save and display
            show(self._plot)
        elif remote: # save to png if remote
            self._build_pathname('png')
            export_png(self._plot, filename=self._pathname)
        else: # save to html if local
            save(self._plot)
