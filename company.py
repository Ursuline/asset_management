#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 20 18:22:19 2021

@author: charles mégnin
"""
import datetime as dt
import FundamentalAnalysis as fa
import cache as ksh
import api_keys as keys

API_KEY = keys.FMP

class Company:
    '''Encapsulates all stock data for a give company. Performs base operations'''
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


    def get_ticker(self):
        '''return ticker name'''
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


    def _load_data(self, expiration_date, start_date, end_date):
        '''Dowload the data or load from file '''

        func = self.data[0]
        cache = ksh.Cache(ticker=self._ticker, datatype=func)
        self._profile = cache.load_cache()
        if self._profile is None: # No data cached
            self._profile = self.funcs[func](self._ticker, API_KEY)
            cache.set_expiration(expiration_date)
            cache.save_to_cache(self._profile)

        func = self.data[1]
        cache = ksh.Cache(ticker=self._ticker, datatype=func)
        self._quote = cache.load_cache()
        if self._quote is None: # No data cached
            self._quote = self.funcs[func](self._ticker, API_KEY)
            cache.set_expiration(expiration_date)
            cache.save_to_cache(self._quote)

        func = self.data[2]
        cache = ksh.Cache(ticker=self._ticker, datatype=func)
        self._enterprise = cache.load_cache()
        if self._enterprise is None: # No data cached
            self._enterprise = self.funcs[func](self._ticker, API_KEY)
            cache.set_expiration(expiration_date)
            cache.save_to_cache(self._enterprise)

        func = self.data[3]
        cache = ksh.Cache(ticker=self._ticker, datatype=func)
        self._rating = cache.load_cache()
        if self._rating is None: # No data cached
            self._rating = self.funcs[func](self._ticker, API_KEY)
            cache.set_expiration(expiration_date)
            cache.save_to_cache(self._rating)

        func = self.data[4]
        cache = ksh.Cache(ticker=self._ticker, datatype=func, period=self._period)
        self._discounted_cash_flow = cache.load_cache()
        if self._discounted_cash_flow is None: # No data cached
            self._discounted_cash_flow = self.funcs[func](self._ticker, API_KEY, period=self._period)
            cache.set_expiration(expiration_date)
            cache.save_to_cache(self._discounted_cash_flow)

        func = self.data[5]
        cache = ksh.Cache(ticker=self._ticker, datatype=func, period=self._period)
        self._cash_flow_statement = cache.load_cache()
        if self._cash_flow_statement is None: # No data cached
            self._cash_flow_statement = self.funcs[func](self._ticker, API_KEY, period=self._period)
            cache.set_expiration(expiration_date)
            cache.save_to_cache(self._cash_flow_statement)

        func = self.data[6]
        cache = ksh.Cache(ticker=self._ticker, datatype=func, period=self._period)
        self._income_statement = cache.load_cache()
        if self._income_statement is None: # No data cached
            self._income_statement = self.funcs[func](self._ticker, API_KEY, period=self._period)
            cache.set_expiration(expiration_date)
            cache.save_to_cache(self._income_statement)

        func = self.data[7]
        cache = ksh.Cache(ticker=self._ticker, datatype=func, period=self._period)
        self._balance_sheet_statement = cache.load_cache()
        if self._balance_sheet_statement is None: # No data cached
            self._balance_sheet_statement = self.funcs[func](self._ticker, API_KEY, period=self._period)
            cache.set_expiration(expiration_date)
            cache.save_to_cache(self._balance_sheet_statement)

        func = self.data[8]
        cache = ksh.Cache(ticker=self._ticker, datatype=func, period=self._period)
        self._key_metrics = cache.load_cache()
        if self._key_metrics is None: # No data cached
            self._key_metrics = self.funcs[func](self._ticker, API_KEY, period=self._period)
            cache.set_expiration(expiration_date)
            cache.save_to_cache(self._key_metrics)

        func = self.data[9]
        cache = ksh.Cache(ticker=self._ticker, datatype=func, period=self._period)
        self._financial_ratios = cache.load_cache()
        if self._financial_ratios is None: # No data cached
            self._financial_ratios = self.funcs[func](self._ticker, API_KEY, period=self._period)
            cache.set_expiration(expiration_date)
            cache.save_to_cache(self._financial_ratios)

        func = self.data[10]
        cache = ksh.Cache(ticker=self._ticker, datatype=func, period=self._period)
        self._financial_statement_growth = cache.load_cache()
        if self._financial_statement_growth is None: # No data cached
            self._financial_statement_growth = self.funcs[func](self._ticker, API_KEY, period=self._period)
            cache.set_expiration(expiration_date)
            cache.save_to_cache(self._financial_statement_growth)

        func = self.data[11]
        cache = ksh.Cache(ticker=self._ticker, datatype=func, period=None)
        self._stock_data = cache.load_cache()
        if self._stock_data is None: # No data cached
            self._stock_data = self.funcs[func](self._ticker, API_KEY)
            cache.set_expiration(expiration_date)
            cache.save_to_cache(self._stock_data)

        func = self.data[12]
        cache = ksh.Cache(ticker=self._ticker, datatype=func, period=None)
        self._stock_data_detailed = cache.load_cache()
        if self._stock_data_detailed is None: # No data cached
            self._stock_data_detailed = self.funcs[func](self._ticker, API_KEY, begin=start_date, end=end_date)
            cache.set_expiration(expiration_date)
            cache.save_to_cache(self._stock_data_detailed)


    # def _load_data_new(self, start_date, end_date, expiration_date):
    #     #varbs[func] Non-functional - switch to this when resolved

    #     varbs = {self.data[0]: f'self._{self.data[0]}',
    #              self.data[1]: f'self._{self.data[1]}',
    #              self.data[2]: f'self._{self.data[2]}',
    #              self.data[3]: f'self._{self.data[3]}',
    #              self.data[4]: f'self._{self.data[4]}',
    #              self.data[5]: f'self._{self.data[5]}',
    #              self.data[6]: f'self._{self.data[6]}',
    #              self.data[7]: f'self._{self.data[7]}',
    #              self.data[8]: f'self._{self.data[8]}',
    #              self.data[9]: f'self._{self.data[9]}',
    #              self.data[10]: f'self._{self.data[10]}',
    #              self.data[11]: f'self._{self.data[11]}',
    #              self.data[12]: f'self._{self.data[12]}',
    #             }

    #     print(varbs)
    #     nvars = 13
    #     for ii in range(0, nvars):
    #         func = self.data[ii]
    #         print(f'\n{ii=} {func=} {varbs[func]} {type(varbs)}')
    #         cache = ksh.Cache(ticker=self._ticker, datatype=func)
    #         varbs[func] = cache.load_cache()
    #         print(f':{varbs[func]=}')
    #         if varbs[func] is None: # No data cached
    #             if ii < 4: # profile, quote, enterprise, rating
    #                 varbs[func] = self.funcs[func](self._ticker, API_KEY)
    #             elif ii < 11:
    #                 varbs[func] = self.funcs[func](self._ticker, API_KEY, period='annual')
    #             elif ii == 11: # stock_data
    #                 varbs[func] = self.funcs[func](self._ticker, period="ytd", interval="1d")
    #             else: # stock_data_detailed
    #                 varbs[func] = self.funcs[func](self._ticker, API_KEY, begin=start_date, end=end_date)
    #             cache.set_expiration(expiration_date)
    #             cache.save_to_cache(varbs[func])


    def get_dcf(self, year:str):
        '''Returns date, stock price, dcf and % dcf over price'''
        try:
            print(self.get_discounted_cash_flow())
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


    def get_pe_ratio(self, year):
        '''Returns P/E ratio'''
        try:
            data = self.get_key_metrics().loc[:, year]
        except KeyError:
            print(f'get_pe_ratio: year {year} data unvailable')
            return 0
        else :
            return data.loc['peRatio']


    def get_current_ratio(self, year):
        '''Returns current ratio'''
        try:
            data = self.get_key_metrics().loc[:, year]
        except KeyError:
            print(f'get_current_ratio: year {year} data unvailable')
            return 0
        else :
            return data.loc['currentRatio']


    def get_roe(self, year):
        '''Returns return on equity'''
        try:
            data = self.get_financial_ratios().loc[:, year]
        except KeyError:
            print(f'get_roe: year {year} data unvailable')
            return 0
        else :
            return data.loc['returnOnEquity']


    def get_roa(self, year):
        '''Returns return on assets'''
        try:
            data = self.get_financial_ratios().loc[:, year]
        except KeyError:
            print(f'get_roa: year {year} data unvailable')
            return 0
        else :
            return data.loc['returnOnAssets']


    def get_net_profit_margin(self, year):
        '''Returns net profit margin (net income / revenue)'''
        try:
            data = self.get_financial_ratios().loc[:, year]
        except KeyError:
            print(f'get_net_profit_margin: year {year} data unvailable')
            return 0
        else :
            return data.loc['netProfitMargin']


    def get_asset_turnover(self, year):
        '''Returns asset turnover (sales / assets)'''
        try:
            data = self.get_financial_ratios().loc[:, year]
        except KeyError:
            print(f'get_asset_turnover: year {year} data unvailable')
            return 0
        else :
            return data.loc['assetTurnover']


    def get_leverage(self, year):
        '''Returns leverage (assets / equity)'''
        try:
            assets = self.get_total_assets(year)
            print(f'{assets=}')
            equity = self.get_total_stockholders_equity(year)
            print(f'{equity=}')
        except KeyError:
            print(f'get_leverage: year {year} data unvailable')
            return 0
        else :
            return assets/equity


    def get_total_assets(self, year):
        '''Returns total assets'''
        try:
            print(f'assets={self.get_balance_sheet_statement()}')
            data = self.get_balance_sheet_statement().loc[:, year]
        except KeyError:
            print(f'get_total_assets: year {year} data unvailable')
            return 0
        else :
            return data.loc['totalAssets']


    def get_total_liabilities(self, year):
        '''Returns total liabilities'''
        try:
            data = self.get_balance_sheet_statement().loc[:, year]
        except KeyError:
            print(f'get_total_liabilities: year {year} data unvailable')
            return 0
        else :
            return data.loc['totalLiabilities']


    def get_total_stockholders_equity(self, year):
        '''Returns total S/E'''
        try:
            data = self.get_balance_sheet_statement().loc[:, year]
        except KeyError:
            print(f'get_total_stockholders_equity: year {year} data unvailable')
            return 0
        else :
            return data.loc['totalStockholdersEquity']
