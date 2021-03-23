#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 14:48:44 2021

Routines for trading

@author: charly
"""
import os
import pandas as pd
import security as sec
from datetime import datetime

def load_security(dirname, ticker, period, refresh=False):
    '''
    Load data from file else upload from Yahoo finance
    '''
    filename = ticker + '_' + period
    pathname = os.path.join(dirname, filename+'.pkl')
    if os.path.exists(pathname) and refresh == False:
        print(f'Loading data from {pathname}')
        data = pd.read_pickle(pathname)
    else:
        print('Downloading data from Yahoo Finance')
        data = sec.Security(ticker, period).get_market_data()
        data.set_index('Date', inplace=True)
        data.to_pickle(pathname) #store locally
    return data


def init_dates(security, start_date, end_date):
    '''
    Determines start and end dates from START_DATE & END_DATE
    Handles gracefully start date smaller than the one in the dataset
    data returned in datetime format
    '''
    start_dt    = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt      = datetime.strptime(end_date, '%Y-%m-%d')
    secu_start  = security.index[0]
    if secu_start > start_dt:
        start_dt = secu_start
        print(f'start date reset to {start_dt}')
    return start_dt, end_dt