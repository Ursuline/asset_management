#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 11 14:33:03 2021

@author: Charles Mégnin
"""
import smtplib
import ssl
import pandas as pd
#import time

import trading_defaults as dft
import private as pvt # recipient names, smtp sender name/pwd

class Recommender():
    '''
    Handles the dispatching of trading recommendations
    '''
    def __init__(self, screen = True, email = True):
        '''
        _screen : print to screen
        _email : send email
        '''
        self._recommendations = [] # list of recommendations
        self._screen = screen
        self._email  = email


    def set_screen(self, screen: bool):
        '''Switch output to screen'''
        self._screen = screen

    def set_email(self, email: bool):
        '''Switch email'''
        self._email = email

    def add_recommendation(self, recommendation):
        '''Add a recommendation to the list of recommendations'''
        self._recommendations.append(recommendation)

    def get_recommendations(self):
        '''Return the list of recommendations'''
        return self._recommendations


    # def notify_SMS(self):

    #     # enter all the details
    #     # get app_key and app_secret by registering
    #     # a app on sinchSMS
    #     number = 'your_mobile_number'
    #     app_key = 'your_app_key'
    #     app_secret = 'your_app_secret'

    #     # enter the message to be sent
    #     message = 'Hello Message!!!'

    #     client = SinchSMS(app_key, app_secret)
    #     print("Sending '%s' to %s" % (message, number))

    #     response = client.send_message(number, message)
    #     message_id = response['messageId']
    #     response = client.check_status(message_id)

    #     # keep trying unless the status retured is Successful
    #     while response['status'] != 'Successful':
    #         print(response['status'])
    #         time.sleep(1)
    #         response = client.check_status(message_id)

    #     print(response['status'])



    def notify(self, screen_nc: bool, email_nc: bool):
        '''
        Dispatches to make recommendations
        screen_nc : output n/c action recommendation to screen
        email_nc : send email if n/c action
        NB: screen & action must aalso be set to True for each to be activated
        '''
        if self._screen:
            self._print_recommendations(screen_nc)

        if self._email:
            self._email_recommendations(email_nc)


    def _print_recommendations(self, screen_nc: bool):
        ''' Output recommendations to screen '''
        root    = '*'
        repeats = 75
        line    = ''.join([char * repeats for char in root])

        print('\n' + line)
        for rec in self._recommendations:
            if screen_nc or not (screen_nc or rec.get_action() == 'n/c'):
                rec.print_recommendation(notify=True)
                print()
        print(line)


    def _email_recommendations(self, email_nc: bool):
        '''Email recommendation (migrate to Recommender)'''
        port         = dft.SSL_PORT
        smtp_server  = dft.SMTP_SERVER
        sender_email = pvt.SENDER_EMAIL
        password     = pvt.PASSWORD

        subject = 'Trade recommendation'
        body    = ''

        n_tickers = 0
        for rcm in self._recommendations:
            name = rcm.get_name()
            symb = rcm.get_symbol()
            if email_nc or not (email_nc or rcm.get_action() == 'n/c'):
                body += f'{name} ({symb})\n{rcm.get_body()}\n'
                n_tickers += 1

        if n_tickers != 0:
            message = f'Subject: {subject}\n\n' + body

            # Create a secure SSL context
            context = ssl.create_default_context()

            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender_email, password)
                for recipient_email in pvt.RECIPIENT_EMAILS:
                    server.sendmail(sender_email, recipient_email, message)
            print('email sent to list')
        else:
            print('no actions required - no email sent')


class Recommendation():
    '''
    encapsulates the recommendation to buy | sell | n/c
    captured in the target date row ACTION column of tthe ticker object's data
    '''
    def __init__(self, ticker_name, ticker_symbol, target_date):
        self._name   = ticker_name
        self._symbol = ticker_symbol
        self._date     = target_date
        self._action   = None
        self._position = None
        self._subject  = None
        self._body     = None

    def get_body(self):
        ''''Return the body of the recommendation'''
        return self._body

    def get_name(self):
        ''''Return the ticker name'''
        return self._name

    def get_symbol(self):
        ''''Return the ticker symbol'''
        return self._symbol

    def get_action(self):
        '''Get the recommended action '''
        return self._action

    def get_position(self):
        '''Get the recommended position '''
        return self._position

    def self_describe(self):
        '''Display all variables in class'''
        print(self.__dict__)


    def build_recommendation(self, ticker_object, topomap, span, buffer):
        '''
        Builds a recommendation for the target_date
        The recommednation returned is a kist consisting of an action (buy, sell, n/c)
        and a position (long, short, cash)
        '''
        data  = ticker_object.get_market_data()
        dates = ticker_object.get_dates()

        security = pd.DataFrame(data.loc[dates[0]:dates[1], #trim
                                f'Close_{self._symbol}'],
                                )
        security.rename(columns = {f'Close_{self._symbol}': "Close"},
                        inplace = True,
                        )
        strategy = topomap.build_strategy(security, span, buffer, dft.INIT_WEALTH)
        rec = strategy.loc[self._date, ["ACTION", "POSITION"]]

        self._action   = rec[0]
        self._position = rec[1]

        subject  = f'Recommendation for {self._name} '
        subject += f'({self._symbol}) | {self._date}'
        self._subject = subject

        body  = f'recommendation: {self._action} | '
        body += f'position: {self._position}'
        self._body = body


    def print_recommendation(self, notify: bool):
        '''Print recommendation to screen'''
        if notify:
            msg  = f'recommendation {self._name} ({self._symbol}): '
            msg += f'{self._action} | position: {self._position}'
            print(msg)
