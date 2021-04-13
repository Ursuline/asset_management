#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 14:48:44 2021

trading.py

Routines for trading

@author: charles mégnin
"""
import os
import pickle
import pandas as pd
import numpy as np
import security as sec

import trading_defaults as dft
import ticker as tkr
import utilities as util


def build_positions(d_frame, position):
    '''
    Builds desired positions for the EMA strategy
    POSITION -> cash, long (short pending)
    ACTION -> buy, sell, n/c (no change)
    *** REWRITE AS SWITCH ***
    '''
    n_time_steps = d_frame.shape[0]
    positions, actions = ([] for i in range(2))

    positions.append(dft.POSITIONS[2])
    actions.append(dft.ACTIONS[2])

    for step in range(1, n_time_steps):
        sign = d_frame.loc[d_frame.index[step], 'SIGN']
        prev_position = positions[step - 1]
        if position.lower() == 'long':
            if prev_position == 'cash':  # if previous position was cash
                if sign in [0, -1]: # in or below buffer
                    positions.append('cash')
                    actions.append('n/c')
                else: # above buffer
                    positions.append('long')
                    actions.append('buy')
            elif prev_position == 'long':  # previous position: long
                if sign in [0, 1]: # in or above buffer
                    positions.append('long')
                    actions.append('n/c')
                else: # below buffer
                    positions.append('cash')
                    actions.append('sell')
            else: # previous position: short (to implement)
                if sign == [0, -1]: # in or below buffer
                    positions.append('short')
                    actions.append('n/c')
                else: # above buffer
                    positions.append('long')
                    actions.append('buy')
        elif position.lower() == 'short':
            if prev_position == 'cash':  # if previous position was cash
                if sign in [0, 1]: # in or above buffer
                    positions.append('cash')
                    actions.append('n/c')
                else: # below buffer
                    positions.append('short')
                    actions.append('sell')
            elif prev_position == 'short':  # previous position: short
                if sign in [0, -1]: # in or below buffer
                    positions.append('short')
                    actions.append('n/c')
                else: # above buffer
                    positions.append('cash')
                    actions.append('buy')
        else:
            raise ValueError('build_positions: long or short positions only')

    d_frame.insert(loc=len(d_frame.columns), column='POSITION', value=positions)
    d_frame.insert(loc=len(d_frame.columns), column='ACTION', value=actions)
    return d_frame


def build_sign(d_frame, buffer, reactivity=dft.REACTIVITY):
    '''
    The SIGN column corresponds to the position wrt ema +/- buffer:
    -1 below buffer / 0 within buffer / 1 above buffer
    '''
    d_frame.loc[:, 'SIGN'] = np.where(d_frame.Close - d_frame.EMA*(1 + buffer) > 0,
                                      1, np.where(d_frame.Close - d_frame.EMA*(1 - buffer) < 0,
                                                  -1, 0)
                                      )
    # shift by reactivity days (should be 1) -> buy/sell action follows close date
    d_frame.loc[:, 'SIGN'] = d_frame['SIGN'].shift(reactivity)
    d_frame.loc[d_frame.index[0], 'SIGN'] = 0.0  # set first value to 0
    return d_frame


def build_hold(d_frame, position, init_wealth):
    '''
    Computes returns, cumulative returns and 'wealth' from initial_wealth
    for hold strategy
    *** MUST INCORPORATE FEES at start/end ***
    '''
    if position == 'long':
        d_frame.loc[:, 'RET'] = 1.0 + d_frame.Close.pct_change()
    else: # short
        d_frame.loc[:, 'RET'] = 1.0 - d_frame.Close.pct_change()
    d_frame.loc[d_frame.index[0], 'RET'] = 1.0  # set first value to 1.0
    d_frame.loc[:, 'CUMRET_HOLD'] = init_wealth * d_frame.RET.cumprod(axis   = None,
                                                                      skipna = True)
    return d_frame


def build_ema(d_frame, init_wealth):
    '''
    Computes returns, cumulative returns and 'wealth' from initial_wealth
    from EMA strategy
    *** INCORPORATE FEES ***
    '''
    # If long, use the daily returns from hold, if short set to 1.0 (ie: cash=no change)
    d_frame.loc[:, 'RET_EMA'] = np.where(d_frame.POSITION == 'cash',
                                         1.0,
                                         d_frame.RET,
                                         )

    # Compute cumulative returns aka 'Wealth'
    d_frame.loc[:, 'CUMRET_EMA'] = d_frame.RET_EMA.cumprod(axis   = None,
                                                           skipna = True) * init_wealth
    # Set first value to init_wealth
    d_frame.loc[d_frame.index[0], 'CUMRET_EMA'] = init_wealth

    return d_frame


def cleanup_strategy(dataframe):
    '''
    Remove unnecessary columns
    '''
    dataframe = dataframe.drop(['SIGN'], axis=1)
    dataframe = dataframe.drop(['RET_EMA'], axis=1)

    return dataframe


def get_fee(data, fee_pct, actions):
    '''
    Return fees associated to buys / sells
    FEE_PCT -> brokers fee
    actions = ['buy', 'sell', 'n/c']
    fee -> $ fee corresponding to fee_pct
    '''
    # Add a fee for each movement: mask buys
    fee  = (fee_pct * data[data.ACTION == actions[0]].CUMRET_EMA.sum())
    # Mask sells
    fee += (fee_pct * data[data.ACTION == actions[1]].CUMRET_EMA.sum())
    return fee


def get_cumret(data, strategy, fee=0):
    '''
    Returns cumulative return for the given strategy
    Value returned is relative difference between final and initial wealth
    If strategy is EMA, returns cumulative returns net of fees
    *** FIX FEES ***
    '''
    if strategy.lower() == 'hold':
        return data.CUMRET_HOLD[-1]/dft.INIT_WEALTH - 1
    if strategy.lower() == 'ema':
        return (data.CUMRET_EMA[-1]-fee)/dft.INIT_WEALTH - 1
    raise ValueError(f'option {strategy} should be either ema or hold')


### I/O ###
def load_security_oo(dirname, ticker, period, dates, refresh=False):
    '''
    Load data from file else upload from Yahoo finance
    dirname -> directory where pkl data is saved
    ticker -> Yahoo Finance ticker symbol
    period -> download period
    refresh -> True : download data from Yahoo / False use pickle data if it exists
    '''
    dirname = os.path.join(dirname, ticker)
    data_filename = ticker + '_' + period
    data_pathname = os.path.join(dirname, data_filename + '.pkl')
    ticker_filename = ticker + '_name'
    ticker_pathname = os.path.join(dirname, ticker_filename + '.pkl')
    if os.path.exists(ticker_pathname) and (not refresh):
        print(f'Loading saved Yahoo data from {data_pathname}')
        data        = pd.read_pickle(data_pathname)
        pickle_file = open(ticker_pathname,'rb')
        ticker_obj  = pickle.load(pickle_file)
        pickle_file.close()
    else:
        print('Downloading data from Yahoo Finance')
        security  = sec.Security(ticker, period)
        data      = security.get_market_data()
        data.set_index('Date', inplace=True)
        ticker_obj = tkr.Ticker(symbol   = ticker,
                                security = security,
                                dates    = dates,
                                )

        os.makedirs(dirname, exist_ok = True)
        data.to_pickle(data_pathname) #store locally

        # write ticker object to file ** MERGE WITH DATA
        pickle_file = open(ticker_pathname,'wb')
        pickle.dump(ticker_obj, pickle_file)
        pickle_file.close()
    print(f'\n{ticker_obj.get_name()} Yahoo data loaded')
    return ticker_obj


def display_full_dataframe(data):
    '''
    Displays all rows & columns of a pandas dataframe
    '''
    with pd.option_context('display.max_rows', None,
                           'display.max_columns', None,
                           'display.width', 1000,
                           'display.precision', 2,
                           'display.colheader_justify',
                           'left'):
        print(data)
