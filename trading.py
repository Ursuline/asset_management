#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 14:48:44 2021

Routines for trading

@author: charly
"""
import os
from datetime import datetime
import pandas as pd
import numpy as np
import security as sec

### TRADING ###

def build_positions(d_frame):
    '''
    Builds desired positions for the EMA strategy
    *** Long strategy only ***
    POSITION -> cash, long (short pending)
    SWITCH -> buy, sell, n/c (no change)
    '''
    n_time_steps = d_frame.shape[0]
    positions, switches = ([] for i in range(2))

    positions.append('cash')
    switches.append('n/c')

    for step in range(1, n_time_steps):  # Long strategy only
        if positions[step - 1] == 'cash':  # if previous position was cash
            # if in or below buffer
            if d_frame.loc[d_frame.index[step], 'SIGN'] in [0, -1]:
                positions.append('cash')
                switches.append('n/c')
            elif d_frame.loc[d_frame.index[step], 'SIGN'] == 1:
                positions.append('long')
                switches.append('buy')
            else:
                msg = f'Inconsistent sign {d_frame.loc[d_frame.index[step], "SIGN"]}'
                raise ValueError(msg)
        elif positions[step - 1] == 'long':  # previous position: long
            if d_frame.loc[d_frame.index[step], 'SIGN'] in [0, 1]:
                positions.append('long')
                switches.append('n/c')
            elif d_frame.loc[d_frame.index[step], 'SIGN'] == -1:
                positions.append('cash')
                switches.append('sell')
            else:
                msg = f'Inconsistent sign {d_frame.loc[d_frame.index[step], "SIGN"]}'
                raise ValueError(msg)
        else:
            msg  = f"step {step}: previous pos {positions[step - 1]} "
            msg += "sign:{d_frame.loc[d_frame.index[step], 'SIGN']}"
            raise ValueError(msg)
    d_frame.insert(loc=len(d_frame.columns), column='POSITION', value=positions)
    d_frame.insert(loc=len(d_frame.columns), column='SWITCH', value=switches)
    return d_frame


def build_sign(d_frame, buffer, reactivity):
    '''
    The SIGN column corresponds to the position wrt ema +/- buffer:
    -1 below buffer / 0 within buffer / 1 above buffer
    '''
    # Assign a value SIGN =  1 if close > EMA + buffer
    #                SIGN = -1 if close < EMA - buffer
    #                SIGN = 0 otherwise
    d_frame['SIGN'] = np.where(d_frame.Close - d_frame.EMA*(1 + buffer) > 0,
                               1,
                               np.where(d_frame.Close - d_frame.EMA*(1 - buffer) < 0,
                                        -1,
                                        0)
                          )
    # shift by reactivity days (should be 1) -> buy/sell action follows close date
    d_frame['SIGN'] = d_frame['SIGN'].shift(reactivity)
    d_frame.loc[d_frame.index[0], 'SIGN'] = 0.0  # set first value to 0
    return d_frame


def build_hold(d_frame, init_wealth):
    '''
    Computes returns, cumulative returns and 'wealth' from initial_wealth
    for hold strategy
    '''
    d_frame['RET'] = 1.0 + d_frame.Close.pct_change()
    d_frame.loc[d_frame.index[0], 'RET'] = 1.0  # set first value to 1.0
    d_frame['CUMRET_HOLD'] = init_wealth * d_frame.RET.cumprod(axis=None, skipna=True)
    return d_frame


def get_strategy(d_frame, span, buffer, init_wealth, debug=False, reactivity=1):
    '''
    *** At this point, only a long strategy is considered ***
    Implements running-mean (ewm) strategy
    Input dataframe d_frame has date index & security value 'Close'

    Variables:
    span       -> number of rolling days
    reactivity -> reactivity to market change in days (should be set to 1)
    buffer     -> % above & below ema to trigger buy/sell

    Returns the 'strategy' consissting of:
    A dataframe with original data + following columns
    EMA -> exponential moving average
    SIGN -> 1 : above buffer 0: in buffer -1: below buffer
    SWITCH -> buy / sell / n/c (no change)
    RET -> 1 + % daily return
    CUMRET_HOLD -> cumulative returns for a hold strategy
    RET2 -> 1 + % daily return when Close > EMA
    CUMRET_EMA -> cumulative returns for the EMA strategy
    '''
    # Compute exponential weighted mean
    d_frame['EMA'] = d_frame.Close.ewm(span=span, adjust=False).mean()

    # include buffer limits in dataframe for printing
    if debug:
        d_frame.insert(loc=1, column='EMA-', value=d_frame['EMA']*(1-buffer))
        d_frame.insert(loc=len(d_frame.columns), column='EMA+',
                  value=d_frame['EMA']*(1+buffer))

    d_frame = build_sign(d_frame, buffer, reactivity)

    # Assign a value SIGN =  1 if close > EMA + buffer
    #                SIGN = -1 if close < EMA - buffer
    #                SIGN = 0 otherwise
    # d_frame['SIGN'] = np.where(d_frame.Close - d_frame.EMA*(1 + buffer) > 0,
    #                            1,
    #                            np.where(d_frame.Close - d_frame.EMA*(1 - buffer) < 0,
    #                                     -1,
    #                                     0)
    #                       )
    # # shift by reactivity days (should be 1) -> buy/sell action follows close date
    # d_frame['SIGN'] = d_frame['SIGN'].shift(reactivity)
    # d_frame.loc[d_frame.index[0], 'SIGN'] = 0.0  # set first value to 0

    d_frame = build_positions(d_frame)  # compute position and switch columns

    d_frame = build_hold(d_frame, init_wealth)

    # Compute returns, cumulative returns and 'wealth' for hold strategy
    # d_frame['RET'] = 1.0 + d_frame.Close.pct_change()
    # d_frame.loc[d_frame.index[0], 'RET'] = 1.0  # set first value to 1.0
    # d_frame['CUMRET_HOLD'] = init_wealth * d_frame.RET.cumprod(axis=None, skipna=True)

    # Cumulative wealth for ema strategy
    d_frame['RET_EMA'] = np.where(d_frame.POSITION == 'long', d_frame.RET, 1.0)
    d_frame['CUMRET_EMA'] = d_frame.RET_EMA.cumprod(
        axis=None, skipna=True) * init_wealth
    d_frame.loc[d_frame.index[0], 'CUMRET_EMA'] = init_wealth
    d_frame = d_frame.drop(['RET_EMA'], axis=1)
    d_frame = d_frame.drop(['SIGN'], axis=1)
    d_frame.to_csv('check.csv', sep=',')
    return d_frame


def get_fee(data, fee_pct, switches):
    '''
    Return fees associated to position switches
    fee_pct -> brokers fee
    switches = ['buy', 'sell', 'n/c']
    fee -> $ fee corresponding to fee_pct
    '''
    # Add a fee for each movement
    fee  = (fee_pct * data[data.SWITCH == switches[0]].CUMRET_EMA.sum())
    fee += (fee_pct * data[data.SWITCH == switches[1]].CUMRET_EMA.sum())
    return fee


def get_cumret(data, strategy, init_wealth, fee=0):
    '''
    Returns cumulative return for the given strategy
    Value returned is relative difference between final and initial wealth
    If strategy is EMA, returns cumulative returns net of fees
    *** FIX FEES ***
    '''
    if strategy.lower() == 'hold':
        return data.CUMRET_HOLD[-1]/init_wealth - 1
    elif strategy.lower() == 'ema':
        return (data.CUMRET_EMA[-1]-fee)/init_wealth - 1
    else:
        raise ValueError(
            f"strategy {strategy} should be either of ema or hold")


### I/O ###
def load_security(dirname, ticker, period, refresh=False):
    '''
    Load data from file else upload from Yahoo finance
    dirname -> directory where pkl data is saved
    ticker -> Yahoo Finance ticker symbol
    period -> download period
    refresh -> True : download data from Yahoo / False use pickle data if it exists
    '''
    filename = ticker + '_' + period
    pathname = os.path.join(dirname, filename+'.pkl')
    if os.path.exists(pathname) and (not refresh):
        print(f'Loading data from {pathname}')
        data = pd.read_pickle(pathname)
    else:
        print('Downloading data from Yahoo Finance')
        data = sec.Security(ticker, period).get_market_data()
        data.set_index('Date', inplace=True)
        data.to_pickle(pathname) #store locally
    return data


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


### DATETIME ###
def init_dates(security, start_date_string, end_date_string):
    '''
    Returns start and end dates in datetime format from start_date & end_date
    in string format
    Handles gracefully start date smaller than the one in the dataset
    data returned in datetime format
    '''
    start_dt    = datetime.strptime(start_date_string, '%Y-%m-%d')
    end_dt      = datetime.strptime(end_date_string, '%Y-%m-%d')
    secu_start  = security.index[0]
    # Check if data downloaded otherwise start with earliest date
    if secu_start > start_dt:
        start_dt = secu_start
        print(f'start date reset to {start_dt}')
    return start_dt, end_dt


def get_title_dates(security, start_date, end_date):
    '''
    Return start and end dates for title format:
    %d-%b-%Y: 03-Jul-2021
    '''
    dates = init_dates(security, start_date, end_date)
    return dates[0].strftime('%d-%b-%Y'), dates[1].strftime('%d-%b-%Y')


def get_datetime_dates(security, start_date, end_date):
    '''
    Return start and end dates in datetime format
    (this is just a wrapper around init_dates)
    '''
    return init_dates(security, start_date, end_date)


def get_filename_dates(security, start_date, end_date):
    '''
    Return start and end dates for file name format:
    %Y-%m-%d: 2021-03-07
    '''
    dates = init_dates(security, start_date, end_date)
    return dates[0].strftime('%Y-%m-%d'), dates[1].strftime('%Y-%m-%d')
