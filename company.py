#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 20 18:22:19 2021

Data source:
https://financialmodelingprep.com/developer/docs
https://financialmodelingprep.com/developer/docs/formula

@author: charles mégnin
"""
import inspect
import math
import datetime as dt
import pandas as pd
import numpy as np
from numerize import numerize
import plotly.graph_objects as go
import plotly.io as pio
#import plotly.express as px
from plotly.subplots import make_subplots
from bokeh.plotting import figure, show, output_file, save
from bokeh.models import HoverTool, Title, Span, Label, NumeralTickFormatter
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.models.widgets import Tabs, Panel
from bokeh.transform import dodge
from bokeh.palettes import Dark2_8
from bokeh.layouts import column
#from bokeh.core.properties import value
import FundamentalAnalysis as fa
import cache as ksh
import api_keys as keys
import metrics as mtr
import utilities as util

API_KEY = keys.FMP

# Utilities
def round_up(val:float, ndigits:int):
    '''round up utility'''
    return (math.ceil(val * math.pow(10, ndigits)) + 1) / math.pow(10, ndigits)


def round_down(val:float, ndigits:int):
    '''round down utility'''
    return (math.floor(val * math.pow(10, ndigits)) - 1) / math.pow(10, ndigits)


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
    end_date_default   = dt.datetime.today().strftime('%Y-%m-%d')
    date_format = '%Y-%m-%d'


    def __init__(self, ticker:str, period:str, expiration_date, start_date=start_date_default, end_date=end_date_default):
        '''
        start & end dates only for stock_data_detailed()
        expiration date: trigger date for cache refresh
        '''
        self._ticker  = ticker
        self._period = period
        self._expiration_date = expiration_date
        self._start_date = start_date
        self._end_date = end_date
        self._company_name = None
        self._currency = None
        self._country = None
        self._sector = None
        self._industry = None
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

        self._self_check()
        self._load_data(expiration_date=expiration_date, start_date=start_date, end_date=end_date)

    # Helper method
    def _map_item_to_name(self, item:str):
        '''Converts column name to readable metric (WIP)'''
        if item.startswith('d_'):
            return '\u0394 ' + self._map_item_to_name(item[2:])
        if item.lower() == 'totalassets': return 'Total assets'
        if item.lower() == 'totalliabilities': return 'Total liabilities'
        if item.lower() == 'totalstockholdersequity': return 'Total stockholders equity'
        if item.lower() == 'freecashflow': return 'FCF'
        if item.lower() == 'ebit': return 'EBIT'
        if item.lower() == 'revenue': return 'Revenue'
        if item.lower() == 'equitymultiplier': return 'Equity multiplier'
        if item.lower() == 'assetturnover': return 'Asset turnover'
        if item.lower() == 'netprofitmargin': return 'Net profit margin'
        if item.lower() == 'returnonequity': return 'ROE'
        if item.lower() == 'currentratio': return 'Current ratio'
        if item.lower() == 'debttoequity': return 'Debt to equity ratio'
        print(f'unknown item {item}')
        return ''


    def _self_check(self):
        '''Consistency checks for the Company class'''
        assert self._period in ['annual', 'quarter'], "period must be 'annual' or 'quarter'"
        # Assert end_date > start_date
        start_object = dt.datetime.strptime(self._start_date, self.date_format)
        end_object = dt.datetime.strptime(self._end_date, self.date_format)
        assert start_object < end_object, 'start date must be prior to end date'
        # Assert expiration_date >= now
        date_object = dt.datetime.strptime(self._expiration_date, self.date_format)
        assert date_object >= dt.datetime.today(), 'expiration must be today or later'


    def _process_data(self, fcn_idx:int, expiration_date, start_date, end_date):
        try:
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
        except KeyError:
            return None
        except ValueError:
            return None
        except IndexError:
            return None


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

        self._company_name = self._profile.loc['companyName'][0]
        self._sector       = self._profile.loc['sector'][0]
        self._industry     = self._profile.loc['industry'][0]
        self._currency     = self._profile.loc['currency'][0]
        self._country      = self._profile.loc['country'][0]
        self._currency_symbol = self._set_currency_symbol()


    def _set_currency_symbol(self):
        '''Sets the symbol corresponding to the currency'''
        if self._currency == 'USD':
            return '$'
        if self._currency == 'EUR':
            return '€'
        return self._currency


    def get_ticker(self):
        '''return company ticker '''
        return self._ticker


    def get_company_name(self):
        '''return company ticker '''
        return self._company_name


    def get_sector(self):
        '''return company sector '''
        return self._sector


    def get_industry(self):
        '''return company industry '''
        return self._industry


    def get_profile(self):
        '''return profile dataframe'''
        return self._profile


    def get_quote(self):
        '''return quote dataframe'''
        return self._quote


    def get_currency(self):
        '''Returns currency'''
        return self._currency


    def get_currency_symbol(self):
        '''Returns symbol corresponding to currency'''
        return self._currency_symbol


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


    ### Profile data ###
    def _get_profile_item(self, item):
        '''Returns company profile data'''
        try:
            data = self.get_profile()
        except KeyError:
            print(f'get_profile_item: {item} profile data unvailable')
            return ''
        else :
            return data.loc[item].iloc[0]


    def get_mktCap(self):
        '''Returns market Cap'''
        item = 'mktCap'
        return self._get_profile_item(item=item)


    ### Balance sheet statement data ###
    def _get_balance_sheet_item(self, item:str, year:str, change:bool=False):
        ''' Returns generic balance sheet item or its time change'''
        try:
            data = self.get_balance_sheet_statement().loc[item]
            if change:
                data = data[::-1].pct_change()
        except KeyError:
            caller_name = inspect.stack()[1][3]
            func_name   = inspect.stack()[0][3]
            msg=f'{func_name}: item {item} or year {year} in {caller_name} unvailable'
            print(msg)
            return 0
        else :
            data.index = data.index.astype(int)
            return data.loc[year]


    def get_balance_sheet_item_over_time(self, item:str, start_year:str, end_year:str, change:bool=False):
        '''
        Returns a generic balance sheet item (or its time change) over year span
        from start_year to end_year (both inclusive) as a Dataframe with year as index
        '''
        try:
            data = self.get_balance_sheet_statement().loc[item].to_frame()
            if change:
                data = data[::-1].pct_change()
        except KeyError:
            caller_name = inspect.stack()[1][3]
            func_name   = inspect.stack()[0][3]
            msg=f'{func_name}: time series item {item} in {caller_name} unvailable'
            print(msg)
            return 0
        else :
            data.index = data.index.astype(int)
            return data[(data.index <= end_year) & (data.index >= start_year)]


    def get_totalAssets(self, year:str, change:bool=False):
        '''Return total assets or its time derivative'''
        item = 'totalAssets'
        return self._get_balance_sheet_item(item=item, year=year, change=change)


    def get_totalLiabilities(self, year:str, change:bool=False):
        '''Return total liabilities or its time derivative'''
        item = 'totalLiabilities'
        return self._get_balance_sheet_item(item=item, year=year, change=change)


    def get_totalStockholdersEquity(self, year:str, change:bool=False):
        '''Return total SE or its time derivative'''
        item = 'totalStockholdersEquity'
        return self._get_balance_sheet_item(item=item, year=year, change=change)


    def get_leverage(self, year:str, change:bool=False):
        '''Returns leverage (assets / equity)'''
        try:
            assets = self._get_balance_sheet_item('totalAssets', year, change)
            equity = self._get_balance_sheet_item('totalStockholdersEquity', year, change)
        except KeyError:
            print(f'get_leverage: year {year} data unvailable')
            return 0
        else :
            if equity == 0:
                return 0
            return assets/equity


    ### Income statement data ###
    def _get_income_statement_item(self, item:str, year:str, change:bool=False):
        '''Returns generic income statement item or its time change'''
        try:
            data = self.get_income_statement().loc[item]
            if change:
                data = data[::-1].pct_change()
        except KeyError:
            caller_name = inspect.stack()[1][3]
            func_name   = inspect.stack()[0][3]
            msg=f'{func_name}: item {item} or year {year} in {caller_name} unvailable'
            print(msg)
            return 0
        else :
            data.index = data.index.astype(int)
            return data.loc[year]


    def get_income_statement_item_over_time(self, item:str, start_year:int, end_year:int, change:bool=False):
        '''
        Returns a generic balance sheet item (or its time change) over year span
        from start_year to end_year (both inclusive) as a Dataframe with year as index
        '''
        try:
            data = self.get_income_statement().loc[item].to_frame()
            if change:
                data = data[::-1].pct_change()
        except KeyError:
            caller_name = inspect.stack()[1][3]
            func_name   = inspect.stack()[0][3]
            msg=f'{func_name}: time series item {item} in {caller_name} unvailable'
            print(msg)
            return 0
        else :
            data.index = data.index.astype(int)
            return data[(data.index <= end_year) & (data.index >= start_year)]


    def get_netIncome(self, year:str, change:bool=False):
        '''Return net income'''
        item = 'netIncome'
        return self._get_income_statement_item(item=item, year=year, change=change)


    def get_depam(self, year:str, change:bool=False):
        '''Returns depreciation & amortization or change in D&A'''
        item = 'depreciationAndAmortization'
        return self._get_income_statement_item(item=item, year=year, change=change)


    def get_ebitda(self, year:str, change:bool=False):
        '''Returns EBITDA or change in EBITDA'''
        item = 'ebitda'
        return self._get_income_statement_item(item=item, year=year, change=change)


    def get_ebit(self, year:str, change:bool=False):
        '''Returns EBIT = ebitda - depreciation & amortization'''
        ebitda = self.get_ebitda(year=year, change=change)
        depam  = self.get_depam(year=year, change=change)
        return ebitda - depam


    def get_revenue(self, year:str, change:bool=False):
        '''Returns revenue or change in revenue'''
        item = 'revenue'
        return self._get_income_statement_item(item=item, year=year, change=change)


    ### Cash flow statement data ###
    def _get_cash_flow_statement_item(self, item:str, year:str, change:bool=False):
        '''
        Returns generic cash flow statement item or its time change
        '''
        try:
            data = self.get_cash_flow_statement().loc[item]
            if change:
                data = data[::-1].pct_change()
        except KeyError:
            caller_name = inspect.stack()[1][3]
            func_name   = inspect.stack()[0][3]
            msg=f'{func_name}: item {item} or year {year} in {caller_name} unvailable'
            print(msg)
            return 0
        else :
            data.index = data.index.astype(int)
            return data.loc[year]


    def get_cash_flow_statement_item_over_time(self, item:str, start_year:str, end_year:str, change:bool=False):
        '''
        Returns a generic balance sheet item (or its time change) over year span
        from start_year to end_year (both inclusive) as a Dataframe with year as index
        '''
        try:
            data = self.get_cash_flow_statement().loc[item].to_frame()
            if change:
                data = data[::-1].pct_change()
        except KeyError:
            caller_name = inspect.stack()[1][3]
            func_name   = inspect.stack()[0][3]
            msg=f'{func_name}: time series item {item} in {caller_name} unvailable'
            print(msg)
            return 0
        else :
            data.index = data.index.astype(int)
            return data[(data.index <= end_year) & (data.index >= start_year)]


    def get_freeCashFlow(self, year:str, change:bool=False):
        '''Returns free cash flow or change in FCF'''
        item = 'freeCashFlow'
        return self._get_cash_flow_statement_item(item=item, year=year, change=change)


    def get_cashConversion(self, year:str, change:bool=False):
        '''Returns cash conversion (FCF/Net income) or change in CC'''
        fcf    = self.get_freeCashFlow(year, change=False)
        income = self.get_netIncome(year, change=False)
        if income == 0:
            return 0
        if change:
            d_fcf = self.get_freeCashFlow(year, change=True)
            d_income = self.get_netIncome(year, change=True)
            return (d_fcf*income - d_income/fcf)/(income**2)
        return fcf/income


    ###Financial ratio data ###
    def _get_financial_ratios_item(self, item:str, year:str, change:bool=False):
        '''Returns generic financial ratios item or its time change'''
        try:
            data = self.get_financial_ratios().loc[item]
            if change:
                data = data[::-1].pct_change()
        except KeyError:
            caller_name = inspect.stack()[1][3]
            func_name   = inspect.stack()[0][3]
            msg=f'{func_name}: item {item} or year {year} in {caller_name} unvailable'
            print(msg)
            return 0
        else :
            data.index = data.index.astype(int)
            query = data.loc[year]
            if query is None:
                print(f'item {item} is None in the data set')
                return 0
            return query


    def get_financial_ratios_item_over_time(self, item:str, start_year:int, end_year:int, change:bool=False):
        '''
        Returns a generic balance sheet item (or its time change) over year span
        from start_year to end_year (both inclusive) as a Dataframe with year as index
        '''
        try:
            data = self.get_financial_ratios().loc[item].to_frame()
            if change:
                data = data[::-1].pct_change()
        except KeyError:
            caller_name = inspect.stack()[1][3]
            func_name   = inspect.stack()[0][3]
            msg=f'{func_name}: time series item {item} in {caller_name} unvailable'
            print(msg)
            return 0
        else :
            data.index = data.index.astype(int)
            return data[(data.index <= end_year) & (data.index >= start_year)]


    def get_netProfitMargin(self, year:str, change:bool=False):
        '''Returns net profit margin (net income/revenue) or change in NPR'''
        item = 'netProfitMargin'
        return self._get_financial_ratios_item(item=item, year=year, change=change)


    def get_assetTurnover(self, year:str, change:bool=False):
        '''Returns asset turnover (revenue/avg total assets) or change in A.T.'''
        item = 'assetTurnover'
        return self._get_financial_ratios_item(item=item, year=year, change=change)


    def get_returnOnAssets(self, year:str, change:bool=False):
        '''Returns return on assets (net income/total assets) or change in ROA'''
        item = 'returnOnAssets'
        return self._get_financial_ratios_item(item=item, year=year, change=change)


    def get_priceEarningsRatio(self, year:str, change:bool=False):
        '''Returns PE ratio or change in PE'''
        item = 'peRatio'
        return self._get_key_metrics_item(item=item, year=year, change=change)


    # def get_priceEarningsRatio_over_time(self, yr_1:int, yr_2:int, change:bool=False):
    #    '''Returns PEG ratio (P/E to growth) or change in PEG'''
    #    item = 'peRatio'
    #    return self._get_key_metrics_item_over_time(item=item, start_year=yr_1, end_year=yr_2, change=change)


    def get_priceEarningsToGrowthRatio(self, year:str, change:bool=False):
        '''Returns PE ratio or change in PE over time'''
        item = 'priceEarningsToGrowthRatio'
        return self._get_financial_ratios_item(item=item, year=year, change=change)


    # def get_priceEarningsToGrowthRatio_over_time(self, yr_1:int, yr_2:int, change:bool=False):
    #     '''Returns PEG ratio (P/E to growth) or change in PEG'''
    #     item = 'priceEarningsToGrowthRatio'
    #     return self.get_financial_ratios_item_over_time(item=item, start_year=yr_1, end_year=yr_2, change=change)


    def get_priceToBookRatio(self, year:str, change:bool=False):
        '''Returns P/B ratio (price to book) or change in P/B'''
        item = 'priceToBookRatio'
        return self._get_financial_ratios_item(item=item, year=year, change=change)


    # def get_priceToBookRatio_over_time(self, yr_1:int, yr_2:int, change:bool=False):
    #     '''Returns P/B ratio (price to book) or change in P/B'''
    #     item = 'priceToBookRatio'
    #     return self.get_financial_ratios_item_over_time(item=item, start_year=yr_1, end_year=yr_2, change=change)


    def get_cashReturnOnEquity(self, year:str, change:bool=False):
        '''Returns cash return on equity (ROE*cash conversion) or change in CROE'''
        roe = self.get_roe(year=year, change=False)
        cash_conv = self.get_cashConversion(year=year, change=False)
        if change:
            d_roe       = self.get_roe(year=year, change=True)
            d_cash_conv = self.get_cashConversion(year=year, change=True)
            return d_roe*cash_conv + roe*d_cash_conv
        return roe*cash_conv


    def get_equityMultiplier(self, year:str, change:bool=False):
        '''Returns equity multiplier = Total Assets/Total Equity or change in EM'''
        assets = self._get_balance_sheet_item('totalAssets', year, change=False)
        equity = self._get_balance_sheet_item('totalStockholdersEquity', year, change=False)
        if change:
            d_assets = self._get_balance_sheet_item('totalAssets', year, change=True)
            d_equity = self._get_balance_sheet_item('totalStockholdersEquity', year, change=True)
            return (d_assets*equity - d_equity/assets)/(equity**2)
        if equity == 0:
            return 0
        return assets/equity


    ### key metrics data ###
    def _get_key_metrics_item(self, item:str, year:str, change:bool=False):
        '''Returns generic key metrics item or its time change'''
        try:
            data = self.get_key_metrics().loc[item]
            if change:
                data = data[::-1].pct_change()
        except KeyError:
            msg=f'get_key_metrics_item: {self.get_ticker()} item {item} or year {year} data unvailable'
            print(msg)
            return 0
        else :
            data.index = data.index.astype(int)
            return data.loc[year]


    def get_key_metrics_item_over_time(self, item:str, start_year:int, end_year:int, change:bool=False):
        '''
        Returns a generic balance sheet item (or its time change) over year span
        from start_year to end_year (both inclusive) as a Dataframe with year as index
        '''
        try:
            data = self.get_key_metrics().loc[item].to_frame()
            if change:
                data = data[::-1].pct_change()
        except KeyError:
            caller_name = inspect.stack()[1][3]
            func_name   = inspect.stack()[0][3]
            msg=f'{func_name}: time series item {item} in {caller_name} unvailable'
            print(msg)
            return 0
        else :
            data.index = data.index.astype(int)
            return data[(data.index <= end_year) & (data.index >= start_year)]


    def get_roe(self, year:str, change:bool=False):
        '''Returns ROE or change in ROE'''
        item = 'returnOnEquity'
        return self._get_financial_ratios_item(item=item, year=year, change=change)


    # def get_roe_over_time(self, yr_1:int, yr_2:int, change:bool=False):
    #     '''Returns ROE or change in ROE'''
    #     item = 'returnOnEquity'
    #     return self._get_financial_ratios_item_over_time(item=item, start_year=yr_1, end_year=yr_2, change=change)


    def get_currentRatio(self, year:str, change:bool=False):
        '''Returns current ratio or change in current ratio'''
        item = 'currentRatio'
        return self._get_key_metrics_item(item=item, year=year, change=change)


    def get_debtToEquity(self, year:str, change:bool=False):
        '''Returns debt to equity ratio or change in debt to equity ratio'''
        item = 'debtToEquity'
        return self._get_key_metrics_item(item=item, year=year, change=change)


    def get_peers(self):
        '''return peers as defined in API (***not preferred method***)'''
        return util.extract_peers(self._ticker, API_KEY)


    def get_metric_over_time(self, items:list, yr_0:int, yr_1:int):
        '''Generic item over time getter'''
        # Metric
        df_0 = self.load_cie_metrics_over_time(items, yr_0, yr_1, change=False)
        # Change in metric
        df_1 = self.load_cie_metrics_over_time(items, yr_0, yr_1, change=True)
        return pd.concat([df_0, df_1], axis=1) # merge the two


    def load_cie_metrics_over_time(self, metrics:list, yr_start:int, yr_end:int, change:bool=False):
        '''
        Calls recursively load_cie_metrics and returns a dataframe with requested metrics
        '''
        dic_met = {}
        if change is True:
            yr_start -= 1 # start one year prior to get relative change

        for year in range(yr_start, yr_end + 1):
            dic_yr = self.load_cie_metrics(year, metrics)
            dic_met[year]= dic_yr
        dfr = pd.DataFrame(dic_met).transpose()
        if change is False:
            return dfr
        # Change = True:
        dfr = dfr.pct_change() # compute relative change
        dfr.drop(dfr.index[0], inplace=True) # remove first row
        # set column names
        new_names = []
        for old_name in dfr.columns:
            new_names.append(f'd_{old_name}')
        dfr.columns = new_names # reset column names
        return dfr


    def load_cie_metrics(self, year:str, requested_metrics:list):
        '''load metrics values corresponding to keys in cie_metrics'''
        cie_metrics = {}
        for metric in requested_metrics:
            if metric == 'debtToEquity':
                cie_metrics['debtToEquity'] = self.get_debtToEquity(year)
            elif metric == 'currentRatio':
                cie_metrics['currentRatio'] = self.get_currentRatio(year)
            elif metric == 'roa':
                cie_metrics['roa'] = self.get_returnOnAssets(year)
            elif metric == 'returnOnAssets':
                cie_metrics['returnOnAssets'] = self.get_returnOnAssets(year)
            elif metric == 'roe':
                cie_metrics['roe'] = self.get_roe(year)
            elif metric == 'returnOnEquity':
                cie_metrics['returnOnEquity'] = self.get_roe(year)
            elif metric == 'peg':
                cie_metrics['peg'] = self.get_priceEarningsToGrowthRatio(year)
            elif metric == 'priceEarningsToGrowthRatio':
                cie_metrics['priceEarningsToGrowthRatio'] = self.get_priceEarningsToGrowthRatio(year)
            elif metric == 'cashReturnOnEquity':
                cie_metrics['cashReturnOnEquity'] = self.get_cashReturnOnEquity(year)
            elif metric == 'netProfitMargin':
                cie_metrics['netProfitMargin'] = self.get_netProfitMargin(year)
            elif metric == 'assetTurnover':
                cie_metrics['assetTurnover'] = self.get_assetTurnover(year)
            elif metric == 'equityMultiplier':
                cie_metrics['equityMultiplier'] = self.get_equityMultiplier(year)
            elif metric =='cashConv':
                cie_metrics['cashConv'] = self.get_cashConversion(year)
            elif metric =='mktCap':
                cie_metrics['mktCap'] = self.get_mktCap()
            elif metric =='totalAssets':
                cie_metrics['totalAssets'] = self.get_totalAssets(year=year)
            elif metric =='totalLiabilities':
                cie_metrics['totalLiabilities'] = self.get_totalLiabilities(year=year)
            elif metric =='totalStockholdersEquity':
                cie_metrics['totalStockholdersEquity'] = self.get_totalStockholdersEquity(year=year)
            elif metric =='revenue':
                cie_metrics['revenue'] = self.get_revenue(year=year)
            elif metric =='netIncome':
                cie_metrics['netIncome'] = self.get_netIncome(year=year)
            elif metric == 'ebit':
                cie_metrics['ebit'] = self.get_ebit(year)
            elif metric == 'freeCashFlow':
                cie_metrics['freeCashFlow'] = self.get_freeCashFlow(year)
            else:
                caller_name = inspect.stack()[1][3]
                func_name   = inspect.stack()[0][3]
                msg         = f'{func_name}: metric {metric} in {caller_name} has no functional counterpart'
                raise ValueError(msg)
        return cie_metrics


    @staticmethod
    def _build_caption(fig, metric_nm):
        '''builds caption title at bottom of plot as a function of the metric set'''
        if metric_nm =='wb_metrics':
            caption  = r'debt to equity=debt/equity | '
            caption += r'current ratio=current assets/current liabilities | '
            caption += r'roe=net income/equity'
        elif metric_nm == 'dupont_metrics':
            caption  = 'net profit margin=net income/revenue | '
            caption += 'asset turnover=revenue/assets | '
            caption += 'equity multiplier=assets/equity | '
            caption += 'cash conversion=fcf/net income | '
            caption += 'roa=net income/assets | '
            caption += 'roe=net income/equity | '
            caption += 'cash roe=fcf/equity'
        elif metric_nm == 'dupont_metrics_short':
            caption  = 'roe=net profit margin*asset turnover*equity multiplier '
            caption += '(roe=net income/equity | '
            caption += 'net profit margin=net income/revenue | '
            caption += 'asset turnover=revenue/assets | '
            caption += 'equity multiplier=assets/equity)'
        else:
            caption = ''

        fig.add_annotation(dict(font=dict(color="steelblue",
                                                      size=12,
                                                      ),
                                            x=0,
                                            y=-.075,
                                            showarrow=False,
                                            text=caption,
                                            textangle=0,
                                            xref="paper",
                                            yref="paper",
                                           )
                                       )

    @staticmethod
    def _build_yscale_dropdown():
        '''Returns linear/log y-axis dropdown menu'''
        button_layer_height = 1.15
        menu = dict(buttons=list([
                        dict(label="Linear y",
                             method="relayout",
                             args=[{"yaxis.type": "linear"}]),
                        dict(label="Log y",
                             method="relayout",
                             args=[{"yaxis.type": "log"}]),
                    ]),
                    direction="down",
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0.,
                    xanchor="left",
                    y=button_layer_height,
                    yanchor="top"
                    )
        return menu


    @staticmethod
    def _build_buttons():
        '''Toggles on-off graphic elements'''
        button_layer_height = 1.1

        menus = [dict(buttons=list([
                                dict(label="Linear y",
                                     method="relayout",
                                     args=[{"yaxis.type": "linear"}]),
                                dict(label="Log y",
                                     method="relayout",
                                     args=[{"yaxis.type": "log"}]),
                                ]),
                direction="down",
                x=0.,
                xanchor="left",
                y=button_layer_height,
                yanchor="top",
                ),
            dict(buttons=list([
                                dict(label="button 1",
                                     method="relayout",
                                     args = [{'visible': [True, True, True, False, False, False]},
                                             {'title': 'metrics on'}]),
                                dict(label="button 2",
                                     method="relayout",
                                     args=[{'visible': [True, True, True, True, True, True]},
                                           {'title': 'metrics & change on'}]),
                                ]),
                type = 'buttons',
                x=0.,
                xanchor="right",
                y=button_layer_height,
                yanchor="top",
                ),
        ]
        print(menus)
        return menus


    @staticmethod
    def _build_title(title_text:str, subtitle_text:str):
        full_text = f'{title_text})<br><sup>{subtitle_text}</sup>'
        title = {'text': full_text,
                 'y': 0.95,
                 'x': 0.5,
                 'xanchor': 'center',
                 'yanchor': 'top',
                 }
        return title


    def plot_peers_comparison(self, year:str, metrics:dict, metric_name:str, peers:list, filename:str):
        '''
        Bar plot of sector peers for a given year
        metrics: metric dictionary
        metric_name: human-friendly metric name
        filename = html output file
        '''
        template = 'presentation'
        title = f"{self._company_name} & peers - {mtr.metrics_set_names[metric_name]} ({year})"

        fig = go.Figure()

        metrics_keys = list(metrics.keys())

        # Add trace from target company
        print(f'Processing base company: {self._ticker}')
        cie_metrics = list(self.load_cie_metrics(year, metrics_keys).values())
        fig.add_trace(go.Bar(x=metrics_keys,
                             y=cie_metrics,
                             name  = f'{self._company_name} ({self._ticker})',
                             hovertemplate = 'Value: %{y:.2f}<br>',
                             ),
                      )

        # Add traces from peers
        for peer in peers:
            print(f'Processing peer {peer}')
            try:
                peer_cie = Company(peer,
                                   period='annual',
                                   expiration_date=self._expiration_date,
                                   start_date=self._start_date,
                                   end_date=self._end_date
                                   )
                cie_metrics = list(peer_cie.load_cie_metrics(year, metrics_keys).values())
                fig.add_trace(go.Bar(x=metrics_keys,
                                     y=cie_metrics,
                                     name  = f'{peer_cie.get_company_name()} ({peer})',
                                     hovertemplate = 'Value: %{y:.2f}<br>',
                                     ),
                              )
                self._build_caption(fig, metric_name)
            except:
                print(f'Could not include {peer} in plot')
        # For each set of metrics, add benchmark trace
        fig.add_trace(go.Bar(x=metrics_keys,
                             y=list(metrics.values()),
                             name='Benchmark',
                             marker_pattern_shape="x",
                             hovertemplate = 'Value: %{y:.2f}<br>',
                             ),
                      )

        fig.update_layout(
            title = title,
            template=template,
            legend = dict(font = dict(size = 13,
                                      color = "black",
                                      )
                          ),
            xaxis_tickfont_size=14,
            yaxis=dict(title='metric value',
                       titlefont_size=16,
                       tickfont_size=14,
                       linecolor="#BCCCDC",
                       showspikes=True, # Show spike line for Y-axis
                       # Format spike
                       spikethickness=1,
                       spikedash="dot",
                       spikecolor="#999999",
                       spikemode="across",
                       ),
            barmode='group',
            bargap=0.15, # gap between bars of adjacent location coordinates.
            bargroupgap=0.1, # gap between bars of the same location coordinate.
            updatemenus=[self._build_yscale_dropdown()],
        )
        pio.write_html(fig, file=filename, auto_open=True)


    def time_plot(self, time_series:pd.DataFrame, filename:str):
        '''Plots time series '''
        template = 'presentation'
        title=self._build_title(f'{self.get_company_name()} ({self.get_ticker()})')

        fig = go.Figure()
        for col in time_series.columns:
            fig.add_trace(go.Bar(x = time_series.index,
                                     y = time_series[col],
                                     name = col,
                                     hovertemplate = '%{y:.3g}<br>',
                                     ),
                          )
        fig.update_layout(
            title    = title,
            template = template,
            legend   = dict(font = dict(size = 12,)),
            xaxis_tickfont_size = 14,
            hovermode="x unified",
            yaxis=dict(title=self.get_currency(),
                       titlefont_size=16,
                       tickfont_size=14,
                       linecolor="#BCCCDC",
                       showspikes=True, # Show spike line for Y-axis
                       # Format spike
                       spikethickness=1,
                       spikedash="dot",
                       spikecolor="#999999",
                       spikemode="across",
                       ),
            updatemenus=[self._build_yscale_dropdown()],
            barmode='group',
            bargap=0.2, # gap between bars of adjacent location coordinates.
            bargroupgap=0.05, # gap between bars of the same location coordinate.
            )
        pio.write_html(fig, file=filename, auto_open=True)

    @staticmethod
    def get_time_plot_defaults():
        '''Return default time plot parameters'''
        theme = 'simple_white'
        defaults = {}
        defaults['template'] = f'{theme}+presentation+xgridoff'
        defaults['bargap'] = .2
        defaults['groupgap'] = .05
        defaults['linewidth'] = 1
        defaults['textfont_size'] = 14
        defaults['linecolors'] = pio.templates[theme].layout['colorway']
        return defaults


    def wb_time_plot(self, time_series:pd.DataFrame, filename:str):
        '''
        Plots balance sheet time series (Assets, liabilities & SHE) and
        ROE, current ratio, debt to equity
        '''
        defaults = self.get_time_plot_defaults()
        template = defaults['template']
        title=self._build_title(f'{self.get_company_name()} ({self.get_ticker()})')

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        for col in time_series.columns:
            if col in ['totalAssets', 'totalLiabilities', 'totalStockholdersEquity']:
                fig.add_trace(go.Bar(x = time_series.index,
                                         y = time_series[col],
                                         name = col,
                                         hovertemplate = '%{y:.3g}<br>',
                                         ),
                              secondary_y=False,
                              )
            elif col in ['roe', 'currentRatio', 'debtToEquity']:
                if col == 'roe':
                    dash = 'dash'
                    color = defaults['linecolors'][0]
                    hovertemplate = '%{y:.1%}'
                elif col == 'currentRatio':
                    dash = 'dot'
                    color = defaults['linecolors'][1]
                    hovertemplate = '%{y:.2f}<br>'
                elif col == 'debtToEquity':
                    dash = 'dashdot'
                    color = defaults['linecolors'][2]
                    hovertemplate = '%{y:.1%}<br>'
                texttemplate = hovertemplate

                fig.add_trace(go.Scatter(x = time_series.index,
                                         y = time_series[col],
                                         name = col,
                                         hovertemplate = hovertemplate,
                                         text=time_series[col],
                                         mode = 'lines+text',
                                         textposition = 'middle center',
                                         texttemplate = texttemplate,
                                         textfont = {'size': defaults['textfont_size'],
                                                     'color': color},
                                         line = dict(color=color,
                                                     width=defaults['linewidth'],
                                                     dash=dash),
                                         ),
                              secondary_y=True,
                              )
            else:
                raise KeyError(f'metric {col} not implemented')

        fig.update_yaxes(title_text=f"{self.get_currency()}" ,
                         secondary_y=False,
                         showticklabels=True,
                         visible=True
                         )
        fig.update_yaxes(title_text="<b>remove this title & axis</b>",
                         secondary_y=True,
                         showticklabels=False,
                         visible=False,
                         )

        fig.update_layout(
            title    = title,
            template = template,
            legend   = dict(font = dict(size = 12,)),
            xaxis_tickfont_size = 14,
            updatemenus=[self._build_yscale_dropdown()],
            hovermode="x unified",
            barmode='group',
            bargap=defaults['bargap'],
            bargroupgap=defaults['groupgap'],
            )
        pio.write_html(fig, file=filename, auto_open=True)

    @staticmethod
    def _get_metric_lists():
        revenue_list = ['revenue', 'freeCashFlow', 'ebit']
        asset_list   = ['totalAssets', 'totalLiabilities', 'totalStockholdersEquity']
        dupont_list  = ['cashReturnOnEquity', 'returnOnEquity', 'returnOnAssets','netProfitMargin', 'assetTurnover', 'equityMultiplier']
        wb_list = ['returnOnEquity', 'debtToEquity', 'currentRatio']
        d_revenue_list = []
        for item in revenue_list:
            d_revenue_list.append(f'd_{item}')
        d_asset_list = []
        for item in asset_list:
            d_asset_list.append(f'd_{item}')
        d_dupont_list = []
        for item in dupont_list:
            d_dupont_list.append(f'd_{item}')
        d_wb_list = []
        for item in wb_list:
            d_wb_list.append(f'd_{item}')
        return revenue_list+asset_list+dupont_list+wb_list, d_revenue_list+d_asset_list+d_dupont_list+d_wb_list

    @staticmethod
    def _get_legend_attributes(defaults, col):
        '''Return legend color and label from column name'''
        if col == 'revenue':
            color = defaults['linecolors'][0]
            legend_name = 'Revenue'
        elif col == 'freeCashFlow':
            color = defaults['linecolors'][1]
            legend_name = 'FCF'
        elif col == 'ebit':
            color = defaults['linecolors'][2]
            legend_name = 'EBIT'
        elif col == 'totalAssets':
            color = defaults['linecolors'][0]
            legend_name = 'Assets'
        elif col == 'totalLiabilities':
            color = defaults['linecolors'][1]
            legend_name = 'Liabilities'
        elif col == 'totalStockholdersEquity':
            color = defaults['linecolors'][2]
            legend_name = "Shareholder's Equity"
        elif col == 'returnOnEquity':
            color = defaults['linecolors'][0]
            legend_name = "ROE"
        elif col == 'netProfitMargin':
            color = defaults['linecolors'][1]
            legend_name = "Net profit margin"
        elif col == 'assetTurnover':
            color = defaults['linecolors'][2]
            legend_name = "Asset turnover"
        elif col == 'equityMultiplier':
            color = defaults['linecolors'][3]
            legend_name = "Equity multiplier"
        elif col == 'debtToEquity':
            color = defaults['linecolors'][1]
            legend_name = "Debt to equity"
        elif col == 'currentRatio':
            color = defaults['linecolors'][2]
            legend_name = "Current ratio"

        elif col == 'd_revenue':
            color = defaults['linecolors'][0]
            legend_name = '\u0394 Revenue'
        elif col == 'd_freeCashFlow':
            color = defaults['linecolors'][1]
            legend_name = "\u0394 FCF"
        elif col == 'd_ebit':
            color = defaults['linecolors'][2]
            legend_name = "\u0394 EBIT"
        elif col == 'd_totalAssets':
            color = defaults['linecolors'][0]
            legend_name = '\u0394 Assets'
        elif col == 'd_totalLiabilities':
            color = defaults['linecolors'][1]
            legend_name = '\u0394 Liabilities'
        elif col == 'd_totalStockholdersEquity':
            color = defaults['linecolors'][2]
            legend_name = "\u0394 Shareholder's Equity"
        elif col == 'd_returnOnEquity':
            color = defaults['linecolors'][0]
            legend_name = "\u0394 ROE"
        elif col == 'd_netProfitMargin':
            color = defaults['linecolors'][1]
            legend_name = "\u0394 Net profit margin"
        elif col == 'd_assetTurnover':
            color = defaults['linecolors'][2]
            legend_name = "\u0394 Asset turnover"
        elif col == 'd_equityMultiplier':
            color = defaults['linecolors'][3]
            legend_name = "\u0394 Equity multiplier"
        elif col == 'd_debtToEquity':
            color = defaults['linecolors'][1]
            legend_name = "Debt to equity"
        elif col == 'd_currentRatio':
            color = defaults['linecolors'][2]
            legend_name = "Current ratio"
        return color, legend_name


    ### BOKEH PLOTS ####

    @staticmethod
    def get_plot_defaults():
        '''Returns default plot settings'''
        defaults = {}
        defaults['plot_width']  = 1200
        defaults['plot_height'] = 600
        defaults['plot_bottom_height'] = 150
        defaults['theme']       = 'light_minimal'
        defaults['palette']     = Dark2_8
        defaults['text_font']   = 'helvetica'
        # Title
        defaults['title_color']        = '#333333'
        defaults['title_font_size']    = '22pt'
        defaults['subtitle_font_size'] = '18pt'
        # Legend
        defaults['legend_font_size'] = '11pt'
        # Bars
        defaults['bar_width_shift_ratio'] = .9 # bar width/shift
        # Lines
        defaults['line_dash'] = ''
        defaults['zero_growth_line_color']     = 'red'
        defaults['zero_growth_line_thickness'] = .5
        defaults['zero_growth_line_dash']      = 'dotted'
        defaults['zero_growth_font_size']      = '8pt'
        defaults['zero_growth_font_color']     = 'dimgray'
        # WB Benchmarks:
        defaults['roe_benchmark']            = .08
        defaults['debt_to_equity_benchmark'] = .5
        defaults['current_ratio_benchmark']  = 1.5
        defaults['benchmark_line_dash']      = 'dashed'
        defaults['benchmark_line_thickness'] = 2
        defaults['benchmark_font_size']      = '9pt'
        # Means
        defaults['means_line_dash']      = 'dotted'
        defaults['means_line_thickness'] = 1
        defaults['means_font_size']      = '9pt'

        defaults['label_alpha']     = .75
        defaults['label_font_size'] = '10pt'
        # Axes
        defaults['top_axis_label_text_font_size']    = '12pt'
        defaults['bottom_axis_label_text_font_size'] = '8pt'
        defaults['axis_label_text_color']            = 'dimgray'
        return defaults

    @staticmethod
    def _initialize_plot(position:str, axis_type:str, defaults:dict, source:ColumnDataSource, min_y:float, max_y:float, linked_figure=None):
        '''Initialize  plot
        position = top or bottom (plot)
        axis_type = log or linear
        '''
        if position == 'top':
            plot_height = defaults['plot_height']
            x_range = source.data['year']
        else:
            plot_height = defaults['plot_bottom_height']
            x_range = linked_figure.x_range # connect bottom x-axis to top
        fig = figure(x_range = x_range,
                     y_range = [min_y, max_y],
                     plot_width  = defaults['plot_width'],
                     plot_height = plot_height,
                     tools       = 'box_zoom, ywheel_zoom, reset, save',
                     #active_scroll = "ywheel_zoom",
                     y_axis_type = axis_type,
                     )
        fig.xgrid.grid_line_color = None
        # Configure toolbar & bokeh logo
        fig.toolbar.autohide = True
        fig.toolbar_location = 'right'
        fig.toolbar.logo     = None
        return fig

    @staticmethod
    def _position_legend(fig, defaults):
        '''Must be set after legend defined'''
        fig.legend.location     = "top_left"
        fig.legend.click_policy = 'hide'
        fig.legend.orientation  = "vertical"
        fig.legend.label_text_font_size = defaults['legend_font_size']
        fig.add_layout(fig.legend[0], 'right')


    def _build_title_bokeh(self, fig, defaults:dict, subtitle:str):
        '''Build plot title and subtitle'''
        #subtitle
        fig.add_layout(Title(text=subtitle,
                             align='center',
                             text_font_size=defaults['subtitle_font_size'],
                             text_color=defaults['title_color'],
                             text_font=defaults['text_font']),
                       'above',
                       )
        #title
        fig.add_layout(Title(text=f'{self.get_company_name()} ({self.get_ticker()})',
                             align='center',
                             text_font_size=defaults['title_font_size'],
                             text_color=defaults['title_color'],
                             text_font=defaults['text_font']),
                       'above',
                       )

    @staticmethod
    def _build_caption_bokeh(fig):
        citation = Label(x = -1,
                         y = -.1,
                         x_units = 'data',
                         y_units = 'data',
                         text    = 'Collected by Luke C. 2016-04-01',
                         )
        fig.add_layout(citation)

    @staticmethod
    def _build_axes(fig, position:str, defaults:dict, axis_format:str, y_axis_label:str):
        '''Sets various parameters for x & y axes'''
        # X axis
        fig.xaxis.major_label_text_font_size = defaults['top_axis_label_text_font_size']
        fig.xaxis.axis_label_text_color      = defaults['axis_label_text_color']
        # Y axis
        fig.yaxis.axis_label_text_font_size  = defaults['top_axis_label_text_font_size']
        if position == 'top':
            fig.yaxis.major_label_text_font_size = defaults['top_axis_label_text_font_size']
        else:
            fig.yaxis.major_label_text_font_size = defaults['bottom_axis_label_text_font_size']
        fig.yaxis.axis_label_text_color      = defaults['axis_label_text_color']
        fig.yaxis.axis_label   = y_axis_label
        fig.yaxis[0].formatter = NumeralTickFormatter(format=axis_format)

    @staticmethod
    def _get_initial_x_offset(metrics):
        '''Returns initial bar offset for bar plot'''
        if len(metrics) == 3: return -.25
        if len(metrics) == 4: return -.375
        if len(metrics) == 5: return -.5
        print(f'_get_initial_x_offset: metrics length {len(metrics)} not handled')
        return 0

    @staticmethod
    def _get_bar_shift(metrics):
        '''Returns shift amount bw successive bars'''
        if len(metrics) == 3: return .75/3
        if len(metrics) == 4: return .8/4
        if len(metrics) == 5: return .75/5
        print(f'_get_bar_shift`; metrics length {len(metrics)} not handled')
        return 0


    def _build_bar_plots(self, fig, defaults:dict, years:list, metrics:list, plot_type:str, source:ColumnDataSource):
        '''Builds bar plots (metrics) on primary axis'''
        x_pos = self._get_initial_x_offset(metrics)
        bar_shift = self._get_bar_shift(metrics)
        bar_width = defaults['bar_width_shift_ratio'] * bar_shift
        for i, metric in enumerate(metrics):
            vbar = fig.vbar(x      = dodge('year', x_pos, FactorRange(*years)),
                            bottom = 1e-6,
                            top    = metric,
                            width  = bar_width,
                            source = source,
                            color  = defaults['palette'][i],
                            legend_label = self._map_item_to_name(metric),
                            )
            self._build_bar_tooltip(fig, vbar, metrics, plot_type)
            x_pos += bar_shift


    def _build_line_plots(self, fig, defaults:dict, metrics:list, source:ColumnDataSource):
        '''Builds line plots (metrics change) on secondary axis'''
        for i, metric in enumerate(metrics):
            legend_label = self._map_item_to_name(metric)
            line = fig.line(x = 'year',
                            y = metric,
                            line_width = 1,
                            line_dash = defaults['line_dash'],
                            color = defaults['palette'][i],
                            legend_label = legend_label,
                            source = source,
                            )
            fig.circle(x='year',
                       y=metric,
                       color=defaults['palette'][i],
                       fill_color='white',
                       size=5,
                       legend_label=legend_label,
                       source = source,
                       )
        self._build_line_tooltips(fig, line, metrics)
        self._build_zero_growth_line(fig, defaults)

    @staticmethod
    def _build_line_caption(text:str, x_value:float, y_value:float, x_units:str, y_units:str, color, font_size:int):
        return Label(x = x_value,
                     y = y_value,
                     x_units = x_units,
                     y_units = y_units,
                     text    = text,
                     text_color     = color,
                     text_font_size = font_size,
                     )


    def _build_zero_growth_line(self, fig, defaults:dict):
        '''Builds zero growth horizontal line on secondary axis'''
        # Build line
        zero_growth = Span(location   = 0.0,
                           dimension  ='width',
                           line_color = defaults['zero_growth_line_color'],
                           line_dash  = defaults['zero_growth_line_dash'],
                           line_width = defaults['zero_growth_line_thickness'],
                           )
        fig.add_layout(zero_growth)
        # Add annotation
        fig.add_layout(self._build_line_caption(text      = '',
                                                x_value   = 2,
                                                y_value   = 0,
                                                x_units   = 'screen',
                                                y_units   = 'data',
                                                color     = defaults['zero_growth_font_color'],
                                                font_size = defaults['zero_growth_font_size'],
                                                )
                        )


    def _build_wb_benchmarks(self, fig, defaults:dict):
        '''
        Plots horizontal lines corresponding to Buffet benchmarks for the
        3 ratios: roe, current ratio & debt to equity
        '''
        # Build line
        benchmarks = ['roe_benchmark', 'debt_to_equity_benchmark','current_ratio_benchmark']
        for idx, benchmark in enumerate(benchmarks):
            bmk = Span(location   = defaults[benchmark],
                       dimension  ='width',
                       line_color = defaults['palette'][idx],
                       line_dash  = defaults['benchmark_line_dash'],
                       line_width = defaults['benchmark_line_thickness'],
                       )
            fig.add_layout(bmk)
            #Add annotation
            text = benchmark.replace('_', ' ')
            text += f': {defaults[benchmark]}'
            fig.add_layout(self._build_line_caption(text      = text,
                                                    x_value   = 2,
                                                    y_value   = defaults[benchmark],
                                                    x_units   = 'screen',
                                                    y_units   = 'data',
                                                    color     = 'dimgray',#defaults['palette'][idx],
                                                    font_size = defaults['benchmark_font_size'],
                                                    )
                               )


    def _build_means_lines(self, fig, defaults:dict, means:dict):
        '''Plots means lines for each metric'''
        for idx, (metric, mean) in enumerate(means.items()):
            mean_line = Span(location   = mean,
                              dimension  ='width',
                              line_color = defaults['palette'][idx],
                              line_dash  = defaults['means_line_dash'],
                              line_width = defaults['means_line_thickness'],
                              )
            fig.add_layout(mean_line)
            #Add annotation
            text  = 'mean ' + self._map_item_to_name(metric).lower()
            text += f': {numerize.numerize(mean)}'
            fig.add_layout(self._build_line_caption(text      = text,
                                                    x_value   = 2,
                                                    y_value   = mean,
                                                    x_units   = 'screen',
                                                    y_units   = 'data',
                                                    color     = 'dimgray',#defaults['palette'][idx],
                                                    font_size = defaults['means_font_size'],
                                                    )
                           )


    def _build_line_tooltips(self, fig, line, metrics:list):
        '''Build tooltips for line plots'''
        tooltips = [('','@year')]
        for metric in metrics:
            tooltips.append( (self._map_item_to_name(metric),
                              f'@{metric}'+"{0.0%}")
                            )
        hover_tool = HoverTool(tooltips   = tooltips,
                               show_arrow = True,
                               renderers  = [line],
                               mode       = 'vline',
                               )
        fig.add_tools(hover_tool)


    def _build_bar_tooltip(self, fig, barplot, metrics:list, plot_type:str):
        '''Build tooltips for bar plots'''
        tooltip = [('','@year')]
        for metric in metrics:
            if plot_type in ['wb', 'dupont']:
                prefix = ''
            else:
                prefix = f'{self._currency_symbol}'
            tooltip.append((self._map_item_to_name(metric),
                            prefix+f'@{metric}'+"{0.00a}",
                            ))
        hover_tool = HoverTool(tooltips   = tooltip,
                               show_arrow = True,
                               renderers  = [barplot],
                               mode       = 'vline',
                               )
        fig.add_tools(hover_tool)


    def fundamentals_plot(self, time_series:pd.DataFrame, plot_type:str, subtitle:str, filename:str):
        '''
        Generic time series bokeh plot for values (bars) and their growth (lines)
        plot_type: either of revenue, bs (balance sheet), dupont, wb ("warren buffet")
        '''
        defaults = self.get_plot_defaults()
        time_series.replace(np.inf, 0, inplace=True) # replace infinity values with 0
        time_series.index.name = 'year'
        time_series.index      = time_series.index.astype('string')
        cds                    = ColumnDataSource(data = time_series)

        if plot_type in ['wb', 'dupont']:
            top_y_axis_label = 'ratio'
        else:
            top_y_axis_label = f'{self.get_currency().capitalize()}'
        cols = time_series.columns.tolist()
        metrics = cols[0:int(len(cols)/2)]
        d_metrics = cols[int(len(cols)/2):]

        # Build a dictionary of metrics and their respective means
        means = dict(zip(metrics, time_series[metrics].mean().tolist()))

        #max value for primary y axis
        max_y = time_series[metrics].max().max()
        if plot_type == 'wb':
            max_y = max(max_y, round_up(defaults['current_ratio_benchmark'], 1))

        panels = []
        for axis_type in ['linear', 'log']:
            if axis_type == 'linear':
                min_y = round_down(time_series[metrics].min().min(), 1)
            else: min_y = 1e-6
            # Initialize top plot (data / bars)
            plot_top = self._initialize_plot(position  = 'top',
                                             min_y     = min_y,
                                             max_y     = max_y,
                                             axis_type = axis_type,
                                             defaults  = defaults,
                                             source    = cds,
                                             )
            # Initialize bottom plot (changes / lines)
            plot_bottom = self._initialize_plot(position  = 'bottom',
                                                max_y     = round_up(time_series[d_metrics].max().max(), 1),
                                                min_y     = round_down(time_series[d_metrics].min().min(), 1),
                                                axis_type = 'linear',
                                                defaults  = defaults,
                                                source    = cds,
                                                linked_figure = plot_top
                                                )
            # Add title to top plot
            self._build_title_bokeh(fig      = plot_top,
                                    defaults = defaults,
                                    subtitle = subtitle,
                                    )
            # Add bars to top plot
            self._build_bar_plots(fig       = plot_top, # top blot is bar plot
                                  defaults  = defaults,
                                  years     = time_series.index.tolist(),
                                  metrics   = metrics,
                                  plot_type = plot_type,
                                  source    = cds,
                                  )
            self._build_means_lines(fig      = plot_top,
                                    defaults = defaults,
                                    means    = means,
                                    )
            # Ad WB benchmarks to WB plots
            if plot_type == 'wb':
                self._build_wb_benchmarks(fig      = plot_top,
                                          defaults = defaults,
                                          )
            # Add lines to bottom plot
            self._build_line_plots(fig       = plot_bottom, # bottom plot is line plot
                                   defaults  = defaults,
                                   metrics   = d_metrics,
                                   source    = cds,
                                   )
            # Format axes and legends on top & bottom plots
            for plot in [plot_top, plot_bottom]:
                if plot == plot_top:
                    y_axis_label = top_y_axis_label
                    fmt = "0.0a"
                    position = 'top'
                else:
                    y_axis_label = 'time \u0394'
                    fmt = "0.%"
                    position = 'bottom'
                self._build_axes(fig      = plot,
                                 position = position,
                                 defaults = defaults,
                                 y_axis_label = y_axis_label,
                                 axis_format  = fmt
                                 )
                self._position_legend(fig      = plot,
                                      defaults = defaults,
                                      )
            # Merge top & bottom plots into column
            plot = column(plot_top, plot_bottom, sizing_mode='stretch_width')
            panel = Panel(child=plot, title=axis_type)
            panels.append(panel)
        #self._build_caption_bokeh(fig = panels)
        tabs = Tabs(tabs=panels)
        show(tabs)
        # Save plot to tile
        output_file(filename)
        save(tabs)
