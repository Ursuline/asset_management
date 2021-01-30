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
import asset as ast
import security as sqr

# valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,3y,5y,10y,ytd,max
NDAYS     = 252 # Number of days in the year
PERIOD    = '1y'
NUM_PORTS = 100000000 # number of portfolios
#PRECISION = 100 # percent = 100 / per 1000 = 1000, etc

#TICKERS = ['MSFT', 'AAPL', 'BRK-B', 'AMZN', 'NFLX', 'XOM']
TICKERS = ['SPIE.PA', 'ALO.PA', 'ELIS.PA', 'BNP.PA',
            'ORA.PA', 'BN.PA', 'FP.PA', 'HO.PA', 'NK.PA', 'SGO.PA',
            'KORI.PA', 'NXI.PA', 'TRI.PA', 'CA.PA' ]
# SKIPPED STLA.PA & GLE.PA
Q_S     = [100 for i in range(len(TICKERS))]
INDEX   = '^GSPC' # ^GSPC (S&P 500), ^IXIC (Nasdaq), ^DJI (Dow Jones)

#Helper utilities
def sample_space(returns_df):
    ''' Explore NUM_PORTS portfolio combinations returns_df is log(returns) '''
    ncolumns  = len(returns_df.columns)
    p_weights = np.zeros((NUM_PORTS, ncolumns))
    p_returns = np.zeros(NUM_PORTS)
    p_volat   = np.zeros(NUM_PORTS)
    p_sharpe  = np.zeros(NUM_PORTS)

    for port in range(NUM_PORTS):
        if port % 1000000 == 0:
            print(f'Iteration {port}/{NUM_PORTS}', end='\r10', flush=True)

        weights = np.array(np.random.random(ncolumns))
        #weights = np.array(np.random.randint(PRECISION, size=ncolumns))
        weights = weights/np.sum(weights)

        # Save new weight
        p_weights[port,:] = weights

        # Expected return
        p_returns[port] = np.sum( (returns_df.mean() * weights * NDAYS))

        # Expected volatility = W^T . COV . W
        p_volat[port] = np.sqrt(np.dot(weights.T, np.dot(returns_df.cov() * NDAYS, weights)))

        p_sharpe[port] = p_returns[port]/p_volat[port]

    return p_weights, p_returns, p_volat, p_sharpe


def display_result(description, p_returns, p_volat, wts, index):
    opt_ret = p_returns[index]
    opt_vol = p_volat[index]

    print(f'{description} portfolio:')
    print(f'{NUM_PORTS} portfolio combinations')
    print(f'weights: {wts[index,:]}\n'
          f'Return={np.exp(opt_ret):.4f}, '
          f'Volatility={opt_vol:.4f}, '
          f'Sharpe ratio={opt_ret/opt_vol:.4f}')

def display_allocation(description, portfolio, wts, index):
    print(f"{description} asset allocation ({portfolio.value:.2f} {portfolio.currency}):")
    for i, weight in enumerate(wts[index,:]):
        name = portfolio.assets[i].symbol
        allocation = portfolio.value * weight
        price = portfolio.assets[i].price
        opt_q = int(round(allocation/price))
        print(f'{name}: {allocation:.2f} {portfolio.currency} = '
              f'{opt_q} * {price:.2f} {portfolio.currency}')
    print()


def plot_rvs(sharpe, volat, ret, idx, period):
    ''' Plot distribution '''
    SHAPE_SZ    = 75
    SHAPE_COLOR = 'red'
    markers = ('o', 's', 'd') # markers for max Sharpe, min volatility and max return

    # shr_ret = ret[idx[0]] # Sharpe
    # shr_vol = volat[idx[0]]
    # min_ret = ret[idx[1]] # Volatility
    # min_vol = volat[idx[1]]
    # max_ret = ret[idx[2]] # Revenue
    # max_vol = volat[idx[2]]

    plt.figure(figsize=(12,8))

    # plot all portfolios
    plt.scatter(volat, ret, c=sharpe, cmap='viridis')
    # plot max sharpe portfolio
    # plt.scatter(shr_vol, shr_ret, c=SHAPE_COLOR, s=SHAPE_SZ, marker='o') # red dot
    # # plot min volatility portfolio
    # plt.scatter(min_vol, min_ret, c=SHAPE_COLOR, s=SHAPE_SZ, marker='s') # red square
    # # plot max revenue portfolio
    # plt.scatter(max_vol, max_ret, c=SHAPE_COLOR, s=SHAPE_SZ, marker='d') # red diamond

    # Plot max sharpe, min volatility and max return portfolios
    for i in range(3):
        plt.scatter(volat[idx[i]], ret[idx[i]], c=SHAPE_COLOR, s=SHAPE_SZ, marker=markers[i])

    plt.colorbar(label = 'Sharpe Ratio')
    plt.xlabel('Volatility')
    plt.ylabel('Return (log)')
    plt.title(f'{NUM_PORTS} portfolios (basis={period})')

    plt.show()


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
        # Sample portfolio space. Returns weights, returns, volatility & sharpe ratios
        all_weights, ret_arr, vol_arr, sharpe_arr = sample_space(self.log_ret)

        print('\n')
        # #indices = list() # 0:Max Sharpe 1:Max Revenue 2:Min volatility
        indices = (sharpe_arr.argmax(), vol_arr.argmin(), ret_arr.argmax())
        descrip = ('Max Sharpe', 'Min volatility', 'Max revenue')

        for i in range(3):
            display_result(descrip[i], ret_arr, vol_arr, all_weights, indices[i])
            display_allocation(descrip[i], self, all_weights, indices[i])

        plot_rvs(sharpe_arr, vol_arr, ret_arr, indices, self.period)

        constraints = ({'type':'eq', 'fun':self.check_sum})
        bounds = list()
        for asset in self.assets:
            bounds.append((0, 1))

        # init_guess = list()
        # for asset in self.assets:
        #     init_guess.append(1./len(self.assets))

        # opt_results = opt.minimize(neg_sharpe,
        #                             init_guess,
        #                             method='SLSQP',
        #                             bounds=bounds,
        #                             constraints=constraints)

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

    assets = list()

    for q, ticker in enumerate(TICKERS):
        assets.append(ast.Asset(sqr.Security(ticker, PERIOD), Q_S[q]))

    portfolio = Portfolio(assets)
    portfolio.describe()
    portfolio.efficient_frontier()
    print(f"Run time : {(time.time() - start_time):.0f}s ---")
