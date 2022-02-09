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


class ChartingParameters():
    '''`Encapsulates charting run data (in remote charting_run.yaml)'''
    def __init__(self):
        self._yaml_data =  yaml_util.yaml_load(path = os.path.join(PORTFOLIO_DIR,
                                                                   PORTFOLIO_FILE,
                                                                   ),
                                               remote = True,
                                               )


    def get_portfolios(self):
        '''Returns portfolio-related parameters as a dictionary'''
        root = os.path.join(self._yaml_data['portfolio_url'], self._yaml_data['portfolio_path'])
        portfolio_files = self._yaml_data['portfolio_files']
        portfolios = []
        for file in portfolio_files:
            portfolios.append(os.path.join(root, file))
        return portfolios


    def get_recipients(self):
        '''Return email recipients'''
        return self._yaml_data['recipients']


    def get_time_span(self):
        '''Returns start and end dates as a list'''
        start_date = self._yaml_data['start_date']
        if self._yaml_data['end_date'].lower() == 'today':
            end_date = dft.TODAY
        elif self._yaml_data['end_date'].lower() == 'yesterday':
            end_date = dft.YESTERDAY
        else:
            end_date = self._yaml_data['end_date']
        return [start_date, end_date]


    def get_recommender_parameters(self):
        '''Returns various parameters for the Recommender as a dictionary'''
        parameters = {}
        pars = ['screen', 'email', 'notify']
        for par in pars:
            parameters[par] = self._yaml_data[par]
        return parameters


    def get_display_parameters(self):
        '''Returns various display parameters as a dictionary'''
        parameters = {}
        pars = ['display_time_series', 'display_surface_plot',
                'display_contour_plot', 'ctr_sfc_plot_formats'
                ]
        for par in pars:
            parameters[par] = self._yaml_data[par]
        return parameters


    def get_refresh_parameters(self):
        '''Returns refresh parameters as a dictionary'''
        parameters = {}
        pars = ['refresh_yahoo', 'refresh_ema']
        for par in pars:
            parameters[par] = self._yaml_data[par]
        return parameters


    def get_smtp_parameters(self):
        '''Returns smtp-related parameters as a dictionary'''
        smtp_parameters={}
        smtp_parameters['ssl_port'] = self._yaml_data['ssl_port']
        smtp_parameters['smtp_server'] = self._yaml_data['smtp_server']
        return smtp_parameters


    def get_db_parameters(self):
        '''Returns database-related parameters as a dictionary'''
        db_parameters={}
        db_parameters['persist'] = self._yaml_data['persist']
        db_parameters['db_ip'] = self._yaml_data['db_ip']
        return db_parameters


if __name__ == '__main__':
    #Test driver
    charting_parameters  = ChartingParameters()

    ptfs = charting_parameters.get_portfolios()
    recipients = charting_parameters.get_recipients()
    time_span  = charting_parameters.get_time_span()
    recommender_parameters = charting_parameters.get_recommender_parameters()
    display_parameters     = charting_parameters.get_display_parameters()
    refresh_parameters     = charting_parameters.get_refresh_parameters()
    ssl_port    = charting_parameters.get_smtp_parameters()['ssl_port']
    smtp_server = charting_parameters.get_smtp_parameters()['smtp_server']
    db_ip       = charting_parameters.get_db_parameters()['db_ip']
    print('*** PORTFOLIOS ***')
    for ptf in ptfs:
        print(ptf)
    print('******************')
    print(recommender_parameters)
    print(display_parameters)
    print(refresh_parameters)
    print(recipients)
    print(time_span)
    print(ssl_port)
    print(smtp_server)
    print(db_ip)
