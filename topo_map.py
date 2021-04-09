#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 17:13:37 2021

@author: charles mégnin
"""
import numpy as np
import pandas as pd

import trading_defaults as dft

class Topomap():
    ''' A Topomap encapsulates :
        span, buffer, EMA, hold
    '''
    def __init__(self, ticker_name, span, buffer, ema, hold):
        self._name      = ticker_name
        self._spans     = span
        self._buffers   = buffer
        self._emas      = ema
        self._hold      = hold
        self._best_emas = None

    def get_name(self):
        '''Return ticker identifier that corresponds to EMA map (ticker symbol)'''
        return self._name

    def get_spans(self):
        '''Return spans'''
        return self._spans

    def get_buffers(self):
        '''Return buffers'''
        return self._buffers

    def get_emas(self):
        '''Return EMAs'''
        return self._emas

    def get_hold(self):
        '''Return hold'''
        return self._hold

    def self_describe(self):
        '''Display all variables in class'''
        print(self.__dict__)

    def get_best_emas(self, n_best):
        '''Return best emas '''
        self._build_best_emas(n_best)
        return self._best_emas

    def _build_best_emas(self, n_best):
        '''computes best emas'''
        results = np.zeros(shape=(n_best, 4))

        # Build a n_best x 4 dataframe
        # copy b/c algorithm destroys top n_maxima EMA values
        _emas = self.get_emas().copy()

        for i in range(n_best):
            # Get coordinates of maximum emas value
            max_idx = np.unravel_index(np.argmax(_emas, axis=None),
                                       _emas.shape)
            results[i][0] = self.get_spans()[max_idx[0]]
            results[i][1] = self.get_buffers()[max_idx[1]]
            results[i][2] = np.max(_emas)
            results[i][3] = self.get_hold()

            # set max emas value to arbitrily small number and re-iterate
            _emas[max_idx[0]][max_idx[1]] = - dft.HUGE

        # Convert numpy array to dataframe
        self._best_emas = pd.DataFrame(results,
                                       columns=['span', 'buffer', 'ema', 'hold']
                                       )
