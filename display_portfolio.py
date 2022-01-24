#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 09:02:04 2021

Outputs the contents of a portfolio to screen
Usage:
python display_portfolio.py [portfolio file name with .csv extension]

display_portfolio.py

@author: charles megnin
"""
import os
import sys
from tabulate import tabulate
import pandas as pd

# Cloud server
SERVER_URL     = 'https://ml-finance.ams3.digitaloceanspaces.com'
SERVER_PATH    = 'charting/portfolios'
PORTFOLIO_DIR  = f'{SERVER_URL}/{SERVER_PATH}/'
RUN = 'local'

if __name__ == '__main__':

    url = os.path.join(PORTFOLIO_DIR,
                       #sys.argv[1],
                       'watchlist.csv'
                       )
    try:
        contents = pd.read_csv(url)
    except:
        print(f'Could not load file {sys.argv[1]} from {url}')
        sys.exit(0)
    contents.loc[0] = ['Ticker', 'Position', 'Strategy']
    if RUN == 'local':
        print(tabulate(contents,
                       showindex = True,
                       tablefmt  = 'fancy_grid',
                       )
              )
    elif RUN == 'remote':
        print(contents.to_html())
    else:
        msg = f'Value for variable {RUN=} should be "remote" or "local"'
        raise KeyError(msg)

