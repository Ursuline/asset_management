#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  8 11:44:40 2021

fundamentals_plot_driver.py

Driver for fundamentals plots

@author: charly
"""
import os
import pandas as pd
import company as cny
import metrics as mtr
import fundamentals_plotter as f_pltr
import plotter_defaults as dft

EXPIRATION_DATE = '2021-12-31'
TICKER   = 'MC.PA'
YEAR_0   = int('2013')
YEAR_1   = int('2020')

def aggregate_metrics(cie:cny.Company, metrics:str, yr_0:int, yr_1:int):
    '''Extract metrics corresponding to plot type and aggregate with changes'''
    return pd.merge(cie.load_cie_metrics_over_time(metrics=metrics, yr_start=yr_0, yr_end=yr_1, change=False),
                    cie.load_cie_metrics_over_time(metrics=metrics, yr_start=yr_0, yr_end=yr_1, change=True),
                    on  = 'year',
                    how = 'inner',
                    )


if __name__ == '__main__':
    prefix = f'{TICKER}_{YEAR_0}-{YEAR_1}'
    company = cny.Company(ticker=TICKER, period='annual', expiration_date=EXPIRATION_DATE)

    for metric_set in mtr.get_metric_set_names():
        subtitle  = mtr.metrics_set_names[f'{metric_set}']
        if metric_set.startswith('valuation'):
            subtitle += f' (5-year \u03b2={company.get_beta():.1f})'
        req_metrics = list(getattr(mtr, metric_set).keys())
        plotter = f_pltr.FundamentalsPlotter(cie      = company,
                                             cie_data = aggregate_metrics(cie     = company,
                                                                          metrics = req_metrics,
                                                                          yr_0    = YEAR_0,
                                                                          yr_1    = YEAR_1,
                                                                          ),
                                            )
        plotter.plot(metric_set = metric_set,
                     subtitle  = subtitle,
                     filename  = os.path.join(dft.get_plot_directory(),
                                              prefix + f'_{metric_set}.html',
                                              ),
                     )
