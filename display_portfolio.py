#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 09:02:04 2021

Outputs the contents of a portfolio to screen

display_portfolio.py

@author: charles megnin
"""
import os
import sys
from tabulate import tabulate
import pandas as pd
from charting import parameters_sync as dft


if __name__ == '__main__':

    url = os.path.join(dft.PORTFOLIO_DIR,
                       sys.argv[1]
                       )
    try:
        contents = pd.read_csv(url)
        contents.loc[0] = ['Ticker', 'Position', 'Strategy']
        print(tabulate(contents,
                       showindex = False,
                       tablefmt  = 'fancy_grid',
                       )
              )
    except:
        print(f'Could not load file {sys.argv[1]} from {url}')
        sys.exit(0)
