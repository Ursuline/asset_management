#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 14:58:19 2021

driver_charting.py

# main driver for charting

@author: charles mégnin
"""
import sys
import time
import pandas as pd
from charting import trading as tra
from charting import trading_defaults as dft
from charting import topo_map as tpm
from charting import recommender as rec
from charting import time_series_plot as tsp
from charting import parameters as par
from finance import utilities as util

FILTER     = par.FILTER
TICKERS    = par.TICKERS
REMOVE     = par.REMOVE
DATE_RANGE = par.DATE_RANGE
ZOOM_RANGE = par.ZOOM_RANGE
POSITIONS  = par.POSITIONS
NOTIFY     = par.NOTIFY
REMOTE     = par.REMOTE
#Contour & surface plot formats
PLOT_FORMATS = par.CTR_SFC_PLOT_FORMATS
DISPLAY_TIME_SERIES = par.DISPLAY_TIME_SERIES
REFRESH_YAHOO = par.REFRESH_YAHOO
REFRESH_EMA   = par.REFRESH_EMA


if __name__ == '__main__':
    start_tm = time.time() # total_time
    save_tm  = time.time() # intermediate time
    recommender = rec.Recommender(ptf_file = None,
                                  screen   = par.SCREEN,
                                  email    = par.EMAIL,
                                  )

    # Remove unwanted tickers
    if FILTER:
        TICKERS[:] = (value for value in TICKERS if value not in REMOVE)
    # remove duplicates
    TICKERS  = set(TICKERS)

    tra.describe_run(tickers     = TICKERS,
                     date_range  = DATE_RANGE,
                     span_dic    = dft.SPAN_DIC,
                     buffer_dic  = dft.BUFFER_DIC,
                     strat_posns = POSITIONS,
                     fee_pct     = dft.FEE_PCT,
                     )

    for i, ticker in enumerate(TICKERS):
        print(f'{i+1}/{len(TICKERS)}: {ticker}')
        for strat_pos in POSITIONS:
            print(f'Strategic position: {strat_pos}')
            try:
                ticker_obj = tra.load_security(dirname = dft.DATA_DIR,
                                               ticker  = ticker,
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
                topomap = tpm.Topomap(ticker, date_range, strat_pos)

                # # Read EMA map values  from file or compute if not saved
                topomap.load_ema_map(ticker_object = ticker_obj,
                                     refresh       = REFRESH_EMA,
                                     )

                # Build & save best EMA results to file
                topomap.build_best_emas(dft.N_MAXIMA_SAVE)


                # Plot EMA contour map
                topomap.surface_plot(ticker_object = ticker_obj,
                                             date_range = date_range,
                                             style = 'contour',
                                             plot_fmt = PLOT_FORMATS,
                                             )

                # Plot EMA 3D map
                topomap.surface_plot(ticker_object = ticker_obj,
                                             date_range = date_range,
                                             style = 'surface',
                                             plot_fmt = PLOT_FORMATS,
                                             )

                # Plot time series with default parameters from best EMA
                best_span, best_buffer, best_ema, hold = topomap.get_global_max()

                # Convert zoom dates to datetime
                date_zoom = util.get_date_range(ticker_obj.get_close(),
                                                ZOOM_RANGE[0],
                                                ZOOM_RANGE[1],
                                                )
                #display flags:
                display_flags = tsp.TimeSeriesPlot.get_default_display_flags()

                plot = tsp.TimeSeriesPlot(ticker_object = ticker_obj,
                                          topomap       = topomap,
                                          strat_pos     = strat_pos,
                                          disp_dates    = date_range,
                                          span          = best_span,
                                          buffer        = best_buffer,
                                          disp_flags    = display_flags,)

                data   = pd.DataFrame(pd.merge(ticker_obj.get_close(), ticker_obj.get_volume(),
                                               left_index=True, right_index=True))
                data   = pd.DataFrame(pd.merge(data, ticker_obj.get_return(),
                                               left_index=True, right_index=True))
                plot.build_plot(data,
                                notebook = False,
                                display  = DISPLAY_TIME_SERIES,
                                remote   = REMOTE,
                                )

                # Determine the action to take for the given END_DATE
                # instantiate recommendation
                rcm = rec.Recommendation(ticker_object = ticker_obj,
                                         topomap       = topomap,
                                         target_date   = date_range[1],
                                         span          = best_span,
                                         buffer        = best_buffer,
                                         stratpos      = strat_pos,
                                         ts_plot       = plot,
                                         )
                rcm.print_recommendation(notify = NOTIFY)
                recommender.add_recommendation(rcm)

                util.print_running_time(ticker, start_tm, save_tm)
                save_tm = time.time() # save intermediate time
            except Exception as ex:
                print(f'Could not process {ticker}: Exception={ex}')
                print(sys.exc_info())
    # send notifications
    email_plot_flags = {'ts': True, 'contour': True, 'surface': True}
    recommender.notify(screen_nc = True,
                       email_nc  = False,
                       email_plot_flags = email_plot_flags,
                       )
    print(f"Total elapsed time: {util.convert_seconds(time.time()-start_tm)}")
