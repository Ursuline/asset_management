#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 15:57:37 2021

The Ticker object encapsulates various elements from a security
used for trading

@author: charles mégnin
"""
import os
import sys
from datetime import timedelta
import pandas as pd
import matplotlib.pyplot as plt

import trading_defaults as dft
import trading_plots as trplt
import utilities as util

class Ticker():
    '''
    A Ticker is an lightweight object extracted from a Security object
    Provides ease of access to relevant meta-data and price/volume data
    '''
    @classmethod
    def get_default_display_flags(cls):
        '''Returns default flags for display'''
        flags = {}
        flags['close']      = True
        flags['ema']        = True
        flags['ema_buffer'] = False
        flags['sma']        = False
        flags['sma_buffer'] = False
        flags['arrows']     = True
        flags['statistics'] = True
        flags['save']       = True
        return flags

    def __init__(self, symbol, security, dates):
        '''
        NB: dates is date range in string format
        '''
        self._symbol   = symbol
        self._name     = security.get_name()
        self._dates    = dates
        self._currency = security.get_currency()
        self._set_currency_symbol()
        self._load_security_data(security)


    def _set_currency_symbol(self):
        '''Set the symbol corresponding to the currency'''
        if self._currency.lower() == 'usd':
            self._currency_symbol = '$'
        elif self._currency.lower() == 'eur':
            self._currency_symbol = '€'
        elif self._currency.lower() in ['jpy', 'yen', 'hkd', 'cny']:
            self._currency_symbol = '¥'
        else: # symbol = currency value
            self._currency_symbol = self._currency


    def _load_security_data(self, security):
        '''extract market data from security object'''
        dfr = security.get_market_data()
        dfr.set_index('Date', inplace=True)
        self._data = dfr


    def get_dates(self):
        '''Return dates'''
        return self._dates

    def get_name(self):
        '''Return ticker name'''
        return self._name

    def get_currency(self):
        '''Return ticker currency'''
        return self._currency

    def get_currency_symbol(self):
        '''Return ticker currency symbol'''
        return self._currency_symbol

    def get_symbol(self):
        '''Return ticker symbol'''
        return self._symbol

    def get_market_data(self):
        '''Return market data'''
        return self._data

    def get_close(self):
        '''Return Close as DataFrame'''
        security = pd.DataFrame(self.get_market_data()[f'Close_{self._symbol}'])
        security = security.loc[self._dates[0]:self._dates[1],:] # trim the data
        security.rename(columns={f'Close_{self._symbol}': "Close"}, inplace=True)
        return security


    def self_describe(self):
        '''Display all variables in class'''
        print(self.__dict__)


    def get_plot_filename(self, display_dates, strat_pos, with_extension, extension):
        '''
        Returns time series plot filename with extension
        accepts input date in string or datetime format
        optionally add extension for compatibility with save_figure()
        '''
        file_dates = []
        for date in display_dates:
            if isinstance(date, str):
                file_dates.append(date)
            else:
                file_dates.append(util.date_to_string(date, '%Y-%m-%d'))
        filename   = f'{self._symbol}_{file_dates[0]}_{file_dates[1]}_{strat_pos}_tmseries'
        if with_extension:
            filename    += f'.{extension}'
        return filename


    def get_plot_pathname(self, display_dates, strat_pos, with_extension=True, extension='png'):
        '''
        Returns time series plot full path
        '''
        plot_dir = os.path.join(dft.PLOT_DIR, self._symbol)
        filename = self.get_plot_filename(display_dates, strat_pos, with_extension, extension)
        return os.path.join(plot_dir, filename)


    ### PLOTS
    def plot_time_series(self, display_dates, security, topomap, span, buffer, flags, fee_pct):
        '''
        Plots security prices with moving average
        span -> rolling window span
        fee_pct -> fee associated with a buy/sell action
        date_range is entire time series
        display_dates are zoom dates
        flags display -> 0: Price  | 1: EMA  | 2: EMA buffer | 3: SMA | 4: SMA buffer
                         5: arrows | 6 : statistics | 7: save
        '''
        timespan = (display_dates[1] - display_dates[0]).days

        title_dates = util.dates_to_strings([display_dates[0], display_dates[1]], '%d-%b-%Y')
        file_dates  = util.dates_to_strings([display_dates[0], display_dates[1]], '%Y-%m-%d')

        # Extract time window
        window_start = display_dates[0] - timedelta(days = span + 1)
        dfr = topomap.build_strategy(security.loc[window_start:display_dates[1], :].copy(),
                                     span,
                                     buffer,
                                     )

        fee  = topomap.get_fee(dfr, dft.get_actions())
        hold = topomap.get_cumret(dfr, 'hold')  # cumulative returns for hold
        ema  = topomap.get_cumret(dfr, 'ema', fee)  # cumulative returns for EMA

        _, axis = plt.subplots(figsize=(dft.FIG_WIDTH, dft.FIG_HEIGHT))

        # Display MY for > 180 days and DMY otherwise
        if timespan > 180:
            axis.xaxis.set_major_formatter(dft.get_month_year_format())
        else:
            axis.xaxis.set_major_formatter(dft.get_day_month_year_format())

        axis.grid(b=None, which='both', axis='both',
                  color=dft.GRID_COLOR, linestyle='-', linewidth=1)

        if flags['close']: # Close
            axis.plot(dfr.loc[display_dates[0]:display_dates[1], :].index,
                      dfr.loc[display_dates[0]:display_dates[1], :].Close,
                      linewidth=1,
                      color = dft.COLOR_SCHEME[0],
                      label='Price',
                      )

        if flags['ema']: # EMA
            axis.plot(dfr.loc[display_dates[0]:display_dates[1], :].index,
                      dfr.loc[display_dates[0]:display_dates[1], :].EMA,
                      linewidth=1,
                      color = dft.COLOR_SCHEME[1],
                      label=f'{span:.0f}-day EMA',
                      )

        if flags['ema_buffer']: #EMA +/- buffer
            axis.plot(dfr.loc[display_dates[0]:display_dates[1], :].index,
                      dfr.loc[display_dates[0]:display_dates[1], :].EMA_MINUS,
                      linewidth = 1,
                      linestyle = '--',
                      color = dft.COLOR_SCHEME[1],
                      label=f'EMA - {buffer:.2%}',
                      )
            axis.plot(dfr.loc[display_dates[0]:display_dates[1], :].index,
                      dfr.loc[display_dates[0]:display_dates[1], :].EMA_PLUS,
                      linewidth = 1,
                      linestyle = '--',
                      color = dft.COLOR_SCHEME[1],
                      label=f'EMA + {buffer:.2%}',
                      )

        if flags['sma']: # SMA
            axis.plot(dfr.loc[display_dates[0]:display_dates[1], :].index,
                      dfr.loc[display_dates[0]:display_dates[1], :].SMA,
                      linewidth = 1,
                      color     = dft.COLOR_SCHEME[4],
                      label     = f'{span:.0f}-day SMA',
                      )

        if flags['sma_buffer']: #SMA +/- buffer
            axis.plot(dfr.loc[display_dates[0]:display_dates[1], :].index,
                      dfr.loc[display_dates[0]:display_dates[1], :].SMA_MINUS,
                      linewidth = 1,
                      linestyle = '--',
                      color = dft.COLOR_SCHEME[4],
                      label=f'SMA - {buffer:.2%}',
                      )
            axis.plot(dfr.loc[display_dates[0]:display_dates[1], :].index,
                      dfr.loc[display_dates[0]:display_dates[1], :].SMA_PLUS,
                      linewidth = 1,
                      linestyle = '--',
                      color = dft.COLOR_SCHEME[4],
                      label=f'SMA + {buffer:.2%}',
                      )

        axis.legend(loc='best')
        axis.set_ylabel(f'Price ({self._currency_symbol})')

        buy_sell = None
        if flags['arrows']: # Buy/sell arrows

            actions  = dft.get_actions()
            filtered = dfr[(dfr.ACTION == actions[0]) | (dfr.ACTION == actions[1])]
            n_buys   = filtered.loc[display_dates[0]:display_dates[1],
                                    'ACTION'].str.count(actions[0]).sum()
            n_sells  = filtered.loc[display_dates[0]:display_dates[1],
                                    'ACTION'].str.count(actions[1]).sum()
            buy_sell = [n_buys, n_sells]

            trplt.plot_arrows(axis,
                              dfr.loc[display_dates[0]:display_dates[1], :],
                              dft.get_actions(),
                              dft.get_color_scheme(),
                              )

        if flags['statistics']: # Statistics
            summary_stats = util.get_summary_stats(dfr.loc[display_dates[0]:display_dates[1], :],
                                                   dft.STATS_LEVEL,
                                                   'RET')
            axis = trplt.plot_stats(summary_stats,
                                    axis,
                                    #dfr.loc[display_dates[0]:display_dates[1], :],
                                    colors = dft.get_color_scheme(),
                                    )

        trplt.build_title(axis        = axis,
                          ticker      = self._symbol,
                          ticker_name = self._name,
                          position    = topomap.get_strategic_position(),
                          dates       = title_dates,
                          span        = span,
                          buffer      = buffer,
                          ema         = ema,
                          hold        = hold,
                          buy_sell    = buy_sell,
                          )

        if flags['save']: # Save plot to file
            plot_dir = os.path.join(dft.PLOT_DIR, self._symbol)
            self.save_figure(directory = plot_dir,
                             pathname  = self.get_plot_pathname(file_dates,
                                                                topomap.get_strategic_position(),
                                                                with_extension=True,
                                                                extension='png',
                                                                ),
                             dpi = dft.DPI,
                             )

        plt.show()
        return dfr

    @staticmethod
    def save_figure(directory, pathname, dpi):
        '''
        Saves figure to file
        variables:
            directory - directory to plot to
            prefix - filename with its extension
        '''
        os.makedirs(directory, exist_ok = True)
        try:
            plt.savefig(pathname,
                        dpi         = dpi,
                        transparent = False,
                        facecolor   ='white',
                        edgecolor   ='none',
                        orientation = 'landscape',
                        bbox_inches = 'tight',
                        )
        except TypeError as ex:
            print(f'Could not save to {pathname}: {ex}')
        except:
            print(f'Error type {sys.exc_info()[0]}')
        else:
            pass
