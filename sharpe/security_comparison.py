#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 22:15:11 2021

comparisons between two securities
- correlation
- price P
- volatility as standard deviation
- daily returns dP = d/dt & histograms
- change in daily returns s2P = d2/dt2 & histograms
- P1/P2 dP1/dP2 & histograms
- risk-adjusted returns with histograms
- decomposition into Trend + seasonality + error
- Max drawdown
- Semi-deviation

TO DO:
    VaR
    CVaR
    Display stats on histograms

@author: charles megnin
"""
import os.path
import datetime
import pandas as pd
import numpy as np
import scipy
import statsmodels.api as sm
import security as sec
import comparison_plots as cplots
import utilities as util

TICKERS  = ['BTC-USD', 'ETH-USD']
SECUS    = ['BTC', 'ETH']
DIRNAME  = 'data'
PREFIX   = f'secu_{TICKERS[0]}_{TICKERS[1]}'
PERIOD   = '5y'
HEADER   = f'{SECUS[0]}-{SECUS[1]}: '

def load_data(dirname=DIRNAME, prefix=PREFIX, period=PERIOD):
    '''
    Load data from file else upload from Yahoo finance
    '''
    #pathname = os.path.join(dirname, prefix+'.csv')
    pathname = os.path.join(dirname, prefix+'.pkl')
    if os.path.exists(pathname):
        print(f'Loading data from {pathname}')
        data = pd.read_pickle(pathname)
        # data = pd.read_csv(pathname,
        #                    sep         = ',',
        #                    header      = 0,
        #                    index_col   = 0,
        #                    parse_dates = True)
    else:
        print('Downloading data from Yahoo Finance')
        data = pd.merge(sec.Security(TICKERS[0], period).get_market_data(),
                        sec.Security(TICKERS[1], period).get_market_data(),
                        on  = "Date",
                        how = "inner")
        data.rename(columns={f"Close_{TICKERS[0]}":SECUS[0]}, inplace=True)
        data.rename(columns={f"Close_{TICKERS[1]}":SECUS[1]}, inplace=True)
        data.set_index('Date', inplace=True)
        #store locally
        data.to_pickle(pathname)
        #data.to_csv(pathname, sep=',', encoding='utf-8')
    return data


def feature_engineer(data, window):
    '''
    Feature engineering
    CORR & D-CORR rolling
    '''
    data.reset_index(level=0, inplace=True)
    data['ndays'] = (data['Date'] - data['Date'].shift(1)) / np.timedelta64(1, 'D')
    data = data.set_index('Date')

    # Change name of volume columns from TICKER to SECU
    data.rename(columns = {f'Vol_{TICKERS[0]}':f'Vol_{SECUS[0]}'}, inplace = True)
    data.rename(columns = {f'Vol_{TICKERS[1]}':f'Vol_{SECUS[1]}'}, inplace = True)

    #Relative returns (1st derivative)
    data[f'D-{SECUS[0]}'] = data[SECUS[0]].pct_change()/data['ndays']
    data[f'D-{SECUS[1]}'] = data[SECUS[1]].pct_change()/data['ndays']

    #Change in relative returns (2nd derivative)
    data[f'D2-{SECUS[0]}'] = data[f'D-{SECUS[0]}'].pct_change()/data['ndays']
    data[f'D2-{SECUS[1]}'] = data[f'D-{SECUS[1]}'].pct_change()/data['ndays']

    #Relative volume (1st derivative)
    data[f'D-Vol_{SECUS[0]}'] = data[f'Vol_{SECUS[0]}'].pct_change()/data['ndays']
    data[f'D-Vol_{SECUS[1]}'] = data[f'Vol_{SECUS[1]}'].pct_change()/data['ndays']

    # Ratios
    data[f'{SECUS[0]}/{SECUS[1]}']     = data[SECUS[0]] / data[SECUS[1]]
    data[f'D-{SECUS[0]}/D-{SECUS[1]}'] = data[f'D-{SECUS[0]}'] / data[f'D-{SECUS[1]}']

    # Rolling correlations:
    data['CORR']   = data[SECUS[0]].rolling(window).corr(data[SECUS[1]])
    data['D-CORR'] = data[f'D-{SECUS[0]}'].rolling(window).corr(data[f'D-{SECUS[1]}'])

    # Sensitivity of returns to volume
    data[f'D-{SECUS[0]}_V'] = data[f'D-{SECUS[0]}']/data[f'Vol_{SECUS[0]}']
    data[f'D-{SECUS[1]}_V'] = data[f'D-{SECUS[1]}']/data[f'Vol_{SECUS[1]}']

    data.drop('ndays', axis=1, inplace=True)
    return data.dropna()


def display_corrrelations(data):
    cols = data.columns
    for i, col1 in enumerate(cols):
        for j, col2 in enumerate(cols):
            if j < i:
                corr, p_value = scipy.stats.pearsonr(data[col1], data[col2])
                if np.abs(corr) > .5:
                    print(f'{col1}-{col2}\t\t\tcorr={corr:.2g}\tp-value={p_value:.2g}')


if __name__ == '__main__':
    ROLLING_WINDOW = 30
    START          = '2019-01-01'
    data_start     = util.get_start_date(START, ROLLING_WINDOW)
    print(f'Desired start date:{START} / window={ROLLING_WINDOW} days / data start:{data_start}')

    crypto = load_data()
    print(crypto)
    crypto = feature_engineer(crypto, ROLLING_WINDOW)

    #### Plots ####
    cryp_win = crypto[data_start:]

    # ret, rel_ret = util.get_return(crypto,
    #                           ticker        = 'BTC-USD',
    #                           purchase_date = '2019-03-25',
    #                           sale_date     = '2021-02-22')
    # print(f'return = ${ret:.2f} ({rel_ret:.2%})')
    # correlation heatmap
    title =  HEADER
    title += f'Correlations since {START}'
    cplots.corrplot(cryp_win.corr(), title)

    c_values = cryp_win.corr()
    print(c_values)

    display_corrrelations(cryp_win)

    title =  HEADER
    title += f'scatter correlations since {START}'
    cplots.scatter_matrix(cryp_win.drop(['D-BTC/D-ETH',
                                        'CORR',
                                        'D-CORR',
                                        'D2-BTC',
                                        'D2-ETH',
                                        'BTC/ETH',
                                        'D-Vol_BTC',
                                        'D-Vol_ETH'],
                                        axis=1),
                          title)

    # Price comparison: BTC vs ETH
    # Mean
    title =   HEADER
    title += f'mean daily price ({ROLLING_WINDOW}-day rolling)'
    cplots.plot_time_series(cryp_win,
                            [SECUS[0], SECUS[1]],
                            title  = title,
                            window = ROLLING_WINDOW,
                            dtype = 'MEAN',
                            secondary_y = True,
                            )

    # Price comparison:  BTC vs ETH
    # Standard deviation
    title =   HEADER
    title += f'daily price volatility ({ROLLING_WINDOW}-day rolling)'
    cplots.plot_time_series(cryp_win,
                            [SECUS[0], SECUS[1]],
                            title  = title,
                            window = ROLLING_WINDOW,
                            dtype = 'STD',
                            secondary_y = True,
                            )

    # Volume comparison: Vol BTC vs Vol ETH
    # Mean
    title =   HEADER
    title += f'mean daily volume ({ROLLING_WINDOW}-day rolling)'
    cplots.plot_time_series(cryp_win,
                            [f'Vol_{SECUS[0]}', f'Vol_{SECUS[1]}'],
                            title  = title,
                            window = ROLLING_WINDOW,
                            dtype = 'MEAN',
                            secondary_y = True,
                            )

    # Volume comparison: Vol BTC vs Vol ETH
    # Standard deviation
    title =   HEADER
    title += f'daily volume volatility ({ROLLING_WINDOW}-day rolling)'
    cplots.plot_time_series(cryp_win,
                            [f'Vol_{SECUS[0]}', f'Vol_{SECUS[1]}'],
                            title  = title,
                            window = ROLLING_WINDOW,
                            dtype = 'STD',
                            secondary_y = True,
                            )

    # Daily returns: D-BTC vs D-ETH (rolling window)
    # Mean
    title =  HEADER
    title += f'mean daily return ({ROLLING_WINDOW}-day rolling)'
    cplots.plot_time_series(cryp_win,
                            [f'D-{SECUS[0]}', f'D-{SECUS[1]}'],
                            title  = title,
                            window = ROLLING_WINDOW,
                            dtype  = 'MEAN',
                            plot_0 = True,
                            )

    # Daily returns: D-BTC vs D-ETH (rolling window)
    # Standard deviation
    title =  HEADER
    title += f'daily return volatility ({ROLLING_WINDOW}-days rolling)'
    cplots.plot_time_series(cryp_win,
                            [f'D-{SECUS[0]}', f'D-{SECUS[1]}'],
                            title  = title,
                            window = ROLLING_WINDOW,
                            dtype  = 'STD',
                            )

    # Change in daily returns: D2-BTC vs D2-ETH (rolling window)
    # Mean
    title =  HEADER
    title += f'mean change in daily return ({ROLLING_WINDOW}-day rolling)'
    cplots.plot_time_series(cryp_win,
                            [f'D2-{SECUS[0]}', f'D2-{SECUS[1]}'],
                            title  = title,
                            window = ROLLING_WINDOW,
                            dtype  = 'MEAN',
                            )

    # Change in daily returns: D2-BTC vs D2-ETH (rolling window)
    # Standard deviation
    title =  HEADER
    title += f'volatility of change in daily returns ({ROLLING_WINDOW}-day rolling)'
    cplots.plot_time_series(cryp_win,
                            [f'D2-{SECUS[0]}', f'D2-{SECUS[1]}'],
                            title  = title,
                            window = ROLLING_WINDOW,
                            dtype  = 'STD',
                            )

    # sensitivity of returns to volume:
    # Mean
    title =  HEADER
    title += f'mean return-to-volume ratios ({ROLLING_WINDOW}-day rolling)'
    cplots.plot_time_series(cryp_win,
                            [f'D-{SECUS[0]}_V', f'D-{SECUS[1]}_V'],
                            title  = title,
                            window = ROLLING_WINDOW,
                            dtype  = 'MEAN',
                            secondary_y = False,
                            plot_0 = True,
                            )

    # Mean returns vs volume: (rolling window)
    # BTC
    title =  'BTC: '
    title += f'mean daily price vs volume ({ROLLING_WINDOW}-day rolling)'
    cplots.plot_time_series(cryp_win,
                            [f'{SECUS[0]}', f'Vol_{SECUS[0]}'],
                            title  = title,
                            window = ROLLING_WINDOW,
                            dtype  = 'MEAN',
                            secondary_y = True,
                            )

    # Mean returns vs volume: (rolling window)
    # ETH
    title =  'ETH: '
    title += f'mean daily price vs volume ({ROLLING_WINDOW}-day rolling)'
    cplots.plot_time_series(cryp_win,
                            [f'{SECUS[1]}', f'Vol_{SECUS[1]}'],
                            title  = title,
                            window = ROLLING_WINDOW,
                            dtype  = 'MEAN',
                            secondary_y = True,
                            )

    # Daily returns histograms superimposed (1st derivatives)
    title =  HEADER
    title += f'daily returns since {START}'
    cplots.plot_d_histograms(cryp_win,
                             [f'D-{SECUS[0]}', f'D-{SECUS[1]}'],
                             title  = title,
                             xlim   = .2,
                             plot_0 = True,
                             )

    # Change in daily returns histograms superimposed (2nd derivatives)
    title =  HEADER
    title += f'change in daily returns since {START}'
    cplots.plot_dual_histograms(cryp_win,
                                [f'D2-{SECUS[0]}', f'D2-{SECUS[1]}'],
                                title  = title,
                                xlim   = 25,
                                bins   = 1500,
                                plot_0 = True,
                                )

    # Histogram of returns ratio: D-BTC/D-ETH
    title =  HEADER
    title += f'returns ratio since {START}'
    cplots.plot_histogram(cryp_win,
                          f'D-{SECUS[0]}/D-{SECUS[1]}',
                          title   = title,
                          bins    = 1000,
                          xlim    = 5,
                          density = False,
                          plot_v  = True,
                          )

    # Histogram of price correlation
    title =  HEADER
    title += f'{ROLLING_WINDOW}-day rolling price correlation since {START}'
    cplots.plot_histogram(cryp_win,
                          'CORR',
                          title = title,
                          bins  = 15,
                          )

    # Histogram of returns correlation
    title  = HEADER
    title += f'{ROLLING_WINDOW}-day rolling returns correlation since {START}'
    cplots.plot_histogram(cryp_win,
                          'D-CORR',
                          title = title,
                          bins  = 15,
                          )

    # Comparison of risk-adjusted returns = returns / sdev
    title  = HEADER
    title += f'risk-adjusted return ({ROLLING_WINDOW}-day rolling window)'
    cplots.plot_rar(cryp_win,
                    SECUS,
                    title  = title,
                    window = ROLLING_WINDOW,
                    start_date = START,
                    )

    # DOWNSIDE RISK:
    # Semi-deviation of returns
    title =  HEADER
    title += f'daily returns semi-deviation ({ROLLING_WINDOW}-day rolling)'
    cplots.plot_time_series(cryp_win,
                            [f'D-{SECUS[0]}', f'D-{SECUS[1]}'],
                            title  = title,
                            dtype  = 'SEMI_STD',
                            window = ROLLING_WINDOW
                            )

    # Drawdowns
    cplots.plot_drawdown(cryp_win[START:], f'D-{SECUS[0]}', SECUS[0], START)
    cplots.plot_drawdown(cryp_win[START:], f'D-{SECUS[1]}', SECUS[1], START)

    # END DOWNSIDE RISK

    # Trend + seasonality + error decomposition
    cplots.plot_decomposition(sm.tsa.seasonal_decompose(cryp_win[f'D-{SECUS[0]}'].values,
                                                        model='additive',
                                                        extrapolate_trend='freq',
                                                        period=14),
                              SECUS[0],
                              START)

    cplots.plot_decomposition(sm.tsa.seasonal_decompose(cryp_win[f'D-{SECUS[1]}'].values,
                                                        model='additive',
                                                        extrapolate_trend='freq',
                                                        period=14),
                              SECUS[1],
                              START)

    # for column in cryp_win.columns:
    #     util.display_stats(cryp_win, column)
