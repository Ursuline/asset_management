#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 7 13:07:11 2021

Holdings are a collection of securities to which a position
is associated. That position can be 'long, 'short' or 'cash'

@author: charles mégnin
"""
import os
import pandas as pd
from charting import trading_defaults as dft

class Holdings():
    '''
    A Holdings object consists of a set of securities with:
    - ticker symbol
    - ticker position (short, long, cash) in dft.POSITIONS
    - strategic position (long, short) in dft.STRATEGIES
    '''
    def __init__(self, directory:str, filename:str):
        self._directory  = directory
        self._filename   = filename
        self._securities = None
        self._load_securities()


    def add_security(self, symbol:str, position:str, strategy:str):
        '''
        Adds a security position for a given strategy
        '''
        if (position in dft.POSITIONS) and (strategy in dft.STRATEGIES):
            sec = self._securities
            print(f'initial df:\n{sec}')
            row = {'Ticker'  : symbol,
                   'Position': position,
                   'Strategy': strategy}
            self._securities = self._securities.append(row,
                                                       ignore_index = True,
                                                       )
            # remove duplicates keeping last entry
            self._securities.drop_duplicates(subset='Ticker', keep='last', inplace=True)
        else:
            msg  = f'Holdings.add_security: {position} not in {dft.POSITIONS} '
            msg += f'or {strategy} not in {dft.STRATEGIES} '
            msg += f'***{symbol} not added***'
            print(msg)


    def get_securities(self):
        '''
        Returns a dataframe of securities & their positions
        '''
        return self._securities


    def _load_securities(self):
        '''
        Load securities from csv file
        expected format: ticker symbol; position
        eg: ARKK;long
        '''
        def strip_all_columns(df):
            """
            Trim beg/end whitespace of each value across all series in dataframe
            """
            trim_strings = lambda x: x.strip() if isinstance(x, str) else x
            return df.applymap(trim_strings)

        filepath = os.path.join(self._directory, self._filename)
        try:
            securities = pd.read_csv(filepath)
            n_assets = len(securities)
            # remove duplicates keeping first entry
            securities.drop_duplicates(subset='Ticker', keep='first', inplace=True)
            n_deletes = n_assets - len(securities)
            self._securities = strip_all_columns(securities)
            if n_deletes != 0:
                print(f'*** WARNING: removed {n_deletes} position(s)')
            msg  = f'{len(securities)} securities '
            msg += f'in portfolio {self._filename}'
            print(msg)
            print(self._securities)
        except:
            raise IOError(f'Could not load {filepath}')


    def save_securities(self, directory=None, filename=None):
        '''
        Save _securities to csv file
        '''
        if (directory is None) and (filename is None):
            filepath = os.path.join(self._directory, self._filename)
            os.makedirs(self._directory, exist_ok = True)
        else:
            filepath = os.path.join(directory, filename)
            os.makedirs(directory, exist_ok = True)
        try:
            self._securities.to_csv(filepath, index = False)
        except IOError:
            print(f'***Could not save securities to {filepath}***')


    def get_current_position(self, symbol:str, strategy:str):
        '''Returns the position of a given ticker symbol/strategy pair'''
        try:
            sec = self._securities
            pos = sec[(sec.Ticker==symbol) & (sec.Strategy==strategy)].iloc[0].Position.strip()
            return pos
        except:
            print(f'***Ticker/strategy pair {symbol}/{strategy} not in Holdings***')
            return None


    def get_strategy(self, symbol:str):
        '''
        Returns the strategy for a given ticker symbol
        '''
        try:
            return self._securities[self._securities.Ticker == symbol].Strategy.iloc[0]
        except:
            print(f'***Ticker {symbol} not in Holdings***')
            return None
