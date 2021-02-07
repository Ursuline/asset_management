#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 17:34:49 2021

@author: charles mégnin
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
        self.data             = {}
        self.security         = sec
        self.data['currency'] = self.security.data['currency']
        self.data['close']    = self.security.close
        self.data['name']     = self.security.data['name']
        self.data['symbol']   = self.security.data['symbol']
        self.data['type']     = self.security.data['type']
        self.data['period']   = self.security.data['period']
        self.data['quantity'] = quant
        self._set_value() # compute value of asset


    def describe(self):
        ''' class descriptor '''
        print(f'{self.data["name"]} '
              f'({self.data["symbol"]}) '
              f'{self.data["type"]}')
        print(f'Quantity held: {self.data["quantity"]}')
        print(f'Price: {self.data["price"]:.2f} {self.data["currency"]}')
        print(f'Asset value: {self.data["value"]:.2f} {self.data["currency"]}')


    def _set_value(self):
        ''' set the value of the asset held'''
        self.data['price'] = self.security.close.iloc[-1,1]
        self.data['value'] = self.data['quantity'] * self.data['price']


    def get_value(self):
        ''' return asset value = price * quantity'''
        return self.data['value']
