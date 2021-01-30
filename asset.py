#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 17:34:49 2021

List of securities downloaded from:
ftp://ftp.nasdaqtrader.com/symboldirectory

@author: charly
"""

class Asset():
    ''' Class for assets in a portfolio
        Assets consist of
        - a Security object
        - the quantity held
        - convenience shortcuts to the underlying Security
        '''
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-arguments

    def __init__(self, sec, quant):
        '''sec is Security object, quant is number of assets held'''
        self.security   = sec
        self.currency   = self.security.currency
        self.close      = self.security.close
        self.name       = self.security.name
        self.symbol     = self.security.symbol
        self.type       = self.security.type
        self.period     = self.security.period
        self.quantity   = quant
        self._set_value() # compute value of asset


    def describe(self):
        '''class descriptor'''
        print(f'{self.name} ({self.symbol}) {self.type}')
        print(f'Quantity held: {self.quantity}')
        print(f'Price: {self.price:.2f} {self.currency}')
        print(f'Asset value: {self.value:.2f} {self.currency}')


    def _set_value(self):
        '''set the value of the asset held'''
        self.price = self.security.close.iloc[-1,1]
        self.value = self.quantity * self.price


    def get_value(self):
        '''return asset value = price * quantity'''
        return self.value
