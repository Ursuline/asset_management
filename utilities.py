#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  7 19:42:16 2021

General use utilities

@author: charles mégnin
"""
import math
import datetime as dt
import scipy.stats
from dateutil.relativedelta import relativedelta

MAX_YEARS = 20 # number of years corresponding to 'max'

def skewness(data):
    ''' Alternative to scipy.stats.skew()'''
    demeaned_d = data - data.mean()
    #use population sdev: dof=0
    sigma_d = data.std(ddof=0)
    exp = (demeaned_d**3).mean()
    return exp/sigma_d**3


def kurtosis(data):
    ''' Alternative to scipy.stats.kurtosis()'''
    demeaned_d = data - data.mean()
    #use population sdev: dof=0
    sigma_d = data.std(ddof=0)
    exp = (demeaned_d**4).mean()
    return exp/sigma_d**4


def is_normal(data, level=.01):
    '''
    Applies Jarque-Bera test at the 1% level by default
    Returns:
    JB statistic which should be 0 for normal distribution,
    p-value,
    True if r is normally distributed at the level level, False o/w
    '''
    statistic, p_value = scipy.stats.jarque_bera(data)
    return statistic, p_value, p_value > level


def get_start(period: str):
    ''' returns the start date from period assuming end date is today
        valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    '''
    if period == 'max':
        t_diff = relativedelta(years=MAX_YEARS)
    elif period == 'ytd':
        raise ValueError('ytd not implemented')
    elif period[-1] == 'y':
        t_diff = relativedelta(years=int(period[:-1]))
    elif period[-1] == 'd':
        t_diff = dt.timedelta(days=int(period[:-1]))
    elif period[-1] == 'o' and period[-2] == 'm':
        t_diff = relativedelta(months=int(period[:-2]))
    else:
        raise ValueError(f'invalid period {period}')
    return dt.datetime.now() - t_diff


def round_up(number, decimals = 0):
    ''' rounding up a number to a specified number of digits '''
    multiplier = 10 ** decimals
    return math.ceil(number * multiplier) / multiplier


def list_to_string(str_list: list):
    ''' Converts a list of strings to single string '''
    return ', '.join(map(str, str_list))


def annualized_return(rate, ndays):
    ''' Returns annnualized daily return '''
    return ndays * (pow(1. + rate/ndays, ndays) - 1.)


def relative_change(df_column):
    ''' computes relative change bw one column value & the next.
        First value is NaN'''
    return df_column.pct_change()


def absolute_change(df_column):
    ''' computes difference bw one column value & the next.
        First value is NaN'''
    return df_column - df_column.shift(1)
