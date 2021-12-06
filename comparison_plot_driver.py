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

# Target company specs
TARGET_TICKER   = 'SU.PA'
START_DATE      = '2010-01-02'
END_DATE        = '2021-11-01'
EXPIRATION_DATE = '2021-12-31'
YEAR            = '2019'

if __name__ == '__main__':
    YEAR = str(YEAR)

    stocks = pd.read_csv(DATA_PATH)
    target_stock = stocks[stocks.symbol == TARGET_TICKER]
    cie = cny.Company(TARGET_TICKER,
                      period          = PERIOD,
                      expiration_date = EXPIRATION_DATE,
                      start_date      = START_DATE,
                      end_date        = END_DATE,
                      )

    filter_d = {
                'industry':          (target_stock['industry'].values[0], INDUSTRY),
                'sector':            (target_stock['sector'].values[0], SECTOR),
                'mktCapUSD':         (target_stock['mktCapUSD'].values[0], MKTCAP),
                'mktCap_interval':   (MKT_CAP_WINDOW['lower'],
                                      MKT_CAP_WINDOW['upper']),
                'currency':          (target_stock['currency'].values[0], CURRENCY),
                'country':           (target_stock['country'].values[0], COUNTRY),
                'exchangeShortName': (target_stock['exchangeShortName'].values[0], XCHANGE),
                }

    util.filter_to_screen(filter_d)

    peers = util.extract_peers(target_ticker=TARGET_TICKER, filt=filter_d)
    # If it exists, remove target stock
    peers.discard(TARGET_TICKER)
    print(f'{len(peers)} peers returned\n')
    print(peers)
    prefix = f'{TARGET_TICKER}_{YEAR}_'
    for metric in mtr.metrics_set_names:
        filename = prefix + f'{metric}_comparison.html'
        cie.plot_peers_comparison(year        = YEAR,
                                  metrics     = mtr.get_metrics(metric),
                                  metric_name = metric,
                                  peers       = peers,
                                  filename    = filename,
                                  )
