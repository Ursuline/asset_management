#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 13 11:31:19 2021

sync_tickers.py

# main driver for charting

@author: charles mégnin
"""
import os
import sys
import time
import pandas as pd
from charting import trading as tra
from charting import trading_defaults as dft
from charting import topo_map as tpm
from charting import recommender as rec
from charting import time_series_plot as tsp
from charting import parameters as par
from charting import holdings as hld
from finance import utilities as util

DATE_RANGE = par.DATE_RANGE
ZOOM_RANGE = par.ZOOM_RANGE
POSITIONS  = par.POSITIONS
NOTIFY     = par.NOTIFY
REMOTE     = par.REMOTE
DISPLAY_TIME_SERIES = par.DISPLAY_TIME_SERIES
REFRESH_YAHOO = par.REFRESH_YAHOO
REFRESH_EMA   = par.REFRESH_EMA

PORTFOLIO_DIR = 'charting/data'
PORTFOLIO_FILES = ['holdings.csv', 'saxo_cycliques.csv']

if __name__ == '__main__':
    start_tm = time.time() # total_time
    save_tm  = time.time() # intermediate time
    recommender = rec.Recommender(screen = par.SCREEN,
                                  email  = par.EMAIL,
                                  )
    for file in PORTFOLIO_FILES:
        holdings = hld.Holdings(PORTFOLIO_DIR, file)
        securities = holdings.get_securities()
        print(f'Processing {file}')

        for i, security in enumerate(securities.Ticker):
            position  = securities.iloc[i].Position.strip()
            strat_pos = securities.iloc[i].Strategy.strip()
            msg  = f'{i+1}/{len(securities)}: {security} | '
            msg += f'Position: "{position}" | '
            msg += f'Strategic position: "{strat_pos}"'
            print(msg)
            try:
                ticker_obj = tra.load_security(dirname = dft.DATA_DIR,
                                               ticker  = security,
                                               refresh = REFRESH_YAHOO,
                                               period  = dft.DEFAULT_PERIOD,
                                               dates   = DATE_RANGE,
                                               )
                volume = ticker_obj.get_volume()

                # Convert dates to datetime
                date_range = util.get_date_range(ticker_obj.get_close(),
                                                 DATE_RANGE[0],
                                                 DATE_RANGE[1],
                                                 )

                # Instantiate a Topomap object
                topomap = tpm.Topomap(security, date_range, strat_pos)

                # # Read EMA map values  from file or compute if not saved
                topomap.load_ema_map(ticker_object = ticker_obj,
                                     refresh       = REFRESH_EMA,
                                     )

                # Build & save best EMA results to file
                topomap.build_best_emas(dft.N_MAXIMA_SAVE)

                # Plot EMA contour map
                topomap.surface_plot(ticker_object = ticker_obj,
                                     date_range = date_range,
                                     style  = 'contour',
                                     remote = REMOTE,
                                     )

                # Plot EMA 3D map
                topomap.surface_plot(ticker_object = ticker_obj,
                                     date_range = date_range,
                                     style  = 'surface',
                                     remote = REMOTE,
                                     )

                # Get optimal span/buffer
                best_span, best_buffer, best_ema, hold = topomap.get_global_max()

                # Convert zoom dates to datetime
                date_zoom = util.get_date_range(ticker_obj.get_close(),
                                                ZOOM_RANGE[0],
                                                ZOOM_RANGE[1],
                                                )
                #display flags:
                display_flags = tsp.TimeSeriesPlot.get_default_display_flags()

                # Plot time series with default parameters from best EMA
                plot = tsp.TimeSeriesPlot(ticker_object = ticker_obj,
                                          topomap       = topomap,
                                          strat_pos     = strat_pos,
                                          disp_dates    = date_range,
                                          span          = best_span,
                                          buffer        = best_buffer,
                                          disp_flags    = display_flags,)

                #Combine close, volume, and return data
                data   = pd.DataFrame(pd.merge(ticker_obj.get_close(), ticker_obj.get_volume(),
                                               left_index=True, right_index=True))
                data   = pd.DataFrame(pd.merge(data, ticker_obj.get_return(),
                                               left_index=True, right_index=True))
                plot.build_plot(data,
                                notebook = False,
                                display  = DISPLAY_TIME_SERIES,
                                remote   = REMOTE,
                                )

                # strat = topomap.get_current_strategy()
                # in_sync = holdings.is_in_sync(security, strat.POSITION, strat_pos)
                # print(f'{security} recommended position: {strat.POSITION} actual position {strat_pos}')
                # if in_sync == False:
                #     print('<--- --->')
                # print(f'{security} {strat_pos} in sync: {in_sync}')

                # Determine the action to take for the given END_DATE
                # instantiate recommendation
                rcm = rec.Recommendation_sync(ticker_object = ticker_obj,
                                         topomap       = topomap,
                                         holdings      = holdings,
                                         target_date   = date_range[1],
                                         span          = best_span,
                                         buffer        = best_buffer,
                                         stratpos      = strat_pos,
                                         ts_plot       = plot,
                                         )
                rcm.print_recommendation(notify = NOTIFY)
                recommender.add_recommendation(rcm)

                util.print_running_time(security, start_tm, save_tm)
                save_tm = time.time() # save intermediate time
            except Exception as ex:
                print(f'Could not process {security}: Exception={ex}')
                print(sys.exc_info())
    # send notifications
    recommender.notify(screen_nc = True,
                       email_nc  = False,
                       )
    print(f"Total elapsed time: {util.convert_seconds(time.time()-start_tm)}")
