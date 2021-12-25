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
#import sys
import inspect
import yaml
import plotter_defaults as dft

def get_metric_set_data():
    '''Returns metric-set data from yaml file'''
    with open(dft.get_metric_sets_path()) as file:
        try:
            data = yaml.safe_load(file)
        except yaml.YAMLError as exception:
            print(exception)
    return data


def get_metrics_data():
    '''Returns individual metrics data from yaml file'''
    with open(dft.get_metrics_path()) as file:
        try:
            data = yaml.safe_load(file)
        except yaml.YAMLError as exception:
            print(exception)
        except FileNotFoundError as exception:
            print(exception)
    return data


def get_tooltip_format(metric):
    '''Return tooltip format from yaml file'''
    yaml_data = get_metric_set_data()
    return yaml_data[metric]['tooltip_format']


def get_metric_set_names():
    '''Returns the names of the metric sets'''
    yaml_data = get_metric_set_data()
    return list(yaml_data.keys())


def get_metric_set_description(met_set:str):
    '''Returns the desciption of a metric sets'''
    yaml_data = get_metric_set_data()
    return yaml_data[met_set]['description']


def get_set_metrics(met_set:str):
    '''Return metrics in a metric set'''
    yaml_data = get_metric_set_data()
    return yaml_data[met_set]['metrics']


def map_item_to_name(metric:str):
    '''Converts metric code to readable format defined in yaml file'''
    if metric.startswith('d_'):
        return '\u0394 ' + map_item_to_name(metric[2:])
    yaml_data = get_metrics_data()
    keys      = list(yaml_data.keys()) # clone keys
    for key in keys: # set all keys to lower case
        if key.lower() != key:
            yaml_data[key.lower()] = yaml_data[key]
            del yaml_data[key]
    try:
        return yaml_data[metric.lower()]['name']
    except:
        print(f'map_item_to_name(): No mapping for "{metric}"')
        return metric # return as is if not in dictionary
    return yaml_data[metric.lower()]['name']


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
