#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  7 13:07:11 2021

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
        else:
            msg  = f'Holdings.add_security: {position} not in {dft.POSITIONS} '
            msg += f'or {strategy} not in {dft.STRATEGIES} '
            msg += f'***{symbol} not added***'
            print(msg)


    def get_securities(self):
        '''
        Returns the dictionary of securities & their positions
        '''
        return self._securities


    def _load_securities(self):
        '''
        Load securities from csv file
        expected format: ticker symbol; position
        eg: ARKK;long
        '''
        filepath = os.path.join(self._directory, self._filename)
        try:
            self._securities = pd.read_csv(filepath)
            self._securities = pd.DataFrame.drop_duplicates(self._securities)
            print(f'_load_securities: {len(self._securities)} securities loaded')
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


    def get_position(self, symbol:str, strategy:str):
        '''Returns the position of a given ticker symbol/strategy pair'''
        try:
            sec = self._securities
            return sec[(sec.Ticker == symbol) & (sec.Strategy==strategy)].iloc[0].Position
        except:
            print(f'***Ticker/strategy pair {symbol}/{strategy} not in Holdings***')
            return None


    def get_strategy(self, symbol:str):
        '''
        Returns the strategy(ies) for a given ticker symbol
        '''
        try:
            return self._securities[self._securities.Ticker == symbol].Strategy
        except:
            print(f'***Ticker {symbol} not in Holdings***')
            return None


    def is_in_sync(self, symbol:str, recommended_position:str, strategy:str):
        '''
        Determines if a particular ticker position
        is in sync with a recommendation / strategy pair
        '''
        sec = self._securities
        if (symbol in sec.Ticker) and (strategy in sec.Strategy):
            target = sec[(sec.Ticker == symbol) & (sec.Strategy == strategy)].iloc[0].Position
            if target == recommended_position:
                return True
            return False
        else:
            print(f'***Ticker/strategy pair {symbol}/{strategy} not in Holdings***')
            return False
