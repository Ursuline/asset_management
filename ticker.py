#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 15:57:37 2021

The Ticker object encapsulates various elements from a security
used for trading

@author: charles mégnin
"""
# import pandas as pd
# import security as sec
import os
from datetime import timedelta
import matplotlib.pyplot as plt

import trading as tra
import trading_defaults as dft
import trading_plots as trplt
import utilities as util

class Ticker():
    ''' A Ticker is an lightweight object extracted from a Security object
        Provides ease of access to relevant meta-data and price/volume data
    '''
    def __init__(self, symbol, security):
        print(f'Loading ticker {symbol}')
        super().__init__()
        self._symbol = symbol
        self._name = security.get_name()
        self._currency = security.get_currency()
        self._data = self._load_security_data(security)

    def _load_security_data(self, security):
        dfr = security.get_market_data()
        dfr.set_index('Date', inplace=True)
        return dfr

    def get_name(self):
        '''Return ticker name'''
        return self._name

    def get_currency(self):
        '''Return ticker currency'''
        return self._currency

    def get_symbol(self):
        '''Return ticker symbol'''
        return self._symbol

    def get_market_data(self):
        '''Return market data'''
        return self._data

    def self_describe(self):
        '''Display all variables in class'''
        print(self.__dict__)

### PLOTS

    def plot_time_series(self, date_range, display_dates, security, span, buffer, flags, fee_pct):
        '''
        Plots security prices with moving average
        span -> rolling window span
        fee_pct -> fee associated with a buy/sell action
        date_range is entire time series
        display_dates are zoom dates
        flags display -> 0: Price  | 1: EMA  | 2: buffer |
                         3: arrows | 4 : statistics | 5: save
        '''
        timespan = (display_dates[1] - display_dates[0]).days

        title_dates = util.dates_to_strings([display_dates[0], display_dates[1]], '%d-%b-%Y')
        file_dates  = util.dates_to_strings([display_dates[0], display_dates[1]], '%Y-%m-%d')

        # Extract time window
        window_start = display_dates[0] - timedelta(days = span + 1)
        dfr = tra.build_strategy(security.loc[window_start:display_dates[1], :].copy(),
                                 span,
                                 buffer,
                                 dft.INIT_WEALTH,
                                 )

        fee  = tra.get_fee(dfr, fee_pct, dft.get_actions())
        hold = tra.get_cumret(dfr, 'hold')  # cumulative returns for hold strategy
        ema  = tra.get_cumret(dfr, 'ema', fee)  # cumulative returns for EMA strategy

        _, axis = plt.subplots(figsize=(dft.FIG_WIDTH, dft.FIG_HEIGHT))

        # Display MY for > 180 days and DMY otherwise
        if timespan > 180:
            axis.xaxis.set_major_formatter(dft.get_month_year_format())
        else:
            axis.xaxis.set_major_formatter(dft.get_day_month_year_format())

        axis.grid(b=None, which='both', axis='both',
                  color=dft.GRID_COLOR, linestyle='-', linewidth=1)

        # Plot Close
        if flags[0]:
            axis.plot(dfr.loc[display_dates[0]:display_dates[1], :].index,
                      dfr.loc[display_dates[0]:display_dates[1], :].Close,
                      linewidth=1,
                      color = dft.COLOR_SCHEME[0],
                      label='Price')
        # Plot EMA
        if flags[1]:
            axis.plot(dfr.loc[display_dates[0]:display_dates[1], :].index,
                      dfr.loc[display_dates[0]:display_dates[1], :].EMA,
                      linewidth=1,
                      color = dft.COLOR_SCHEME[1],
                      label=f'{span:.0f}-day EMA')
        # Plot EMA +/- buffer
        if flags[2]:
            axis.plot(dfr.loc[display_dates[0]:display_dates[1], :].index,
                      dfr.loc[display_dates[0]:display_dates[1], :].EMA_MINUS,
                      linewidth = 1,
                      linestyle = '--',
                      color = dft.COLOR_SCHEME[2],
                      label=f'EMA - {buffer:.2%}')
            axis.plot(dfr.loc[display_dates[0]:display_dates[1], :].index,
                      dfr.loc[display_dates[0]:display_dates[1], :].EMA_PLUS,
                      linewidth = 1,
                      linestyle = '--',
                      color = dft.COLOR_SCHEME[2],
                      label=f'EMA + {buffer:.2%}')
        axis.legend(loc='best')
        axis.set_ylabel('Price')

        buy_sell = None
        if flags[3]: # plot buy/sell arrows

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

        if flags[4]:
            summary_stats = util.get_summary_stats(dfr.loc[display_dates[0]:display_dates[1], :],
                                                   dft.STATS_LEVEL,
                                                   'RET')
            axis = trplt.plot_stats(summary_stats,
                                    axis,
                                    dfr.loc[display_dates[0]:display_dates[1], :],
                                    dft.get_color_scheme(),
                                    )

        trplt.build_title(axis=axis,
                          ticker=self._symbol,
                          ticker_name=self._name,
                          dates=title_dates,
                          span=span,
                          buffer=buffer,
                          ema=ema,
                          hold=hold,
                          buy_sell=buy_sell,)
        if flags[5]:
            data_dir = os.path.join(dft.PLOT_DIR, self._symbol)
            trplt.save_figure(data_dir,
                              f'{self._symbol}_{file_dates[0]}_{file_dates[1]}_tmseries')
            plt.show()

        return dfr
