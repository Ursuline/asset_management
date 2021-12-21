#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 12:35:47 2021

metrics.py - metrics/ratio & values

ratios & related-utilities

Dupont metrics split cash return on equity (CROE) into:
net profit margin * asset turnover * equity multiplier * cash conversion
        |__________________|
                ROA
                |____________________________|
                                ROE
                                |______________________________|
                                                CROE
net profit margin = net income/sales -> profitability
asset turnover = sales/mean asset ->` efficiency of management
equity multiplier = asset/equity -> leverage
cash conversion -> Free cash flow / Net income
roe = NI / Equity & croe = FCF / Equity

@author: charly
"""
import inspect

# Set name and plot title
metrics_set_names = {#'mktcap_metrics': 'Assets, Revenue & Market Cap',
                     'wb_metrics':'"Warren Buffet" metrics',
                     'dupont_metrics': 'Dupont metrics',
                     'bs_metrics': 'Balance sheet metrics',
                     'income_metrics': 'Income & Free cash flow metrics',
                     'income2_metrics': 'Income & Free cash flow metrics #2',
                     'valuation_metrics': 'Valuation metrics',
                     'valuation2_metrics': 'Valuation metrics #2',
                     'dividend_metrics': 'Dividend metrics',
                     'debt_metrics': 'Debt metrics',
                     }

#mktcap_metrics = {'totalAssets': 0., 'revenue': 0., 'marketCap': 0.,}
bs_metrics = {'totalAssets': 0., 'totalLiabilities': 0., 'totalStockholdersEquity': 0.,}
income_metrics = {'revenue': 0., 'ebit': 0., 'freeCashFlow': 0.,}
income2_metrics = {'grossProfitRatio': 0., 'ebitPerRevenue': 0., 'freeCashFlowToRevenue': 0.,'croic':0}
wb_metrics  = {'returnOnEquity':.08, 'debtToEquity':0.5, 'currentRatio':1.5,}
valuation_metrics = {'priceToBookRatio':0, 'peg':0,}
valuation2_metrics = {'peRatio':0, 'evToebit':0, 'priceToSalesRatio':0,}
dividend_metrics = {'dividendYield':0, 'payoutRatio':0,}
dupont_metrics = {'returnOnEquity':.08, 'netProfitMargin':0, 'assetTurnover':0, 'equityMultiplier':0,}
full_dupont_metrics = {'cashReturnOnEquity':0, 'returnOnEquity':.08, 'netProfitMargin':0, 'assetTurnover':0,\
                       'equityMultiplier':0, 'cashConv':0, 'roa':0,}
debt_metrics = {'debtToEquity':0.5, 'debtToAssets':0, 'interestCoverage':0, \
                'shortTermCoverageRatios':0,}

captions = {'assetTurnover':     'Asset turnover: Sales / Mean total assets',
            'cashConversion':    'Cash conversion: Free cash flow / Net income',
            'currentRatio':      'Current ratio: Total current assets / Total current liabilities',
            'debtToEquity':      'Debt-to-equity ratio: LT debt / Total shareholder equity',
            'debtToAssets':      'Debt-to-assets ratio: LT debt / Total assets',
            'dividendYield':     'Dividend yield: Dividend paid / Market cap',
            'ebitPerRevenue':    'Ebit-to-sales: ebit / Revenue',
            'equityMultiplier':  'Equity multiplier: Total assets / Total equity',
            'evToebit':          'E.V.-to-ebit: Enterprise value / ebit',
            'freeCashFlowToRevenue': 'FCF-to-revenue: FCF / Revenue',
            'grossProfitRatio':  'Gross margin: Gross profit / Revenue',
            'interestCoverage':  'Interest coverage: Interest expense / ebit',
            'netDebtToebit':     'Net debt-to-ebit: (Total debt - Cash & Cash equivalents) / ebit',
            'netProfitMargin':   'Net profit margin: Net income / Sales',
            'payoutRatio':       'Payout ratio: Dividend paid / Net income',
            'peg':               'P/E-to-growth: P/E ratio / expected growth',
            'peRatio':           'P/E ratio: Market cap / Net income',
            'priceToBookRatio':  'P/B: Market cap / Total shareholder equity',
            'priceToSalesRatio': 'P/B: Market cap / Revenue',
            'shortTermCoverageRatios': 'ST coverage ratio: ST debt / Operationg cash flow',
            'ROE':               'ROE: Net income / Total shareholder equity',
            }

metrics_captions = {'dupont'    : f'{captions["ROE"]} | {captions["netProfitMargin"]} | \
                    {captions["assetTurnover"]} | {captions["equityMultiplier"]}',
                    'wb'        : f'{captions["ROE"]} | {captions["debtToEquity"]} | {captions["currentRatio"]}',
                    'valuation' : f'{captions["priceToBookRatio"]} | {captions["peg"]}',
                    'valuation2': f'{captions["peRatio"]} | {captions["evToebit"]}| {captions["priceToSalesRatio"]}',
                    'income2'   : f'{captions["grossProfitRatio"]} | {captions["ebitPerRevenue"]}| {captions["freeCashFlowToRevenue"]}',
                    'dividend'  : f'{captions["dividendYield"]} | {captions["payoutRatio"]}',
                    'debt'      : f'{captions["debtToEquity"]} | {captions["debtToAssets"]} | \
                    {captions["netDebtToebit"]} | {captions["interestCoverage"]} | {captions["shortTermCoverageRatios"]}',
                    }

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
        # if group == 'mktcap_metrics':
        #     if metric is None:
        #         return mktcap_metrics #return dictionary
        #     return mktcap_metrics[metric] # return value
        if group == 'bs_metrics':
            if metric is None:
                return bs_metrics #return dictionary
            return bs_metrics[metric] # return value
        if group == 'income_metrics':
            if metric is None:
                return income_metrics #return dictionary
            return income_metrics[metric] # return value
        if group == 'income2_metrics':
            if metric is None:
                return income2_metrics #return dictionary
            return income2_metrics[metric] # return value
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
        if group == 'debt_metrics':
            if metric is None:
                return debt_metrics #return dictionary
            return debt_metrics[metric] # return value

        caller_name = inspect.stack()[1][3]
        func_name   = inspect.stack()[0][3]
        msg         = f'{func_name}: non-existent group in {caller_name}'
        raise ValueError(msg)
    except:
        raise ValueError(f'metrics.py > get_metrics: unknown metric "{group}"')
