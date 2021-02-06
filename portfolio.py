#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 17:34:49 2021

A Portfolio object is a collection of Assets

@author: charly
"""
import time
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.optimize as opt
from tqdm import tqdm
import asset as ast
import security as sqr

# TICKERS = ['SPIE.PA', 'ALO.PA', 'ELIS.PA', 'BNP.PA',
#             'ORA.PA', 'BN.PA', 'FP.PA', 'HO.PA', 'NK.PA', 'SGO.PA',
#             'KORI.PA', 'NXI.PA', 'TRI.PA', 'CA.PA' ]
# TICKERS = ['MSFT', 'AAPL', 'BRK-B', 'AMZN', 'NFLX']
#Q_S     = [10 for i in range(len(TICKERS))]
#Q_S     = [500, 210, 100]

#INDEX   = '^GSPC' # ^GSPC (S&P 500), ^IXIC (Nasdaq), ^DJI (Dow Jones)

#Helper utilities
def list_to_string(str_list):
    ''' Converts a list of strings to singe string'''
    return ', '.join(map(str, str_list))


def sample_space(portfolio):
    ''' Explore NUM_PORTS portfolio combinations returns_df is log(returns) '''
    returns   = portfolio.log_ret
    ncolumns  = len(returns.columns)
    ndays     = portfolio.ndays
    p_weights = np.zeros((NUM_PORTS, ncolumns))
    p_returns = np.zeros(NUM_PORTS)
    p_volat   = np.zeros(NUM_PORTS)
    p_sharpe  = np.zeros(NUM_PORTS)

    for port in tqdm(range(NUM_PORTS)):

        weights = np.array(np.random.random(ncolumns))
        #weights = np.array(np.random.randint(PRECISION, size=ncolumns))
        weights = weights/np.sum(weights)

        # Save new weight
        p_weights[port,:] = weights

        # Expected return
        p_returns[port] = np.sum( (returns.mean() * weights * ndays))

        # Expected volatility = SQRT(W^T . COV . W)
        p_volat[port] = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * ndays, weights)))

        p_sharpe[port] = p_returns[port]/p_volat[port]

        #print(port, p_returns[port], p_volat[port], p_sharpe[port])
    print(p_returns.max(), p_sharpe.max(), p_returns.argmax(), p_sharpe.argmax())

    return p_weights, p_returns, p_volat, p_sharpe


def get_portfolio_stats(portfolio):
    ''' Compute existing portfolio weights, return, volatility & Sharpe
        ratio from Q_S '''
    ndays      = portfolio.ndays
    weights    = np.zeros(portfolio.nassets)
    returns_df = portfolio.log_ret
    for i in range(portfolio.nassets):
        weights[i]  = portfolio.assets[i].price * portfolio.assets[i].quantity
        weights[i] /= portfolio.value

    p_returns = np.sum( (returns_df.mean() * weights * ndays))
    p_volat   = np.sqrt(np.dot(weights.T, np.dot(returns_df.cov() * ndays, weights)))
    p_sharpe  = p_returns/p_volat

    return weights, p_returns, p_volat, p_sharpe


def display_result(description, p_returns, p_volat, wts, index):
    ''' Descriptor '''
    opt_ret = p_returns[index]
    opt_vol = p_volat[index]

    print(f'{description} portfolio:')
    print(f'{NUM_PORTS} portfolio combinations')
    print(f'weights: {wts[index,:]}\n'
          f'Return={opt_ret:.4f}, '
          f'Volatility={opt_vol:.4f}, '
          f'Sharpe ratio={opt_ret/opt_vol:.4f}')


def display_allocation(description, portfolio, wts, index):
    ''' Displays allocation results '''
    print(f"{description} asset allocation ({portfolio.value:.2f} {portfolio.currency}):")
    for i, weight in enumerate(wts[index,:]):
        name = portfolio.assets[i].symbol
        allocation = portfolio.value * weight
        price = portfolio.assets[i].price
        opt_q = int(round(allocation/price))
        print(f'{name}: {allocation:.2f} {portfolio.currency} = '
              f'{opt_q} * {price:.2f} {portfolio.currency}')
    print()


def plot_rvs(portfolio, title, descr, sharpe, volat, ret, idx):
    ''' Plot distribution idx has indices of the 4 portfoios of interest
        idx[0]=Sharpe idx[1]=Volat idx[2]=Return idx[3]:portfolio
    '''
    MARKER_SZ  = 100
    TITLE_SZ   = 18
    LABEL_SZ   = 12
    CAPTION_SZ = 12
    COLOR     = 'red'
    # markers for max Sharpe, min volatility, max return, portfoio
    markers  = ('o', 's', 'd', '*')
    period   = portfolio.period
    end_date = portfolio.end_date.date()

    #plt.figure(figsize=(12,8))
    fig, ax = plt.subplots(figsize=(12,8), tight_layout=True)

    # plot all portfolios
    scat = ax.scatter(volat, ret, c=sharpe, cmap='viridis')

    # Plot max sharpe, min volatility and max return portfolios
    x_offset = .0025
    for i in range(len(idx)):
        ax.scatter(volat[idx[i]], ret[idx[i]], c=COLOR, s=MARKER_SZ, marker=markers[i])
        ax.annotate(descr[i], xy =(volat[idx[i]], ret[idx[i]]),
                xytext =(volat[idx[i]] + x_offset, ret[idx[i]]))

    fig.colorbar(scat, label='Sharpe Ratio')
    ax.set_xlabel('Volatility', size=LABEL_SZ)
    ax.set_ylabel('Return (log)', size=LABEL_SZ)
    ax.set_title('Asset allocation ' + title, size=TITLE_SZ)

    caption = list_to_string(portfolio.get_asset_names()) + '\n'
    caption += f'{NUM_PORTS} portfolios (basis: {period} ending on {end_date})'
    fig.text(.01, -0.05, caption, ha='left', wrap=True, size=CAPTION_SZ, style='italic')

    plt.show()


class Portfolio():
    '''Portfolio of Assets for a given currency'''

    def __init__(self, asset_list):
        self.value    = 0.0
        self.currency = ''
        self.assets   = asset_list
        self.nassets  = len(asset_list)
        self.period   = self.assets[0].period
        self._set_value()
        self._build_return_matrix()


    def _build_return_matrix(self):
        ''' Build log returns matrix
            Extract & stores end date and # of days '''
        for i, asset in enumerate(self.assets):
            if i == 0:
                stocks = asset.close
            else:
                stocks = pd.merge(stocks, asset.close, on='Date', how='inner')
            stocks = stocks.rename(columns = {'Close_' + asset.symbol : asset.symbol})
        self.end_date = stocks.Date.iloc[-1]

        stocks       = stocks.set_index('Date')
        self.log_ret = np.log(stocks/stocks.shift(1))
        self.ndays   = stocks.shape[0]
        print(f"Number of days in portfolio: {self.period}/{self.ndays} days")


    def _set_value(self):
        ''' Compute the value of the portfolio as the sum of the asset values '''
        for i, asset in enumerate(self.assets):
            if i == 0:
                self.currency = asset.currency
            if self.currency == asset.currency: # check currencies are consistent
                self.value += asset.value
            else:
                raise Exception(f'Inconsistent currency: {asset.curency} ')


    def get_asset_names(self):
        names = list()
        for asset in self.assets:
            names.append(asset.name)
        return names


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
        ret     = np.sum(self.log_ret.mean() * weights) * self.ndays
        vol     = np.sqrt(np.dot(weights.T, np.dot(self.log_ret.cov() * self.ndays, weights)))
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
        ''' return minimum volatility '''
        return self.get_rvs(weights)[1]


    def efficient_frontier(self, title):
        ''' WIP '''
        # Sample portfolio space. Returns weights, returns, volatility & sharpe ratios
        all_weights, ret_arr, vol_arr, sharpe_arr = sample_space(self)

        # add portfolio from Q_S as last value im arrays
        p_weights, p_returns, p_volat, p_sharpe = get_portfolio_stats(self)
        all_weights = np.vstack([all_weights, p_weights])
        ret_arr     = np.append(ret_arr, p_returns)
        vol_arr     = np.append(vol_arr, p_volat)
        sharpe_arr  = np.append(sharpe_arr, p_sharpe)

        print('\n')
        # 0:Max Sharpe 1:Min volatility 2:Max Revenue 3: Portfolio
        indices = (sharpe_arr.argmax(), vol_arr.argmin(), ret_arr.argmax(), sharpe_arr.shape[0]-1)
        print(f'Indices: {sharpe_arr.argmax()} {vol_arr.argmin()} {ret_arr.argmax()} {sharpe_arr.shape[0]-1}')
        descrip = ('Max Sharpe', 'Min volatility', 'Max revenue', 'Present')

        for i in range(len(descrip)):
            display_result(descrip[i], ret_arr, vol_arr, all_weights, indices[i])
            display_allocation(descrip[i], self, all_weights, indices[i])

        plot_rvs(self, title, descrip, sharpe_arr, vol_arr, ret_arr, indices)

        # constraints = ({'type':'eq', 'fun':self.check_sum})
        # bounds = list()
        # for asset in self.assets:
        #     bounds.append((0, 1))

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

DIR_NAME = './'

def load_csv(prefix):
    '''Load csv data & return as a dataframe'''
    filename = os.path.join(DIR_NAME, prefix + ".csv")
    return pd.read_csv(filename, sep=';')

#### Driver ####
if __name__ == '__main__':
    SEED       = 42
    PREFIX     = 'Adrien_ptf'
    NUM_PORTS  = int( 1.5e6 ) # number of portfolios

    start_time = time.time()
    np.random.seed(SEED)

    ptf = load_csv(PREFIX)

    # periods: 1d,5d,1mo,3mo,6mo,1y,2y,3y,5y,10y,ytd,max
    periods = ('1y', '5y', '10y')
    for period in periods:
        assets = list()
        print(f'Processing {period} period')
        for i, ticker in enumerate(ptf.Valeur):
            quantity = ptf.iloc[i,1]
            print(f'{ticker} Q={ptf.iloc[i,1]}')
            assets.append(ast.Asset(sqr.Security(ticker, period), quantity))

        portfolio = Portfolio(assets)
        portfolio.describe()

        portfolio.efficient_frontier(PREFIX.replace('_ptf', ''))
    print(f"--- Total run time: {(time.time() - start_time):.0f}s ---")
