#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 17:03:05 2021

@author: charly
"""
import math
import json
import pandas as pd
import requests
from numerize import numerize

URL  = 'https://ml-finance.ams3.digitaloceanspaces.com'
PATH = 'fundamentals'
FILE = 'stocks.csv'
DATA_PATH  = f'{URL}/{PATH}/{FILE}'

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


def echo_filter(filt:dict, currency:str):
    '''Outputs company filter characteristics to screen'''
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


# Math utilities
def round_up(val:float, ndigits:int):
    '''round up utility'''
    return (math.ceil(val * math.pow(10, ndigits)) + 1) / math.pow(10, ndigits)


def round_down(val:float, ndigits:int):
    '''round down utility'''
    return (math.floor(val * math.pow(10, ndigits)) - 1) / math.pow(10, ndigits)


def convert_seconds(time_s):
    '''
    Given a time duration in seconds, convert to DHMS & return as a string
    DUPLICATE FROM finance directory
    '''
    minute = 60
    hour   = 60 * minute
    day    = 24 * hour
    def sec_to_min(sec):
        time_m = sec // minute
        time_s = sec % minute
        return time_m, time_s

    def sec_to_hour(sec):
        time_h = sec // hour
        time_s = sec % hour
        time_m, time_s = sec_to_min(time_s)
        return time_h, time_m, time_s

    def sec_to_day(sec):
        time_d = sec // day
        time_s = sec % day
        time_h, time_m, time_s = sec_to_hour(time_s)
        return time_d, time_h, time_m, time_s

    if time_s >= day:
        time_d, time_h, time_m, time_s = sec_to_day(time_s)
        suffix = 'day'
        if time_d > 1:
            suffix += 's'
        return f'{time_d:.0f} {suffix} {time_h:.0f}hr:{time_m:.0f}mn:{time_s:.1f}s'
    if time_s >= hour:
        time_h, time_m, time_s = sec_to_hour(time_s)
        return f'{time_h:.0f}hr:{time_m:.0f}mn:{time_s:.1f}s'
    if time_s >= minute:
        time_m, time_s = sec_to_min(time_s)
        return f'{time_m:.0f}mn:{time_s:.1f}s'
    return f'{time_s:.1f}s'