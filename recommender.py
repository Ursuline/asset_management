#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 11 14:33:03 2021

@author: Charles Mégnin
"""
import smtplib
import ssl
import pandas as pd

import trading as tra
import trading_defaults as dft
import private as pvt

class Recommender():
    '''
    Handles the dispatching of trading recommendations

    '''
    def __init__(self):
        self._recommendations = [] # list of recommendations


    def add_recommendation(self, recommendation):
        '''Add a recommendation to the list of recommendations'''
        self._recommendations += recommendation

    def get_recommendations(self):
        '''Return the list of recommendations'''
        return self._recommendations


class Recommendation():
    '''
    A recommendation
    '''
    def __init__(self, ticker_name, ticker_symbol, target_date):
        self._name   = ticker_name
        self._symbol = ticker_symbol
        self._date          = target_date
        self._action        = None
        self._position      = None
        self._subject       = None
        self._body          = None


    def make_recommendation(self, ticker_object, span, buffer, screen=True, email=False):
        '''
        Make recommendation & dispatches to various outputs
        '''
        self._build_recommendation(ticker_object, span, buffer)
        if screen:
            self._print_recommendation()
        if email:
            self._email_recommendation()


    def _build_recommendation(self, ticker_object, span, buffer):
        '''
        Builds a recommendation for the target_date
        The recommednation returned is a kist consisting of an action (buy, sell, n/c)
        and a position (long, short, cash)
        '''
        data  = ticker_object.get_market_data()
        dates = ticker_object.get_dates()

        security = pd.DataFrame(data.loc[dates[0]:dates[1], #trim
                                f'Close_{self._symbol}']
                                )
        security.rename(columns={f'Close_{self._symbol}': "Close"},
                        inplace=True
                        )
        strategy = tra.build_strategy(security, span, buffer, dft.INIT_WEALTH)
        rec = strategy.loc[self._date, ["ACTION", "POSITION"]]

        self._action   = rec[0]
        self._position = rec[1]

        subject  = f'Recommendation for {self._name} '
        subject += f'({self._symbol}) | {self._date}'
        self._subject = subject

        body  = f'action: {self._action} | '
        body += f'new position: {self._position}'
        self._body = body


    def _print_recommendation(self):
        '''Print recommendation to screen'''
        s = '*'
        n = 75
        line = ''.join([char*n for char in s])

        print('\n' + line)
        print(self._subject + '\n' + self._body)
        print(line + '\n')


    def _email_recommendation(self):
        '''Email recommendation (migrate to Recommender)'''
        port         = dft.SSL_PORT
        smtp_server  = dft.SMTP_SERVER
        sender_email = pvt.SENDER_EMAIL
        password     = pvt.PASSWORD

        message = f'Subject: {self._subject}\n\n' + self._body

        # Create a secure SSL context
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            for recipient_email in pvt.RECIPIENT_EMAILS:
                server.sendmail(sender_email, recipient_email, message)
