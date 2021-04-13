#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 20:50:46 2021

Security object encapsulates yfinance download and provides
convenience shortcuts
References:
https://pypi.org/project/yfinance/
https://github.com/ranaroussi/yfinance
https://aroussi.com/post/python-yahoo-finance

@author: charles mégnin
"""
import sys
import traceback
import datetime as dt
import pandas as pd
import yfinance as yf
import equity as eq
import utilities as util

class Security(eq.Equity):
    ''' A Security is an object resulting from Yahoo finance download using yfinance
        - Provides ease of access to relevant variables
    '''
    def __init__(self, symbol, period):
        print(f'Loading ticker {symbol}')
        super().__init__()
        self.data['symbol'] = symbol
        self.data['period'] = period
        try:
            self.ticker   = yf.Ticker(self.data['symbol'])

        except Exception as ex:
            print(f"Couldn't load {symbol}: Exception={ex}")
            print(sys.exc_info())
            print(traceback.format_exc())
        else:
            self.history = yf.download(symbol,
                                       util.get_start(period),
                                       dt.datetime.now(),
                                       interval='1d')
            self.data['name']     = self.ticker.info['shortName']
            self.data['currency'] = self.ticker.info['currency']
            self.data['type']     = self.ticker.info['quoteType']
            self._set_mkt_data()


    def _set_mkt_data(self):
        ''' Makes date index a regular column & extracts Adjusted Close '''
        df_hist = self.history
        df_hist.reset_index(level=0, inplace = True)
        self.close  = df_hist[['Date', 'Adj Close']].copy(deep = True)
        self.close  = self.close.rename(columns = {'Adj Close':'Close_' + self.data['symbol']})
        self.volume = df_hist[['Date', 'Volume']].copy(deep = True)
        self.volume  = self.volume.rename(columns = {'Volume':'Vol_' + self.data['symbol']})


    def get_close(self):
        return self.close


    def get_currency(self):
        return self.data['currency']


    def get_volume(self):
        return self.volume


    def get_name(self):
        return self.data['name']


    def get_market_data(self):
        '''print volume for the given period'''
        clo = self.get_close()
        vol = self.get_volume()
        return pd.merge(clo, vol, on='Date', how='inner')


    def display_details(self):
        ''' print Security information'''
        for key,value in self.ticker.info.items():
            print("{}: {}".format(key,value))


    def display_close(self):
        '''print close for the given period'''
        print(self.close)


    def display_volume(self):
        '''print volume for the given period'''
        print(self.volume)


#### Test Driver ####
if __name__ == '__main__':
    TICKER   = 'SPIE.PA'
    PERIOD   = '5y'
    security = Security(TICKER, PERIOD)
    #security.display_details()
    security.display_close()
    # security.display_volume()
    security.describe()
    print(security.get_market_data())
