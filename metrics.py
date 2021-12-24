#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 12:35:47 2021

metrics.py - metrics/ratio & values

metrics-related definitions & utilities

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

metric_set : bs_metrics etc
metrics: collection of metrics

@author: charles megnin
"""
import sys
import inspect


# Set name and plot title
metrics_set_names = {'bs_metrics'         : 'Balance sheet metrics',
                     'income_metrics'     : 'Income & Free cash flow metrics',
                     'income2_metrics'    : 'Income & Free cash flow metrics #2',
                     'wb_metrics'         : '"Warren Buffet" metrics',
                     'dupont_metrics'     : 'Dupont metrics',
                     'debt_metrics'       : 'Debt metrics',
                     'valuation_metrics'  : 'Valuation metrics',
                     'valuation2_metrics' : 'Valuation metrics #2',
                     'dividend_metrics'   : 'Dividend metrics',
                     }

metrics_tooltip_format = {'bs_metrics'         : '{0.0a}',
                          'income_metrics'     : '{0.0a}',
                          'income2_metrics'    : '{0.0%}',
                          'wb_metrics'         : '{0.0a}',
                          'dupont_metrics'     : '{0.0a}',
                          'debt_metrics'       : '{0.0%}',
                          'valuation_metrics'  : '{0.0a}',
                          'valuation2_metrics' : '{0.0a}',
                          'dividend_metrics'   : '{0.0%}',
                          }

def get_tooltip_format(metric):
    return metrics_tooltip_format[metric]

def get_metric_set_names():
    return list(metrics_set_names.keys())

    return [name.replace('_metrics', '') for name in get_metric_set_names()]

bs_metrics         = {'totalAssets': 0., 'totalLiabilities': 0., 'totalStockholdersEquity': 0.,}
income_metrics     = {'revenue': 0., 'ebit': 0., 'freeCashFlow': 0.,}
income2_metrics    = {'grossProfitRatio': 0., 'ebitPerRevenue': 0., 'freeCashFlowToRevenue': 0.,'croic':0}
wb_metrics         = {'returnOnEquity':.08, 'debtToEquity':0.5, 'currentRatio':1.5,}
dupont_metrics     = {'returnOnEquity':.08, 'netProfitMargin':0, 'assetTurnover':0, 'equityMultiplier':0,}
debt_metrics       = {'debtToEquity':0.5, 'debtToAssets':0, 'interestCoverage':0, \
                      'shortTermCoverageRatios':0,}
valuation_metrics  = {'priceToBookRatio':0, 'peg':0,}
valuation2_metrics = {'peRatio':0, 'evToebit':0, 'priceToSalesRatio':0,}
dividend_metrics   = {'dividendYield':0, 'payoutRatio':0,}
full_dupont_metrics = {'cashReturnOnEquity':0, 'returnOnEquity':.08, 'netProfitMargin':0, \
                       'assetTurnover':0, 'equityMultiplier':0, 'cashConv':0, 'roa':0,}


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
            'shortTermCoverageRatios': 'ST coverage ratio: ST debt / Operating cash flow',
            'ROE':               'ROE: Net income / Total shareholder equity',
            }

# Captions appear at the bottom of the plots
metrics_captions = {'dupont_metrics'    : f'{captions["ROE"]} | {captions["netProfitMargin"]} | \
                    {captions["assetTurnover"]} | {captions["equityMultiplier"]}',
                    'wb_metrics'        : f'{captions["ROE"]} | {captions["debtToEquity"]} | {captions["currentRatio"]}',
                    'valuation_metrics' : f'{captions["priceToBookRatio"]} | {captions["peg"]}',
                    'valuation2_metrics': f'{captions["peRatio"]} | {captions["evToebit"]} | {captions["priceToSalesRatio"]}',
                    'income2_metrics'   : f'{captions["grossProfitRatio"]} | {captions["ebitPerRevenue"]}| {captions["freeCashFlowToRevenue"]}',
                    'dividend_metrics'  : f'{captions["dividendYield"]} | {captions["payoutRatio"]}',
                    'debt_metrics'      : f'{captions["debtToEquity"]} | {captions["debtToAssets"]} | \
                    {captions["netDebtToebit"]} | {captions["interestCoverage"]} | {captions["shortTermCoverageRatios"]}',
                    'bs_metrics'        : '',
                    'income_metrics'    : '',
                    }


def get_metrics_set_caption(metrics_set):
    '''Utility to return metrics_captions value from key. If no caption, return blank'''
    try:
        return metrics_captions[metrics_set]
    except:
        print(f'get_metrics_set_caption: metrics_set {metrics_set} has no associated caption')
        return ''


def get_metrics(group:str, metric:str=None):
    '''returns metric value group=dictionary name / metric=metric kind.
        If no metric specified, return dictionary'''
    try:
        if metric is None:
            exec(f'return {group}')
        exec(f'return {group}[{metric}]')
        caller_name = inspect.stack()[1][3]
        func_name   = inspect.stack()[0][3]
        msg         = f'{func_name}: non-existent group in {caller_name}'
        raise ValueError(msg)
    except:
        raise ValueError(f'get_metrics: unknown metric "{group}"')


#REFACTOR AS A LIST COMPREHENSION
def map_items_to_names(items:list):
    '''Recursively calls map_item_to_name() on elements in items'''
    names = []
    for item in items:
        names.append(map_item_to_name(item))
    return names


def map_item_to_name(item:str):
    '''Converts column name to readable metric (WIP)'''
    if item.startswith('d_'):
        return '\u0394 ' + map_item_to_name(item[2:])
    itemdict = {'assetturnover':           'Asset turnover',
                'croic':                   'Cash ROIC',
                'currentratio':            'Current ratio',
                'debttoassets':            'Debt-to-assets ratio',
                'debttoequity':            'Debt-to-equity ratio',
                'dividendyield':           'Dividend yield',
                'ebit':                    'EBIT',
                'ebitperrevenue':          'EBIT-to-revenue',
                'evtoebit':                'E.V.-to-ebit',
                'equitymultiplier':        'Equity multiplier',
                'freecashflow':            'FCF',
                'grossprofitratio':        'Gross profit margin',
                'interestcoverage':        'Interest coverage',
                'freecashflowtorevenue':   'FCF-to-revenue',
                'netdebttoebit':           'Net debt-to-ebit',
                'netprofitmargin':         'Net profit margin',
                'payoutratio':             'Payout ratio',
                'peg':                     'P/E-to-growth',
                'peratio':                 'P/E ratio',
                'pricetobookratio':        'Price-to-book ratio',
                'pricetosalesratio':       'Price-to-sales ratio',
                'returnonequity':          'ROE',
                'revenue':                 'Revenue',
                'roic':                    'ROIC',
                'shorttermcoverageratios': 'Short term coverage ratio',
                'totalassets':             'Total assets',
                'totalliabilities':        'Total liabilities',
                'totalstockholdersequity': "Total stockholders' equity",
                }
    try:
        return itemdict[item.lower()]
    except:
        print(f'map_item_to_name(): No mapping for item "{item}"')
        return item # return as is if not in dictionary
