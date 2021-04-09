#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 17:13:37 2021

@author: charles mégnin
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

import trading as tra
import trading_defaults as dft
import trading_plots as trplt
import utilities as util

class Topomap():
    ''' A Topomap encapsulates :
        span, buffer, EMA, hold
    '''
    def __init__(self, ticker_symbol, date_range):
        '''
        name -> identifier / ticker name that corresponds to EMA map
        date_range in datetime format
        spans, buffers, emas -> numpy arrays
        hold -> float
        '''
        self._name       = ticker_symbol
        self._date_range = date_range
        self._spans      = None
        self._buffers    = None
        self._emas       = None
        self._hold       = None
        self._best_emas  = None
        self._n_best     = None # number of best_emas


    def set_date_range(self, date_range):
        '''Reset date range'''
        self._date_range = date_range


    def set_hold(self, hold):
        '''
        If hold passed as a float keep it as is,
        if a list-like object, take first element only
        '''
        if isinstance(hold, (list, np.ndarray, pd.Series)):
            self._hold = hold[0]
        else:
            self._hold = hold


    def get_name(self):
        '''Return ticker identifier '''
        return self._name

    def get_spans(self):
        '''Return spans'''
        return self._spans

    def get_buffers(self):
        '''Return buffers'''
        return self._buffers

    def get_emas(self):
        '''Return EMAs'''
        return self._emas

    def get_hold(self):
        '''Return hold'''
        return self._hold

    def self_describe(self):
        '''Display all variables in class'''
        print(self.__dict__)

    def get_best_emas(self):
        '''Return best emas dataframe '''
        return self._best_emas

    def get_global_max(self):
        '''Returns the top span, buffer, ema, hold combination'''
        return self._best_emas.iloc[0]

    def get_ema_map_filename(self):
        '''
        Return the persist filename for the ema portion of the topomap
        '''
        data_dir = dft.DATA_DIR
        data_dir = os.path.join(data_dir, self._name)

        dates    = util.dates_to_strings(self._date_range, '%Y-%m-%d')
        suffix   = f'{dates[0]}_{dates[1]}_ema_map'
        filename = f'{self._name}_{suffix}'
        return os.path.join(data_dir, filename + '.csv')


    def build_ema_map(self, security, dates):
        '''
        Builds a 2D numpy array of EMAs as a function of span and buffer
        This function iteratively calls build_strategy()
        '''
        # define rolling window span range

        span_par = dft.get_spans()
        spans = np.arange(span_par[0],
                          span_par[1] + 1,
                          step = 1
                         )

        # define buffer range
        buff_par = dft.get_buffers()
        buffers = np.linspace(buff_par[0],
                              buff_par[1],
                              buff_par[2],
                             )

        # Initialize EMA returns
        emas = np.zeros((spans.shape[0], buffers.shape[0]), dtype=np.float64)

        # Fill EMAS for all span/buffer combinations
        desc = f'Outer Level (spans) / {span_par[1] - span_par[0] + 1}'
        for i, span in tqdm(enumerate(spans), desc = desc):
            for j, buffer in enumerate(buffers):
                data  = tra.build_strategy(security.loc[dates[0]:dates[1], :].copy(),
                                       span,
                                       buffer,
                                       dft.INIT_WEALTH,
                                      )
                emas[i][j] = tra.get_cumret(data,
                                        'ema',
                                        tra.get_fee(data,
                                                dft.FEE_PCT,
                                                dft.get_actions()))
                if i == 0 and j == 0:
                    hold = tra.get_cumret(data, 'hold')

        self._spans   = spans
        self._buffers = buffers
        self._emas    = emas
        self.set_hold(hold)


    def read_ema_map(self): # Incorporate into topomap
        '''Reads raw EMA data from csv file, reshape and  and returns as a dataframe'''
        pathname = self.get_ema_map_filename()

        ema_map = pd.read_csv(pathname, sep=';', index_col=0)

        spans   = ema_map['span'].to_numpy()
        buffers = ema_map['buffer'].to_numpy()
        emas    = ema_map['ema'].to_numpy()
        hold    = ema_map['hold'].to_numpy()

        # reshape the arrays
        spans   = np.unique(spans)
        buffers = np.unique(buffers)
        emas    = np.reshape(emas, (spans.shape[0], buffers.shape[0]))

        self._spans   = spans
        self._buffers = buffers
        self._emas    = emas
        self.set_hold(hold)


    def build_best_emas(self, n_best):
        '''computes best emas'''
        self._n_best = n_best
        results = np.zeros(shape=(n_best, 4))

        # Build a n_best x 4 dataframe
        # copy b/c algorithm destroys top n_maxima EMA values
        _emas = self.get_emas().copy()

        for i in range(n_best):
            # Get coordinates of maximum emas value
            max_idx = np.unravel_index(np.argmax(_emas, axis=None),
                                       _emas.shape)

            results[i][0] = self._spans[max_idx[0]]
            results[i][1] = self._buffers[max_idx[1]]
            results[i][2] = np.max(_emas)
            results[i][3] = self._hold

            # set max emas value to arbitrily small number and re-iteratedates_to_strings
            _emas[max_idx[0]][max_idx[1]] = - dft.HUGE

        # Convert numpy array to dataframe
        self._best_emas = pd.DataFrame(results,
                                       columns=['span', 'buffer', 'ema', 'hold']
                                       )

    def save_emas(self):
        '''
        Save ema map to file
        '''
        temp = []
        for i, span in enumerate(self.get_spans()):
            for j, buffer in enumerate(self.get_buffers()):
                temp.append([span, buffer, self.get_emas()[i,j], self._hold])

        temp = pd.DataFrame(temp, columns=['span', 'buffer', 'ema', 'hold'])

        dates = util.dates_to_strings(self._date_range, '%Y-%m-%d')
        suffix = f'{dates[0]}_{dates[1]}_ema_map'
        self._save_dataframe(suffix, temp, 'csv')


    def save_best_emas(self):
        '''
        Outputs n_best results to file
        date_range im datetime format
        The output data is n_best rows of:
        | span | buffer | ema | hold |
        '''
        if self._date_range is None:
            msg = 'save_best_emas: date_range should be set via set_date_range'
            raise ValueError(msg)
        start, end = util.dates_to_strings(self._date_range, '%Y-%m-%d')
        suffix = f'{start}_{end}_results'
        self._save_dataframe(suffix, self._best_emas, 'csv')


    def _save_dataframe(self, suffix, dataframe, extension): # Implement json save
        '''
        Save a dataframe in either csv or pkl format
        '''
        data_dir = dft.DATA_DIR
        data_dir = os.path.join(data_dir, self._name)
        os.makedirs(data_dir, exist_ok = True)

        filename = f'{self._name}_{suffix}'

        if extension == 'pkl':
            pathname = os.path.join(data_dir, filename + '.pkl')
            dataframe.to_pickle(pathname)
        elif extension == 'csv':
            pathname = os.path.join(data_dir, filename + '.csv')
            dataframe.to_csv(pathname, sep=';')
        else:
            raise ValueError(f'{extension} not supported should be pkl or csv')


    ### Plotting functions ###

    def contour_plot(self, ticker_object, date_range):
        '''
        Contour plot of EMA as a function of rolling-window span & buffer
        '''
        n_contours = dft.N_CONTOURS # number of contours
        n_maxima   = dft.N_MAXIMA_DISPLAY # number of maximum points to plot

        # Get start & end dates in title (%d-%b-%Y) and output file (%Y-%m-%d) formats
        title_range = util.dates_to_strings([date_range[0],
                                            date_range[1]],
                                           '%d-%b-%Y')
        name_range  = util.dates_to_strings([date_range[0],
                                             date_range[1]],
                                            '%Y-%m-%d')

        # Plot
        _, axis = plt.subplots(figsize=(dft.FIG_WIDTH, dft.FIG_WIDTH))
        plt.contourf(self._buffers,
                     self._spans,
                     self._emas,
                     levels = n_contours,
                     cmap   = dft.CONTOUR_COLOR_SCHEME,
                     )
        plt.colorbar(label='EMA return')

        axis = trplt.build_3D_axes_labels(axis)

        # Plot maxima points
        max_ema, max_span, max_buff = trplt.plot_maxima(self._emas,
                                                        self._spans,
                                                        self._buffers,
                                                        self._hold,
                                                        axis,
                                                        n_maxima,)

        # Build title
        symbol = ticker_object.get_symbol()
        axis = trplt.build_title(axis,
                                 symbol,
                                 ticker_object.get_name(),
                                 title_range,
                                 max_ema, self._hold, max_span, max_buff)

        plt.grid(b=None, which='major', axis='both', color=dft.GRID_COLOR)
        trplt.save_figure(dft.PLOT_DIR,
                          f'{symbol}_{name_range[0]}_{name_range[1]}_contours',
                          extension='png')
        plt.show()


    def surface_plot(self, ticker_object, date_range, colors, azim=None, elev=None, rdist=10):
        '''
        Surface plot of EMA as a function of rolling-window span & buffer
        '''
        def extract_best_ema():
            idx_max  = self._best_emas['ema'].idxmax()
            max_ema  = self._best_emas['ema'].max()
            max_span = self._best_emas.span.iloc[idx_max]
            max_buff = self._best_emas.buffer.iloc[idx_max]
            return max_span, max_buff, max_ema

        def re_format_data():
            temp = []
            for i, span in enumerate(self._spans):
                for j, buffer in enumerate(self._buffers):
                    temp.append([span, buffer, self._emas[i,j]])
            return pd.DataFrame(temp, columns=['span', 'buffer', 'ema'])

        def remove_axes_grids(axis):
            # Remove gray panes and axis grid
            remove_z = False
            axis.xaxis.pane.fill = False
            axis.xaxis.pane.set_edgecolor('white')
            axis.yaxis.pane.fill = False
            axis.yaxis.pane.set_edgecolor('white')
            axis.zaxis.pane.fill = False
            axis.zaxis.pane.set_edgecolor('white')
            axis.grid(False)
            # Remove z-axis
            if remove_z:
                axis.w_zaxis.line.set_lw(0.)
                axis.set_zticks([])
            return axis

        # Get start & end dates in title (%d-%b-%Y) and output file (%Y-%m-%d) formats
        title_range = util.dates_to_strings([date_range[0],
                                            date_range[1]],
                                           '%d-%b-%Y')

        name_range   = util.dates_to_strings([date_range[0],
                                             date_range[1]],
                                            '%Y-%m-%d')
        max_span, max_buff, max_ema = extract_best_ema()
        temp = re_format_data()
        # Plot
        fig  = plt.figure(figsize=(10, 10))
        axis = fig.gca(projection='3d')
        # Set perspective
        axis.view_init(elev=elev, azim=azim)
        axis.dist=rdist

        surf = axis.plot_trisurf(temp['buffer'],
                                 temp['span'],
                                 temp['ema'],
                                 cmap      = colors,
                                 linewidth = 1)
        fig.colorbar(surf, shrink=.5, aspect=25, label = 'EMA return')

        axis = trplt.build_3D_axes_labels(axis)
        #axis.set_zlabel(r'Return', rotation=60)
        axis = remove_axes_grids(axis)
        symbol = ticker_object.get_symbol()
        axis = trplt.build_title(axis,
                                 symbol,
                                 self._name,
                                 title_range,
                                 max_ema,
                                 self._hold,
                                 max_span,
                                 max_buff)

        trplt.save_figure(dft.PLOT_DIR,
                          f'{symbol}_{name_range[0]}_{name_range[1]}_3D',
                          extension='png')
        plt.show()
