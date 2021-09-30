#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 21 14:47:36 2021

@author: charles mégnin
"""
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

import pandas_datareader as pdr
from pandas_datareader import wb
from pandas_datareader.yahoo.headers import DEFAULT_HEADERS
import FundamentalAnalysis as fa

import requests_cache

import api_keys as keys

KEY = keys.ALPHA_VANTAGE
CACHE_DAYS = 3


if __name__ == '__main__':
    expire_after = dt.timedelta(days=CACHE_DAYS)
    session = requests_cache.CachedSession(cache_name   = 'cache',
                                           backend      = 'sqlite',
                                           expire_after = expire_after
                                           )
    session.headers = DEFAULT_HEADERS

    print(f'{DEFAULT_HEADERS}')

    ticker = "AAPL"
    api_key = keys.FMP

    # Show the available companies
    companies = fa.available_companies(api_key)
    print(f'companies:{companies}')

    # Collect general company information
    profile = fa.profile(ticker, api_key)
    print(f'profile:{profile}')

    # Collect recent company quotes
    quotes = fa.quote(ticker, api_key)
    print(f'quotes:{quotes}')

    # Collect market cap and enterprise value
    entreprise_value = fa.enterprise(ticker, api_key)
    print(f'entreprise_value:{entreprise_value}')

    # Show recommendations of Analysts
    ratings = fa.rating(ticker, api_key)
    print(f'ratings:{ratings}')

    # Obtain DCFs over time
    dcf_annually = fa.discounted_cash_flow(ticker, api_key, period="annual")
    dcf_quarterly = fa.discounted_cash_flow(ticker, api_key, period="quarter")
    print(f'dcf_quarterly:{dcf_quarterly}')

    # Collect the Balance Sheet statements
    balance_sheet_annually = fa.balance_sheet_statement(ticker, api_key, period="annual")
    balance_sheet_quarterly = fa.balance_sheet_statement(ticker, api_key, period="quarter")
    print(f'balance_sheet_quarterly:{balance_sheet_quarterly}')

    # Collect the Income Statements
    income_statement_annually = fa.income_statement(ticker, api_key, period="annual")
    income_statement_quarterly = fa.income_statement(ticker, api_key, period="quarter")
    print(f'income_statement_quarterly:{income_statement_quarterly}')

    # Collect the Cash Flow Statements
    cash_flow_statement_annually = fa.cash_flow_statement(ticker, api_key, period="annual")
    cash_flow_statement_quarterly = fa.cash_flow_statement(ticker, api_key, period="quarter")
    print(f'cash_flow_statement_quarterly:{cash_flow_statement_quarterly}')

    # Show Key Metrics
    key_metrics_annually = fa.key_metrics(ticker, api_key, period="annual")
    key_metrics_quarterly = fa.key_metrics(ticker, api_key, period="quarter")
    print(f'key_metrics_quarterly:{key_metrics_quarterly}')

    # Show a large set of in-depth ratios
    financial_ratios_annually = fa.financial_ratios(ticker, api_key, period="annual")
    financial_ratios_quarterly = fa.financial_ratios(ticker, api_key, period="quarter")
    print(f'financial_ratios_quarterly:{financial_ratios_quarterly}')

    # Show the growth of the company
    growth_annually = fa.financial_statement_growth(ticker, api_key, period="annual")
    growth_quarterly = fa.financial_statement_growth(ticker, api_key, period="quarter")
    print(f'growth_quarterly:{growth_quarterly}')

    # Download general stock data
    stock_data = fa.stock_data(ticker, period="ytd", interval="1d")
    print(f'stock_data:{stock_data}')

    # Download detailed stock data
    stock_data_detailed = fa.stock_data_detailed(ticker, api_key, begin="2000-01-01", end="2020-01-01")
    print(f'stock_data_detailed:{stock_data_detailed}')