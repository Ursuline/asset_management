#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 2 08:43:19 2021

trading_driver.py

# Cfrates a moving window trading animation

@author: charles mégnin
"""
#import os
import time
from datetime import datetime
from datetime import timedelta
import pandas as pd
import trading as tra
import trading_plots as trp
import trading_defaults as dft
import utilities as util

N_MAXIMA_SAVE = 20 # number of maxima to save to file

TICKER = 'CPR.MI'

START_DATE = '2017-07-07' # Friday
END_DATE   = '2021-04-06'
INCREMENT  = 28
INCREMENT_START = False

def describe_run(tickers):
    span_range   = dft.MAX_SPAN - dft.MIN_SPAN + 1
    buffer_range = dft.N_BUFFERS
    dims         = span_range * buffer_range
    print(f'Span range: {dft.MIN_SPAN:.0f} - {dft.MAX_SPAN:.0f} days')
    print(f'Buffer range: {dft.MIN_BUFF:.2%} - {dft.MAX_BUFF:.2%} / {dft.N_BUFFERS} samples')
    print(f'Running {len(tickers)} tickers: {dims:.0f} runs/ticker')

if __name__ == '__main__':
    start_tm = time.time() # total_time
    save_tm  = time.time() # intermediate time
    ticker = TICKER
    YESTERDAY = datetime.strftime(datetime.now() - timedelta(days = 1), '%Y-%m-%d')

    start_dt  = datetime.strptime(START_DATE, '%Y-%m-%d')
    end_dt    = datetime.strptime(START_DATE, '%Y-%m-%d') + timedelta(days=364)

    date_range = [start_dt, end_dt] # datetime format

    while date_range[1] <= datetime.strptime(END_DATE, '%Y-%m-%d'):
        try:
            # Get data and reformat
            raw, ticker_name = tra.load_security(dirname = dft.DATA_DIR,
                                                 ticker  = ticker,
                                                 refresh = True,
                                                 period  = 'max',
                                                 )
            security = pd.DataFrame(raw[f'Close_{ticker}'])
            security.rename(columns={f'Close_{ticker}': "Close"}, inplace=True)

            spans, buffers, emas, hold = tra.build_ema_map(ticker,
                                                           security,
                                                           date_range,)

            # Plot EMA contour map
            trp.plot_buffer_span_contours(ticker, ticker_name, date_range,
                                          spans, buffers,
                                          emas, hold,
                                          )

            # Plot EMA 3D map
            trp.plot_buffer_span_3D(ticker, ticker_name, date_range,
                                    spans, buffers,
                                    emas, hold,
                                    dft.SURFACE_COLOR_SCHEME,
                                    azim  = dft.PERSPECTIVE[0],
                                    elev  = dft.PERSPECTIVE[1],
                                    rdist = dft.PERSPECTIVE[2],
                                    )

            msg  = f'{ticker} running time: '
            msg += f'{util.convert_seconds(time.time()-save_tm)} | '
            msg += 'elapsed time: '
            msg += f'{util.convert_seconds(time.time()-start_tm)}\n'
            print(msg)
            save_tm = time.time() # save intermediate time
        except Exception as ex:
            print(f'Could not process {ticker}: Exception={ex}')
        if INCREMENT_START:
            date_range[0] += timedelta(days=INCREMENT)
        date_range[1] += timedelta(days=INCREMENT)
    print(f"Total elapsed time: {util.convert_seconds(time.time()-start_tm)}")
