#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 14:58:19 2021

trading_driver.py

# Moving average trading

@author: charles mégnin
"""
import time
from datetime import datetime
from datetime import timedelta
import pandas as pd
import trading as tra
import trading_plots as trp
import trading_defaults as dft
import utilities as util

N_MAXIMA_SAVE = 20 # number of maxima to save to file

INDICES    = ['^GSPC', '^DJI', '^IXIC', '^FCHI', '^N225', '^HSI', '^DJSH']
DEFENSE    = ['HO.PA']
HEALTHCARE = ['TDOC', 'BLC.PA', 'PHA.PA', 'KORI.PA', 'ORP.PA']
FRENCH     = ['SU.PA', 'MC.PA', 'RMS.PA', 'FP.PA', 'STLA.PA']
K_WOOD     = ['ARKF', 'ARKG', 'ARKK', 'ARKQ', 'ARKW']
TECH       = ['AAPL', 'TSLA', 'AMZN', 'MSFT', 'SPOT', 'SQ', 'SHOP']
COMM       = ['ROKU', 'ZM', 'BIDU']
CRYPTO     = ['BTC-USD', 'ETH-USD']

TICKERS = CRYPTO
REFRESH = True # Download fresh Yahoo data

TODAY     = datetime.strftime(datetime.now(), '%Y-%m-%d')
YESTERDAY = datetime.strftime(datetime.now() - timedelta(days = 1), '%Y-%m-%d')

DATE_RANGE = ['2017-07-15', YESTERDAY]

if __name__ == '__main__':
    start_tm = time.time() # total_time
    save_tm  = time.time() # intermediate time
    for i, ticker in enumerate(TICKERS):
        print(f'{i+1}/{len(TICKERS)}: {ticker}')
        try:
            # Get data and reformat
            raw = tra.load_security(dirname = dft.DATA_DIR,
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

            # Compute EMA map values
            spans, buffers, emas, hold = tra.build_ema_map(ticker,
                                                           security,
                                                           date_range,)

            # save EMA map values to file
            tra.save_ema_map(ticker, date_range,
                             spans, buffers,
                             emas,)

            # Save best EMA results to file
            tra.save_best_emas(ticker, date_range,
                               spans, buffers,
                               emas, hold,
                               N_MAXIMA_SAVE,)

            # Plot EMA map
            trp.plot_buffer_span_contours(ticker, date_range,
                                          spans, buffers,
                                          emas, hold,
                                          )

            msg  = f'{ticker} elapsed time: '
            msg += f'{util.convert_seconds(time.time()-save_tm)} '
            msg += 'total time: '
            msg += f'{util.convert_seconds(time.time()-start_tm)}\n'
            print(msg)
            save_tm = time.time() # save intermediate time
        except Exception as ex:
            print(f'Could not process {ticker}: {ex}')
    print(f"Total elapsed time: {util.convert_seconds(time.time()-start_tm)}")
