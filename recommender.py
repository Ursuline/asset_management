#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 11 14:33:03 2021

recommender.py

@author: Charles Mégnin
"""
import smtplib
import os
import mimetypes
from email.message import EmailMessage
import datetime as dt

from charting import trading_defaults as dft
from charting import private as pvt
import parameters_sync as params
from finance import utilities as util

class Recommender():
    '''
    Handles the dispatching of trading recommendations
    '''
    def __init__(self, yaml_data, ptf_file = None, screen = True, email = True, sms = False):
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
        self._ptf_file = ptf_file
        if ptf_file is not None:
            self._ptf_file = os.path.splitext(os.path.basename(ptf_file))[0]
        self._screen = screen
        self._email  = email
        self._sms    = sms
        self._yaml_data = yaml_data


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
            msg += f'position "{recommendation.get_strategic_position()}" '
            msg += 'should be long or short.'
            raise ValueError(msg)

    def notify(self, screen_nc: bool, email_nc: bool, email_plot_flags=None):
        '''
        Dispatches to make recommendations
        screen_nc : output n/c action recommendation to screen
        email_nc : send email if n/c action
        plot_flags: which plots to include in email:
            ts, contour, surface
        NB: screen & action must aalso be set to True for each to be activated
        '''
        if self._screen:
            self._print_recommendations(screen_nc)

        if self._email:
            self._email_recommendations(email_nc, email_plot_flags)


    def _print_recommendations(self, screen_nc: bool):
        ''' Output recommendations to screen '''
        root    = '*'
        repeats = 75
        line    = ''.join([char * repeats for char in root])
        nrecs = len(self._long_recommendations) + len(self._short_recommendations)

        if nrecs >0: # if there are recommendations
            print(dt.datetime.now().strftime('%d %B %Y %H:%M:%S'))
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


    def _email_recommendations(self, email_nc: bool, email_plot_flags):
        '''Email recommendations when action is required'''

        def _build_body(email_nc):
            '''
            Generates the recommendation as the body of the email
            Computes the number of buy/sell recommendations self._n_actions
            '''
            body = ''

            if self._n_long_recs > 0:
                body += ' Strategic position: long\n'

                for rcm in self._long_recommendations:
                    name = rcm.get_name()
                    symb = rcm.get_symbol()
                    if rcm.get_action() is not None:
                        if email_nc or not (email_nc or rcm.get_action() == 'n/c'):
                            date = util.date_to_string(rcm.get_date(), '%d %b %Y')
                            body += f'{name} ({symb}) {date}:\n{rcm.get_body()}\n'
                            self._n_actions += 1
                body += '\n'

            if self._n_short_recs > 0:
                body += 'Strategic position: short\n'

                for rcm in self._short_recommendations:
                    name = rcm.get_name()
                    symb = rcm.get_symbol()
                    if rcm.get_action() is not None:
                        if email_nc or not (email_nc or rcm.get_action() == 'n/c'):
                            date = util.date_to_string(rcm.get_date(), '%d %b %Y')
                            body += f'{name} ({symb}) {date}:\n{rcm.get_body()}\n'
                            self._n_actions += 1
            return body

        def add_attachment(msg, plot_path):
            '''Adds a file to the body of the message '''
            mime_type, _ = mimetypes.guess_type(plot_path)
            mime_type, mime_subtype = mime_type.split('/', 1)
            with open(plot_path, 'rb') as atp:
                msg.add_attachment(atp.read(),
                                   maintype = mime_type,
                                   subtype  = mime_subtype,
                                   filename = os.path.basename(plot_path),
                                   )
            atp.close()

        def add_attachments(msg, email_nc, email_plot_flags):
            '''
            Adds all attachments to body
            source: https://varunver.wordpress.com/2017/08/10/python-smtplib-send-email-with-attachments/
            '''
            if self._n_long_recs > 0:
                for rcm in self._long_recommendations:
                    if rcm.get_action() is not None:
                        if email_nc or not (email_nc or rcm.get_action() == 'n/c'):
                            if email_plot_flags['ts']: # add time series attachment
                                plot_path = rcm.get_time_series_plot().get_pathname()
                                add_attachment(msg, plot_path)
                            if email_plot_flags['contour']: # add contour plot attachment
                                plot_path = rcm.get_plot_pathname('contour')
                                add_attachment(msg, plot_path)
                            if email_plot_flags['surface']: # add surface plot attachment
                                plot_path = rcm.get_plot_pathname('surface')
                                add_attachment(msg, plot_path)

            if self._n_short_recs > 0:
                for rcm in self._short_recommendations:
                    if rcm.get_action() is not None:
                        if email_nc or not (email_nc or rcm.get_action() == 'n/c'):
                            if email_plot_flags['ts']: # add time series attachment
                                plot_path = rcm.get_time_series_plot().get_pathname()
                                add_attachment(msg, plot_path)
                            if email_plot_flags['contour']: # add contour plot attachment
                                plot_path = rcm.get_plot_pathname('contour')
                                add_attachment(msg, plot_path)
                            if email_plot_flags['surface']: # add surface plot attachment
                                plot_path = rcm.get_plot_pathname('surface')
                                add_attachment(msg, plot_path)

        body = _build_body(email_nc)
        if self._n_actions != 0: # send email if there is something to send
            message = EmailMessage()
            message["From"] = pvt.SENDER_EMAIL
            message["To"]   = ",".join(params.get_recipients(self._yaml_data))
            if self._ptf_file is None:
                message["Subject"] = 'Subject: Trade recommendation'
            else:
                msg  = f'Subject: Trade recoms for *{self._ptf_file}* '
                msg += 'portfolio'
                message["Subject"] = msg

            message.set_content(body)

            # add html plot files to email body
            add_attachments(message, email_nc, email_plot_flags)

            mail_server = smtplib.SMTP_SSL(dft.SMTP_SERVER, dft.SSL_PORT)
            mail_server.login(pvt.SENDER_EMAIL, pvt.PASSWORD)
            for recipient_email in params.get_recipients(self._yaml_data):
                mail_server.send_message(message, pvt.SENDER_EMAIL, recipient_email)

            mail_server.quit()
            print('recommendation email sent')
        else:
            print('no actions required - no email sent')

####################################
###### RECOMMENDATION CLASSES ######
####################################
class Recommendations():
    '''
    encapsulates the recommendation to buy | sell | n/c
    captured in the target date row ACTION column of the ticker object's data
    NB: position is the recommended position for the security
        stratpos is the long/short position strategy for the security
    '''
    def __init__(self, ticker_object, topomap, target_date, span, buffer, strategic_pos, ts_plot):
        self._strategic_pos = strategic_pos.strip()
        self._ticker   = ticker_object
        self._date     = target_date
        self._span     = span
        self._buffer   = buffer
        self._ts_plot  = ts_plot
        self._topomap  = topomap
        self._ptf_file = None
        self._name     = None
        self._symbol   = None
        self._action   = None
        self._position = None
        self._subject  = None
        self._body     = None
        self._last_action_date = None
        self.set_name()
        self.set_symbol()

    # Getters
    def get_body(self):
        '''Return the body of the recommendation'''
        return self._body

    def get_date(self):
        '''Return the date corresponding to the recommendation'''
        return self._date

    def get_name(self):
        '''Return the ticker name'''
        return self._name

    def get_symbol(self):
        '''Return the ticker symbol'''
        return self._symbol

    def get_action(self):
        '''Get the recommended action '''
        return self._action

    def get_position(self):
        '''Get the recommended position '''
        return self._position

    def get_strategic_position(self):
        '''Get the strategic position '''
        return self._strategic_pos

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


    def print_recommendation(self, notify: bool, enhanced = True):
        '''Print recommendation to screen'''
        if notify:
            date = util.date_to_string(self._date, '%d %b %Y')
            msg = f'{date}: '
            msg += f'{self._name} ({self._symbol}) '
            msg += f'action:{self._action} | position: {self._position} | '
            msg += f'span={self._span:.0f} days buffer={self._buffer:.2%}'
            if (self._action in ['buy', 'sell']) & enhanced:
                msg = '-----> ' + msg + ' <-----'
            print(msg)


class Recommendation_sync(Recommendations):
    '''
    encapsulates the recommendation to buy | sell | n/c
    captured in the target date row ACTION column of the ticker object's data
    '''
    def __init__(self, ticker_object, topomap, holdings, target_date, span, buffer, ts_plot):
        holdings_strategy = holdings.get_strategy(ticker_object.get_symbol()).strip()
        super().__init__(ticker_object, topomap, target_date, span, buffer, holdings_strategy, ts_plot)
        self._holdings = holdings
        self._build_recommendation()


    def get_plot_pathname(self, style:str):
        '''return style  plot (contour or surface)'''
        if style in ['contour', 'surface']:
            return self._topomap.get_plot_pathname(style)
        msg = f'get_plot_pathname: style {style} should be contour or surface'
        raise AssertionError(msg)


    def get_action(self):
        '''Return action'''
        return self._action


    def _build_recommendation(self):
        '''Builds a recommendation for the target_date to be emailed'''
        recom_strat    = self._topomap.get_recom_strategy()
        recom_position = recom_strat.POSITION
        #recom_sign     = recom_strat.SIGN
        strategic_pos  = self._strategic_pos
        symbol         = self._ticker.get_symbol()
        current_position = self._holdings.get_current_position(symbol,
                                                               strategic_pos)
        last_action_date = self._ts_plot.get_last_action_date()


        def _make_recommendation(current_pos:str, recom_pos:str):
            '''
            Test when in sync (no recommendation)
                 when out of sync recommend
            '''
            if current_pos == recom_pos:
                return None
            if recom_pos == 'long':
                return 'buy'
            if recom_pos == 'cash':
                if current_pos == 'long':
                    return 'sell'
                if current_pos == 'short':
                    return 'buy'
                return None
            if recom_pos == 'short':
                return 'sell'
            raise IOError(f'{recom_pos} should be long short or cash')


        def _make_recommendation2(current_pos:str, recom_pos:str, recom_sign:int):
            '''
            Alternative recommendation strategy:
                stay cash when in buffer
            '''
            if current_pos == 'long':
                if recom_pos == 'long':
                    return None
                return 'sell'
            if current_pos == 'short':
                if recom_pos == 'short':
                    return None
                return 'buy'
            if current_pos == 'cash':
                if recom_sign == 0:
                    return None
                if recom_sign == -1:
                    return 'sell'
                if recom_sign == 1:
                    return 'buy'
            msg = f'current_pos "{current_pos}" should be long short or cash'
            raise IOError(msg)

            if current_pos == recom_pos:
                return None
            if recom_pos == 'long':
                return 'buy'
            if recom_pos == 'cash':
                if current_pos == 'long':
                    return 'sell'
                if current_pos == 'short':
                    return 'buy'
                return None
            if recom_pos == 'short':
                return 'sell'
            raise IOError(f'{recom_pos} should be long short or cash')

        self._action = _make_recommendation(current_position,
                                            recom_position,
                                            #recom_sign,
                                            )

        subject  = f'Recoms for {self._name} '
        subject += f'({self._symbol}) | {self._date}'
        self._subject = subject

        body  = f'recom: {self._action} | '
        body += f'position current/recommended: {current_position}/{recom_position} '
        body += f'(span={self._span:.0f} days / buffer={self._buffer:.2%}) '
        body += f'since {last_action_date.strftime("%d %b %Y")} '
        body += f'({(self._date - last_action_date).days} days)'
        self._body = body


    def print_recommendation(self, notify: bool, enhanced = True):
        '''Print recommendation to screen'''
        if notify:
            date = util.date_to_string(self._date, '%d %b %Y')
            msg = f'{date}: '
            msg += f'{self._name} ({self._symbol}) '
            msg += self._body
            if (self._action in ['buy', 'sell']) & enhanced:
                msg = '--> ' + msg + ' <--'
            print(msg)
