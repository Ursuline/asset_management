#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 09:52:09 2021

Driver for fundamental analysis plot sequence

@author: charles mégnin
"""
import os
#import pandas as pd
import plotly.io as pio
import company as cny

pio.renderers.default = 'browser'

PERIOD   = 'annual'
PLOT_DIR = 'plots'

# Target company specs
TICKER          = 'ABI.BR'
EXPIRATION_DATE = '2021-12-31'
YEAR_0          = int('2013')
YEAR_1          = int('2020')


def get_balance_sheet(cie, yr_0:int, yr_1:int):
    '''
    Returns a dataframe with assets, liabilities & equity and their relative changes over time
    '''
    items = ['totalAssets', 'totalLiabilities', 'totalStockholdersEquity']
    return cie.get_metrics_over_time(items, yr_0, yr_1)


def get_revenue_fcf_ebit(cie, yr_0:int, yr_1:int):
    '''
    Returns a dataframe with revenue, free cash flow & EBIT and their relative changes over time
    '''
    items = ['revenue', 'ebit', 'freeCashFlow']
    return cie.get_metrics_over_time(items, yr_0, yr_1)


def get_dupont_metrics(cie, yr_0:int, yr_1:int):
    '''
    Returns a dataframe with cash ROE, ROE, net profit margin, asset turnover, equity multiplier
    '''
    items = ['returnOnEquity', 'netProfitMargin', 'assetTurnover', 'equityMultiplier']
    return cie.get_metrics_over_time(items, yr_0, yr_1)


def get_wb_metrics(cie, yr_0:int, yr_1:int):
    '''
    Returns a dataframe with ROE, debt to equity, current ratio
    '''
    items = ['returnOnEquity', 'debtToEquity', 'currentRatio']
    return cie.get_metrics_over_time(items, yr_0, yr_1)


def get_valuation_metrics(cie, yr_0:int, yr_1:int):
    '''
    Returns a dataframe with PEG, debt to equity, current ratio
    '''
    items = ['returnOnEquity', 'debtToEquity', 'currentRatio']
    return cie.get_metrics_over_time(items, yr_0, yr_1)



if __name__ == '__main__':
    os.makedirs(PLOT_DIR, exist_ok = True)
    company = cny.Company(ticker=TICKER, period=PERIOD, expiration_date=EXPIRATION_DATE)
    root = f'{TICKER}_{YEAR_0}_{YEAR_1}'

    # Build & plot revenue/FCF/EBIT dataframe
    rfe = get_revenue_fcf_ebit(company, YEAR_0, YEAR_1)
    path = os.path.join(PLOT_DIR, f'{root}_income.html')
    company.fundamentals_plot(time_series=rfe,
                              plot_type = 'revenue',
                              subtitle=f'Income & Free cash flow ({YEAR_0}-{YEAR_1})',
                              filename=path,
                              )

    # Build & plot balance sheet dataframe
    bs = get_balance_sheet(company, YEAR_0, YEAR_1)
    path = os.path.join(PLOT_DIR, f'{root}_bs.html')
    company.fundamentals_plot(time_series=bs,
                              plot_type = 'bs',
                              subtitle=f'Balance sheet ({YEAR_0}-{YEAR_1})',
                              filename=path,
                              )

    # Build & plot Dupont metrics dataframe
    dupont = get_dupont_metrics(company, YEAR_0, YEAR_1)
    path = os.path.join(PLOT_DIR, f'{root}_dupont.html')
    company.fundamentals_plot(time_series=dupont,
                              plot_type = 'dupont',
                              subtitle=f'Dupont metrics ({YEAR_0}-{YEAR_1})',
                              filename=path,
                              )

    # Build & plot Warren Buffet metrics dataframe
    wb_metrics = get_wb_metrics(company, YEAR_0, YEAR_1)
    path = os.path.join(PLOT_DIR, f'{root}_wb.html')
    company.fundamentals_plot(time_series=wb_metrics,
                              plot_type = 'wb',
                              subtitle=f'"Warren Buffet" metrics ({YEAR_0}-{YEAR_1})',
                              filename=path,
                              )
