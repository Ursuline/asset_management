#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 24 17:18:23 2021

suggest_peers.py

@author: charles megnin
"""
import os
import csv
import time
import pandas as pd
import company as cny
import plotter_defaults as dft
import utilities as util

# Filter flags
INDUSTRY = True
SECTOR   = True
MKTCAP   = True
CURRENCY = True
COUNTRY  = False
XCHANGE  = False

# Window of mktCap to include as a fraction of target company mktCap
MKT_CAP_WINDOW = {'lower': .2,
                  'upper': 5}
EXPIRATION_DATE = '2021-12-31'

# Target company specs
TARGET_TICKER   = 'RMS.PA'


def extract_peers(target_ticker:str, stocks:pd.DataFrame, filt:dict):
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
    target_stock = stocks[stocks.symbol == target_ticker]

    #Returns list of company tickers matching filter values tagged as True'''
    for key in list(filt.keys()):
        if filt[key][1] is True:
            if key == 'mktCapUSD':
                lower  = target_stock[key].values[0] * filt['mktCap_interval'][0]
                upper  = target_stock[key].values[0] * filt['mktCap_interval'][1]
                stocks = stocks[(stocks[key] >= lower) & (stocks[key] <= upper)]
            else: # filter other than market cap
                stocks = stocks[stocks[key] == filt[key][0]]
    return stocks.symbol


def save_data(peers:list, file_name:str):
    '''Save list of peers as a 1-column csv file'''
    os.makedirs(dft.get_data_directory(),
                exist_ok = True,
                )
    output_file = os.path.join(dft.get_data_directory(), file_name)
    with open(output_file, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(zip(peers))
    print(f'list of suggested peer tickers saved as:\n{output_file}')


if __name__ == '__main__':
    start_tm = time.time()
    peer_filename = f'{TARGET_TICKER}_peers.csv'
    securities = pd.read_csv(dft.get_cloud_path())
    target_security = securities[securities.symbol == TARGET_TICKER]
    cie = cny.Company(ticker          = TARGET_TICKER,
                      period          = dft.PERIOD,
                      expiration_date = EXPIRATION_DATE,
                      )
    filter_d = {'industry':          (target_security['industry'].values[0], INDUSTRY),
                'sector':            (target_security['sector'].values[0], SECTOR),
                'mktCapUSD':         (target_security['mktCapUSD'].values[0], MKTCAP),
                'mktCap_interval':   (MKT_CAP_WINDOW['lower'],
                                      MKT_CAP_WINDOW['upper'],
                                      ),
                'currency':          (target_security['currency'].values[0], CURRENCY),
                'country':           (target_security['country'].values[0], COUNTRY),
                'exchangeShortName': (target_security['exchangeShortName'].values[0], XCHANGE),
                }
    util.echo_filter(filt     = filter_d,
                     currency = cie.get_currency_symbol(),
                     )
    peer_list = extract_peers(target_ticker = TARGET_TICKER,
                              stocks        = securities,
                              filt          = filter_d,
                              )
    #Remove any occurence of target from list
    peer_list = [value for value in peer_list if value != TARGET_TICKER]
    peer_list = list(set(peer_list)) # remove other possible duplicates
    # insert target at the beginning of the list
    peer_list.insert(0, TARGET_TICKER)
    print(f'{len(peer_list)-1} peers returned + {TARGET_TICKER}: {peer_list}')
    save_data(peer_list, peer_filename)
    print(f"Total elapsed time: {util.convert_seconds(time.time()-start_tm)}")
