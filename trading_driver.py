#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 14:58:19 2021

trading_driver.py

# Moving average trading

@author: charles mégnin
"""
import sys
import os
import time
import pandas as pd
import trading as tra
import trading_defaults as dft
import trading_portfolio as ptf
import utilities as util
import topo_map as tpm
import recommender as rec

N_MAXIMA_SAVE = 20 # number of maxima to save to file

# Notification defaults
SCREEN = True
EMAIL  = True
NOTIFY = True # item-per-item notificatiton

REMOVE  = ['UL', 'FP.PA', 'ORA.PA', 'KC4.F', 'BNP.PA', 'KER.PA', 'SMC.PA']
REMOVE += ['FB', 'HO.PA', 'LHN.SW', 'SQ', 'BIDU', 'ARKQ', 'KORI.PA']
REMOVE += ['TRI.PA', 'HEXA.PA', 'CA.PA', 'ATO.PA']

TICKERS = ptf.OBSERVE
TICKERS = ['AAPL']

POSITION = 'long' # long or short

REFRESH = True # Download fresh Yahoo data
FILTER  = True # Remove securities from REMOVE

START_DATE = '2017-07-17'
#END_DATE   = '2021-04-09'
END_DATE   = dft.YESTERDAY

DATE_RANGE = [START_DATE, END_DATE]
ZOOM_RANGE = ['2019-04-01', END_DATE]

def describe_run(tickers, position):
    '''print run description'''
    span_range   = dft.MAX_SPAN - dft.MIN_SPAN + 1
    buffer_range = dft.N_BUFFERS
    dims         = span_range * buffer_range
    print(f'Date range: {DATE_RANGE[0]} to {DATE_RANGE[1]}')
    print(f'Span range: {dft.MIN_SPAN:.0f} - {dft.MAX_SPAN:.0f} days')
    print(f'Buffer range: {dft.MIN_BUFF:.2%} - {dft.MAX_BUFF:.2%} / {dft.N_BUFFERS} samples')
    print(f"Broker's fee: {dft.FEE_PCT:.2%}")
    print(f'Running {len(tickers)} tickers: {dims:.0f} runs/ticker')
    print(f'Position: {position}')

if __name__ == '__main__':
    start_tm = time.time() # total_time
    save_tm  = time.time() # intermediate time

    # Remove unwanted tickers
    if FILTER:
        TICKERS[:] = (value for value in TICKERS if value not in REMOVE)
    # remove duplicates
    TICKERS  = set(TICKERS)
    describe_run(TICKERS, POSITION)
    recommender = rec.Recommender(screen = SCREEN,
                                  email  = EMAIL,
                                  )
    for i, ticker in enumerate(TICKERS):
        print(f'{i+1}/{len(TICKERS)}: {ticker}')
        try:
            ticker_obj = tra.load_security_oo(dirname = dft.DATA_DIR,
                                              ticker  = ticker,
                                              refresh = REFRESH,
                                              period  = dft.DEFAULT_PERIOD,
                                              dates   = DATE_RANGE,
                                              )

            # security is the Close
            security = pd.DataFrame(ticker_obj.get_market_data()[f'Close_{ticker}'])
            security = security.loc[START_DATE:END_DATE,:] # trim the data
            security.rename(columns={f'Close_{ticker}': "Close"}, inplace=True)

            # Convert dates to datetime
            date_range = util.get_datetime_date_range(security,
                                                      DATE_RANGE[0],
                                                      DATE_RANGE[1])

            # Instantiate a Topomap object
            topomap = tpm.Topomap(ticker, date_range, POSITION)

            # Read EMA map values  from file or compute if not saved
            data_dir = os.path.join(dft.DATA_DIR, ticker)
            file     = topomap.get_ema_map_filename() + '.csv'
            map_path = os.path.join(data_dir, file)
            if os.path.exists(map_path):
                print(f'Loading EMA map {map_path}')
                topomap.load_ema_map(data_dir)
            else: # If not saved, compute it
                #print(f'No EMA map {map_path}')
                topomap.build_ema_map(security, date_range)

            # save EMA map values to file
            topomap.save_emas()

            # Build & save best EMA results to file
            topomap.build_best_emas(N_MAXIMA_SAVE)
            topomap.save_best_emas()

            # Plot EMA contour map
            topomap.contour_plot(ticker_obj, date_range)

            # Plot EMA 3D map
            topomap.surface_plot(ticker_object = ticker_obj,
                                 date_range = date_range,
                                 colors = dft.SURFACE_COLOR_SCHEME,
                                 azim   = dft.PERSPECTIVE[0],
                                 elev   = dft.PERSPECTIVE[1],
                                 rdist  = dft.PERSPECTIVE[2],
                                 )

            # Plot time series with default parameters from best EMA
            best_span, best_buffer, best_ema, hold = topomap.get_global_max()

            # Convert zoom dates to datetime
            date_zoom = util.get_datetime_date_range(security,
                                                     ZOOM_RANGE[0],
                                                     ZOOM_RANGE[1])
            #display flags:
            #0: Price  | 1: EMA  | 2: buffer | 3: arrows |
            #4: statistics | 5: save
            display_flags = [True, True, False, True, True, True]
            ticker_obj.plot_time_series(display_dates = date_zoom,
                                        security      = security,
                                        topomap       = topomap,
                                        span          = best_span,
                                        buffer        = best_buffer,
                                        flags         = display_flags,
                                        fee_pct       = dft.FEE_PCT,
                                        )

            # Determine the action to take for the given END_DATE
            # instantiate recommendation
            rcm = rec.Recommendation(ticker_obj.get_name(),
                                     ticker,
                                     END_DATE,
                                     )
            # build recommendation
            rcm.build_recommendation(ticker_object = ticker_obj,
                                     topomap       = topomap,
                                     span          = best_span,
                                     buffer        = best_buffer,
                                     )
            rcm.print_recommendation(notify = NOTIFY)
            # add recommendation to recommender object
            recommender.add_recommendation(rcm)

            msg  = f'{ticker} running time: '
            msg += f'{util.convert_seconds(time.time()-save_tm)} | '
            msg += 'elapsed time: '
            msg += f'{util.convert_seconds(time.time()-start_tm)}\n'
            print(msg)
            save_tm = time.time() # save intermediate time
        except Exception as ex:
            print(f'Could not process {ticker}: Exception={ex}')
            print(sys.exc_info())
    # send notifications
    recommender.notify(screen_nc = True,
                       email_nc  = False,
                       )
    print(f"Total elapsed time: {util.convert_seconds(time.time()-start_tm)}")
