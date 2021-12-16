#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 17:03:05 2021

@author: charly
"""
import json
import pandas as pd
import requests
from numerize import numerize

URL  = 'https://ml-finance.ams3.digitaloceanspaces.com'
PATH = 'fundamentals'
FILE = 'stocks.csv'
DATA_PATH  = f'{URL}/{PATH}/{FILE}'
MILLION = 1000000.

def build_url(ticker:str, api_key:str):
    '''Builds the FMP URL for the given ticker'''
    root = 'https://financialmodelingprep.com/api/v4/stock_peers?'
    request = f'symbol={ticker}&apikey={api_key}'
    url = f'{root}{request}'
    return url


def extract_peers_fmp(ticker:str, api_key:str):
    '''
    Extract list of peers as defined by financialmodelingprep
    This is *not* the preferred method ->
    peers are selected by sector
    rather than industry, no visibility on filter on market cap,
    necessarily in same stock exchange etc
    '''
    try:
        url = requests.get(build_url(ticker, api_key))
        text = url.text
        data = json.loads(text)
        cie_name = data[0]
        return cie_name['peersList']
    except:
        raise ValueError('Badly formed URL {url}')


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
            else: # not market cap
                stocks = stocks[stocks[key] == filt[key][0]]
    return set(stocks.symbol)


def filter_to_screen(filt:dict, currency:str):
    '''Outputs company filter characterisitcs to screen'''
    for key in filt:
        if filt[key][1] == True:
            status = 'on'
        else:
            status = 'off'
        if key == 'mktCapUSD':
            base = filt[key][0]
            lower = base * filt['mktCap_interval'][0]
            upper = base * filt['mktCap_interval'][1]
            msg  = f'{key}: {currency}{numerize.numerize(lower)} - {currency}{numerize.numerize(upper)} '
            msg += f'(base={currency}{numerize.numerize(base)} / status={status})'
            print(msg)
        elif key == 'mktCap_interval':
            continue
        else:
            print(f'{key}: {filt[key][0]} status={status}')
    print()
