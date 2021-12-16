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

if __name__ == '__main__':
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
    util.filter_to_screen(filt=filter_d,
                          currency=cie.get_currency_symbol(),
                          )

    peers = util.extract_peers(target_ticker=TARGET_TICKER, filt=filter_d)
    peers.discard(TARGET_TICKER) # If it exists, remove target stock to avoid duplicate
    print(f'{len(peers)} peers returned\n')
    print(peers)
    prefix = f'{TARGET_TICKER}_{YEAR}_'
    for metric in mtr.metrics_set_names:
        filename = prefix + f'{metric}_comparison.html'
        cie.plot_peers_comparison(year        = int(YEAR),
                                  metrics     = mtr.get_metrics(metric),
                                  metric_name = metric,
                                  peers       = peers,
                                  filename    = filename,
                                  )
