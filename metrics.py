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
import inspect
import sys
import yaml
import urllib
import plotter_defaults as dft

# ----- YAML loader methods -----
def yaml_load(file_handle):
    try:
        data = yaml.safe_load(file_handle)
    except yaml.YAMLError as exception:
        print(exception)
        sys.exit()
    return data


def get_yaml_data(datatype:str):
    '''Returns metric-set (metric_set) or metrics (metrics) data from yaml file'''
    if datatype == 'metric_set':
        func = dft.get_metric_sets_path()
    elif datatype == 'metrics':
        func = dft.get_metrics_path()
    else:
        msg = f'datatype {datatype} should be "metric_set" or "metrics"'
        raise KeyError(msg)

    if dft.METRICS_SOURCE == 'URL':
        return yaml_load(urllib.request.urlopen(func))
    else:
        with open(func) as file:
            return yaml_load(file)
# --------------------------

def get_metric_set_names():
    '''Returns the names of the metric sets'''
    yaml_data = get_yaml_data(datatype='metric_set')
    return list(yaml_data.keys())


def get_set_metrics(met_set:str):
    '''Return the metrics in a metric set as a list'''
    yaml_data = get_yaml_data(datatype='metric_set')
    try:
        return yaml_data[met_set]['metrics']
    except KeyError as exception:
        print(exception)


def get_metric_set_description(met_set:str):
    '''Returns the desciption of a metric sets'''
    yaml_data = get_yaml_data(datatype='metric_set')
    return yaml_data[met_set]['description']


def get_tooltip_format(metric:str):
    '''Return tooltip format from yaml file'''
    yaml_data = get_yaml_data(datatype='metric_set')
    return yaml_data[metric]['tooltip_format']


def map_metric_to_name(metric:str):
    '''Converts metric code to readable format defined in yaml file'''
    if metric.startswith('d_'):
        return '\u0394 ' + map_metric_to_name(metric[2:])
    yaml_data = get_yaml_data(datatype='metrics')
    keys      = list(yaml_data.keys()) # clone keys
    for key in keys: # set all keys to lower case
        if key.lower() != key:
            yaml_data[key.lower()] = yaml_data[key]
            del yaml_data[key]
    try:
        return yaml_data[metric.lower()]['name']
    except:
        print(f'map_metric_to_name(): No mapping for "{metric}"')
        return metric # return as is if not in dictionary
    return yaml_data[metric.lower()]['name']


def get_metrics_set_caption(met_set):
    metrics_data = get_yaml_data(datatype='metrics')
    metrics = get_set_metrics(met_set)
    caption = ''
    for i, metric in enumerate(metrics):
        temp = metrics_data[metric]['definition']
        if temp != '':
            caption += temp
            if i != len(metrics)-1: #don't add a separation after last metric
                caption += ' | '
    return caption


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
def map_metrics_to_names(items:list):
    '''Recursively calls map_item_to_name() on elements in items'''
    names = []
    for item in items:
        names.append(map_metric_to_name(item))
    return names
