#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 22:39:05 2021

Examines the moments of distribution of the value of a stock

@author: charles mégnin
"""
import scipy
import datetime as dt
import pandas as pd
import numpy as np
from sklearn import linear_model
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate
import security as sec
import portfolio_io as pio
import utilities as util


def linear_regression(data):
    ''' Performs a linear regression on the Date and Close columns'''
    data_x = pd.to_datetime(data['Date'])
    data_x = data_x.map(dt.datetime.toordinal)

    data_x = data_x.values.reshape(-1, 1)
    data_y = data['Close'].values

    # Create linear regression object
    regr = linear_model.LinearRegression()

    # Train the model using the training sets
    regr.fit(data_x, data_y)
    y_pred = regr.predict(data_x)

    return data_x, data_y, y_pred


def plot_data(title, data, data_y, y_pred):
    ''' Plot raw data '''
    sdev = np.std(data_y-y_pred)
    plt.plot(data['Date'], y_pred,          c='r', linestyle='dashed', linewidth=1)
    plt.plot(data['Date'], data_y)
    plt.plot(data['Date'], y_pred - sdev,   c='y', linestyle='dotted', linewidth=1)
    plt.plot(data['Date'], y_pred + sdev,   c='y', linestyle='dotted', linewidth=1)
    plt.plot(data['Date'], y_pred - 2*sdev, c='g', linestyle='dotted', linewidth=1)
    plt.plot(data['Date'], y_pred + 2*sdev, c='g', linestyle='dotted', linewidth=1)
    plt.title(title)
    plt.ylabel('price (log)')
    plt.grid(True)
    plt.show()


def plot_detrended_data(name, data, delta_y):
    ''' plots de-trended data where linear regression has been removed '''
    sdev = delta_y.std()
    plt.plot(data['Date'], delta_y)
    plt.axhline(y =       0, color = 'r', linestyle = 'dashed', linewidth=1)
    plt.axhline(y =    sdev, color = 'y', linestyle = 'dotted', linewidth=1)
    plt.axhline(y =   -sdev, color = 'y', linestyle = 'dotted', linewidth=1)
    plt.axhline(y =  2*sdev, color = 'g', linestyle = 'dotted', linewidth=1)
    plt.axhline(y = -2*sdev, color = 'g', linestyle = 'dotted', linewidth=1)
    plt.ylabel('detrended price (log)')
    plt.title(f'{name}')
    plt.grid(True)
    plt.show()


def plot_histogram(name, delta_y, stats):
    ''' Plots a histogram of the departures from the mean in the de-trended data '''
    sns.displot(data=delta_y, bins=10, kde=True)
    plt.axvline(x = delta_y.mean(),     color = 'r', linestyle='dashed', linewidth=1)
    plt.axvline(x = np.median(delta_y), color = 'k', linestyle='dashed', linewidth=1)
    plt.title(f'{name}\n'
              f'(skew={stats["skewness"]:.2f} '
              f'kurt={stats["kurtosis"]:.1f})')
    plt.xlabel('D from mean')
    plt.grid(True)
    plt.show()


def moments(name, delta_y, verbose=False):
    ''' computes skewness & kurtosis of the data and performs
        Jarque-Bera test for normalcy
    '''
    stats = {}
    stats['variable']    = name
    stats['count']       = delta_y.shape[0]
    stats['mean']        = delta_y.mean()
    stats['median']      = delta_y.median()
    stats['mode']        = delta_y.mode()
    stats['sdev']        = delta_y.std()
    stats['skewness']    = util.skewness(delta_y)
    stats['kurtosis']    = util.kurtosis(delta_y)
    stats['jarque-bera'] = util.is_normal(delta_y)

    if verbose:
        print(f'{name}: '
              f'count={stats["count"]:d}, '
              f'mean={stats["mean"]:.2g}, '
              f'median={stats["median"]:.2g}, '
              f'mode={stats["mode"]}, '
              f'sdev={stats["sdev"]:.2g}, '
              f'skewness={stats["skewness"]:.2g}, '
              f'kurtosis={stats["kurtosis"]:.2g}\n'
              f'Jarque-Bera: statistic={stats["jarque-bera"][0]:.2f} '
              f'p-value={stats["jarque-bera"][1]:.2g} '
              f'Normal={stats["jarque-bera"][2]}')

    return stats


def extract_nested_values(it):
    if isinstance(it, list):
        for sub_it in it:
            yield from extract_nested_values(sub_it)
    elif isinstance(it, dict):
        for value in it.values():
            yield from extract_nested_values(value)
    else:
        yield it


if __name__ == '__main__':
    # periods: 1d,5d,1mo,3mo,6mo,1y,2y,3y,5y,10y,ytd,max
    PERIOD = 'max'

    csv_df  = pio.load_csv('cac_40')
    results = {}

    for ii, ticker in enumerate(csv_df.Valeur):
        # if ii == 2:
        #     break
        security = sec.Security(ticker, PERIOD)
        sec_name = security.get_name()
        prices   = security.get_close()

        prices.columns = ['Date', 'Close']
        #prices.iloc[:,1] = prices.iloc[:,1]/prices.iloc[:,1].shift(1)
        prices.iloc[:,1] = np.log(prices.iloc[:,1])
        prices = prices.dropna()

        X, y, y_hat = linear_regression(prices)
        stat = moments(sec_name, y - y_hat)
        print(f'{prices.shape[0]} data points')

        plot_data(sec_name, prices, y, y_hat)
        plot_detrended_data(sec_name, prices, y - y_hat)
        plot_histogram(sec_name, y - y_hat, stat)

        results[sec_name] = extract_nested_values(stat)
    summary = pd.DataFrame(results).transpose()
    cols = ['count', 'mean', 'sdev', 'skew', 'kurt', 'JB_stat', 'p-value', 'normal']
    summary.columns=cols
    print (tabulate(summary,
                    headers=cols,
                    floatfmt=('d', 'd', '.3g', '.3f','.2f', '.2f', '.3g', '.2g')))

    summary.to_csv('summary.csv', sep=',', encoding='utf-8')
