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

def build_ema_map(ticker, security, dates):
    '''
    Builds a 2D numpy array of EMAs as a function of span and buffer
    '''
    # define rolling window span range
    start = dates[0]
    end   = dates[1]
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
    for i, span in tqdm(enumerate(spans),
                        desc = f'Outer Level / {span_par[1] - span_par[0] + 1}'
                        ):
        for j, buffer in enumerate(buffers):
            data  = build_strategy(security.loc[start:end, :].copy(),
                                   span,
                                   buffer,
                                   dft.INIT_WEALTH,
                                  )
            emas[i][j] = get_cumret(data,
                                    'ema',
                                    get_fee(data,
                                            dft.FEE_PCT,
                                            dft.get_actions()))
            if i == 0 and j == 0:
                hold = get_cumret(data, 'hold')

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


def build_sign(d_frame, buffer, reactivity=dft.REACTIVITY):
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
    *** MUST INCORPORATE FEES at start/end ***
    '''
    d_frame['RET'] = 1.0 + d_frame.Close.pct_change()
    d_frame.loc[d_frame.index[0], 'RET'] = 1.0  # set first value to 1.0
    d_frame['CUMRET_HOLD'] = init_wealth * d_frame.RET.cumprod(axis=None, skipna=True)
    return d_frame


def build_ema(d_frame, init_wealth):
    '''
    Computes returns, cumulative returns and 'wealth' from initial_wealth
    from EMA strategy
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


def build_strategy(d_frame, span, buffer, debug=False):
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
    init_wealth = dft.INIT_WEALTH
    reactivity  = dft.REACTIVITY

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

    return d_frame


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
    raise ValueError(f'strategy {strategy} should be either ema or hold')


### I/O ###
def save_best_emas(ticker, date_range, spans, buffers, emas, hold, n_best):
    '''
    Outputs n_best results to file
    The output data is n_best rows of:
    | span | buffer | ema | hold |
    '''
    results = np.zeros(shape=(n_best, 4))
    # Build a n_best x 4 dataframe
    _emas = emas.copy() # b/c algorithm destroys top n_maxima EMA values
    for i in range(n_best):
        # Get coordinates of maximum emas value
        max_idx = np.unravel_index(np.argmax(_emas, axis=None),
                                   _emas.shape)
        results[i][0] = spans[max_idx[0]]
        results[i][1] = buffers[max_idx[1]]
        results[i][2] = np.max(_emas)
        results[i][3] = hold

        # set max emas value to arbitrily small number and re-iterate
        _emas[max_idx[0]][max_idx[1]] = - dft.HUGE

    # Convert numpy array to dataframe
    best_emas = pd.DataFrame(results,
                             columns=['span', 'buffer', 'ema', 'hold']
                             )

    start, end = dates_to_strings(date_range, '%Y-%m-%d')
    suffix = f'{start}_{end}_results'
    save_dataframe(ticker, suffix, best_emas, 'csv')


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


def save_ema_map(ticker, date_range, spans, buffers, emas):
    '''
    Save ema map to pkl
    '''
    temp = []
    for i, span in enumerate(spans):
        for j, buffer in enumerate(buffers):
            temp.append([span, buffer, emas[i,j]])

    temp = pd.DataFrame(temp, columns=['span', 'buffer', 'ema'])

    dates = dates_to_strings(date_range, '%Y-%m-%d')
    suffix = f'{dates[0]}_{dates[1]}_ema_map'
    save_dataframe(ticker, suffix, temp, 'csv')



def save_dataframe(ticker, suffix, dataframe, extension):
    '''
    Save strategy to either csv or pkl file
    '''
    data_dir = dft.DATA_DIR
    filename = f'{ticker}_{suffix}'

    if extension == 'pkl':
        pathname = os.path.join(data_dir, filename + '.pkl')
        dataframe.to_pickle(pathname)
    elif extension == 'csv':
        pathname = os.path.join(data_dir, filename + '.csv')
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
    return [start_dt, end_dt]


def get_datetime_date_range(security, start_date, end_date):
    '''
    Return start and end dates in datetime format
    (this is just a wrapper around init_dates)
    '''
    return init_dates(security, start_date, end_date)


def dates_to_strings(date_range, fmt):
    '''
    takes a range of datetime dates and returns the string equivalent
    in the required format (default='%d-%b-%Y')
    '''
    start = date_range[0]
    end   = date_range[1]
    start_string = start.strftime(fmt)
    end_string   = end.strftime(fmt)
    return [start_string, end_string]
