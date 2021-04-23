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
import security as sec

import ticker as tkr


### I/O ###
def load_security(dirname, ticker, period, dates, refresh=False):
    '''
    Load data from file else upload from Yahoo finance
    dirname -> directory where pkl data is saved
    ticker -> Yahoo Finance ticker symbol
    period -> download period
    refresh -> True : download data from Yahoo / False use pickle data if it exists
    '''
    dirname = os.path.join(dirname, ticker)
    ticker_filename = ticker + f'_{dates[0]}-{dates[1]}_raw'
    ticker_pathname = os.path.join(dirname, ticker_filename + '.pkl')

    if os.path.exists(ticker_pathname) and (not refresh):
        #print(f'Loading saved Yahoo data from {ticker_pathname}')
        pickle_file = open(ticker_pathname,'rb')
        ticker_obj  = pickle.load(pickle_file)
        pickle_file.close()
    else:
        #print('Downloading data from Yahoo Finance')
        security  = sec.Security(ticker, period)
        ticker_obj = tkr.Ticker(symbol   = ticker,
                                security = security,
                                dates    = dates,
                                )

        # write ticker object to file
        os.makedirs(dirname, exist_ok = True)
        pickle_file = open(ticker_pathname,'wb')
        pickle.dump(ticker_obj, pickle_file)
        pickle_file.close()
    print(f'{ticker_obj.get_name()} Yahoo data loaded\n')
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
