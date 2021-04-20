#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 17:34:49 2021

The Asset object encapsulates a Security + quantity held

@author: charles mégnin
"""
import equity as eq

class Asset(eq.Equity):
    ''' Class for assets in a portfolio
        Assets consist of
        - a Security object
        - the quantity held
        - convenience shortcuts to the underlying Security
        '''

    def __init__(self, sec, quant):
        '''sec is Security object, quant is number of assets held'''
        super().__init__()
        self.data['currency'] = sec.data['currency']
        self.data['name']     = sec.data['name']
        self.data['symbol']   = sec.data['symbol']
        self.data['type']     = sec.data['type']
        self.data['period']   = sec.data['period']
        self.data['quantity'] = quant
        self.close            = sec.close
        self._set_value() # compute value of asset


    def _set_value(self):
        ''' set the value of the asset held'''
        self.data['price'] = self.close.iloc[-1,1]
        self.data['value'] = self.data['quantity'] * self.data['price']


    def get_value(self):
        ''' return asset value = price * quantity'''
        return self.data['value']
