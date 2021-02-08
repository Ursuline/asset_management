#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 20:50:46 2021

Security object encapsulates yfinance download and provides
convenience shortcuts
https://pypi.org/project/yfinance/
https://github.com/ranaroussi/yfinance
https://aroussi.com/post/python-yahoo-finance

valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max

@author: charles mégnin
"""
import datetime as dt
from dateutil.relativedelta import relativedelta
import yfinance as yf
import equity as eq

def get_start(period):
    if period == 'max':
        td = relativedelta(years=20)
    elif period[-1] == 'y':
        td = relativedelta(years=int(period[:-1]))
    elif period[-1] == 'd':
        td = dt.timedelta(days=int(period[:-1]))
    elif period[-1] == 'o' and period[-2] == 'm':
        td = relativedelta(months=int(period[:-2]))
    else:
        raise ValueError(f'invalid period {period}')

    # if period == '1d':
    #     td = dt.timedelta(days=1)
    # elif period == '5d':
    #     td = dt.timedelta(days=5)
    # elif period == '1mo':
    #     td = dt.timedelta(months=1)
    # elif period == '3mo':
    #     td = dt.timedelta(months=3)
    # elif period == '6mo':
    #     td = dt.timedelta(months=6)
    # elif period == '1y':
    #     td = relativedelta(years=1)
    # elif period == '2y':
    #     td = relativedelta(years=2)
    # elif period == '3y':
    #     td = relativedelta(years=3)
    # elif period == '5y':
    #     td = relativedelta(years=5)
    # elif period == '10y':
    #     td = relativedelta(years=10)
    # elif period == 'max':
    #     td = relativedelta(years=20)
    # else:
    #     raise ValueError(f"period {period} to be coded")

    return dt.datetime.now() - td



class Security(eq.Equity):
    ''' A Security is an object resulting from Yahoo finance download using yfinance
        - Provides simplified access to several variables
    '''

    def __init__(self, symbol, period):
        print(f'Loading ticker {symbol}')
        super().__init__()
        self.data['symbol'] = symbol
        self.data['period'] = period
        try:
            self.ticker   = yf.Ticker(self.data['symbol'])
        except:
            print(f"Couldn't load {symbol}")
        else:
            self.history          = yf.download(symbol, get_start(period), dt.datetime.now(), interval='1d')
            self.data['name']     = self.ticker.info['shortName']
            self.data['currency'] = self.ticker.info['currency']
            self.data['type']     = self.ticker.info['quoteType']
            self.dividends        = self.ticker.dividends
            self.splits           = self.ticker.splits
            #self._get_close()
            self._get_adj_close()


    # def _get_close(self):
    #     ''' Makes date index a regular column & extracts  Close '''
    #     df_hist = self.ticker.history(self.data['period'])
    #     df_hist.reset_index(level=0, inplace = True)
    #     self.close = df_hist[['Date', 'Close']].copy(deep = True)
    #     self.close = self.close.rename(columns = {'Close':'Close_' + self.data['symbol']})


    def _get_adj_close(self):
        ''' Makes date index a regular column & extracts Adjusted Close '''

        df_hist = self.history
        df_hist.reset_index(level=0, inplace = True)
        self.close = df_hist[['Date', 'Adj Close']].copy(deep = True)
        self.close = self.close.rename(columns = {'Adj Close':'Close_' + self.data['symbol']})


    def display_details(self):
        ''' print Security information'''
        for key,value in self.ticker.info.items():
            print("{}: {}".format(key,value))


    def display_close(self):
        '''print history for the given period'''
        print(self.close)


#### Test Driver ####
if __name__ == '__main__':
    TICKER   = 'MSFT'
    PERIOD   = '6mo'
    security = Security(TICKER, PERIOD)
    security.display_details()
    security.display_close()
    # security.describe()
