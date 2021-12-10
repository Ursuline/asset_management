#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 12:35:47 2021

metrics.py - metrics/ratio & values

ratios & related-utilities

@author: charly
"""
import inspect

# Set name and plot title
metrics_set_names = {'mktcap_metrics': 'Assets, Revenue & Market Cap',
                     'wb_metrics':'"Warren Buffet" metrics',
                     'dupont_metrics': 'Dupont metrics',
                     'bs_metrics': 'Balance sheet metrics',
                     'income_metrics': 'Income & Free cash flow metrics',
                     'valuation_metrics': 'Valuation metrics',
                     'valuation2_metrics': 'Valuation metrics #2',
                     'dividend_metrics': 'Dividend metrics',
                     }

wb_metrics  = {'returnOnEquity':.08, 'debtToEquity':0.5, 'currentRatio':1.5}
valuation_metrics = {'priceToBookRatio':0, 'peg':0}
valuation2_metrics = {'peRatio':0, 'evToebit':0, 'priceToSalesRatio':0}
dividend_metrics = {'dividendYield':0, 'payoutRatio':0}

captions = {'ROE':              'ROE: Net income / Total shareholder equity',
            'assetTurnover':    'Asset turnover: Sales / Mean total assets',
            'netProfitMargin': ' Net profit margin: Net income / Sales',
            'equityMultiplier': 'Equity multiplier: Total assets / Total equity',
            'cashConversion':   'Cash conversion: Free cash flow / Net income',
            'debtToEquity':     'Debt to equity ratio: Long-term debt / Total shareholder equity',
            'currentRatio':     'Current ratio: Total current assets / Total current liabilities',
            'peRatio':          'P/E ratio: Price * # of shares / Net income',
            'payoutRatio':      'Payout ratio: Dividend paid / Net income',
            'dividendYield':    'Dividend yield: Dividend paid / (Price * # of shares)',
            }

metrics_captions = {'dupont': f'{captions["ROE"]} | {captions["netProfitMargin"]} | \
                    {captions["assetTurnover"]} | {captions["equityMultiplier"]}',
                    'wb': f'{captions["ROE"]} | {captions["debtToEquity"]} | {captions["currentRatio"]}',
                    'dividend': f'{captions["payoutRatio"]} | {captions["dividendYield"]}',
                    }

mktcap_metrics = {'totalAssets': 0., 'revenue': 0., 'mktCap': 0.}

bs_metrics = {'totalAssets': 0., 'totalLiabilities': 0., 'totalStockholdersEquity': 0.}
income_metrics = {'revenue': 0., 'ebit': 0., 'freeCashFlow': 0.}



# Dupont metrics split cash return on equity (CROE) into:
# net profit margin * asset turnover * equity multiplier * cash conversion
#        |__________________|
#                ROA
#                 |____________________________|
#                                ROE
#                                 |______________________________|
#                                                CROE
# net profit margin = net income/sales -> profitability
# asset turnover = sales/mean asset ->` efficiency of management
# equity multiplier = asset/equity -> leverage
# cash conversion -> Free cash flow / Net income
# roe = NI / Equity & croe = FCF / Equity

dupont_metrics = {'returnOnEquity':.08, 'netProfitMargin':0, 'assetTurnover':0, 'equityMultiplier':0}
full_dupont_metrics = {'returnOnEquity':.08, 'netProfitMargin':0, 'assetTurnover':0, 'equityMultiplier':0, 'cashConv':0, 'roa':0, 'cashReturnOnEquity':0}

def get_metrics(group:str, metric:str=None):
    '''returns metric value group=dictionary name / metric=metric kind.
        If no metric specified, return dictionary'''
    try:
        if group == 'wb_metrics':
            if metric is None:
                return wb_metrics #return dictionary
            return wb_metrics[metric] # return value
        if group == 'dupont_metrics':
            if metric is None:
                return dupont_metrics #return dictionary
            return dupont_metrics[metric] # return value
        if group == 'mktcap_metrics':
            if metric is None:
                return mktcap_metrics #return dictionary
            return mktcap_metrics[metric] # return value
        if group == 'bs_metrics':
            if metric is None:
                return bs_metrics #return dictionary
            return bs_metrics[metric] # return value
        if group == 'income_metrics':
            if metric is None:
                return income_metrics #return dictionary
            return income_metrics[metric] # return value
        if group == 'income_metrics':
            if metric is None:
                return income_metrics #return dictionary
            return income_metrics[metric] # return value
        if group == 'valuation_metrics':
            if metric is None:
                return valuation_metrics #return dictionary
            return valuation_metrics[metric] # return value
        if group == 'valuation2_metrics':
            if metric is None:
                return valuation2_metrics #return dictionary
            return valuation2_metrics[metric] # return value
        if group == 'dividend_metrics':
            if metric is None:
                return dividend_metrics #return dictionary
            return dividend_metrics[metric] # return value

        caller_name = inspect.stack()[1][3]
        func_name   = inspect.stack()[0][3]
        msg         = f'{func_name}: non-existent group in {caller_name}'
        raise ValueError(msg)
    except:
        raise ValueError(f'metrics.py > get_metrics: unknown metric "{group}"')
