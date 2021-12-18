#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  4 09:52:09 2021

Driver for fundamentals comparison plots

@author: charly
"""
import pandas as pd
import plotly.io as pio
import utilities as util
import metrics as mtr
import company as cny
import comparison_plotter as c_pltr

pio.renderers.default='browser'

URL        = 'https://ml-finance.ams3.digitaloceanspaces.com'
PATH       = 'fundamentals'
FILE       = 'stocks.csv'
DATA_PATH  = f'{URL}/{PATH}/{FILE}'
PERIOD     = 'annual'

# Filter flags
INDUSTRY = True
SECTOR   = True
MKTCAP   = True
CURRENCY = True
COUNTRY  = False
XCHANGE  = False

# Window of mktCap to include as a fraction of target company mktCap
MKT_CAP_WINDOW = {'lower': .1,
                  'upper': 10}
EXPIRATION_DATE = '2021-12-31'

# Target company specs
TARGET_TICKER   = 'MC.PA'
YEAR            = '2019'


def extract_peers(target_ticker:str, filt:dict):
    '''
    Extracts list of peers. Expects:
    target ticker
    filter: a dictionary of the form:
    filter = {
        'industry': (target_stock['industry'].values[0], True),
        'sector': (target_stock['sector'].values[0], True),
        'mktCapUSD': (target_stock['mktCapUSD'].values[0], True),
        'mktCap_interval':(mkt_cap_lower, mkt_cap_upper),
        'currency': (target_stock['currency'].values[0], False),
        'country': (target_stock['country'].values[0], False),
        'exchangeShortName': (target_stock['exchangeShortName'].values[0], False),
        }
    where True/False is the flag that determines whether or not to apply
    the filter
    mkt_cap_lower, mkt_cap_upper are upper and lower bounds of market cap
    expressed as fractions of the target market cap
    returns a set of tickers
    '''
    stocks = pd.read_csv(DATA_PATH)
    target_stock = stocks[stocks.symbol == target_ticker]

    #Returns list of companies matching filter values tagged as True'''
    for key in list(filt.keys()):
        if filt[key][1] is True:
            if key == 'mktCapUSD':
                lower = target_stock[key].values[0] * filt['mktCap_interval'][0]
                upper = target_stock[key].values[0] * filt['mktCap_interval'][1]
                stocks = stocks[(stocks[key] >= lower) & (stocks[key] <= upper)]
            else: # filter other than market cap
                stocks = stocks[stocks[key] == filt[key][0]]
    return set(stocks.symbol)


def build_metric_dataframe(cie, ticker:str, requested_metrics:list, year:str, idx:str):
    metric_df         = pd.DataFrame.from_dict(cie.load_cie_metrics(year=year,
                                                                    requested_metrics=requested_metrics,
                                                                    ),
                                               orient='index',
                                               )
    metric_df.columns    = [ticker]
    metric_df = metric_df.transpose()
    metric_df.index.name = idx
    return metric_df


def aggregate_peers(target_ticker:str, peers:list, req_metrics:str, year:str):
    '''Extract metrics for peers and aggregate '''
    idx = 'company'
    cie         = cny.Company(ticker=target_ticker,
                              period='annual',
                              expiration_date=EXPIRATION_DATE,
                              )
    metric_df   = build_metric_dataframe(cie,
                                         ticker=TARGET_TICKER,
                                         requested_metrics=req_metrics,
                                         year=year,
                                         idx=idx,
                                         )
    d_metric_df = cie.load_cie_metrics_over_time(metrics=req_metrics,
                                                 yr_start=int(year),
                                                 yr_end=int(year),
                                                 change=True,
                                                 )
    # build metric dataframe
    for peer in peers:
        cie       = cny.Company(ticker=peer,
                                period='annual',
                                expiration_date=EXPIRATION_DATE,
                                )
        temp_df   = build_metric_dataframe(cie,
                                           ticker=peer,
                                           requested_metrics=req_metrics,
                                           year=year,
                                           idx=idx,
                                           )
        metric_df = metric_df.append(temp_df, ignore_index = False)
    # build change in metric dataframe
    for peer in peers:
        cie     = cny.Company(ticker=peer,
                              period='annual',
                              expiration_date=EXPIRATION_DATE,
                              )
        temp_df = cie.load_cie_metrics_over_time(metrics=req_metrics,
                                                 yr_start=int(year),
                                                 yr_end=int(year),
                                                 change=True,
                                                 )
        temp_df.index.name = peer
        d_metric_df = d_metric_df.append(temp_df, ignore_index = False)

    peer_list= list(peers) # peers is a set
    peer_list.insert(0, target_ticker)
    d_metric_df.insert(0, idx, peer_list)
    d_metric_df = d_metric_df.set_index(idx, drop=True)
    # merge metric and its change:
    metric_df = pd.merge(metric_df, d_metric_df, on=idx, how='inner')
    metric_df.index.name = None
    metric_df = metric_df.transpose()
    metric_df.index.name = 'metric'

    return metric_df


if __name__ == '__main__':
    prefix = f'{TARGET_TICKER}_peers_{YEAR}.html'
    stocks = pd.read_csv(DATA_PATH)
    target_stock = stocks[stocks.symbol == TARGET_TICKER]
    cie = cny.Company(ticker          = TARGET_TICKER,
                      period          = PERIOD,
                      expiration_date = EXPIRATION_DATE,
                      )
    filter_d = {'industry':          (target_stock['industry'].values[0], INDUSTRY),
                'sector':            (target_stock['sector'].values[0], SECTOR),
                'mktCapUSD':         (target_stock['mktCapUSD'].values[0], MKTCAP),
                'mktCap_interval':   (MKT_CAP_WINDOW['lower'],
                                      MKT_CAP_WINDOW['upper'],
                                      ),
                'currency':          (target_stock['currency'].values[0], CURRENCY),
                'country':           (target_stock['country'].values[0], COUNTRY),
                'exchangeShortName': (target_stock['exchangeShortName'].values[0], XCHANGE),
                }
    util.echo_filter(filt=filter_d,
                          currency=cie.get_currency_symbol(),
                          )
    peers = extract_peers(target_ticker=TARGET_TICKER, filt=filter_d)
    peers.discard(TARGET_TICKER) # If it exists, remove target stock to avoid duplicate
    print(f'{len(peers)} peers returned: {peers}\n')

    df = aggregate_peers(target_ticker=TARGET_TICKER, peers=peers, req_metrics=mtr.bs_metrics, year=YEAR)
    print(df)

    plotter = c_pltr.ComparisonPlotter(base_cie=cie, cie_data=df, year=YEAR)
    plot_type = 'bs'
    subtitle = mtr.metrics_set_names[plot_type + '_metrics']
    plotter.plot(plot_type = plot_type,
                 subtitle  = subtitle,
                 filename  = prefix,
                 )
