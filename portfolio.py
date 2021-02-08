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
import scipy.optimize as opt
from tqdm import tqdm
import asset as ast
import security as sqr
import equity as eq
import portfolio_io as pio
import portfolio_plot as pplot


### Efficient frontier:
def check_sum(weights):
    ''' Checks that weights sum up to 1 '''
    return np.sum(weights) - 1


def get_rvs(ptf, weights):
    ''' returns return, volatility & sharpe ratio for a given weight distribution '''
    weights = np.array(weights)
    ret     = np.sum(ptf.log_ret.mean() * weights) * ptf.data['ndays']
    vol     = np.sqrt(np.dot(weights.T, np.dot(ptf.log_ret.cov() * ptf.data['ndays'], weights)))
    sharpe  = ret/vol
    return np.array([ret, vol, sharpe])


def neg_sharpe(ptf, weights):
    ''' Returns negative Sharpe ratio to feed optimization function '''
    # 2 is the sharpe ratio index from get_rvs
    return get_rvs(ptf, weights)[2] * -1
### END Efficient frontier

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


def sample_space_to_df(p_weights, p_returns, p_volat, p_sharpe):
    ''' Stores results from sample_space as pandas dataframe '''
    # build combined array
    temp = np.vstack((p_returns, p_volat, p_sharpe, p_weights.transpose())).transpose()
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
    if LOG_PLOT:
        opt_ret = np.exp(p_returns[idx])
    else:
        opt_ret = p_returns[idx]
    opt_vol = p_volat[idx]

    print(f'{description} portfolio:')
    print(f'{NUM_PORTS} portfolio combinations')
    print(f'weights: {wts[idx,:]}\n'
          f'Return={opt_ret:.4f}, '
          f'Volatility={opt_vol:.4f}, '
          f'Sharpe ratio={opt_ret/opt_vol:.4f}')


def display_allocation(description, ptf, wts, idx):
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
        self.descriptions    = ['Max Sharpe', 'Min volatility', 'Max revenue', 'Present']
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
            stocks = stocks.rename(columns = {'Close_' + asset.data['symbol'] : asset.data['symbol']})
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
        return get_rvs(self, weights)[1]


    def efficient_frontier(self, perd):
        ''' WIP '''
        # Sample portfolio space. Returns weights, returns, volatility & sharpe ratios
        all_weights, ret_arr, vol_arr, sharpe_arr = sample_space(self)
        res = sample_space_to_df(all_weights, ret_arr, vol_arr, sharpe_arr)
        # Save results to file
        pio.write_portfolio_space(res, self.data['title'], NUM_PORTS, perd)

        # add portfolio from Q_S as last value in arrays
        p_weights, p_returns, p_volat, p_sharpe = get_portfolio_stats(self)
        all_weights = np.vstack([all_weights, p_weights])
        ret_arr     = np.append(ret_arr, p_returns)
        vol_arr     = np.append(vol_arr, p_volat)
        sharpe_arr  = np.append(sharpe_arr, p_sharpe)

        print('\n')
        # 0:Max Sharpe 1:Min volatility 2:Max Revenue 3: Portfolio
        indices = (sharpe_arr.argmax(), vol_arr.argmin(), ret_arr.argmax(), sharpe_arr.shape[0]-1)
        print(f'Indices: {sharpe_arr.argmax()} '
              f'{vol_arr.argmin()} '
              f'{ret_arr.argmax()} '
              f'{sharpe_arr.shape[0]-1}')

        for i, descrip in enumerate(self.descriptions):
            display_result(descrip, ret_arr, vol_arr, all_weights, indices[i])
            display_allocation(descrip, self, all_weights, indices[i])

        # Merge returns, volatility and Sharpe ratio into one 3-D array
        rvs = np.vstack((ret_arr, vol_arr, sharpe_arr)).transpose()

        pplot.plot_rvs(self, rvs, indices, NUM_PORTS, LOG_PLOT)

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


#### Driver ####
if __name__ == '__main__':
    SEED     = 42
    LOG_PLOT = False # display data as log of return
    prefixes = ['test2_ptf']

    # periods: 1d,5d,1mo,3mo,6mo,1y,2y,3y,5y,10y,ytd,max
    periods = ('10y', '5y', '1y')
    SKIP      = ['ELIS.PA'] # do not optimize for these values
    NUM_PORTS = int( 5.e3 ) # number of portfolios

    start_time = time.time()
    np.random.seed(SEED)

    for prefix in prefixes: # Loop over files
        # download current portfolio
        csv_df = pio.load_csv(prefix)
        print(f'Processing {prefix}.csv')
        for period in periods: # Loop over periods
            print(f'Processing {period} period')
            assets = list()
            for ii, ticker in enumerate(csv_df.Valeur):
                quantity = csv_df.iloc[ii, 1]
                print(f'{ticker} Q={csv_df.iloc[ii, 1]}')
                if ticker in SKIP:
                    print(f'*** Skipping {ticker} ***')
                else:
                    assets.append(ast.Asset(sqr.Security(ticker, period), quantity))

            # Build a portfolio of assets for each period
            portfolio = Portfolio(assets, prefix.replace('_ptf', ''))
            portfolio.describe()

            portfolio.efficient_frontier(period)
    print(f"--- Total run time: {(time.time() - start_time):.0f}s ---")
