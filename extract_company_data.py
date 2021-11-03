#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  1 19:03:37 2021
extract_company_data.py

Extract individual industry, sector, market cap, currency & country data from
fa.profile() and merge with fa.available_companies() data
Add a market cap in USD column

@author: charly
"""
import time
import pandas as pd
from tqdm import tqdm
import FundamentalAnalysis as fa
from forex_python.converter import CurrencyRates
import api_keys as keys
from finance import utilities as util

API_KEY = keys.FMP
cur_rates = CurrencyRates()


def get_usd_xrate(curr):
    '''
    Returns currency -> USD conversion rate.
    If currency not found, return 0.0
    '''
    try:
        return cur_rates.get_rate(curr, "USD")
    except:
        msg  = f'get_usd_xrate: Could not convert currency {curr} '
        msg += 'setting mktCapUSD to 0'
        print(msg)
        return 0.0


def add_mktcap_usd(dataframe):
    '''Adds a mktCapUSD column '''
    all_dfs = []
    for currency in list(dataframe.currency.unique()):
        xrate = get_usd_xrate(currency)
        print(f'Exchange rate = {xrate}')
        df_usd = dataframe[dataframe.currency == currency].copy()
        df_usd['mktCapUSD'] = df_usd['mktCap'] * xrate
        all_dfs.append(df)
    return pd.concat(all_dfs)


if __name__ == '__main__':
    start_tm = time.time() # total_time

    # Load list of available companies
    companies = fa.available_companies(API_KEY)

    # Filter out non-stock data (etfs, etc)
    companies = companies[companies.type == 'stock']
    print(f'Processing {companies.shape[0]} companies')

    # For each company, aggregate data in lists
    industries = []
    sectors    = []
    currencies = []
    mktCaps    = []
    countries  = []
    for company in tqdm(companies.index, position=0, leave=True):
        print(f'Processing {company}')
        company_profile = fa.profile(company, API_KEY)

        industries.append(company_profile.loc['industry'][0])
        sectors.append(company_profile.loc['sector'][0])
        mktCaps.append(company_profile.loc['mktCap'][0])
        currencies.append(company_profile.loc['currency'][0])
        countries.append(company_profile.loc['country'][0])

    # Aggregate lists into a dataframe with company ticker symbol as index
    df = pd.DataFrame(
                     {'industry': industries,
                      'sector': sectors,
                      'mktCap': mktCaps,
                      'currency': currencies,
                      'country': countries,
                     }, index=companies.index
                     )

    # Merge with initial data
    merged = companies.merge(df, on='symbol')

    #Add column of mktCap in USD
    merged = add_mktcap_usd(merged)

    # Save to csv file
    merged.to_csv('stocks.csv', index=True)

    print(f"Total elapsed time: {util.convert_seconds(time.time()-start_tm)}")
