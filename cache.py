#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 17:22:03 2021

This class caches fundamental stock data (fmp data)
https://financialmodelingprep.com/developer/docs

@author: charles megnin
"""
import os
import glob
import datetime as dt
import pandas as pd
from path import Path


class Cache:
    '''Implementation of caching'''
    cache_dir   = './.cache/'
    date_format = '%Y-%m-%d'
    today = dt.datetime.today()

    def __init__(self, ticker:str, datatype:str, expiration=today, period=None, suffix='pkl'):
        self._ticker     = ticker
        self._datatype   = datatype
        self._expiration = expiration #datetime object
        self._suffix     = suffix
        self._period     = period
        self._path       = None
        self._build_cache_path()


    def set_expiration(self, expiration_str:str):
        '''re-sets cache expiration date from expiration as string'''
        self._expiration = dt.datetime.strptime(expiration_str, self.date_format)
        self._build_cache_path()


    def get_path(self):
        '''Return full path of cache file'''
        return self._path


    def _get_cache_expiration(self, path=None):
        '''Extract & return expiration date from cache filename as a string'''
        try:
            if path is None:
                path = self._path
            # the expiration date is the last element in the base filename
            return dt.datetime.strptime(Path(path).stem.split('_')[-1],
                                        self.date_format)
        except ValueError:
            print('*** Cannot extract date from filename ***')
            return -1


    def _build_cache_basename(self):
        '''Builds cache base filename of the form: ticker_datatype_expiration'''
        basename = f'{self._ticker}_{self._datatype}'
        expiration_string = self._expiration.strftime(self.date_format)

        if self._period == 'annual':
            basename = basename + '_a'
        elif self._period == 'quarter':
            basename = basename + '_q'
        elif self._period is None:
            pass
        else:
            msg = f"Period {self._period} should be 'annual' or 'quarter'"
            raise ValueError(msg)

        basename =  basename + f'_{expiration_string}'
        #print(f'{basename=} ')
        return basename


    def _build_cache_path(self):
        '''Builds full path from directory, base filename & suffix'''
        os.makedirs(self.cache_dir, exist_ok=True)
        basename = f'{self._build_cache_basename()}.{self._suffix}'
        #print(f'building cache path from {basename}')
        self._path = os.path.join(self.cache_dir, basename)
        #print(f'{self._path=}')


    def save_to_cache(self, dataframe):
        '''Stores dataframe locally as pickle file'''
        try:
            assert self._path is not None, 'Initialize path first'
            dataframe.to_pickle(self._path)
        except AssertionError as error:
            print(error)


    def load_cache(self):
        '''Determines if a current cached version exists & returns it if so'''
        date_pattern = '????-??-??'
        if self._period == 'annual':
            pattern = f'{self._ticker}_{self._datatype}_a_{date_pattern}.{self._suffix}'
        elif self._period == 'quarter':
            pattern = f'{self._ticker}_{self._datatype}_q_{date_pattern}.{self._suffix}'
        elif self._period is None:
            pattern = f'{self._ticker}_{self._datatype}_{date_pattern}.{self._suffix}'
        else:
            msg = 'self._period should be annual, quarter or None'
            raise ValueError(msg)
        pattern = os.path.join(self.cache_dir, pattern)
        matching_caches = glob.glob(pattern)
        #print(f'{matching_caches=}')
        for matching_cache in matching_caches:
            if self._get_cache_expiration(matching_cache) > dt.datetime.now(): # return if expiration date is later
                dataframe = pd.read_pickle(matching_cache)
                return dataframe
        return None
