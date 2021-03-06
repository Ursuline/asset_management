#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  7 19:42:16 2021

All-purpose use utilities

@author: charles mégnin
"""
import time
from datetime import datetime
import pprint
import math
import pandas as pd
import scipy.stats
from dateutil.relativedelta import relativedelta
from finance import moments

MAX_YEARS = 20 # number of years corresponding to 'max'

def display_stats(data, feature):
    '''
    Display statistics about data and engineered features
    '''
    stat = moments.moments(feature, data[feature])
    pprint.pprint(stat)


def drawdown(return_series: pd.Series):
    ''' Takes a time series of asset returns
        Computes & returns a dataframe that contains:
        - the wealth index
        - the previous peaks
        - percent drawdown
    '''
    wealth_index   = 1000 * (1 + return_series).cumprod()
    previous_peaks = wealth_index.cummax()
    drawdowns      = (wealth_index - previous_peaks) / previous_peaks
    return pd.DataFrame({
        'Wealth': wealth_index,
        'Peaks' : previous_peaks,
        'Drawdown' : drawdowns
    })


def semideviation(arr):
    '''
    Returns the semi-deviation (aka negative semi-deviation)
    '''
    is_negative = arr<0
    return arr[is_negative].std(ddof=0)


def skewness(data):
    '''
    Alternative to scipy.stats.skew()
    '''
    demeaned_d = data - data.mean()
    #use population sdev: dof=0
    sigma_d = data.std(ddof=0)
    exp = (demeaned_d**3).mean()
    return exp/sigma_d**3


def kurtosis(data):
    '''
    Alternative to scipy.stats.kurtosis()
    '''
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
    return dict(zip(['statistic', 'p-value', 'normal'], [statistic, p_value, p_value > level]))


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
        t_diff = datetime.timedelta(days=int(period[:-1]))
    elif period[-1] == 'o' and period[-2] == 'm':
        t_diff = relativedelta(months=int(period[:-2]))
    else:
        raise ValueError(f'invalid period {period}')
    return datetime.now() - t_diff


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


def get_start_date(start_str, window: int):
    '''
    Returns start date before rolling window
    '''
    start  = datetime.strptime(start_str, '%Y-%m-%d')
    return (start - datetime.timedelta(window)).date()


def get_return(data, ticker, purchase_date, sale_date):
    '''
    Given purchase and sale date, return absolute & relative profit/loss
    '''
    if ticker not in data.columns:
        raise ValueError(f'{ticker} inconsistent with data')
    if purchase_date not in data.index:
        raise ValueError(f'purchase date {purchase_date} not in data')
    if sale_date not in data.index:
        raise ValueError(f'sale date {sale_date} not in data')
    purchase_price = data.loc[purchase_date, ticker]
    sale_price     = data.loc[sale_date, ticker]
    print(f'{ticker}: '
          f'{purchase_date} purchase ${purchase_price:.2f} / '
          f'{sale_date} sale ${sale_price:.2f}')

    d_price = sale_price-purchase_price
    if datetime.strptime(sale_date, '%Y-%m-%d') > \
        datetime.strptime(purchase_date, '%Y-%m-%d'):
        rel_price = d_price/purchase_price
    else:
        rel_price = d_price/sale_price

    return d_price, rel_price

### DATE & TIME ###

def convert_seconds(time_s):
    '''
    Given a time duration in seconds, convert to DHMS & return as a string
    '''
    minute = 60
    hour   = 60 * minute
    day    = 24 * hour
    def sec_to_min(sec):
        time_m = sec // minute
        time_s = sec % minute
        return time_m, time_s

    def sec_to_hour(sec):
        time_h = sec // hour
        time_s = sec % hour
        time_m, time_s = sec_to_min(time_s)
        return time_h, time_m, time_s

    def sec_to_day(sec):
        time_d = sec // day
        time_s = sec % day
        time_h, time_m, time_s = sec_to_hour(time_s)
        return time_d, time_h, time_m, time_s

    if time_s >= day:
        time_d, time_h, time_m, time_s = sec_to_day(time_s)
        suffix = 'day'
        if time_d > 1:
            suffix += 's'
        return f'{time_d:.0f} {suffix} {time_h:.0f}hr:{time_m:.0f}mn:{time_s:.1f}s'
    if time_s >= hour:
        time_h, time_m, time_s = sec_to_hour(time_s)
        return f'{time_h:.0f}hr:{time_m:.0f}mn:{time_s:.1f}s'
    if time_s >= minute:
        time_m, time_s = sec_to_min(time_s)
        return f'{time_m:.0f}mn:{time_s:.1f}s'
    return f'{time_s:.1f}s'


def get_summary_stats(data, level, target):
    '''
    Return a dictionary of summary statistics and test for normality
    '''
    summary_stats = dict()
    summary_stats['mean'] = data[target].mean()
    summary_stats['std']  = math.sqrt(data[target].var())
    summary_stats['skewness']  = scipy.stats.skew(data[target], nan_policy='omit')
    summary_stats['kurtosis']  = scipy.stats.kurtosis(data[target], nan_policy='omit')
    statistic, p_value = scipy.stats.jarque_bera(data[target])
    summary_stats['jb']  = dict(zip(['statistic', 'p-value', 'gaussian', 'level'],
                                    [statistic, p_value, p_value > level, level]))
    return summary_stats


### DATETIME Utilities ###
def to_dt_format(start_date_string, end_date_string, fmt):
    '''
    Returns start and end dates in datetime format from start_date & end_date
    in string format
    '''
    start_dt   = datetime.strptime(start_date_string, fmt)
    end_dt     = datetime.strptime(end_date_string,   fmt)
    return[start_dt, end_dt]


def reset_dates(security, date_range):
    '''
    Checks if requested start and end dates are prent in the dataset
    if not, returns best date range
    '''
    secu_start = security.index[0]
    secu_end   = security.index[-1]
    start_dt = date_range[0]
    end_dt   = date_range[1]
    # Check if data downloaded otherwise start with earliest date
    if secu_start > date_range[0]:
        print(f'start date reset from {date_range[0].date()} to {secu_start.date()}')
        start_dt = secu_start
    if secu_end < date_range[1]:
        end_dt = secu_end
        print(f'end date reset from {date_range[1].date()} to {secu_end.date()}')
    if start_dt > end_dt:
        raise ValueError('reset_dates: start date {start_dt} later than end date {end_dt}')
    return [start_dt, end_dt]


def get_date_range(security, start_date, end_date):
    '''
    Return start and end dates in datetime format by:
        1. converting to datetime format
        2. checking for consistency in dates
    '''
    fmt = '%Y-%m-%d'
    date_range = to_dt_format(start_date, end_date, fmt)
    date_range = reset_dates(security, date_range)
    return date_range


def date_to_string(date, fmt):
    '''Convert date time date to string with specified format'''
    return date.strftime(fmt)


def dates_to_strings(date_range, fmt='%d-%b-%Y'):
    '''
    takes a range of datetime dates and returns the string equivalent
    in the required format (default='%d-%b-%Y')
    '''
    # start = date_range[0]
    # end   = date_range[1]
    # start_string = start.strftime(fmt)
    # end_string   = end.strftime(fmt)
    return [date_to_string(date_range[0], fmt), date_to_string(date_range[1], fmt)]

def print_running_time(ticker, start_tm, save_tm):
    '''Called by trading_driver for leap time'''
    msg  = f'{ticker} running time: '
    msg += f'{convert_seconds(time.time()-save_tm)} | '
    msg += 'elapsed time: '
    msg += f'{convert_seconds(time.time()-start_tm)}\n'
    print(msg)
