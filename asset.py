#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 17:34:49 2021

List of securities downloaded from:
ftp://ftp.nasdaqtrader.com/symboldirectory

@author: charly
"""
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.optimize as opt
import security as sqr


TICKERS = ['MSFT', 'AAPL', 'BRK-B', 'AMZN', 'NFLX', 'XOM']
Q_S     = [100, 200, 250, 150, 50, 75]
INDEX   = '^GSPC' # ^GSPC (S&P 500), ^IXIC (Nasdaq), ^DJI (Dow Jones)

#Helper utilities
def sample_space(returns_df):
    ''' Explore NUM_PORTS portfolio combinations '''
    ncolumns  = len(returns_df.columns)
    p_weights = np.zeros((NUM_PORTS, ncolumns))
    p_returns = np.zeros(NUM_PORTS)
    p_volat   = np.zeros(NUM_PORTS)
    p_sharpe  = np.zeros(NUM_PORTS)

    for port in range(NUM_PORTS):
        if port % 20000 == 0:
            print(f'Iteration {port}/{NUM_PORTS}', end='\r', flush=True)

        weights = np.array(np.random.random(ncolumns))
        #weights = np.array(np.random.randint(PRECISION, size=ncolumns))
        weights = weights/np.sum(weights)

        # Save new weight
        p_weights[port,:] = weights

        # Expected return
        p_returns[port] = np.sum( (returns_df.mean() * weights * NDAYS))

        # Expected volatility
        p_volat[port] = np.sqrt(np.dot(weights.T, np.dot(returns_df.cov() * NDAYS, weights)))

        p_sharpe[port] = p_returns[port]/p_volat[port]

    return p_weights, p_returns, p_volat, p_sharpe


def display_result(description, opt_value, opt_ret, opt_vol, wts, index):
    print(f'{description} = {opt_value:.4f}')
    print(f'Location = {index}')
    print(f'weights: {wts[index,:]}, '
          f'ret={opt_ret:.4f}, '
          f'vol={opt_vol:.4f}\n')


def plot_rvs(ret, volat, sharpe, max_ret, max_vol, min_ret, min_vol, period):
    ''' Plot distribution '''
    SHAPE_SZ    = 75
    SHAPE_COLOR = 'red'

    plt.figure(figsize=(12,8))
    # all portfolios
    plt.scatter(volat, ret, c=sharpe, cmap='viridis')

    plt.colorbar(label='Sharpe Ratio')
    plt.xlabel('Volatility')
    plt.ylabel('Return')
    plt.title(f'Period = {period}')
    # max sharpe
    plt.scatter(max_vol, max_ret, c=SHAPE_COLOR, s=SHAPE_SZ, marker='o') # red dot
    # min volatility
    plt.scatter(min_vol, min_ret, c=SHAPE_COLOR, s=SHAPE_SZ, marker='s') # red square
    plt.show()


class Asset():
    ''' Class for assets in a portfolio
        Assets consist of
        - a Security object
        - the quantity held
        - convenience shortcuts to the underlying Security
        '''
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-arguments

    def __init__(self, sec, quant):
        '''sec is Security object, quant is number of assets held'''
        self.security   = sec
        self.currency   = self.security.currency
        self.close      = self.security.close
        self.name       = self.security.name
        self.symbol     = self.security.symbol
        self.type       = self.security.type
        self.period     = self.security.period
        self.quantity   = quant
        self._set_value() # compute value of asset


    def describe(self):
        '''class descriptor'''
        print(f'{self.name} ({self.symbol}) {self.type}')
        print(f'Quantity held: {self.quantity}')
        print(f'Price: {self.price:.2f} {self.currency}')
        print(f'Asset value: {self.value:.2f} {self.currency}')


    def _set_value(self):
        '''set the value of the asset held'''
        self.price = self.security.close.iloc[-1,1]
        self.value = self.quantity * self.price


    def get_value(self):
        '''return asset value = price * quantity'''
        return self.value


class Portfolio():
    '''Portfolio of assets for a given currency'''

    def __init__(self, asset_list):
        self.value    = 0.0
        self.currency = ''
        self.assets   = asset_list
        self.nassets  = len(asset_list)
        self.period   = self.assets[0].period
        self._set_value()
        self._build_return_matrix()


    def _build_return_matrix(self):
        ''' Build log returns matrix '''
        for i, asset in enumerate(self.assets):
            if i == 0:
                stocks = asset.close
            else:
                stocks = pd.merge(stocks, asset.close, on='Date', how='inner')
            stocks = stocks.rename(columns = {'Close_' + asset.symbol : asset.symbol})
        self.end_date = stocks.Date.iloc[-1]

        print(f'End date={self.end_date.date()}')

        stocks = stocks.set_index('Date')
        self.log_ret = np.log(stocks/stocks.shift(1))


    def _set_value(self):
        ''' Compute the value of the portfolio as the sum of the asset values '''
        for i, asset in enumerate(self.assets):
            if i == 0:
                self.currency = asset.currency
            if self.currency == asset.currency: # check currencies are consistent
                self.value += asset.value
            else:
                raise Exception(f'Inconsistent currency: {asset.curency} ')


    def describe(self):
        ''' Portfolio descriptor '''
        print("\n*** Portfolio ***")
        print(f'{self.nassets} assets in portfolio:')
        for i, asset in enumerate(self.assets):
            print(f'Asset {i}:')
            asset.describe()

        print(f'Total portfolio value: {self.value:.2f} {self.currency}')


    def get_rvs(self, weights):
        ''' returns return, volatility & sharpe ratio for a given weight distribution '''
        weights = np.array(weights)
        ret     = np.sum(self.log_ret.mean() * weights) * NDAYS
        vol     = np.sqrt(np.dot(weights.T, np.dot(self.log_ret.cov() * NDAYS, weights)))
        sharpe  = ret/vol
        return np.array([ret, vol, sharpe])


    def neg_sharpe(self, weights):
        ''' Returns negative Sharpe ratio to feed optimization function '''
        # 2 is the sharpe ratio index from get_rvs
        return self.get_rvs(weights)[2] * -1


    def check_sum(self, weights):
        ''' Checks that weights sum up to 1 '''
        return np.sum(weights) - 1


    def minimize_volatility(self, weights):
        return(self.get_rvs(weights)[1])



    def efficient_frontier(self):
        ''' WIP '''
        all_weights, ret_arr, vol_arr, sharpe_arr = sample_space(self.log_ret)

        max_i      = sharpe_arr.argmax()
        max_sr_vol = vol_arr[max_i]
        max_sr_ret = ret_arr[max_i]

        min_i      = vol_arr.argmin()
        min_sr_vol = vol_arr[min_i]
        min_sr_ret = ret_arr[min_i]
        print('\n\n')
        display_result('Max Sharpe ratio', sharpe_arr.max(), max_sr_ret, max_sr_vol, all_weights, max_i)
        display_result('Min volatiliy', vol_arr.min(), min_sr_ret, min_sr_vol, all_weights, min_i)


        print(f"Max Sharpe asset allocation ({self.value:.2f} {self.currency}):")
        for i, weight in enumerate(all_weights[max_i,:]):
            name = self.assets[i].symbol
            allocation = self.value * weight
            price = self.assets[i].price
            opt_q = int(round(allocation/price))
            print(f'{name}: {allocation:.2f} {self.currency} = '
                  f'{opt_q} * {price:.2f} {self.currency}')

        print(f"Min volatility asset allocation ({self.value:.2f} {self.currency}):")
        for i, weight in enumerate(all_weights[min_i,:]):
            name = self.assets[i].symbol
            allocation = self.value * weight
            price = self.assets[i].price
            opt_q = int(round(allocation/price))
            print(f'{name}: {allocation:.2f} {self.currency} = '
                  f'{opt_q} * {price:.2f} {self.currency}')

        plot_rvs(ret_arr, vol_arr, sharpe_arr, max_sr_ret, max_sr_vol, min_sr_ret, min_sr_vol, self.period)

        constraints = ({'type':'eq', 'fun':check_sum})
        bounds = list()
        for asset in self.assets:
            bounds.append((0, 1))

        init_guess = list()
        for asset in self.assets:
            init_guess.append(1./len(self.assets))

        opt_results = opt.minimize(neg_sharpe,
                                    init_guess,
                                    method='SLSQP',
                                    bounds=bounds,
                                    constraints=constraints)

        # print(get_rvs(opt_results.x))

        # frontier_y = np.linspace(0, 0.5, 200)
        # frontier_x = []

        # for possible_return in frontier_y:
        #     cons = ({'type':'eq', 'fun':check_sum},
        #             {'type':'eq', 'fun': lambda w: get_ret_vol_sr(w)[0] - possible_return})

        #     result = opt.minimize(minimize_volatility,
        #                           init_guess,
        #                           method='SLSQP',
        #                           bounds=bounds,
        #                           constraints=cons)
        #     frontier_x.append(result['fun'])

        # plt.figure(figsize=(12,8))
        # plt.scatter(vol_arr, ret_arr, c=sharpe_arr, cmap='viridis')
        # plt.colorbar(label='Sharpe Ratio')
        # plt.xlabel('Volatility')
        # plt.ylabel('Return')
        # plt.plot(frontier_x, frontier_y, 'r--', linewidth=3)
        # plt.savefig('cover.png')
        # plt.show()




#### Driver ####
if __name__ == '__main__':
    start_time = time.time()
    np.random.seed(42)

    PERIOD    = '1y'
    NDAYS     = 252 # Number of days in the year
    NUM_PORTS = 1000000 # number of portfolios
    PRECISION = 100 # percent = 100 / per 1000 = 1000, etc

    # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,3y,5y,10y,ytd,max
    assets = list()

    for q, ticker in enumerate(TICKERS):
        assets.append(Asset(sqr.Security(ticker, PERIOD), Q_S[q]))

    portfolio = Portfolio(assets)
    portfolio.describe()
    portfolio.efficient_frontier()
    print(f"Run time : {(time.time() - start_time):.0f}s ---")
