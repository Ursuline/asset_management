#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 11 14:33:03 2021

@author: Charles Mégnin
"""
import smtplib
import ssl


import trading_defaults as dft
import utilities as util
import private as pvt # recipient names, smtp sender name/pwd

class Recommender():
    '''
    Handles the dispatching of trading recommendations
    '''
    def __init__(self, screen = True, email = True, sms = False):
        '''
        Collects recommendations and dispatches to selected notification method
        _screen : print to screen
        _email : send email
        '''
        self._long_recommendations  = [] # list of long recommendations
        self._short_recommendations = [] # list of short recommendations
        self._screen = screen
        self._email  = email
        self._sms    = sms


    def set_screen(self, screen: bool):
        '''Switch output to screen'''
        self._screen = screen

    def set_email(self, email: bool):
        '''Switch email'''
        self._email = email

    def add_recommendation(self, recommendation):
        '''Add a recommendation to the list of recommendations'''
        if recommendation.get_strategic_position() == 'long':
            self._long_recommendations.append(recommendation)
        elif recommendation.get_strategic_position() == 'short':
            self._short_recommendations.append(recommendation)
        else:
            msg  = 'Recommender.add_recommendation: '
            msg += f'position {recommendation.get_strategic_position()} '
            msg += 'should be long or short.'
            raise ValueError(msg)

    # def get_long_recommendations(self):
    #     '''Return the list of long recommendations'''
    #     return self._long_recommendations

    # def get_short_recommendations(self):
    #     '''Return the list of short recommendations'''
    #     return self._short_recommendations


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
        nrecs = len(self._long_recommendations) + len(self._short_recommendations)

        if nrecs >0: # if there are recommendations
            print(line)
            if len(self._long_recommendations) > 0:
                print('Long strategic position recommendations:')
                for rec in self._long_recommendations:
                    if screen_nc or not (screen_nc or rec.get_action() == 'n/c'):
                        rec.print_recommendation(notify=True, enhanced = True)
            if len(self._short_recommendations) > 0:
                print('Short strategic position recommendations:')
                for rec in self._short_recommendations:
                    if screen_nc or not (screen_nc or rec.get_action() == 'n/c'):
                        rec.print_recommendation(notify=True, enhanced = True)
            print(line)


    def _email_recommendations(self, email_nc: bool):
        '''Email all recommendations'''
        body = ''
        n_tickers = 0

        if len(self._long_recommendations) > 0:
            body += 'Strategic position: long\n'
            for rcm in self._long_recommendations:
                name = rcm.get_name()
                symb = rcm.get_symbol()
                if email_nc or not (email_nc or rcm.get_action() == 'n/c'):
                    body += f'{name} ({symb})\n{rcm.get_body()}\n'
                    n_tickers += 1
            body += '\n'

        if len(self._short_recommendations) > 0:
            body += 'Strategic position: short\n'
            for rcm in self._short_recommendations:
                name = rcm.get_name()
                symb = rcm.get_symbol()
                if email_nc or not (email_nc or rcm.get_action() == 'n/c'):
                    body += f'{name} ({symb})\n{rcm.get_body()}\n'
                    n_tickers += 1

        if n_tickers != 0:
            message = 'Subject: Trade recommendation\n\n' + body

            # Create a secure SSL context
            context = ssl.create_default_context()

            with smtplib.SMTP_SSL(dft.SMTP_SERVER,
                                  dft.SSL_PORT,
                                  context=context) as server:
                server.login(pvt.SENDER_EMAIL,
                             pvt.PASSWORD)
                for recipient_email in pvt.RECIPIENT_EMAILS:
                    server.sendmail(dft.SMTP_SERVER, recipient_email, message)
            print('email sent to list')
            server.close()
        else:
            print('no actions required - no email sent')


class Recommendation():
    '''
    encapsulates the recommendation to buy | sell | n/c
    captured in the target date row ACTION column of tthe ticker object's data
    NB: position is the recommended position for the security
        strategic_position is the long/short position strategy for the security
    '''
    def __init__(self, ticker_name, ticker_symbol, target_date, span, buffer, strategic_position):
        self._name   = ticker_name
        self._symbol = ticker_symbol
        self._date     = target_date
        self._stratpos = strategic_position
        self._action   = None
        self._position = None
        self._span     = span
        self._buffer   = buffer
        self._subject  = None
        self._body     = None

    # Getters
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

    def get_strategic_position(self):
        '''Get the strategic position '''
        return self._stratpos

    def self_describe(self):
        '''Display all variables in class'''
        print(self.__dict__)


    def build_recommendation(self, ticker_object, topomap):
        '''
        Builds a recommendation for the target_date
        '''
        #data  = ticker_object.get_market_data()
        #dates = ticker_object.get_dates()
        security = ticker_object.get_close()
        strategy = topomap.build_strategy(security, self._span, self._buffer)

        # Update the date by shifting dft.LAG days
        data_index  = strategy.index.get_loc(self._date) # row number
        target_date = strategy.iloc[data_index].name
        rec = strategy.loc[target_date, ["ACTION", "POSITION"]]

        self._action   = rec[0]
        self._position = rec[1]

        subject  = f'Recommendation for {self._name} '
        subject += f'({self._symbol}) | {self._date}'
        self._subject = subject

        body  = f'recommendation: {self._action} | '
        body += f'position: {self._position} '
        body += f'(span={self._span} days / buffer={self._buffer:.2%})'
        self._body = body


    def print_recommendation(self, notify: bool, enhanced = True):
        '''Print recommendation to screen'''
        if notify:
            date = util.date_to_string(self._date, '%d %B %Y')
            msg  = f'{self._name} ({self._symbol}) '
            msg += f'{date}: '
            msg += f'{self._action} | position: {self._position} | '
            msg += f'span={self._span} days buffer={self._buffer:.2%}'
            if (self._action in ['buy', 'sell']) & enhanced:
                msg += ' <-----'
            print(msg)
