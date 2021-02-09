#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 17:34:49 2021

A Portfolio object is a collection of Assets

@author: charles mégnin
"""
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.optimize as opt
from tqdm import tqdm
import asset as ast
import security as sqr
import equity as eq
import portfolio_io as pio
import portfolio_plot as pplot
import utilities as util

### Efficient frontier functions ###
def check_sum(weights):
    ''' Checks that weights sum up to 1 '''
    return np.sum(weights) - 1
### END Efficient frontier functions ###

#Helper utilities
def sample_space(ptf):
    ''' Explore NUM_PORTS portfolio combinations returns_df is log(returns) '''
    returns   = ptf.log_ret
    ncolumns  = len(returns.columns)
    ndays     = ptf.data['ndays']
    p_weights = np.zeros((NUM_PORTS, ncolumns))
    p_returns = np.zeros(NUM_PORTS)
    p_volat   = np.zeros(NUM_PORTS)
    p_sharpe  = np.zeros(NUM_PORTS)

    for port in tqdm(range(NUM_PORTS)):
        weights = np.array(np.random.random(ncolumns))
        weights = weights/np.sum(weights)

        # Save new weight
        p_weights[port,:] = weights

        # Expected return
        p_returns[port] = np.sum( (returns.mean() * weights * ndays))

        # Expected volatility = SQRT(W^T . COV . W)
        p_volat[port] = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * ndays, weights) ) )

        p_sharpe[port] = p_returns[port]/p_volat[port]

        #print(port, p_returns[port], p_volat[port], p_sharpe[port])
    print(p_returns.max(), p_sharpe.max(), p_returns.argmax(), p_sharpe.argmax())

    return p_weights, p_returns, p_volat, p_sharpe


def sample_space_to_df(p_weights, rvs_arr):
    ''' Stores results from sample_space as pandas dataframe '''
    # build combined array
    temp = np.vstack((rvs_arr[:,0], rvs_arr[:,1], rvs_arr[:,2], p_weights.transpose())).transpose()
    weights_col = ['w_'+ str(i) for i in range(0, p_weights.shape[1])]
    cols = ['log_ret', 'volat', 'sharpe']
    for name in weights_col:
        cols.append(name)
    # wrap array into dataframe
    return pd.DataFrame(temp, columns=cols)


def get_portfolio_stats(ptf):
    ''' Compute existing portfolio weights, return, volatility & Sharpe
        ratio from Q_S '''
    ndays      = ptf.data['ndays']
    weights    = np.zeros(ptf.data['nassets'])
    returns_df = ptf.log_ret
    for i in range(ptf.data['nassets']):
        weights[i]  = ptf.assets[i].data['price'] * ptf.assets[i].data['quantity']
        weights[i] /= ptf.data['value']

    p_returns = np.sum( (returns_df.mean() * weights * ndays))
    p_volat   = np.sqrt(np.dot(weights.T, np.dot(returns_df.cov() * ndays, weights)))
    p_sharpe  = p_returns/p_volat

    return weights, p_returns, p_volat, p_sharpe


def display_result(description, p_returns, p_volat, wts, idx):
    ''' Descriptor '''
    opt_ret = p_returns[idx]
    lin_ret = np.exp(opt_ret)-1
    opt_vol = p_volat[idx]

    print(f'{description} portfolio:')
    print(f'{NUM_PORTS} portfolio combinations')
    print(f'weights: {wts[idx,:]}')
    print(f'Expected return={lin_ret:.2%}', end=' ')
    print(f'(log={opt_ret:.4f})')
    print(f'Volatility={opt_vol:.4f}, '
          f'Sharpe ratio={opt_ret/opt_vol:.4f}')


def display_allocation(ptf, description, wts, idx):
    ''' Displays allocation results '''
    print(f'{description} asset allocation ({ptf.data["value"]:.2f} {ptf.data["currency"]}):')
    for i, weight in enumerate(wts[idx,:]):
        name = ptf.assets[i].data['symbol']
        allocation = ptf.data['value'] * weight
        price = ptf.assets[i].data['price']
        opt_q = int(round(allocation/price))
        print(f'{name}: {allocation:.2f} {ptf.data["currency"]} = '
              f'{opt_q} * {price:.2f} {ptf.data["currency"]}')
    print()


class Portfolio(eq.Equity):
    ''' Portfolio of Assets in a given currency '''

    def __init__(self, asset_list, title):
        super().__init__()
        self.data['title']   = title
        self.assets          = asset_list
        self.data['nassets'] = len(asset_list)
        self.data['period']  = self.assets[0].data['period']
        self.descriptions    = ['Max Sharpe',
                                'Min volatility',
                                'Max revenue',
                                'Present',
                                'Optimal Sharpe']
        self._set_value()
        self._build_return_matrix()


    def _build_return_matrix(self):
        ''' Build log returns matrix
            Extract & stores end date and # of days '''
        for i, asset in enumerate(self.assets):
            symbol = asset.data['symbol']
            if i == 0:
                stocks = asset.close
            else:
                stocks = pd.merge(stocks, asset.close, on='Date', how='inner')
            stocks = stocks.rename(columns = {'Close_' + symbol : symbol})
        self.data['end_date'] = stocks.Date.iloc[-1]

        stocks             = stocks.set_index('Date')
        self.log_ret       = np.log(stocks/stocks.shift(1))
        self.data['ndays'] = stocks.shape[0]


    def _set_value(self):
        ''' Compute the value of the portfolio as the sum of the asset values '''
        self.data['value'] = 0.0
        for i, asset in enumerate(self.assets):
            if i == 0:
                self.data['currency'] = asset.data['currency']
            if self.data['currency'] == asset.data['currency']: # check currencies are consistent
                self.data['value'] += asset.data['value']
            else:
                raise Exception(f'Inconsistent currency for {asset.name}: {asset.currency} ')


    def get_asset_names(self):
        ''' return list of all asset names'''
        names = list()
        for asset in self.assets:
            names.append(asset.data['name'])
        return names


    def describe(self):
        ''' Portfolio descriptor '''
        print("\n*** Portfolio ***")
        print(f'{self.data["nassets"]} assets in portfolio:')
        for i, asset in enumerate(self.assets):
            print(f'Asset {i}:')
            asset.describe()
        print(f'Total portfolio value: {self.data["value"]:.2f} {self.data["currency"]}')


    def minimize_volatility(self, weights):
        ''' return minimum volatility '''
        return self.get_rvs(weights)[1]


    def get_rvs(self, weights):
        ''' returns return, volatility & sharpe ratio for a given weight distribution '''
        weights = np.array(weights)
        ret     = np.sum(self.log_ret.mean() * weights) * self.data['ndays']
        vol     = np.sqrt(np.dot(weights.T, np.dot(self.log_ret.cov() * self.data['ndays'], weights)))
        sharpe  = ret/vol
        return np.array([ret, vol, sharpe])


    def neg_sharpe(self, weights):
        ''' Returns negative Sharpe ratio to feed optimization function '''
        return self.get_rvs(weights)[2] * -1


    def get_frontier(self, rvs, init_guess, bounds):
        ''' returns efficient frontier '''
        maxy = util.round_up(np.max(rvs[:,0]), 1) * 1.1 # round up & add 10%
        print(f'maxy = {maxy}')

        frontier_y = np.linspace(0, maxy, 200)
        frontier_x = []

        # Find the minimum volatility for a given return:
        for possible_return in tqdm(frontier_y):
            cons = ({'type':'eq', 'fun':check_sum},
                    {'type':'eq', 'fun': lambda w: self.get_rvs(w)[0] - possible_return})

            result = opt.minimize(self.minimize_volatility,
                                  init_guess,
                                  method='SLSQP',
                                  bounds=bounds,
                                  constraints=cons)
            frontier_x.append(result['fun'])

        frontier = np.vstack((frontier_x, frontier_y)).transpose()
        return frontier


    def efficient_frontier(self):
        ''' WIP '''
        # Sample portfolio space. Returns weights, returns, volatility & sharpe ratios
        all_weights, ret_arr, vol_arr, sharpe_arr = sample_space(self)

        # Merge returns, volatility and Sharpe ratio into one 3-D array
        rvs = np.vstack((ret_arr, vol_arr, sharpe_arr)).transpose()

        # Save results to file
        pio.write_portfolio_space(self,
                                  sample_space_to_df(all_weights, rvs),
                                  NUM_PORTS)

        # add present portfolio from Q_S as last value in arrays
        p_weights, p_returns, p_volat, p_sharpe = get_portfolio_stats(self)
        all_weights = np.vstack([all_weights, p_weights])
        rvs = np.vstack([rvs, [p_returns, p_volat, p_sharpe]])

        # 0:Max Sharpe 1:Min volatility 2:Max Revenue 3: Present portfolio
        indices = [rvs[:,2].argmax(),
                   rvs[:,1].argmin(),
                   rvs[:,0].argmax(),
                   rvs[:,0].shape[0]-1]

        cons       = ({'type':'eq', 'fun':check_sum})
        init_guess = [1./len(self.assets) for asset in self.assets]
        bounds     = [(0, 1) for asset in self.assets]

        # Find result which minimizes sharpe ratio
        opt_results = opt.minimize(self.neg_sharpe,
                                   init_guess,
                                   method='SLSQP',
                                   bounds=bounds,
                                   constraints=cons)
        print(f'optimal result: {opt_results}')
        print(f'RVS={self.get_rvs(opt_results.x)}')

        # Add optimal Sharpe as last value in rvs array
        rvs         = np.vstack([rvs, self.get_rvs(opt_results.x)])
        all_weights = np.vstack([all_weights, opt_results.x])
        indices.append(rvs.shape[0]-1) # Add index of optimal Sharpe

        for i, descrip in enumerate(self.descriptions):
            display_result(descrip, rvs[:,0], rvs[:,1], all_weights, indices[i])
            display_allocation(self, descrip, all_weights, indices[i])

        frontier = self.get_frontier(rvs, init_guess, bounds)
        pplot.plot_rvs(self, rvs, frontier, indices, NUM_PORTS, LOG_PLOT)


#### Driver ####
if __name__ == '__main__':
    SEED     = 42
    LOG_PLOT = True # display data as log of return
    SKIP     = ['ELIS.PA'] # do not optimize for these values
    prefixes = ['Adrien_ptf', 'JP_ptf', 'Jacqueline_ptf']
    prefixes = ['Adrien_ptf']

    # periods: 1d,5d,1mo,3mo,6mo,1y,2y,3y,5y,10y,ytd,max
    periods   = ['10y', '5y', '1y']
    periods   = ['10y']
    NUM_PORTS = int( 1e5 ) # number of portfolios

    start_time = time.time()
    np.random.seed(SEED)

    for prefix in prefixes: # Loop over files
        # download current portfolio
        csv_df = pio.load_csv(prefix)
        print(f'Processing {prefix}.csv')
        for period in periods: # Loop over periods
            print(f'Processing {period} period')
            assets = list() # initialize the list of assets in portfolio
            for ii, ticker in enumerate(csv_df.Valeur):
                quantity = csv_df.iloc[ii, 1]
                print(f'{ticker} Q={csv_df.iloc[ii, 1]}')
                if ticker in SKIP:
                    print(f'*** Skipping {ticker} ***')
                else:
                    assets.append(ast.Asset(sqr.Security(ticker, period), quantity))

            # Build a portfolio of assets for each period
            portfolio = Portfolio(assets, prefix.replace('_ptf', ''))

            portfolio.efficient_frontier()
    print(f"--- Total run time: {(time.time() - start_time):.0f}s ---")
