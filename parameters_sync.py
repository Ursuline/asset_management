#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 9 11:16 2022

Parameter set for sync_tickers.py

@author: charles mégnin
"""
import os
from charting import trading_defaults as dft
import yaml_utilities as yaml_util

# Cloud server
PORTFOLIO_URL  = 'https://ml-finance.ams3.digitaloceanspaces.com'
PORTFOLIO_PATH = 'charting/resources'
PORTFOLIO_DIR  = os.path.join(PORTFOLIO_URL, PORTFOLIO_PATH)
PORTFOLIO_FILE = 'charting_run.yaml'
YAML_FILE      = os.path.join(PORTFOLIO_DIR, PORTFOLIO_FILE)


def load_data():
    return yaml_util.yaml_load(path=YAML_FILE, remote=True)


def get_portfolios(yml_data):
    root = os.path.join(yml_data['portfolio_url'], yml_data['portfolio_path'])
    portfolio_files = yml_data['portfolio_files']
    portfolios = []
    for file in portfolio_files:
        portfolios.append(os.path.join(root, file))
    return portfolios


def get_recipients(yml_data):
    '''Return email recipients'''
    return yml_data['recipients']


def get_time_span(yml_data):
    '''Returns start and end dates as a list'''
    start_date = yml_data['start_date']
    if yml_data['end_date'].lower() == 'today':
        end_date = dft.TODAY
    elif yml_data['end_date'].lower() == 'yesterday':
        end_date = dft.YESTERDAY
    else:
        end_date = yml_data['end_date']
    return [start_date, end_date]


def get_recommender_parameters(yml_data):
    '''Returns various parameters for the Recommender as a dictionary'''
    parameters = {}
    pars = ['screen', 'email', 'notify']
    for par in pars:
        parameters[par] = yml_data[par]
    return parameters


def get_display_parameters(yml_data):
    '''Returns various display parameters as a dictionary'''
    parameters = {}
    pars = ['display_time_series', 'display_surface_plot',
            'display_contour_plot', 'ctr_sfc_plot_formats'
            ]
    for par in pars:
        parameters[par] = yml_data[par]
    return parameters


def get_refresh_parameters(yml_data):
    '''Returns refresh parameters as a dictionary'''
    parameters = {}
    pars = ['refresh_yahoo', 'refresh_ema']
    for par in pars:
        parameters[par] = yml_data[par]
    return parameters


def get_smtp_parameters(yml_data):
    smtp_parameters={}
    smtp_parameters['ssl_port'] = yml_data['ssl_port']
    smtp_parameters['smtp_server'] = yml_data['smtp_server']
    return smtp_parameters


def get_db_parameters(yml_data):
    db_parameters={}
    db_parameters['persist'] = yml_data['persist']
    return db_parameters


if __name__ == '__main__':
    '''Test driver'''
    yaml_data  = load_data()
    print({type(yaml_data)})
    portfolios = get_portfolios(yaml_data)
    recipients = get_recipients(yaml_data)
    time_span  = get_time_span(yaml_data)
    recommender_parameters = get_recommender_parameters(yaml_data)
    display_parameters     = get_display_parameters(yaml_data)
    refresh_parameters     = get_refresh_parameters(yaml_data)
    ssl_port    = get_smtp_parameters(yaml_data)['ssl_port']
    smtp_server = get_smtp_parameters(yaml_data)['smtp_server']
    for portfolio in portfolios:
        print(portfolio)
    print(recommender_parameters)
    print(display_parameters)
    print(refresh_parameters)
    print(recipients)
    print(time_span)
    print(ssl_port)
    print(smtp_server)
