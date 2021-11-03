#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 12:35:47 2021

metrics.py - metrics/ratio & values

ratios & related-utilities

@author: charly
"""
import inspect

metrics_set_names = {'wb_metrics':'Warren Buffet', 'dupont_metrics': 'Dupont'}

# warren buffet metrics
wb_metrics  = {'debtToEquity':0.5, 'currentRatio':1.5, 'roe':.08}

# Dupont metrics split cash return on equity (CROE) into:
# net profit margin * asset turnover * equity multiplier * cash conversion
#        |__________________|
#                ROA
#                 |____________________________|
#                                ROE
#                                 |______________________________|
#                                                CROE
# net profit margin -> profitability
# asset turnover -> efficiency of management
# equity multiplier = asset/equity -> leverage
# cash conversion -> Free cash-flow / Net income
# roe = NI / Equity & croe = FCF / Equity
dupont_metrics = {'netProfitMargin':0, 'assetTurnover':0, 'equityMultiplier':0, 'cashConv':0, 'roa':0, 'roe':0.08, 'cashReturnOnEquity':0}


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

        caller_name = inspect.stack()[1][3]
        func_name   = inspect.stack()[0][3]
        msg         = f'{func_name}: non-existent group in {caller_name}'
        raise ValueError(msg)
    except:
        raise ValueError('problem')
