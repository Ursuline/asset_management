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
import datetime as dt
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

import FundamentalAnalysis as fa
import cache as ksh
import api_keys as keys
import metrics as mtr
import utilities as util

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
        self._beta = None
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
        self._beta         = self._profile.loc['beta'][0]
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


    def get_beta(self):
        '''Returns symbol corresponding to currency'''
        return self._beta


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
            date  = data.loc['date']
            price = data.loc['Stock Price']
            dcf   = data.loc['DCF']
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
            return data.loc[int(year)]


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
            return data.loc[int(year)]


    def get_netIncome(self, year:str, change:bool=False):
        '''Return net income'''
        item = 'netIncome'
        return self._get_income_statement_item(item=item, year=year, change=change)


    def get_incomeTaxExpense(self, year:str, change:bool=False):
        '''Return income tax expense'''
        item = 'incomeTaxExpense'
        return self._get_income_statement_item(item=item, year=year, change=change)


    def get_interestExpense(self, year:str, change:bool=False):
        '''Return interest expense'''
        item = 'interestExpense'
        return self._get_income_statement_item(item=item, year=year, change=change)


    def get_grossProfitRatio(self, year:str, change:bool=False):
        '''Return gross profit ratio'''
        item = 'grossProfitRatio'
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
        net_income = self.get_netIncome(year=year, change=change)
        tax_expense = self.get_incomeTaxExpense(year=year, change=change)
        interest_expense = self.get_interestExpense(year=year, change=change)
        if (ebitda-depam) != (net_income+tax_expense+interest_expense):
            msg = 'WARNING: get_ebit(): '
            msg += f"ebit calculation doesn't check: ebitda-depam={ebitda-depam} "
            msg += f'NI+TE+IE={net_income+tax_expense+interest_expense}'
            print(msg)
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
            return data.loc[int(year)]


    def get_freeCashFlow(self, year:str, change:bool=False):
        '''Returns free cash flow or change in FCF'''
        item = 'freeCashFlow'
        return self._get_cash_flow_statement_item(item=item, year=year, change=change)


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
            query = data.loc[int(year)]
            if query is None:
                print(f'_get_financial_ratios_item(): item {item} is None in the data set')
                return 0
            return query


    def get_netProfitMargin(self, year:str, change:bool=False):
        '''Returns net profit margin (net income/revenue) or change in NPR'''
        item = 'netProfitMargin'
        return self._get_financial_ratios_item(item=item, year=year, change=change)


    def get_ebitPerRevenue(self, year:str, change:bool=False):
        '''Returns EBIT/Sales or its change'''
        item = 'ebitPerRevenue'
        return self._get_financial_ratios_item(item=item, year=year, change=change)


    def get_assetTurnover(self, year:str, change:bool=False):
        '''Returns asset turnover (revenue/avg total assets) or change in A.T.'''
        item = 'assetTurnover'
        return self._get_financial_ratios_item(item=item, year=year, change=change)


    def get_returnOnAssets(self, year:str, change:bool=False):
        '''Returns return on assets (net income/total assets) or change in ROA'''
        item = 'returnOnAssets'
        return self._get_financial_ratios_item(item=item, year=year, change=change)


    def get_priceEarningsToGrowthRatio(self, year:str, change:bool=False):
        '''Returns PE ratio or change in PE over time'''
        item = 'priceEarningsToGrowthRatio'
        return self._get_financial_ratios_item(item=item, year=year, change=change)


    def get_priceToBookRatio(self, year:str, change:bool=False):
        '''Returns P/B ratio (price to book) or change in P/B'''
        item = 'priceToBookRatio'
        return self._get_financial_ratios_item(item=item, year=year, change=change)


    def get_roe(self, year:str, change:bool=False):
        '''Returns ROE or change in ROE'''
        item = 'returnOnEquity'
        return self._get_financial_ratios_item(item=item, year=year, change=change)


    def get_shortTermCoverageRatios(self, year:str, change:bool=False):
        '''Returns *inverse of* short term coverage ratio or its change'''
        item = 'shortTermCoverageRatios'
        ratio = self._get_financial_ratios_item(item=item, year=year, change=change)
        if ratio == 0:
            return 0
        return 1.0/ratio


    ### key metrics data ###
    def _get_key_metrics_item(self, item:str, year:str, change:bool=False):
        '''Returns generic key metrics item or its time change'''
        try:
            data = self.get_key_metrics().loc[item]

            if change:
                data = data[::-1].pct_change()
        except KeyError:
            caller_name = inspect.stack()[1][3]
            func_name   = inspect.stack()[0][3]
            msg=f'{caller_name} > {func_name}: {self.get_ticker()} item {item} or year {year} data unvailable\n'
            print(msg)
            return 0
        else :
            data.index = data.index.astype(int)
            return data.loc[int(year)]


    def get_enterpriseValue(self, year:str, change:bool=False):
        '''Returns enterpriuse value (assets + liabs - cash) or its change'''
        item = 'enterpriseValue'
        return self._get_key_metrics_item(item=item, year=year, change=change)


    def get_payoutRatio(self, year:str, change:bool=False):
        '''Returns payout ratio (dividend rate / earnings) or change in payout ratio'''
        item = 'payoutRatio'
        return self._get_key_metrics_item(item=item, year=year, change=change)


    def get_marketCap(self, year:str, change:bool=False):
        '''Returns market cap or change in market cap'''
        item = 'marketCap'
        return self._get_key_metrics_item(item=item, year=year, change=change)


    def get_interestCoverage(self, year:str, change:bool=False):
        '''Returns *inverse of* interest coverage or its change'''
        item = 'interestCoverage'
        return 1.0 / self._get_key_metrics_item(item=item, year=year, change=change)


    def get_currentRatio(self, year:str, change:bool=False):
        '''Returns current ratio or change in current ratio'''
        item = 'currentRatio'
        return self._get_key_metrics_item(item=item, year=year, change=change)


    def get_peRatio(self, year:str, change:bool=False):
        '''Returns price/earnings ratio or change in p/e ratio'''
        item = 'peRatio'
        return self._get_key_metrics_item(item=item, year=year, change=change)


    def get_dividendYield(self, year:str, change:bool=False):
        '''Returns Dividend yield or its change'''
        item = 'dividendYield'
        return self._get_key_metrics_item(item=item, year=year, change=change)


    def get_debtToAssets(self, year:str, change:bool=False):
        '''Returns debt to assets ratio or its change'''
        item = 'debtToAssets'
        return self._get_key_metrics_item(item=item, year=year, change=change)


    def get_debtToEquity(self, year:str, change:bool=False):
        '''Returns debt to equity ratio or change in debt to equity ratio'''
        item = 'debtToEquity'
        return self._get_key_metrics_item(item=item, year=year, change=change)


    def get_priceToSalesRatio(self, year:str, change:bool=False):
        '''Returns price to sales ratio or its change'''
        item = 'priceToSalesRatio'
        return self._get_key_metrics_item(item=item, year=year, change=change)


    def get_roic(self, year:str, change:bool=False):
        '''Returns return on invested capital or its change
        ebit/(totalAsset - totalCurrentLiabilities)
        '''
        item = 'roic'
        return self._get_key_metrics_item(item=item, year=year, change=change)


    def get_netDebtToEBITDA(self, year:str, change:bool=False):
        '''Returns net debt / ebitda or its change'''
        item = 'netDebtToEBITDA'
        return self._get_key_metrics_item(item=item, year=year, change=change)


    ### Derived metrics ###
    def get_croic(self, year:str, change:bool=False):
        '''Returns cash return on invested capital = FCF/ebit*roic'''
        try:
            roic = self.get_roic(year=year, change=False)
            fcf  = self.get_freeCashFlow(year=year, change=False)
            ebit = self.get_ebit(year=year, change=False)
            if ebit in [0]:
                print('get_croic(): {year} - ebit=0 / croic set to 0')
                return 0
            if change is True:
                d_roic = self.get_roic(year=year, change=True)
                d_fcf  = self.get_freeCashFlow(year=year, change=True)
                d_ebit = self.get_ebit(year=year, change=True)
                return ((d_fcf*roic+fcf*d_roic)*ebit - d_ebit*fcf*roic)/(ebit*ebit)
            return fcf*roic/ebit
        except:
            print('get_croic(): {year} - inconsistent value / croic set to 0')
            return 0


    def get_evToebit(self, year:str, change:bool=False):
        '''Returns enterprise value to ebit ratio or change '''
        ev   = self.get_enterpriseValue(year=year, change=False)
        ebit = self.get_ebit(year=year, change=False)
        if ebit == 0:
            print('get_evToebit(): {year} - ebit=0 / ev to ebit set to 0')
            return 0
        if change is True:
            d_ev   = self.get_enterpriseValue(year=year, change=True)
            d_ebit = self.get_ebit(year=year, change=True)
        if change is False:
            return ev/ebit
        return (d_ev*ebit-d_ebit*ev)/(ebit*ebit)


    def get_freeCashFlowToRevenue(self, year:str, change:bool=False):
        '''Returns FCF to revenue ratio or its change'''
        fcf   = self.get_freeCashFlow(year=year, change=False)
        revenue = self.get_revenue(year=year, change=False)
        if revenue == 0:
            print('get_freeCashFlowToRevenue(): {year} - revenue=0 / fcf to revenue set to 0')
            return 0
        if change is True:
            d_fcf     = self.get_freeCashFlow(year=year, change=True)
            d_revenue = self.get_revenue(year=year, change=True)
        if change is False:
            return fcf/revenue
        return (d_fcf*revenue-d_revenue*fcf)/(revenue*revenue)


    def get_cashConversion(self, year:str, change:bool=False):
        '''Returns cash conversion (FCF/Net income) or change in CC'''
        fcf    = self.get_freeCashFlow(year, change=False)
        income = self.get_netIncome(year, change=False)
        if income == 0:
            print('get_cashConversion(): {year} - income=0 / cash conversion set to 0')
            return 0
        if change:
            d_fcf = self.get_freeCashFlow(year, change=True)
            d_income = self.get_netIncome(year, change=True)
            return (d_fcf*income - d_income/fcf)/(income**2)
        return fcf/income


    def get_equityMultiplier(self, year:str, change:bool=False):
        '''Returns equity multiplier = Total Assets/Total Equity or change in EM'''
        assets = self._get_balance_sheet_item('totalAssets', year, change=False)
        equity = self._get_balance_sheet_item('totalStockholdersEquity', year, change=False)
        if equity == 0:
            print('get_cashConversion(): {year} - equity=0 / cequity multiplier set to 0')
            return 0
        if change:
            d_assets = self._get_balance_sheet_item('totalAssets', year, change=True)
            d_equity = self._get_balance_sheet_item('totalStockholdersEquity', year, change=True)
            return (d_assets*equity - d_equity/assets)/(equity**2)
        return assets/equity


    def get_netDebtToebit(self, year:str, change:bool=False):
        '''Returns net debt to ebit or its change D/EBIT = D/EBITDA*EBITDA/EBIT'''
        ndtoebitda = self.get_netDebtToEBITDA(year=year, change=False)
        ebitda     = self.get_ebitda(year=year, change=False)
        ebit       = self.get_ebit(year=year, change=False)
        if ebit == 0:
            print('get_netDebtToebit(): {year} - ebit=0 / net debt to ebit set to 0')
            return 0
        if change is True:
            d_ndtoebitda = self.get_netDebtToEBITDA(year=year, change=True)
            d_ebitda     = self.get_ebitda(year=year, change=True)
            d_ebit       = self.get_ebit(year=year, change=True)
            return d_ndtoebitda*ebitda/ebit + ndtoebitda*(d_ebitda*ebit-d_ebit*ebitda)/(ebit*ebit)
        return ndtoebitda*ebitda/ebit


    def get_cashReturnOnEquity(self, year:str, change:bool=False):
        '''Returns cash return on equity (ROE*cash conversion) or change in CROE'''
        roe = self.get_roe(year=year, change=False)
        cash_conv = self.get_cashConversion(year=year, change=False)
        if change:
            d_roe       = self.get_roe(year=year, change=True)
            d_cash_conv = self.get_cashConversion(year=year, change=True)
            return d_roe*cash_conv + roe*d_cash_conv
        return roe*cash_conv


    # def get_peers(self):
    #     '''return peers as defined in API (***not preferred method***)'''
    #     return util.extract_peers(self._ticker, API_KEY)


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
            dic_yr = self.load_cie_metrics(year=year, req_metrics=metrics)
            dic_met[year]= dic_yr
        dfr = pd.DataFrame(dic_met).transpose()
        dfr.index.name = 'year'
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

    # REFACTOR THIS: THERE'S GOTTA BE A BETTER WAY
    def load_cie_metrics(self, year:str, req_metrics:list):
        '''load metrics values corresponding to keys in cie_metrics, save as dictionary & return'''
        cie_metrics = {}
        for metric in req_metrics:
            if metric == 'assetTurnover':
                cie_metrics['assetTurnover'] = self.get_assetTurnover(year=year)
            elif metric =='cashConv':
                cie_metrics['cashConv'] = self.get_cashConversion(year=year)
            elif metric == 'cashReturnOnEquity':
                cie_metrics['cashReturnOnEquity'] = self.get_cashReturnOnEquity(year=year)
            elif metric == 'croic':
                cie_metrics['croic'] = self.get_croic(year=year)
            elif metric == 'currentRatio':
                cie_metrics['currentRatio'] = self.get_currentRatio(year=year)
            elif metric == 'debtToAssets':
                cie_metrics['debtToAssets'] = self.get_debtToAssets(year=year)
            elif metric == 'debtToEquity':
                cie_metrics['debtToEquity'] = self.get_debtToEquity(year=year)
            elif metric == 'dividendYield':
                cie_metrics['dividendYield'] = self.get_dividendYield(year=year)
            elif metric == 'ebit':
                cie_metrics['ebit'] = self.get_ebit(year=year)
            elif metric == 'ebitPerRevenue':
                cie_metrics['ebitPerRevenue'] = self.get_ebitPerRevenue(year=year)
            elif metric == 'enterpriseValue':
                cie_metrics['enterpriseValue'] = self.get_enterpriseValue(year=year)
            elif metric == 'evToebit':
                cie_metrics['evToebit'] = self.get_evToebit(year=year)
            elif metric == 'equityMultiplier':
                cie_metrics['equityMultiplier'] = self.get_equityMultiplier(year=year)
            elif metric == 'freeCashFlow':
                cie_metrics['freeCashFlow'] = self.get_freeCashFlow(year=year)
            elif metric == 'freeCashFlowToRevenue':
                cie_metrics['freeCashFlowToRevenue'] = self.get_freeCashFlowToRevenue(year=year)
            elif metric == 'grossProfitRatio':
                cie_metrics['grossProfitRatio'] = self.get_grossProfitRatio(year=year)
            elif metric == 'interestCoverage':
                cie_metrics['interestCoverage'] = self.get_interestCoverage(year=year)
            elif metric =='marketCap':
                cie_metrics['marketCap'] = self.get_marketCap(year=year)
            elif metric =='netDebtToebit':
                cie_metrics['netDebtToebit'] = self.get_netDebtToebit(year=year)
            elif metric =='netIncome':
                cie_metrics['netIncome'] = self.get_netIncome(year=year)
            elif metric == 'netProfitMargin':
                cie_metrics['netProfitMargin'] = self.get_netProfitMargin(year=year)
            elif metric == 'payoutRatio':
                cie_metrics['payoutRatio'] = self.get_payoutRatio(year=year)
            elif metric == 'peg':
                cie_metrics['peg'] = self.get_priceEarningsToGrowthRatio(year=year)
            elif metric == 'priceEarningsToGrowthRatio':
                cie_metrics['priceEarningsToGrowthRatio'] = self.get_priceEarningsToGrowthRatio(year=year)
            elif metric == 'priceToBookRatio':
                cie_metrics['priceToBookRatio'] = self.get_priceToBookRatio(year=year)
            elif metric == 'priceToSalesRatio':
                cie_metrics['priceToSalesRatio'] = self.get_priceToSalesRatio(year=year)
            elif metric == 'peRatio':
                cie_metrics['peRatio'] = self.get_peRatio(year=year)
            elif metric == 'returnOnAssets':
                cie_metrics['returnOnAssets'] = self.get_returnOnAssets(year=year)
            elif metric == 'roa':
                cie_metrics['roa'] = self.get_returnOnAssets(year=year)
            elif metric == 'roe':
                cie_metrics['roe'] = self.get_roe(year=year)
            elif metric == 'roic':
                cie_metrics['roic'] = self.get_roic(year=year)
            elif metric == 'returnOnEquity':
                cie_metrics['returnOnEquity'] = self.get_roe(year=year)
            elif metric =='revenue':
                cie_metrics['revenue'] = self.get_revenue(year=year)
            elif metric =='shortTermCoverageRatios':
                cie_metrics['shortTermCoverageRatios'] = self.get_shortTermCoverageRatios(year=year)
            elif metric =='totalAssets':
                cie_metrics['totalAssets'] = self.get_totalAssets(year=year)
            elif metric =='totalLiabilities':
                cie_metrics['totalLiabilities'] = self.get_totalLiabilities(year=year)
            elif metric =='totalStockholdersEquity':
                cie_metrics['totalStockholdersEquity'] = self.get_totalStockholdersEquity(year=year)
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
        cie_metrics = list(self.load_cie_metrics(year, metrics_keys))
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
        title=self._build_title(f'{self.get_company_name()} ({self.get_ticker()})', '')

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
        title=self._build_title(f'{self.get_company_name()} ({self.get_ticker()})','')

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

    # @staticmethod
    # def _get_metric_lists():
    #     revenue_list = ['revenue', 'freeCashFlow', 'ebit']
    #     asset_list   = ['totalAssets', 'totalLiabilities', 'totalStockholdersEquity']
    #     dupont_list  = ['cashReturnOnEquity', 'returnOnEquity', 'returnOnAssets','netProfitMargin', 'assetTurnover', 'equityMultiplier']
    #     wb_list = ['returnOnEquity', 'debtToEquity', 'currentRatio']
    #     valuation_list = ['priceToBook', 'peg']
    #     d_revenue_list = []
    #     for item in revenue_list:
    #         d_revenue_list.append(f'd_{item}')
    #     d_asset_list = []
    #     for item in asset_list:
    #         d_asset_list.append(f'd_{item}')
    #     d_dupont_list = []
    #     for item in dupont_list:
    #         d_dupont_list.append(f'd_{item}')
    #     d_wb_list = []
    #     for item in wb_list:
    #         d_wb_list.append(f'd_{item}')
    #     return revenue_list+asset_list+dupont_list+wb_list, d_revenue_list+d_asset_list+d_dupont_list+d_wb_list

    # @staticmethod
    # def _get_legend_attributes(defaults, col):
    #     '''Return legend color and label from column name'''
    #     if col == 'revenue':
    #         color = defaults['linecolors'][0]
    #         legend_name = 'Revenue'
    #     elif col == 'freeCashFlow':
    #         color = defaults['linecolors'][1]
    #         legend_name = 'FCF'
    #     elif col == 'ebit':
    #         color = defaults['linecolors'][2]
    #         legend_name = 'EBIT'
    #     elif col == 'totalAssets':
    #         color = defaults['linecolors'][0]
    #         legend_name = 'Assets'
    #     elif col == 'totalLiabilities':
    #         color = defaults['linecolors'][1]
    #         legend_name = 'Liabilities'
    #     elif col == 'totalStockholdersEquity':
    #         color = defaults['linecolors'][2]
    #         legend_name = "Shareholder's Equity"
    #     elif col == 'returnOnEquity':
    #         color = defaults['linecolors'][0]
    #         legend_name = "ROE"
    #     elif col == 'netProfitMargin':
    #         color = defaults['linecolors'][1]
    #         legend_name = "Net profit margin"
    #     elif col == 'assetTurnover':
    #         color = defaults['linecolors'][2]
    #         legend_name = "Asset turnover"
    #     elif col == 'equityMultiplier':
    #         color = defaults['linecolors'][3]
    #         legend_name = "Equity multiplier"
    #     elif col == 'debtToEquity':
    #         color = defaults['linecolors'][1]
    #         legend_name = "Debt to equity"
    #     elif col == 'currentRatio':
    #         color = defaults['linecolors'][2]
    #         legend_name = "Current ratio"
    #     elif col == 'priceToBook':
    #         color = defaults['linecolors'][0]
    #         legend_name = "P/B"
    #     elif col == 'dividendYield':
    #         color = defaults['linecolors'][0]
    #         legend_name = "Dividend yield"
    #     elif col == 'payoutRatio':
    #         color = defaults['linecolors'][1]
    #         legend_name = "Payout ratio"

    #     elif col == 'd_revenue':
    #         color = defaults['linecolors'][0]
    #         legend_name = '\u0394 Revenue'
    #     elif col == 'd_freeCashFlow':
    #         color = defaults['linecolors'][1]
    #         legend_name = "\u0394 FCF"
    #     elif col == 'd_ebit':
    #         color = defaults['linecolors'][2]
    #         legend_name = "\u0394 EBIT"
    #     elif col == 'd_totalAssets':
    #         color = defaults['linecolors'][0]
    #         legend_name = '\u0394 Assets'
    #     elif col == 'd_totalLiabilities':
    #         color = defaults['linecolors'][1]
    #         legend_name = '\u0394 Liabilities'
    #     elif col == 'd_totalStockholdersEquity':
    #         color = defaults['linecolors'][2]
    #         legend_name = "\u0394 Shareholder's Equity"
    #     elif col == 'd_returnOnEquity':
    #         color = defaults['linecolors'][0]
    #         legend_name = "\u0394 ROE"
    #     elif col == 'd_netProfitMargin':
    #         color = defaults['linecolors'][1]
    #         legend_name = "\u0394 Net profit margin"
    #     elif col == 'd_assetTurnover':
    #         color = defaults['linecolors'][2]
    #         legend_name = "\u0394 Asset turnover"
    #     elif col == 'd_equityMultiplier':
    #         color = defaults['linecolors'][3]
    #         legend_name = "\u0394 Equity multiplier"
    #     elif col == 'd_debtToEquity':
    #         color = defaults['linecolors'][1]
    #         legend_name = "\u0394 Debt to equity"
    #     elif col == 'd_currentRatio':
    #         color = defaults['linecolors'][2]
    #         legend_name = "\u0394 Current ratio"
    #     elif col == 'd_priceToBook':
    #         color = defaults['linecolors'][0]
    #         legend_name = "\u0394 P/B"
    #     elif col == 'dividendYield':
    #         color = defaults['linecolors'][0]
    #         legend_name = "\u0394 Dividend yield"
    #     elif col == 'payoutRatio':
    #         color = defaults['linecolors'][1]
    #         legend_name = "\u0394 Payout ratio"
    #     return color, legend_name
