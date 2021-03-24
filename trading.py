#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 14:48:44 2021

trading.py

Routines for trading

@author: charly
"""
import os
from datetime import datetime
import pandas as pd
import numpy as np
from tqdm import tqdm
import security as sec

import trading_defaults as dft

### TRADING ###

def build_ema_map(ticker, security, start, end):
    '''
    Builds a 2D numpy array of EMAs as a function of span and buffer
    '''
    init_wealth = dft.get_init_wealth()

    # define rolling window span range
    span_par = dft.get_spans()
    spans = np.arange(span_par[0],
                      span_par[1] + 1,
                      step = 1
                     )

    # define buffer range
    buff_par = dft.get_buffers()
    buffers = np.linspace(buff_par[0],
                          buff_par[1],
                          buff_par[2],
                         )

    # Initialize EMA returns
    emas = np.zeros((spans.shape[0], buffers.shape[0]), dtype=np.float64)

    # Fill EMAS for all span/buffer combinations
    tqdm_desc = f'Outer Level / {span_par[1] - span_par[0] + 1}'
    for i, span in tqdm(enumerate(spans), desc=tqdm_desc):
        for j, buffer in enumerate(buffers):
            data  = build_strategy(ticker,
                                   security.loc[start:end, :].copy(),
                                   span,
                                   buffer,
                                   init_wealth,
                                  )
            emas[i][j] = get_cumret(data,
                                    'ema',
                                    init_wealth,
                                    get_fee(data,
                                            dft.get_fee_pct(),
                                            dft.get_actions()))
            if i == 0 and j == 0:
                hold = get_cumret(data, 'hold', init_wealth)

    return spans, buffers, emas, hold


def build_positions(d_frame):
    '''
    Builds desired positions for the EMA strategy
    *** Long strategy only ***
    POSITION -> cash, long (short pending)
    ACTION -> buy, sell, n/c (no change)
    '''
    n_time_steps = d_frame.shape[0]
    positions, actions = ([] for i in range(2))

    positions.append('cash')
    actions.append('n/c')

    for step in range(1, n_time_steps):  # Long strategy only
        if positions[step - 1] == 'cash':  # if previous position was cash
            # if in or below buffer
            if d_frame.loc[d_frame.index[step], 'SIGN'] in [0, -1]:
                positions.append('cash')
                actions.append('n/c')
            elif d_frame.loc[d_frame.index[step], 'SIGN'] == 1:
                positions.append('long')
                actions.append('buy')
            else:
                msg = f'Inconsistent sign {d_frame.loc[d_frame.index[step], "SIGN"]}'
                raise ValueError(msg)
        elif positions[step - 1] == 'long':  # previous position: long
            if d_frame.loc[d_frame.index[step], 'SIGN'] in [0, 1]:
                positions.append('long')
                actions.append('n/c')
            elif d_frame.loc[d_frame.index[step], 'SIGN'] == -1:
                positions.append('cash')
                actions.append('sell')
            else:
                msg = f'Inconsistent sign {d_frame.loc[d_frame.index[step], "SIGN"]}'
                raise ValueError(msg)
        else:
            msg  = f"step {step}: previous pos {positions[step - 1]} "
            msg += "sign:{d_frame.loc[d_frame.index[step], 'SIGN']}"
            raise ValueError(msg)
    d_frame.insert(loc=len(d_frame.columns), column='POSITION', value=positions)
    d_frame.insert(loc=len(d_frame.columns), column='ACTION', value=actions)
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
    *** MUST INCORPORATE FEES ***
    '''
    d_frame['RET'] = 1.0 + d_frame.Close.pct_change()
    d_frame.loc[d_frame.index[0], 'RET'] = 1.0  # set first value to 1.0
    d_frame['CUMRET_HOLD'] = init_wealth * d_frame.RET.cumprod(axis=None, skipna=True)
    return d_frame


def build_ema(d_frame, init_wealth):
    '''
    Computes returns, cumulative returns and 'wealth' from initial_wealth
    for EMA strategy
    *** MUST INCORPORATE FEES ***
    '''
    # If long, use the daily returns from hold, else set to 1.0 (ie: cash=no change)
    d_frame['RET_EMA'] = np.where(d_frame.POSITION == 'long',
                                  d_frame.RET,
                                  1.0)
    # Compute cumulative returns aka 'Wealth'
    d_frame['CUMRET_EMA'] = d_frame.RET_EMA.cumprod(axis   = None,
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


def build_strategy(ticker, d_frame, span, buffer, init_wealth, debug=False, reactivity=1):
    '''
    *** At this point, only a long strategy is considered ***
    Implements running-mean (ewm) strategy
    Input dataframe d_frame has date index & security value 'Close'

    Variables:
    span       -> number of rolling days
    reactivity -> reactivity to market change in days (should be set to 1)
    buffer     -> % above & below ema to trigger buy/sell

    Returns the 'strategy' consisting of a dataframe with original data + following columns:
    EMA -> exponential moving average
    SIGN -> 1 : above buffer 0: in buffer -1: below buffer
    ACTION -> buy / sell / n/c (no change)
    RET -> 1 + % daily return
    CUMRET_HOLD -> cumulative returns for a hold strategy
    RET2 -> 1 + % daily return when Close > EMA
    CUMRET_EMA -> cumulative returns for the EMA strategy
    '''
    # Compute exponential weighted mean 'EMA'
    d_frame['EMA'] = d_frame.Close.ewm(span=span, adjust=False).mean()

    if debug: # include buffer limits in dataframe (for printing)
        d_frame.insert(loc=1, column='EMA-', value=d_frame['EMA']*(1-buffer))
        d_frame.insert(loc=len(d_frame.columns), column='EMA+',
                  value=d_frame['EMA']*(1+buffer))

    # build the SIGN column (above/in/below buffer)
    d_frame = build_sign(d_frame, buffer, reactivity)

    # build the POSITION (long/cash) & ACTION (buy/sell) columns
    d_frame = build_positions(d_frame)

    # compute returns from a hold strategy
    d_frame = build_hold(d_frame, init_wealth)

    # compute returns from the EMA strategy
    d_frame = build_ema(d_frame, init_wealth)

    # remove junk
    d_frame = cleanup_strategy(d_frame)

    # Save strategy to file (either csv or pkl)
    save_strategy(ticker, d_frame, 'csv')

    return d_frame


def get_fee(data, fee_pct, actions):
    '''
    Return fees associated to buys / sells
    fee_pct -> brokers fee
    actions = ['buy', 'sell', 'n/c']
    fee -> $ fee corresponding to fee_pct
    '''
    # Add a fee for each movement: mask buys
    fee  = (fee_pct * data[data.ACTION == actions[0]].CUMRET_EMA.sum())
    # Mask sells
    fee += (fee_pct * data[data.ACTION == actions[1]].CUMRET_EMA.sum())
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
    if strategy.lower() == 'ema':
        return (data.CUMRET_EMA[-1]-fee)/init_wealth - 1
    raise ValueError(f'strategy {strategy} should be either ema or hold')


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


def save_strategy(ticker, dataframe, extension):
    '''
    Save strategy to either csv or pkl file
    '''
    data_dir = 'data'

    start = dataframe.index[0].strftime('%y-%m-%d')
    end   = dataframe.index[-1].strftime('%y-%m-%d')
    prefix = f'{ticker}_{start}_{end}'

    if extension == 'pkl':
        pathname = os.path.join(data_dir, prefix+'.pkl')
        dataframe.to_pickle(pathname)
    elif extension == 'csv':
        pathname = os.path.join(data_dir, prefix+'.csv')
        dataframe.to_csv(pathname, sep=';')
    else:
        raise ValueError(f'{extension} not supported should be pkl or csv')


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
