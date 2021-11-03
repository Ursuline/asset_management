#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 17:03:05 2021

@author: charly
"""
import requests, json

def build_url(ticker:str, api_key:str):
    root = 'https://financialmodelingprep.com/api/v4/stock_peers?'
    request = f'symbol={ticker}&apikey={api_key}'
    url = f'{root}{request}'
    return url


def extract_peers(ticker:str, api_key:str):
    try:
        url = requests.get(build_url(ticker, api_key))
        text = url.text
        data = json.loads(text)
        cie_name = data[0]
        peerList = cie_name['peersList']
        return peerList
    except:
        raise ValueError('Badly formed URL {url}')
