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

def build_metrics_dataframe(metrics:str, yr_0:int, yr_1:int):
    return pd.merge(cie.load_cie_metrics_over_time(metrics=metrics, yr_start=yr_0, yr_end=yr_1, change=False),
                    cie.load_cie_metrics_over_time(metrics=metrics, yr_start=yr_0, yr_end=yr_1, change=True),
                    on='year',
                    how ="inner",
                    )


if __name__ == '__main__':
    prefix = f'{TICKER}_{YEAR_0}-{YEAR_1}_{EXPIRATION_DATE}'
    cie = cny.Company(ticker=TICKER, period='annual', expiration_date=EXPIRATION_DATE)

    cie.fundamentals_plot(time_series = build_metrics_dataframe(mtr.get_metrics('bs_metrics'),
                                                                YEAR_0,
                                                                YEAR_1,
                                                                ),
                          plot_type   = 'bs',
                          subtitle    = 'Balance sheet metrics',
                          filename    = os.path.join(DIR, prefix + '_bs.html'),
                          )

    cie.fundamentals_plot(time_series = build_metrics_dataframe(mtr.get_metrics('income_metrics'),
                                                                YEAR_0,
                                                                YEAR_1,
                                                                ),
                          plot_type   = 'income',
                          subtitle    = 'Income & Free cash flow metrics',
                          filename    = os.path.join(DIR, prefix + '_bs.html'),
                          )

    cie.fundamentals_plot(time_series = build_metrics_dataframe(mtr.get_metrics('wb_metrics'),
                                                                YEAR_0,
                                                                YEAR_1,
                                                                ),
                          plot_type   = 'wb',
                          subtitle    = '"Warren Buffet" metrics',
                          filename    = os.path.join(DIR, prefix + '_wb.html'),
                          )

    cie.fundamentals_plot(time_series = build_metrics_dataframe(mtr.get_metrics('dupont_metrics'),
                                                                YEAR_0,
                                                                YEAR_1,
                                                                ),
                          plot_type   = 'dupont',
                          subtitle    = 'Dupont metrics',
                          filename    = os.path.join(DIR, prefix + '_dupont.html'),
                          )
