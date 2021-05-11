#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  7 20:05:36 2021

The Equity object contains elements and functionality common to
Security, Asset and Portfolio objects

@author: charles mégnin
"""

class Equity():
    ''' Extended by Security, Asset and Portfolio objects'''
    def __init__(self):
        # initialize the data dictionary
        self.data = {}


    def describe(self):
        ''' Self-descriptor '''
        print('Data:')
        for key, value in self.data.items():
            print(f'{key}: {value}')
