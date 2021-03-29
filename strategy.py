#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 11:18:04 2021

@author: charles mégnin
"""

class Strategy():
    '''
    The Strategy class encapsulates raw prices, ema prices and all the meta info
    associated to the strategy
    '''
    def __init__(self, ticker_symbol, ticker_name, strategy_name, date_range):
        self['ticker']     = ticker_symbol
        self['name']       = ticker_name
        self['strategy']   = strategy_name
        self['date_range'] = date_range # in datetime format

    def set_market_data(self, close_df):
        '''
        Store raw market data as self.close
        '''
        self.close  = close_df.copy(deep = True)

    def set_mean(self, span):

