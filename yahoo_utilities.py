#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 31 16:19:17 2022

@author: charly
"""
import os
import re
import requests
import time
from bs4 import BeautifulSoup
import utilities as util

URL = 'https://finance.yahoo.com/quote/'

def get_names_from_tickers(tickers:list):
    '''Returns a list of tickers & company names from a list of tickers'''
    # Spoof browser
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    try:
        security_list = []
        for ticker in tickers:
            path = os.path.join(URL,
                                f'{ticker}?p={ticker}&.tsrc=fin-srch',
                                )
            soup = BeautifulSoup(requests.get(path,
                                              headers=headers).text,
                                 "html.parser",
                                 )
            if soup.h1 is None:
                name = ''
            else:
                name = soup.h1.text.strip()
            # Remove the ticker between parentheses
            name = re.sub("[\(\[].*?[\)\]]", "", name).strip()
            if name:
                security_list.append([ticker, name])
        return security_list
    except:
        print(f'{__name__} Failed to return names for ticker list {tickers}')
        raise


if __name__ == '__main__':
    '''Test driver'''
    start_tm = time.time() # total_time
    tickers = ['^N225', 'AAPL', 'MC.PA']
    print(get_names_from_tickers(tickers=tickers))
    print(f"Total elapsed time: {util.convert_seconds(time.time()-start_tm)}")
