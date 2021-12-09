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

TICKER   = 'RMS.PA'
YEAR_0   = int('2013')
YEAR_1   = int('2020')

def aggregate_metrics(metrics:str, yr_0:int, yr_1:int):
    return pd.merge(cie.load_cie_metrics_over_time(metrics=metrics, yr_start=yr_0, yr_end=yr_1, change=False),
                    cie.load_cie_metrics_over_time(metrics=metrics, yr_start=yr_0, yr_end=yr_1, change=True),
                    on='year',
                    how ="inner",
                    )


if __name__ == '__main__':
    prefix = f'{TICKER}_{YEAR_0}-{YEAR_1}_{EXPIRATION_DATE}'
    cie = cny.Company(ticker=TICKER, period='annual', expiration_date=EXPIRATION_DATE)

    plot_types = ['bs', 'income', 'wb', 'dupont', 'valuation', 'dividend']
    for plot_type in plot_types:
        cie.fundamentals_plot(time_series = aggregate_metrics(metrics = mtr.get_metrics(f'{plot_type}_metrics'),
                                                              yr_0    = YEAR_0,
                                                              yr_1    = YEAR_1,
                                                              ),
                              plot_type   = plot_type,
                              subtitle    = mtr.metrics_set_names[f'{plot_type}_metrics'],
                              filename    = os.path.join(DIR, prefix + f'_{plot_type}.html'),
                              )