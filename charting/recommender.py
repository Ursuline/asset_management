#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 11 14:33:03 2021

@author: Charles Mégnin
"""
import smtplib
import ssl
import os
import mimetypes
from email.message import EmailMessage
#from email.mime.multipart import MIMEMultipart
#from email.mime.text import MIMEText
#from email.mime.application import MIMEApplication
#from email.mime.base import MIMEBase
#from email import encoders

from charting import trading_defaults as dft
from charting import private as pvt
from finance import utilities as util

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
        self._n_long_recs  = 0 # of long recommendations
        self._n_short_recs = 0 # of short recommendations
        self._n_actions    = 0
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
            self._n_long_recs += 1
        elif recommendation.get_strategic_position() == 'short':
            self._short_recommendations.append(recommendation)
            self._n_short_recs += 1
        else:
            msg  = 'Recommender.add_recommendation: '
            msg += f'position {recommendation.get_strategic_position()} '
            msg += 'should be long or short.'
            raise ValueError(msg)


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
            if self._n_long_recs > 0:
                print('Long strategic position recommendations:')
                for rec in self._long_recommendations:
                    if screen_nc or not (screen_nc or rec.get_action() == 'n/c'):
                        rec.print_recommendation(notify=True, enhanced = True)
            if self._n_short_recs > 0:
                print('Short strategic position recommendations:')
                for rec in self._short_recommendations:
                    if screen_nc or not (screen_nc or rec.get_action() == 'n/c'):
                        rec.print_recommendation(notify=True, enhanced = True)
            print(line)


    def _email_recommendations(self, email_nc: bool):
        '''Email all recommendations'''

        def _build_body(email_nc):
            '''
            Generates the recommendation as the body of the email
            Computes the number of buy/sell recommendations self._n_actions
            '''
            body = ''
            if self._n_long_recs > 0:
                body += 'Strategic position: long\n'
                for rcm in self._long_recommendations:
                    name = rcm.get_name()
                    symb = rcm.get_symbol()
                    if email_nc or not (email_nc or rcm.get_action() == 'n/c'):
                        body += f'{name} ({symb})\n{rcm.get_body()}\n'
                        self._n_actions += 1
                body += '\n'

            if self._n_short_recs > 0:
                body += 'Strategic position: short\n'
                for rcm in self._short_recommendations:
                    name = rcm.get_name()
                    symb = rcm.get_symbol()
                    if email_nc or not (email_nc or rcm.get_action() == 'n/c'):
                        body += f'{name} ({symb})\n{rcm.get_body()}\n'
                        self._n_actions += 1
            return body

        def add_attachment(msg, rcm):
            '''Adds a file to the body of the message '''
            attachment_path = rcm.get_time_series_plot().get_pathname()

            mime_type, _ = mimetypes.guess_type(attachment_path)
            mime_type, mime_subtype = mime_type.split('/', 1)
            with open(attachment_path, 'rb') as ap:
                msg.add_attachment(ap.read(),
                                   maintype = mime_type,
                                   subtype  = mime_subtype,
                                   filename = os.path.basename(attachment_path),
                                   )
            ap.close()

        def add_attachments(msg, email_nc):
            '''
            Adds all attachments to body
            source: https://varunver.wordpress.com/2017/08/10/python-smtplib-send-email-with-attachments/
            '''
            if self._n_long_recs > 0:
                for rcm in self._long_recommendations:
                    if email_nc or not (email_nc or rcm.get_action() == 'n/c'):
                        add_attachment(msg, rcm)

            if self._n_short_recs > 0:
                for rcm in self._short_recommendations:
                    if email_nc or not (email_nc or rcm.get_action() == 'n/c'):
                        add_attachment(msg, rcm)

        body = _build_body(email_nc)
        if self._n_actions != 0: # send email if there is something to send
            message = EmailMessage()
            message["From"] = pvt.SENDER_EMAIL
            message["To"]   = ",".join(pvt.RECIPIENT_EMAILS)
            message["Subject"] = 'Subject: Trade recommendation'

            message.set_content(body)

            # add html plot files to email body
            add_attachments(message, email_nc)

            mail_server = smtplib.SMTP_SSL(dft.SMTP_SERVER, dft.SSL_PORT)
            mail_server.login(pvt.SENDER_EMAIL, pvt.PASSWORD)
            for recipient_email in pvt.RECIPIENT_EMAILS:
                mail_server.send_message(message, pvt.SENDER_EMAIL, recipient_email)

            mail_server.quit()
            print('recommendation email sent')
        else:
            print('no actions required - no email sent')


    def _email_recommendations_old(self, email_nc: bool):
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
        stratpos is the long/short position strategy for the security
    '''
    def __init__(self, ticker_object, topomap, target_date, span, buffer, stratpos, ts_plot):
        self._ticker   = ticker_object
        self._date     = target_date
        self._stratpos = stratpos
        self._span     = span
        self._buffer   = buffer
        self._ts_plot  = ts_plot
        self._name     = None
        self._symbol   = None
        self._action   = None
        self._position = None
        self._subject  = None
        self._body     = None
        self.set_name()
        self.set_symbol()
        self._build_recommendation(topomap)

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

    def get_ticker_object(self):
        ''''Return the ticker object'''
        return self._ticker

    def get_time_series_plot(self):
        '''Return time series plot'''
        return self._ts_plot

    def self_describe(self):
        '''Display all variables in class'''
        print(self.__dict__)

    # Setters
    def set_name(self):
        '''Sets the ticker name as recommendation name'''
        self._name = self._ticker.get_name()

    def set_symbol(self):
        '''Sets the ticker symbol as recommendation symbol'''
        self._symbol = self._ticker.get_symbol()


    def _build_recommendation(self, topomap):
        '''
        Builds a recommendation for the target_date to be emailed
        '''
        security = self._ticker.get_close()
        strategy = topomap.build_strategy(security, self._span, self._buffer)


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
        body += f'(span={self._span:.0f} days / buffer={self._buffer:.2%})'
        self._body = body


    def print_recommendation(self, notify: bool, enhanced = True):
        '''Print recommendation to screen'''
        if notify:
            date = util.date_to_string(self._date, '%d %b %Y')
            msg = f'{date}: '
            msg += f'{self._name} ({self._symbol}) '
            msg += f'{self._action} | position: {self._position} | '
            msg += f'span={self._span:.0f} days buffer={self._buffer:.2%}'
            if (self._action in ['buy', 'sell']) & enhanced:
                msg = '-----> ' + msg + ' <-----'
            print(msg)
