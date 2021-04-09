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

    def get_ticker_name(self):
        '''Return ticker name'''
        return self._name

    def get_currency(self):
        '''Return ticker currency'''
        return self._currency

    def get_ticker_symbol(self):
        '''Return ticker symbol'''
        return self._symbol

    def get_market_data(self):
        '''Return market data'''
        return self._data

    def self_describe(self):
        '''Display all variables in class'''
        print(self.__dict__)
