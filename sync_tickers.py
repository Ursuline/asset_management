#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 13 11:31:19 2021

sync_tickers.py

# main driver for charting

@author: charles mégnin
"""
import sys
import time
import pandas as pd
from charting import trading as tra
from charting import trading_defaults as dft
from charting import topo_map as tpm
import recommender as rec
from charting import time_series_plot as tsp
import parameters_sync as par
from charting import holdings as hld
from finance import utilities as util


if __name__ == '__main__':
    start_tm = time.time() # total_time
    save_tm  = time.time() # intermediate time
    # Load run parameters
    yaml_data  = par.load_data()
    DATE_RANGE = par.get_time_span(yaml_data)
    ZOOM_RANGE = DATE_RANGE
    NOTIFY     = par.get_recommender_parameters(yaml_data)['notify']
    SCREEN     = par.get_recommender_parameters(yaml_data)['screen']
    EMAIL      = par.get_recommender_parameters(yaml_data)['email']
    DISPLAY_TIME_SERIES = par.get_display_parameters(yaml_data)['display_time_series']
    PLOT_FORMATS  = par.get_display_parameters(yaml_data)['ctr_sfc_plot_formats']
    REFRESH_YAHOO = par.get_refresh_parameters(yaml_data)['refresh_yahoo']
    REFRESH_EMA   = par.get_refresh_parameters(yaml_data)['refresh_ema']
    PERSIST       = par.get_db_parameters(yaml_data)['persist']

    print(f'** run time span: {DATE_RANGE} **')


    for ptf_file in par.get_portfolios(yaml_data):
        holdings = hld.Holdings(par.PORTFOLIO_DIR, ptf_file)
        securities = holdings.get_securities()
        recommender = rec.Recommender(yaml_data = yaml_data,
                                      ptf_file = ptf_file,
                                      screen = SCREEN,
                                      email  = EMAIL,
                                      )

        for i, security in enumerate(securities.Ticker):
            strategic_pos = securities.iloc[i].Strategy.strip()
            msg  = f'Security {i+1}/{len(securities)}: {security} | '
            msg += f'Strategic position: {strategic_pos} | '
            msg += f'Position: {securities.iloc[i].Position.strip()}'
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
                topomap = tpm.Topomap(security, date_range, strategic_pos)

                # Read EMA map values from file or compute if not saved
                topomap.load_ema_map(ticker_object = ticker_obj,
                                     refresh       = REFRESH_EMA,
                                     )

                # Build & save best EMA results to file
                topomap.build_best_emas(dft.N_MAXIMA_SAVE)

                # Plot EMA contour map
                ctr_plot = topomap.surface_plot(ticker_object = ticker_obj,
                                                date_range = date_range,
                                                style  = 'contour',
                                                plot_fmt = PLOT_FORMATS,
                                                )

                # Plot EMA 3D map
                sfc_plot = topomap.surface_plot(ticker_object = ticker_obj,
                                                date_range = date_range,
                                                style  = 'surface',
                                                plot_fmt = PLOT_FORMATS,
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
                ts_plot = tsp.TimeSeriesPlot(ticker_object = ticker_obj,
                                             topomap       = topomap,
                                             strat_pos     = strategic_pos,
                                             disp_dates    = date_range,
                                             span          = best_span,
                                             buffer        = best_buffer,
                                             disp_flags    = display_flags,
                                             )

                #Combine close, volume and return data
                data   = pd.DataFrame(pd.merge(ticker_obj.get_close(), ticker_obj.get_volume(),
                                               left_index=True, right_index=True))
                data   = pd.DataFrame(pd.merge(data, ticker_obj.get_return(),
                                               left_index=True, right_index=True))
                ts_plot.build_plot(data,
                                   notebook = False,
                                   display  = DISPLAY_TIME_SERIES,
                                   )

                # Determine the action to take for the given END_DATE
                # instantiate recommendation
                rcm = rec.Recommendation_sync(ticker_object = ticker_obj,
                                              topomap       = topomap,
                                              holdings      = holdings,
                                              target_date   = date_range[1],
                                              span          = best_span,
                                              buffer        = best_buffer,
                                              ts_plot       = ts_plot,
                                              )
                rcm.print_recommendation(notify = NOTIFY)
                recommender.add_recommendation(rcm)

                util.print_running_time(security, start_tm, save_tm)
                save_tm = time.time() # save intermediate time
            except Exception as ex:
                print(f'Could not process {security}: Exception={ex}')
                print(sys.exc_info())
        # send notifications
        email_plot_flags = {'ts': True, 'contour': True, 'surface': True}
        recommender.notify(screen_nc = True,  # display n/c positions to screen
                           email_nc  = False, # email n/c positions
                           email_plot_flags = email_plot_flags,
                           )
        if PERSIST:
            recommender.persist()
    print(f"Total elapsed time: {util.convert_seconds(time.time()-start_tm)}")
