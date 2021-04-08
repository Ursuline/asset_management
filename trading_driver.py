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
import pandas as pd
import trading as tra
import trading_plots as trp
import trading_defaults as dft
import trading_portfolio as ptf
import utilities as util

N_MAXIMA_SAVE = 20 # number of maxima to save to file

REMOVE = ['UL', 'FP.PA', 'ORA.PA', 'KC4.F', 'BNP.PA', 'KER.PA', 'SMC.PA']
REMOVE += ['FB', 'HO.PA', 'LHN.SW', 'SQ', 'BIDU', 'ARKQ', 'KORI.PA']
REMOVE += ['TRI.PA', 'HEXA.PA', 'CA.PA', 'ATO.PA']

TICKERS  = ptf.ADRIEN + ptf.JP + ptf.PEA_MC + ptf.PEA + ptf.JACQUELINE + ptf.SAXO_CY
TICKERS += ptf.K_WOOD + ptf.TECH + ptf.COMM + ptf.FNB + ptf.CHEM + ptf.NRJ
TICKERS += ptf.FRENCH + ptf.HEALTHCARE + ptf.SWISS + ptf.AUTOMOBILE
TICKERS += ptf.INDUSTRIAL
TICKERS += ptf.INDICES + ptf.DEFENSE + ptf.OBSERVE
TICKERS += ptf.CSR + ptf.LUXURY + ptf.GAFAM + ptf.CRYPTO + ptf.FINANCIAL

TICKERS = ['SU.PA']
TICKERS = ptf.CRYPTO

REFRESH = False # Download fresh Yahoo data
FILTER  = True # Remove securities from REMOVE

END_DATE   = dft.TODAY
#END_DATE   = '2021-04-06'

DATE_RANGE = ['2017-07-15', END_DATE]
ZOOM_RANGE = ['2019-04-01', END_DATE]

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

    # Remove unwanted tickers
    if FILTER:
        TICKERS[:] = (value for value in TICKERS if value not in REMOVE)
    # remove duplicates
    TICKERS  = set(TICKERS)
    describe_run(TICKERS)
    for i, ticker in enumerate(TICKERS):
        print(f'{i+1}/{len(TICKERS)}: {ticker}')
        try:
            # Get data and reformat
            # raw, ticker_name = tra.load_security(dirname = dft.DATA_DIR,
            #                                      ticker  = ticker,
            #                                      refresh = REFRESH,
            #                                      period  = dft.DEFAULT_PERIOD,
            #                                      )

            ticker_obj = tra.load_security_new(dirname = dft.DATA_DIR,
                                               ticker  = ticker,
                                               refresh = REFRESH,
                                               period  = dft.DEFAULT_PERIOD,
                                               )
            raw = ticker_obj.get_market_data()
            ticker_name = ticker_obj.get_ticker_name()

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
            trp.plot_buffer_span_3D(ticker=ticker,
                                    ticker_name=ticker_name,
                                    date_range=date_range,
                                    spans=spans,
                                    buffers=buffers,
                                    emas=emas,
                                    hold=hold,
                                    azim  = dft.PERSPECTIVE[0],
                                    elev  = dft.PERSPECTIVE[1],
                                    rdist = dft.PERSPECTIVE[2],
                                    colors = dft.SURFACE_COLOR_SCHEME
                                    )

            # Plot timeline with default parameters from best EMA
            # Get default paramters
            best_span, best_buffer, best_ema, hold = tra.get_default_parameters(ticker,
                                                                                date_range)
            # Convert dates to datetime
            date_zoom = tra.get_datetime_date_range(security,
                                                    ZOOM_RANGE[0],
                                                    ZOOM_RANGE[1])
            #display flags --
            #0: Price  | 1: EMA  | 2: buffer | 3: arrows |
            #4: statistics | 5: save
            display_flags = [True, True, False, True, True, True]
            trp.plot_time_series(ticker        = ticker,
                                 ticker_name   = ticker_name,
                                 date_range    = date_range,
                                 display_dates = date_zoom,
                                 security      = security,
                                 span          = best_span,
                                 buffer        = best_buffer,
                                 fee_pct       = dft.FEE_PCT,
                                 flags         = display_flags,
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
