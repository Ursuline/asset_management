#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  4 09:52:09 2021

Driver for fundamentals comparison plots

@author: charly
"""
import os
import pandas as pd
import utilities as util
import metrics as mtr
import company as cny
import comparison_plotter as c_pltr
import plotter_defaults as dft

USE_NAME = True # use company name instead of ticker
TRUNC    = 15   # of characters to keep in company name

# Filter flags
INDUSTRY = True
SECTOR   = True
MKTCAP   = True
CURRENCY = True
COUNTRY  = False
XCHANGE  = False

# Window of mktCap to include as a fraction of target company mktCap
MKT_CAP_WINDOW = {'lower': .1,
                  'upper': 10}
EXPIRATION_DATE = '2021-12-31'

# Target company specs
TARGET_TICKER   = 'MC.PA'
YEAR            = '2019'


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
    returns a set of tickers
    '''
    stocks       = pd.read_csv(dft.get_data_path()) # load stock data from cloud storage
    target_stock = stocks[stocks.symbol == target_ticker]

    #Returns list of company tickers matching filter values tagged as True'''
    for key in list(filt.keys()):
        if filt[key][1] is True:
            if key == 'mktCapUSD':
                #CHECK THAT THIS WORKS
                lower  = target_stock[key].values[0] * filt['mktCap_interval'][0]
                upper  = target_stock[key].values[0] * filt['mktCap_interval'][1]
                stocks = stocks[(stocks[key] >= lower) & (stocks[key] <= upper)]
            else: # filter other than market cap
                stocks = stocks[stocks[key] == filt[key][0]]
    return set(stocks.symbol)


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
    if USE_NAME is True:
        ticker = company.get_company_name()[0:TRUNC]
    else:
        ticker = TARGET_TICKER
    list_of_peers = [ticker]
    # Build first row with target company data
    metric_df   = build_metric_dataframe(company    = company,
                                         ticker     = ticker,
                                         req_metrix = req_metrix,
                                         year       = year,
                                         idx        = idx,
                                         )
    d_metric_df = company.load_cie_metrics_over_time(metrics  = req_metrix,
                                                 yr_start = int(year),
                                                 yr_end   = int(year),
                                                 change   = True,
                                                 )
    # Add peer companies to  metric dataframe
    for peer in peers:
        company = cny.Company(ticker          = peer,
                              period          = dft.PERIOD,
                              expiration_date = EXPIRATION_DATE,
                          )
        if USE_NAME is True:
            ticker = company.get_company_name()[0:TRUNC]
        else:
            ticker = peer
        list_of_peers.append(ticker)
        temp_df   = build_metric_dataframe(company    = company,
                                           ticker     = ticker,
                                           req_metrix = req_metrix,
                                           year       = year,
                                           idx        = idx,
                                           )
        metric_df = metric_df.append(temp_df, ignore_index = False)
    # Add peer companies to change in metric dataframe
    for peer in peers:
        company = cny.Company(ticker      = peer,
                          period          = dft.PERIOD,
                          expiration_date = EXPIRATION_DATE,
                          )
        if USE_NAME is True:
            ticker = company.get_company_name()[0:TRUNC]
        else:
            ticker = peer
        temp_df = company.load_cie_metrics_over_time(metrics  = req_metrix,
                                                 yr_start = int(year),
                                                 yr_end   = int(year),
                                                 change   = True,
                                                 )
        temp_df.index.name = ticker
        d_metric_df = d_metric_df.append(temp_df, ignore_index = False)
    d_metric_df.insert(0, idx, list_of_peers)
    d_metric_df = d_metric_df.set_index(idx, drop=True)
    # merge metric and its change:
    metric_df = pd.merge(metric_df, d_metric_df, on=idx, how='inner')
    metric_df.index.name = None
    metric_df = metric_df.transpose()
    metric_df.index.name = 'metric'
    return list_of_peers, metric_df


if __name__ == '__main__':
    prefix = f'{TARGET_TICKER}_peers_{YEAR}'
    securities = pd.read_csv(dft.get_data_path())
    target_security = securities[securities.symbol == TARGET_TICKER]
    cie = cny.Company(ticker          = TARGET_TICKER,
                      period          = dft.PERIOD,
                      expiration_date = EXPIRATION_DATE,
                      )
    filter_d = {'industry':          (target_security['industry'].values[0], INDUSTRY),
                'sector':            (target_security['sector'].values[0], SECTOR),
                'mktCapUSD':         (target_security['mktCapUSD'].values[0], MKTCAP),
                'mktCap_interval':   (MKT_CAP_WINDOW['lower'],
                                      MKT_CAP_WINDOW['upper'],
                                      ),
                'currency':          (target_security['currency'].values[0], CURRENCY),
                'country':           (target_security['country'].values[0], COUNTRY),
                'exchangeShortName': (target_security['exchangeShortName'].values[0], XCHANGE),
                }
    util.echo_filter(filt     = filter_d,
                     currency = cie.get_currency_symbol(),
                     )
    peer_list = extract_peers(target_ticker = TARGET_TICKER,
                                  filt          = filter_d,
                                  )
    peer_list.discard(TARGET_TICKER) # If it exists, remove target stock to avoid duplicate
    print(f'main: {len(peer_list)} peers returned: {peer_list}')
    plot_types = ['bs', 'income', 'income2', 'wb', 'dupont']
    for plot_type in plot_types:
        metrics_set = f'{plot_type}_metrics'
        req_metrics = list(getattr(mtr, metrics_set).keys())
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
                                   prefix + f'_{plot_type}.html')
        subtitle    = mtr.metrics_set_names[metrics_set]
        plotter.plot(plot_type = plot_type,
                     subtitle  = subtitle,
                     filename  = output_file,
                     )
