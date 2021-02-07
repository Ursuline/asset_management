#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 20:50:46 2021

Security object encapsulates yfinance download and provides
convenience shortcuts

valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max

@author: charles mégnin
"""
import yfinance as yf

### Helper utilities ###
def annualized_return(rate, ndays):
    ''' Returns annnualized daily return '''
    return ndays * (pow(1. + rate/ndays, ndays) - 1.)


def relative_change(df_column):
    ''' computes relative change bw one column value & the next. First value is NaN'''
    return (df_column - df_column.shift(1))/df_column.shift(1)


def absolute_change(df_column):
    ''' computes difference bw one column value & the next. First value is NaN'''
    return df_column - df_column.shift(1)


class Security():
    ''' A Security is an object resulting from Yahoo finance download using yfinance
        - Provides simplified access to several variables
    '''

    def __init__(self, symbol, period):
        print(f'Loading ticker {symbol}')
        self.data = {}
        self.data['symbol'] = symbol
        self.data['period'] = period
        #self.symbol   = symbol
        #self.period   = period
        try:
            self.ticker   = yf.Ticker(self.data['symbol'])
        except:
            print(f"Couldn't load {symbol}")
        else:
            # self.name     = self.ticker.info['shortName']
            # self.currency = self.ticker.info['currency']
            # self.type     = self.ticker.info['quoteType']
            self.data['name']     = self.ticker.info['shortName']
            self.data['currency'] = self.ticker.info['currency']
            self.data['type']     = self.ticker.info['quoteType']

            self._extract_history()


    def _extract_history(self):
        ''' Makes date index a regular column & extracts Close '''
        df_hist = self.ticker.history(self.data['period'])
        df_hist.reset_index(level=0, inplace = True)
        self.close = df_hist[['Date', 'Close']].copy(deep = True)
        self.close = self.close.rename(columns = {'Close':'Close_' + self.data['symbol']})


    def describe(self):
        ''' Short Security description '''
        print(f'{self.data["name"]} '
              f'({self.data["symbol"]}) '
              f'{self.data["currency"]} '
              f'{self.data["type"]}')


    def display_details(self):
        ''' print Security information'''
        for key,value in self.ticker.info.items():
            print("{}: {}".format(key,value))


    def display_close(self):
        '''print history for the given period'''
        print(self.close)


#### Driver ####
if __name__ == '__main__':
    TICKER = 'SPIE.PA'
    PERIOD = 'max'
    security = Security(TICKER, PERIOD)
    security.display_details()
    security.describe()
    security.display_close()
