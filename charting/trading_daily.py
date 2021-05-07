#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  1 09:57:39 2021

trading_daily.py

Runs trough a list of tickers and flags buys/sells at a given date

@author: charly
"""
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
#import trading_plots as trp
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
#TICKERS = ptf.PORTFOLIOS

REFRESH = True # Download fresh Yahoo data
FILTER  = True # Remove securities from REMOVE

END_DATE   = '2021-03-29'

DATE_RANGE = ['2017-07-15', dft.YESTERDAY]
ZOOM_RANGE = ['2020-01-01', dft.YESTERDAY]

# LMT 19 mars
TARGET_DATE = '2021-03-19'

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
                tra.save_ema_map(ticker,
                                 date_range,
                                 spans,
                                 buffers,
                                 emas,
                                 hold)


            msg  = f'{ticker} running time: '
            msg += f'{util.convert_seconds(time.time()-save_tm)} | '
            msg += 'elapsed time: '
            msg += f'{util.convert_seconds(time.time()-start_tm)}\n'
            print(msg)
            save_tm = time.time() # save intermediate time
        except Exception as ex:
            print(f'Could not process {ticker}: Exception={ex}')
    print(f"Total elapsed time: {util.convert_seconds(time.time()-start_tm)}")