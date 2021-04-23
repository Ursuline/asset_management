#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 14:58:19 2021

trading_driver.py

# Moving average trading main driver

@author: charles mégnin
"""
import sys
import time
import trading as tra
import trading_defaults as dft
import trading_portfolio as ptf
import utilities as util
import topo_map as tpm
import recommender as rec
import ticker as tck

# Skip these securities
REMOVE  = ['UL', 'FP.PA', 'ORA.PA', 'KC4.F', 'BNP.PA', 'KER.PA', 'SMC.PA']
REMOVE += ['FB', 'HO.PA', 'LHN.SW', 'SQ', 'BIDU', 'ARKQ', 'KORI.PA']
REMOVE += ['TRI.PA', 'HEXA.PA', 'CA.PA', 'ATO.PA']

# SWITCHES
# Notifications defaults
SCREEN = True
EMAIL  = True
NOTIFY = True # item-per-item notificattion

REFRESH_YAHOO = False # Download fresh Yahoo data
REFRESH_EMA   = False # Recompute ema map
FILTER  = True # Remove securities from REMOVE

POSITIONS = ['long', 'short']

TICKERS = ptf.OBSERVE
TICKERS = ['BTC-USD']

START_DATE = '2018-01-02'
END_DATE   = '2021-04-19'
END_DATE   = dft.TODAY

DATE_RANGE = [START_DATE, END_DATE]
ZOOM_RANGE = [START_DATE, END_DATE]


if __name__ == '__main__':
    start_tm = time.time() # total_time
    save_tm  = time.time() # intermediate time
    recommender = rec.Recommender(screen = SCREEN,
                                  email  = EMAIL,
                                  )

    # Remove unwanted tickers
    if FILTER:
        TICKERS[:] = (value for value in TICKERS if value not in REMOVE)
    # remove duplicates
    TICKERS  = set(TICKERS)
    tra.describe_run(TICKERS,
                     DATE_RANGE,
                     dft.MIN_SPAN,
                     dft.MAX_SPAN,
                     dft.MIN_BUFF,
                     dft.MAX_BUFF,
                     dft.N_BUFFERS,
                     POSITIONS,
                     dft.FEE_PCT,
                     )
    for strat_pos in POSITIONS:
        print(f'Strategic position: {strat_pos}')
        for i, ticker in enumerate(TICKERS):
            print(f'{i+1}/{len(TICKERS)}: {ticker}')
            try:
                ticker_obj = tra.load_security(dirname = dft.DATA_DIR,
                                               ticker  = ticker,
                                               refresh = REFRESH_YAHOO,
                                               period  = dft.DEFAULT_PERIOD,
                                               dates   = DATE_RANGE,
                                               )

                security = ticker_obj.get_close()

                # Convert dates to datetime
                date_range = util.get_date_range(security,
                                                 DATE_RANGE[0],
                                                 DATE_RANGE[1],
                                                 )

                # Instantiate a Topomap object
                topomap = tpm.Topomap(ticker, date_range, strat_pos)

                # # Read EMA map values  from file or compute if not saved
                topomap.load_ema_map_new(ticker     = ticker,
                                         security   = security,
                                         refresh    = REFRESH_EMA,
                                         )


                # Build & save best EMA results to file
                topomap.build_best_emas(dft.N_MAXIMA_SAVE)


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
                date_zoom = util.get_date_range(security,
                                                ZOOM_RANGE[0],
                                                ZOOM_RANGE[1],
                                                )
                #display flags:
                display_flags = tck.Ticker.get_default_display_flags()
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
                rcm = rec.Recommendation(ticker_object = ticker_obj,
                                         topomap       = topomap,
                                         target_date   = date_range[1],
                                         span          = best_span,
                                         buffer        = best_buffer,
                                         stratpos      = strat_pos,
                                         )
                rcm.print_recommendation(notify = NOTIFY)
                recommender.add_recommendation(rcm)

                util.print_running_time(ticker, start_tm, save_tm)
                save_tm = time.time() # save intermediate time
            except Exception as ex:
                print(f'Could not process {ticker}: Exception={ex}')
                print(sys.exc_info())
    # send notifications
    recommender.notify(screen_nc = True,
                       email_nc  = False,
                       )
    print(f"Total elapsed time: {util.convert_seconds(time.time()-start_tm)}")
