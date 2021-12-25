#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  4 09:52:09 2021

comparison_plot_driver.py

Driver for fundamentals comparison plots

@author: charly
"""
import os
import sys
import time
import pandas as pd
import metrics as mtr
import company as cny
import comparison_plotter as c_pltr
import plotter_defaults as dft
import utilities as util

TRUNC           = 15   # of characters to retain in company name
EXPIRATION_DATE = '2021-12-31'

# Target company specs
TARGET_TICKER = 'RMS.PA'
YEAR          = '2019'


def build_metric_dataframe(company:cny.Company, ticker:str, req_metrix:list, year:str, idx:str):
    '''Returns a dataframe of company metrics'''
    metric_df = pd.DataFrame.from_dict(company.load_cie_metrics(year = year,
                                                                req_metrics = req_metrix,
                                                                ),
                                       orient = 'index',
                                       )
    metric_df.columns    = [ticker]
    metric_df            = metric_df.transpose()
    metric_df.index.name = idx
    return metric_df


def aggregate_peers(target_ticker:str, peers:list, req_metrix:list, year:str):
    '''Extract metrics for peers and aggregate
       Returns list of peer names & dataframe
    '''
    idx = 'company'
    company = cny.Company(ticker          = target_ticker,
                          period          = dft.PERIOD,
                          expiration_date = EXPIRATION_DATE,
                          )

    ticker = company.get_company_name()[0:TRUNC]

    list_of_peers = [ticker]

    for i, peer in enumerate(peers):
        company = cny.Company(ticker          = peer,
                              period          = dft.PERIOD,
                              expiration_date = EXPIRATION_DATE,
                          )
        ticker = company.get_company_name()[0:TRUNC]
        temp_df   = build_metric_dataframe(company    = company,
                                           ticker     = ticker,
                                           req_metrix = req_metrix,
                                           year       = year,
                                           idx        = idx,
                                           )
        if i == 0:
            metric_df = temp_df.copy()
        else:
            list_of_peers.append(ticker)
            metric_df = metric_df.append(temp_df, ignore_index = False)
    # Add peer companies to change in metric dataframe
    for i, peer in enumerate(peers):
        company = cny.Company(ticker      = peer,
                          period          = dft.PERIOD,
                          expiration_date = EXPIRATION_DATE,
                          )
        ticker = company.get_company_name()[0:TRUNC]
        temp_df = company.load_cie_metrics_over_time(metrics  = req_metrix,
                                                 yr_start = int(year),
                                                 yr_end   = int(year),
                                                 change   = True,
                                                 )
        temp_df.index.name = ticker
        if i == 0:
            d_metric_df = temp_df.copy()
        else:
            d_metric_df = d_metric_df.append(temp_df, ignore_index = False)
    d_metric_df.insert(0, idx, list_of_peers)
    d_metric_df = d_metric_df.set_index(idx, drop=True)
    # merge metric and its change:
    metric_df = pd.merge(metric_df, d_metric_df, on=idx, how='inner')
    metric_df.index.name = None
    metric_df = metric_df.transpose()
    metric_df.index.name = 'metric'
    return list_of_peers, metric_df


def load_peers(argv):
    try:
        peers = pd.read_csv(argv[1],
                            header=None)
        peers = peers[0].tolist()
        if peers[0] != TARGET_TICKER:
            print(f'input data file {sys.argv[1]} does not correspond to requested ticker {TARGET_TICKER}')
            sys.exit()
        return (peers)
    except FileNotFoundError:
        print(f'{argv[1]} does not exist')
        sys.exit()


if __name__ == '__main__':
    start_tm = time.time()
    try:
        peer_list=load_peers(sys.argv)
    except IndexError:
        print('usage: python comparison_plot_driver.py peer_filename.csv')
        sys.exit()

    prefix = f'{TARGET_TICKER}_{YEAR}_peers'

    cie = cny.Company(ticker          = TARGET_TICKER,
                      period          = dft.PERIOD,
                      expiration_date = EXPIRATION_DATE,
                      )

    for metric_set in mtr.get_metric_set_names():
        req_metrics = mtr.get_set_metrics(metric_set)
        peer_names, df = aggregate_peers(target_ticker = TARGET_TICKER,
                                         peers         = peer_list,
                                         req_metrix    = req_metrics,
                                         year          = YEAR,
                                         )
        plotter = c_pltr.ComparisonPlotter(base_cie   = cie,
                                           cie_data   = df,
                                           peer_names = peer_names,
                                           year       = YEAR,
                                           )
        output_file = os.path.join(dft.get_plot_directory(),
                                   prefix + f'_{metric_set}.html')
        subtitle = mtr.get_metric_set_description(metric_set)
        plotter.plot(metric_set = metric_set,
                     subtitle  = subtitle,
                     filename  = output_file,
                     )
        print(f"Total elapsed time: {util.convert_seconds(time.time()-start_tm)}")
