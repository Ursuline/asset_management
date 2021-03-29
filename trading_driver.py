#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 14:58:19 2021

trading_driver.py

# Moving average trading

@author: charles mégnin
"""
import os
import time
from datetime import datetime
from datetime import timedelta
import pandas as pd
import trading as tra
import trading_plots as trp
import trading_defaults as dft
import trading_portfolio as ptf
import utilities as util

N_MAXIMA_SAVE = 20 # number of maxima to save to file

TICKERS  = ptf.PEA + ptf.ADRIEN + ptf.JP + ptf.FRENCH + ptf.HEALTHCARE + ptf.K_WOOD
TICKERS += ptf.INDICES + ptf.TECH + ptf.COMM + ptf.DEFENSE + ptf.SAXO_CY
TICKERS += ptf.CSR + ptf.LUXURY
TICKERS += ptf.CRYPTO
#TICKERS = ptf.NEW
TICKERS = ptf.FUTURES
REFRESH = True # Download fresh Yahoo data

TODAY     = datetime.strftime(datetime.now(), '%Y-%m-%d')
END_DATE  = '2021-03-26'
YESTERDAY = datetime.strftime(datetime.now() - timedelta(days = 1), '%Y-%m-%d')

DATE_RANGE = ['2017-07-15', END_DATE]

if __name__ == '__main__':
    start_tm = time.time() # total_time
    save_tm  = time.time() # intermediate time
    for i, ticker in enumerate(TICKERS):
        print(f'{i+1}/{len(TICKERS)}: {ticker}')
        try:
            # Get data and reformat
            raw, ticker_name = tra.load_security(dirname = dft.DATA_DIR,
                                                 ticker  = ticker,
                                                 refresh = REFRESH,
                                                 period  = dft.DEFAULT_PERIOD,
                                                 )
            security = pd.DataFrame(raw[f'Close_{ticker}'])
            security.rename(columns={f'Close_{ticker}': "Close"}, inplace=True)

            # Convert dates to datetime
            date_range = tra.get_datetime_date_range(security,
                                                     DATE_RANGE[0],
                                                     DATE_RANGE[1])

            # Read EMA map values from file or compute if not saved
            if os.path.exists(tra.get_ema_map_filename(ticker, date_range)):
                spans, buffers, emas, hold  = tra.read_ema_map(ticker,
                                                               date_range,)
            else: # If not saved, compute it
                spans, buffers, emas, hold = tra.build_ema_map(ticker,
                                                               security,
                                                               date_range,)
                # save EMA map values to file
                tra.save_ema_map(ticker, date_range,
                                 spans, buffers,
                                 emas, hold)

            # Save best EMA results to file
            tra.save_best_emas(ticker, date_range,
                               spans, buffers,
                               emas, hold,
                               N_MAXIMA_SAVE,)

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
                                    azim=dft.PERSPECTIVE[0],
                                    elev=dft.PERSPECTIVE[1],
                                    rdist=dft.PERSPECTIVE[2],
                                    )

            # Plot timeline with default parameters from best EMA
            # Get default paramters
            best_span, best_buffer, best_ema, hold = tra.get_default_parameters(ticker,
                                                                                date_range)
            trp.plot_time_series(ticker, ticker_name,
                                 date_range,
                                 security,
                                 best_span,
                                 dft.FEE_PCT,
                                 best_buffer,
                                 )

            msg  = f'{ticker} running time: '
            msg += f'{util.convert_seconds(time.time()-save_tm)} | '
            msg += 'elapsed time: '
            msg += f'{util.convert_seconds(time.time()-start_tm)}\n'
            print(msg)
            save_tm = time.time() # save intermediate time
        except Exception as ex:
            print(f'Could not process {ticker}: Exception={ex}')
    print(f"Total elapsed time: {util.convert_seconds(time.time()-start_tm)}")
