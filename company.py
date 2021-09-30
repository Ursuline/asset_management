#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 20 18:22:19 2021

@author: charles mégnin
"""
import datetime as dt
import numpy as np
import FundamentalAnalysis as fa
import cache as ksh
import api_keys as keys

API_KEY = keys.FMP

class Company:
    '''
    Encapsulates  stock+fundamental data for a given company.
    Performs base operations
    '''
    data = ['profile', 'quote', 'enterprise', 'rating', 'discounted_cash_flow', 'cash_flow_statement',
            'income_statement', 'balance_sheet_statement', 'key_metrics', 'financial_ratios',
            'financial_statement_growth', 'stock_data', 'stock_data_detailed'
            ]

    funcs = {data[0]:fa.profile,
             data[1]:fa.quote,
             data[2]:fa.enterprise,
             data[3]:fa.rating,
             data[4]:fa.discounted_cash_flow,
             data[5]:fa.cash_flow_statement,
             data[6]:fa.income_statement,
             data[7]:fa.balance_sheet_statement,
             data[8]:fa.key_metrics,
             data[9]:fa.financial_ratios,
             data[10]:fa.financial_statement_growth,
             data[11]:fa.stock_data,
             data[12]:fa.stock_data_detailed
            }
    start_date_default = '2000-01-02'
    end_date_default   = dt.datetime.today()
    date_format = '%Y-%m-%d'


    def __init__(self, ticker:str, period:str, expiration_date, start_date=start_date_default, end_date=end_date_default):
        self._ticker  = ticker
        self._period = period
        self._profile = None
        self._quote  = None
        self._enterprise = None
        self._rating = None
        self._discounted_cash_flow = None
        self._cash_flow_statement = None
        self._income_statement = None
        self._balance_sheet_statement = None
        self._key_metrics = None
        self._financial_ratios = None
        self._financial_statement_growth = None
        self._stock_data = None
        self._stock_data_detailed = None

        self._self_check(expiration_date, start_date, end_date)
        self._load_data(expiration_date=expiration_date, start_date=start_date, end_date=end_date)


    def _self_check(self, expiration_date, start_date, end_date):
        '''Consistency checks for the Company class'''
        assert self._period in ['annual', 'quarter'], "period must be 'annual' or 'quarter'"
        # Assert end_date > start_date
        start_object = dt.datetime.strptime(start_date, self.date_format)
        end_object = dt.datetime.strptime(end_date, self.date_format)
        assert start_object < end_object, 'start date must be prior to end date'
        # Assert expiration_date >= now
        date_object = dt.datetime.strptime(expiration_date, self.date_format)
        assert date_object >= dt.datetime.today(), 'expiration must be today or later'


    def _process_data(self, fcn_idx:int, expiration_date, start_date, end_date):
        func = self.data[fcn_idx]
        cache = ksh.Cache(ticker=self._ticker, datatype=func, period=self._period)
        temp = cache.load_cache()
        if temp is None: # No data cached
            if fcn_idx < 4:
                temp = self.funcs[func](self._ticker, API_KEY)
            elif fcn_idx < 11:
                temp = self.funcs[func](self._ticker, API_KEY)
            elif fcn_idx == 11:
                temp = self.funcs[func](self._ticker)
            elif fcn_idx == 12:
                temp = self.funcs[func](self._ticker, API_KEY, begin=start_date, end=end_date)
            else:
                msg = f'_processs_data: {fcn_idx=} out of range 0-12'
                raise ValueError(msg)
            cache.set_expiration(expiration_date)
            cache.save_to_cache(temp)
        return temp


    def _load_data(self, expiration_date, start_date, end_date):
        '''Dowload the data or load from file '''
        self._profile    = self._process_data(0, expiration_date, None, None)
        self._quote      = self._process_data(1, expiration_date, None, None)
        self._enterprise = self._process_data(2, expiration_date, None, None)
        self._rating     = self._process_data(3, expiration_date, None, None)
        self._discounted_cash_flow = self._process_data(4, expiration_date, None, None)
        self._cash_flow_statement  = self._process_data(5, expiration_date, None, None)
        self._income_statement     = self._process_data(6, expiration_date, None, None)
        self._balance_sheet_statement    = self._process_data(7, expiration_date, None, None)
        self._key_metrics                = self._process_data(8, expiration_date, None, None)
        self._financial_ratios           = self._process_data(9, expiration_date, None, None)
        self._financial_statement_growth = self._process_data(10, expiration_date, None, None)
        self._stock_data                 = self._process_data(11, expiration_date, start_date=None, end_date=None)
        self._stock_data_detailed        = self._process_data(12, expiration_date, start_date=start_date, end_date=end_date)


    def get_ticker(self):
        '''return company ticker symbol'''
        return self._ticker


    def get_profile(self):
        '''return profile dataframe'''
        return self._profile


    def get_quote(self):
        '''return quote dataframe'''
        return self._quote


    def get_enterprise(self):
        '''return entreprise dataframe'''
        return self._enterprise


    def get_rating(self):
        '''return rating dataframe'''
        return self._rating


    def get_discounted_cash_flow(self):
        '''return dcf dataframe'''
        return self._discounted_cash_flow


    def get_cash_flow_statement(self):
        '''return cash flow statement dataframe'''
        return self._cash_flow_statement


    def get_income_statement(self):
        '''return income statement dataframe'''
        return self._income_statement


    def get_balance_sheet_statement(self):
        '''return BS statement dataframe'''
        return self._balance_sheet_statement


    def get_key_metrics(self):
        '''return key metrics dataframe'''
        return self._key_metrics


    def get_financial_ratios(self):
        '''return financial ratios dataframe'''
        return self._financial_ratios


    def get_financial_statement_growth(self):
        '''return financial statement growth dataframe'''
        return self._financial_statement_growth


    def get_stock_data(self):
        '''return stock data dataframe'''
        return self._stock_data


    def get_stock_data_detailed(self):
        '''return detailed stock data dataframe'''
        return self._stock_data_detailed


    def get_dcf(self, year:str):
        '''Returns date, stock price, dcf and % dcf over price'''
        try:
            data = self.get_discounted_cash_flow().loc[:, year]
        except KeyError:
            print(f'get_dcf_delta: year {year} data unvailable')
            return 0
        else :
            date = data.loc['date']
            price = data.loc['Stock Price']
            dcf = data.loc['DCF']
            delta_pct = (dcf-price)/price
            return date, price, dcf, delta_pct


    # def get_fcf(self, year:str):
    #     '''Returns free cash flow'''
    #     try:
    #         data = self.get_cash_flow_statement().loc[:, year]
    #     except KeyError:
    #         print(f'get_fcf: year {year} data unvailable')
    #         return 0
    #     else :
    #         return data.loc['freeCashFlow']


    ### Profile data
    def get_profile_item(self, item):
        '''Returns company profile data'''
        try:
            data = self.get_profile()
        except KeyError:
            print(f'get_profile_item: {item} profile data unvailable')
            return ''
        else :
            return data.loc[item].iloc[0]


    def get_currency_symbol(self):
        '''Returns symbol corresponding to currency'''
        currency = self.get_profile_item('currency')
        if currency == 'USD':
            return '$'
        return currency


    ### Balance sheet statement data
    def get_balance_sheet_item(self, item:str, year:str, change:bool=False):
        '''
        Returns generic balance sheet item or its time change
        '''
        try:
            data = self.get_balance_sheet_statement().loc[item]
            if change:
                data = data[::-1].pct_change()
        except KeyError:
            msg=f'get_balance_sheet_item: item {item} or year {year} data unvailable'
            print(msg)
            return 0
        else :
            return data.loc[year]


    def get_leverage(self, year:str, change:bool=False):
        '''Returns leverage (assets / equity)'''
        try:
            assets = self.get_balance_sheet_item('totalAssets', year, change)
            equity = self.get_balance_sheet_item('totalStockholdersEquity', year, change)
        except KeyError:
            print(f'get_leverage: year {year} data unvailable')
            return 0
        else :
            if equity == 0:
                return 0
            return assets/equity


    ### Income statement data ###
    def get_income_statement_item(self, item:str, year:str, change:bool=False):
        '''
        Returns generic income statement item or its time change
        '''
        try:
            data = self.get_income_statement().loc[item]
            if change:
                data = data[::-1].pct_change()
        except KeyError:
            msg=f'get_income_statement_item: item {item} or year {year} data unvailable'
            print(msg)
            return 0
        else :
            return data.loc[year]


    def get_ebit(self, year:str, change:bool=False):
        '''Returns EBIT = ebitda - depreciation & amortization'''
        try:
            ebit  = self.get_income_statement_item('ebitda', year, change)
            depam = self.get_income_statement_item('depreciationAndAmortization', year, change)
        except KeyError:
            print(f'get_ebit: year {year} data unvailable')
            return 0
        else :
            return ebit - depam


    ### Cash flow statement data ###
    def get_cash_flow_statement_item(self, item:str, year:str, change:bool=False):
        '''
        Returns generic cash flow statement item or its time change
        '''
        try:
            data = self.get_cash_flow_statement().loc[item]
            if change:
                data = data[::-1].pct_change()
        except KeyError:
            msg=f'get_cash_flow_statement_item: item {item} or year {year} data unvailable'
            print(msg)
            return 0
        else :
            return data.loc[year]


    ###Financial ratio data ###
    def get_financial_ratios_item(self, item:str, year:str, change:bool=False):
        '''
        Returns generic financial ratios item or its time change
        '''
        try:
            data = self.get_financial_ratios().loc[item]
            if change:
                data = data[::-1].pct_change()
        except KeyError:
            msg=f'get_key_metrics_item: item {item} or year {year} data unvailable'
            print(msg)
            return 0
        else :
            query = data.loc[year]
            if query is None:
                print(f'item {item} is None in the data set')
                return 0
            return query


    ### key metrics data ###
    def get_key_metrics_item(self, item:str, year:str, change:bool=False):
        '''
        Returns generic key metrics item or its time change
        '''
        try:
            data = self.get_key_metrics().loc[item]
            if change:
                data = data[::-1].pct_change()
        except KeyError:
            msg=f'get_key_metrics_item: item {item} or year {year} data unvailable'
            print(msg)
            return 0
        else :
            return data.loc[year]
