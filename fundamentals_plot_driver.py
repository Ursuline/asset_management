#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  8 11:44:40 2021

Driver for fundamentals plots

@author: charly
"""
import os
import pandas as pd
import company as cny
import metrics as mtr

DIR = '/Users/charly/Documents/projects/asset_management/data'

# Target company specs
EXPIRATION_DATE = '2021-12-31'

TICKER   = 'SU.PA'
YEAR_0   = int('2013')
YEAR_1   = int('2020')

if __name__ == '__main__':
    prefix = f'{TICKER}_{YEAR_0}-{YEAR_1}_{EXPIRATION_DATE}'
    cie = cny.Company(ticker=TICKER, period='annual', expiration_date=EXPIRATION_DATE)
    wb_metrics = mtr.get_metrics('wb_metrics')
    # Generate metrics dataframe
    wb = pd.merge(cie.load_cie_metrics_over_time(metrics=wb_metrics, yr_start=YEAR_0, yr_end=YEAR_1, change=False),
                  cie.load_cie_metrics_over_time(metrics=wb_metrics, yr_start=YEAR_0, yr_end=YEAR_1, change=True),
                  on='year',
                  how ="inner",
                  )
    # Plot dataframe

    cie.fundamentals_plot(time_series=wb,
                          plot_type='wb',
                          subtitle = '"Warren Buffet" metrics',
                          filename = os.path.join(DIR, prefix + '_wb.html'),
                          )
