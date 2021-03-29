#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 11:18:04 2021

@author: charles mégnin
"""
import os
import pandas as pd
import numpy as np
import trading as tra
import trading_defaults as dft

class Strategy():
    '''
    The Strategy class encapsulates raw prices, ema prices and all the meta info
    associated to the strategy
    '''
    def __init__(self, ticker_symbol, ticker_name, date_range):
        self.ticker      = ticker_symbol
        self.ticker_name = ticker_name
        self.date_range  = date_range # in datetime format
        self.__close      = None  # raw data from Yahoo finance
        self.__spans      = None # range of rolling window spans
        self.__buffers    = None # range of buffer dimensions
        self.__emas       = None # map of returns on ema strategy
        self.__opt_emas   = None # map of optimal returns on ema strategy
        self.__hold       = None # returns on hold srategy
        self.__ema_pathname = None  # ema map file path
        self.__map_exists   = False # ema map created
        self.__map_saved    = False # ema map saved to file


    def set_market_data(self, close_df):
        '''
        Store raw market data as __close dataframe (from Security class)
        '''
        self.__close  = close_df.copy(deep = True)


    def get_market_data(self):
        '''
        Returns close
        '''
        return self.__close


    def set_map(self, spans, buffers, emas, hold):
        '''
        spans & buffers are 1D numpy arrays emas is n_spans x nbuffers 2d numpy array
        emas is the matrix of returns for all span/buffer combination
        '''
        self.__spans   = spans.copy()
        self.__buffers = buffers.copy()
        self.__emas    = emas.copy()
        self.__hold    = hold.copy()
        self.__map_exists = True


    def set_opt_emas(self, n_opt):
        '''
        Builds a dataframe of n_opt optimal emas consisting of:
        span buffer ema hold
        '''
        if self.__map_exists:
            results = np.zeros(shape=(n_opt, 4))
            # Build a n_opt x 4 dataframe
            emas_temp = self.__emas.copy() # b/c algorithm destroys top n_maxima EMA valuesemas.copy() # b/c algorithm destroys top n_maxima EMA values

            for i in range(n_opt):
                # Get coordinates of maximum emas value
                max_idx = np.unravel_index(np.argmax(emas_temp, axis=None),
                                           emas_temp.shape)
                results[i][0] = self.__spans[max_idx[0]]
                results[i][1] = self.__buffers[max_idx[1]]
                results[i][2] = np.max(emas_temp)
                results[i][3] = self.__hold

                # set max emas value to arbitrily small number and re-iterate
                emas_temp[max_idx[0]][max_idx[1]] = - dft.HUGE

            # Convert numpy array to dataframe
            self.__opt_emas = pd.DataFrame(results,
                                           columns=['span', 'buffer', 'ema', 'hold']
                                           )
        else:
            msg = 'No ema map built - set_map must be called prior to set_opt_emas'
            raise AssertionError(msg)


    def get_opt_emas(self):
        return self.__opt_emas


    def save_map(self, data_dir=dft.DATA_DIR, extension='csv'):
        '''
        Save EMA map to file
        '''
        if self.__map_exists:
            ema_df = self.__build_ema_dataframe()
            self.__set_ema_pathname(data_dir, extension)
            self.__save_dataframe(ema_df, self.__ema_pathname, extension)
            self.__map_saved = True
        else:
            msg = 'No ema map built - set_map must be called prior to save_map'
            raise AssertionError(msg)

    def __build_ema_dataframe(self):
        '''
        Build a dataframe concisting of spans, buffers, emas, & hold.
        Hold value is repeated throughout in last column
        *** TODO: Vectorize this method ***
        '''
        ema_df = []
        for i, span in enumerate(self.__spans):
            for j, buffer in enumerate(self.__buffers):
                ema_df.append([span, buffer, self.__emas[i,j], self.__hold])
        ema_df = pd.DataFrame(ema_df, columns=['span', 'buffer', 'ema', 'hold'])
        return ema_df

    def __set_ema_pathname(self, data_dir, extension):
        '''
        Build EMA map filename
        '''
        dates    = tra.dates_to_strings(self.date_range, '%Y-%m-%d')
        suffix   = f'{dates[0]}_{dates[1]}_ema_map'
        filename = f'{self.ticker}_{suffix}'
        self.__ema_pathname = os.path.join(data_dir, filename + f'.{extension}')

    def load_map(self):
        '''
        Load EMA map from file and split it as:
        - a 2D numpy array __emas
        - 1D numpy arrays __spans and __buffers
        - __hold
        '''
        if self.__map_saved:
            ema_map = pd.read_csv(self.__ema_pathname, sep=';', index_col=0)

            spans   = ema_map['span'].to_numpy()
            buffers = ema_map['buffer'].to_numpy()
            emas    = ema_map['ema'].to_numpy()
            self.__hold = ema_map['hold'].to_numpy()

            # reshape the arrays
            self.__spans   = np.unique(spans)
            self.__buffers = np.unique(buffers)
            self.__emas    = np.reshape(emas, (spans.shape[0], buffers.shape[0]))
            self.__map_exists = True
        else:
            msg = 'No ema map saved - save_map() must be called prior to load_map()'
            raise AssertionError(msg)

    @staticmethod
    def __save_dataframe(dataframe, pathname, extension):
        '''
        Save dataframe to either csv or pkl file
        '''
        if extension == 'pkl':
            dataframe.to_pickle(pathname)
        elif extension == 'csv':
            dataframe.to_csv(pathname, sep=';')
        else:
            raise ValueError(f'{extension} should be "pkl" or "csv"')
