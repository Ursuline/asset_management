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

import trading_defaults as dft
import trading_plots as trplt
import utilities as util

class Topomap():
    ''' A Topomap encapsulates :
        span, buffer, EMA, hold
    '''
    def __init__(self, ticker_symbol, date_range, position):
        '''
        name -> identifier / ticker name that corresponds to EMA map
        date_range in datetime format
        spans, buffers, emas -> numpy arrays
        hold -> float
        trading position strategy: position = 'long' or 'short'
        '''
        self._name       = ticker_symbol
        self._date_range = date_range
        self._position   = position.lower()
        self._fee        = dft.FEE_PCT
        self._init_wealth = dft.INIT_WEALTH
        self._spans      = None
        self._buffers    = None
        self._emas       = None
        self._hold       = None
        self._best_emas  = None
        self._n_best     = None # number of best_emas


    def set_buffers(self, buffers):
        '''Reset buffers'''
        self._buffers = buffers

    def set_spans(self, spans):
        '''Reset spans'''
        self._spans  = spans

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

    def set_fee(self, fee):
        '''reset broker's fee'''
        self._fee = fee


    def get_name(self):
        '''Return ticker identifier '''
        return self._name

    def get_position(self):
        '''Return position '''
        return self._position

    def get_date_range(self):
        '''Return ticker identifier '''
        return self._date_range

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
        desc = f'Building ema map | (spans) / {span_par[1] - span_par[0] + 1}'
        #window = security.loc[dates[0]:dates[1], :].copy()
        for i, span in tqdm(enumerate(spans), desc = desc):
            for j, buffer in enumerate(buffers):
                data  = self.build_strategy(security.loc[dates[0]:dates[1], :].copy(),
                                             span,
                                             buffer,
                                             )
                emas[i][j] = self.get_cumret(data,
                                             'ema',
                                             self.get_fee(data, dft.get_actions()),
                                             )
                if i == 0 and j == 0:
                    hold = self.get_cumret(data, 'hold')

        self._spans   = spans
        self._buffers = buffers
        self._emas    = emas
        self.set_hold(hold)


    def build_strategy(self, d_frame, span, buffer):
        '''
        *** At this point, only a long position is considered ***
        Implements running-mean (ewm) strategy
        Input dataframe d_frame has date index & security value 'Close'

        Variables:
        span       -> number of rolling days
        buffer     -> % above & below ema to trigger buy/sell

        Returns the 'strategy' consisting of a dataframe with original data +
        following columns:
        EMA -> exponential moving average
        SIGN -> 1 : above buffer 0: in buffer -1: below buffer
        ACTION -> buy / sell / n/c (no change)
        RET -> 1 + % daily return
        CUMRET_HOLD -> cumulative returns for a hold strategy
        RET2 -> 1 + % daily return when Close > EMA
        CUMRET_EMA -> cumulative returns for the EMA strategy
        '''

        # Compute exponential weighted mean 'EMA'
        d_frame.loc[:, 'EMA'] = d_frame.Close.ewm(span=span, adjust=False).mean()

        # Add the buffer boundaries as columns
        d_frame.insert(loc = 1,
                       column = 'EMA_MINUS',
                       value  = d_frame['EMA']*(1-buffer)
                       )
        d_frame.insert(loc = len(d_frame.columns),
                       column = 'EMA_PLUS',
                       value  = d_frame['EMA']*(1+buffer)
                       )

        # build the SIGN column (above/in/below buffer)
        d_frame = self.build_sign(d_frame, buffer)

        # build the POSITION (long/cash) & ACTION (buy/sell) columns
        d_frame = self.build_positions(d_frame)

        # compute returns from a hold strategy
        d_frame = self.build_hold(d_frame)

        # compute returns from the EMA strategy
        d_frame = self.build_ema(d_frame)

        # remove junk
        d_frame = self.cleanup_strategy(d_frame)

        return d_frame


    @staticmethod
    def build_sign(d_frame, buffer):
        '''
        The SIGN column corresponds to the position wrt ema +/- buffer:
        below buffer: -1 / within buffer: 0 / above buffer: 1
        '''
        d_frame.loc[:, 'SIGN'] = np.where(d_frame.Close - d_frame.EMA*(1 + buffer) > 0,
                                          1, np.where(d_frame.Close - d_frame.EMA*(1 - buffer) < 0,
                                                      -1, 0)
                                          )
        # shift by lag days -> buy/sell action follows close date 1 is next day#
        d_frame.loc[:, 'SIGN'] = d_frame['SIGN'].shift(dft.LAG)
        d_frame.loc[d_frame.index[0], 'SIGN'] = 0.0  # set first value to 0
        return d_frame


    def build_positions(self, d_frame):
        '''
        Builds desired positions for the EMA strategy
        POSITION -> cash, long, short
        ACTION -> buy, sell, n/c (no change)
        '''
        def handle_long(prev_position, sign):
            '''handler for long trading position'''
            if prev_position == 'cash':  # if previous position was cash
                if sign in [0, -1]: # in or below buffer
                    return ['cash', 'n/c']
                return ['long', 'buy']
            if prev_position == 'long':  # previous position: long
                if sign in [0, 1]: # in or above buffer
                    return ['long', 'n/c']
                return ['cash', 'sell']
            return None

        def handle_short(prev_position, sign):
            '''handler for short trading position'''
            if prev_position == 'cash':  # if previous position was cash
                if sign in [0, 1]: # in or above buffer
                    return ['cash', 'n/c']
                return ['short', 'sell']
            if prev_position == 'short':  # previous position: short
                if sign in [0, -1]: # in or below buffer
                    return ['short', 'n/c']
                return ['cash', 'buy']
            return None

        n_time_steps       = d_frame.shape[0]
        positions, actions = ([] for i in range(2))

        positions.append(dft.POSITIONS[2])
        actions.append(dft.ACTIONS[2])

        for step in range(1, n_time_steps):
            sign = d_frame.loc[d_frame.index[step], 'SIGN']
            prev_position = positions[step - 1]
            if self._position == 'long':
                pos_act = handle_long(prev_position, sign)
            elif self._position == 'short':
                pos_act = handle_short(prev_position, sign)
            else:
                raise ValueError('build_positions: long or short positions only')
            positions.append(pos_act[0])
            actions.append(pos_act[1])

        d_frame.insert(loc=len(d_frame.columns), column='POSITION', value=positions)
        d_frame.insert(loc=len(d_frame.columns), column='ACTION', value=actions)
        return d_frame


    def build_hold(self, d_frame):
        '''
        Computes returns, cumulative returns and 'wealth' from initial_wealth
        for hold strategy
        *** MUST INCORPORATE FEES at start/end ***
        '''
        if self._position == 'long':
            d_frame.loc[:, 'RET'] = 1.0 + d_frame.Close.pct_change()
        else: # short
            d_frame.loc[:, 'RET'] = 1.0 - d_frame.Close.pct_change()
        d_frame.loc[d_frame.index[0], 'RET'] = 1.0  # set first value to 1.0
        d_frame.loc[:, 'CUMRET_HOLD'] = self._init_wealth * d_frame.RET.cumprod(axis   = None,
                                                                                skipna = True)
        return d_frame


    def build_ema(self, d_frame):
        '''
        Computes returns, cumulative returns and 'wealth' from initial_wealth
        for EMA strategy
        *** INCORPORATE FEES ***
        '''
        # return: cash=no change
        d_frame.loc[:, 'RET_EMA'] = np.where(d_frame.POSITION == 'cash',
                                             1.0,
                                             d_frame.RET,
                                             )
        # Compute cumulative returns aka 'Wealth'
        d_frame.loc[:, 'CUMRET_EMA'] = d_frame.RET_EMA.cumprod(axis   = None,
                                                               skipna = True) * self._init_wealth
        # Set initial value to init_wealth
        d_frame.loc[d_frame.index[0], 'CUMRET_EMA'] = self._init_wealth

        return d_frame

    @staticmethod
    def cleanup_strategy(dataframe):
        '''
        Remove unnecessary columns
        '''
        dataframe = dataframe.drop(['SIGN'], axis=1)
        dataframe = dataframe.drop(['RET_EMA'], axis=1)

        return dataframe


    def get_fee(self, data, actions):
        '''
        Return fees associated to buys / sells
        FEE_PCT -> brokers fee
        actions = ['buy', 'sell', 'n/c']
        fee -> $ fee corresponding to fee_pct
        '''
        # Add a fee for each movement: mask buys
        fee  = (self._fee * data[data.ACTION == actions[0]].CUMRET_EMA.sum())
        # Mask sells
        fee += (self._fee * data[data.ACTION == actions[1]].CUMRET_EMA.sum())
        return fee

    @staticmethod
    def get_cumret(data, strategy, fee=0):
        '''
        Returns cumulative return for the given strategy
        Value returned is relative difference between final and initial wealth
        If strategy is EMA, returns cumulative returns net of fees
        *** FIX FEES ***
        '''
        if strategy.lower() == 'hold':
            return data.CUMRET_HOLD[-1]/dft.INIT_WEALTH - 1
        if strategy.lower() == 'ema':
            return (data.CUMRET_EMA[-1]-fee)/dft.INIT_WEALTH - 1
        raise ValueError(f'option {strategy} should be either ema or hold')

    #################
    ###### I/O ######
    #################
    def get_ema_map_filename(self):
        '''
        Return the persist filename for the ema map without extension
        '''

        dates   = util.dates_to_strings(self._date_range, '%Y-%m-%d')
        suffix  = f'{dates[0]}_{dates[1]}_{self._position}_ema_map'
        suffix = f'{self._name}_{suffix}'
        return suffix


    def load_ema_map(self, data_dir):
        '''
        Reads raw EMA data from csv file, reshape and  and returns as a dataframe
        '''
        pathname = os.path.join(data_dir,
                                self.get_ema_map_filename() + '.csv')

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


    def load_ema_map_new(self, ticker, security, refresh):
        '''
        Reads raw EMA data from csv file, reshape and  and returns as a dataframe
        '''
        # Read EMA map values  from file or compute if not saved
        data_dir = os.path.join(dft.DATA_DIR, ticker)
        file     = self.get_ema_map_filename() + '.csv'
        map_path = os.path.join(data_dir, file)
        if (os.path.exists(map_path)) & (not refresh):
            print(f'Loading EMA map {map_path}')

            pathname = os.path.join(data_dir,
                                    self.get_ema_map_filename() + '.csv')

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
        else: # If not saved, compute it
            self.build_ema_map(security, self._date_range)
        # Save ema map to file
        self.save_emas()


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

        temp   = pd.DataFrame(temp, columns=['span', 'buffer', 'ema', 'hold'])
        suffix = self.get_ema_map_filename()
        data_dir = os.path.join(dft.DATA_DIR, self._name)

        self._save_dataframe(temp, data_dir, suffix, 'csv')


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
        suffix = f'{self._name}_{start}_{end}_{self._position}_results'

        data_dir = os.path.join(dft.DATA_DIR, self._name)
        os.makedirs(data_dir, exist_ok = True)

        self._save_dataframe(self._best_emas, data_dir, suffix, 'csv')


    @staticmethod
    def _save_dataframe(dataframe, data_dir, suffix, extension): # Implement json save
        '''
        Save a dataframe in either csv or pkl format
        '''
        os.makedirs(data_dir, exist_ok = True)
        rootname = os.path.join(data_dir, suffix)

        if extension == 'pkl':
            pathname = rootname + '.pkl'
            dataframe.to_pickle(pathname)
        elif extension == 'csv':
            pathname = rootname + '.csv'
            dataframe.to_csv(pathname, sep=';')
        else:
            raise ValueError(f'{extension} not supported should be pkl or csv')


    ##########################
    ### Plotting functions ###
    ##########################
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
        axis = trplt.build_title(axis        = axis,
                                 ticker      = symbol,
                                 ticker_name = ticker_object.get_name(),
                                 position    = self._position,
                                 dates       = title_range,
                                 ema         = max_ema,
                                 hold        = self._hold,
                                 span        = max_span,
                                 buffer      = max_buff,
                                 buy_sell    = None,
                                 )

        plt.grid(b=None, which='major', axis='both', color=dft.GRID_COLOR)
        plot_dir = os.path.join(dft.PLOT_DIR, self._name)
        trplt.save_figure(plot_dir,
                          f'{symbol}_{name_range[0]}_{name_range[1]}_contours_{self._position}',
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

        axis = trplt.build_title(axis        = axis,
                                 ticker      = symbol,
                                 ticker_name = ticker_object.get_name(),
                                 dates       = title_range,
                                 position    = self._position,
                                 ema         = max_ema,
                                 hold        = self._hold,
                                 span        = max_span,
                                 buffer      = max_buff,
                                 buy_sell    = None,
                                 )

        plot_dir = os.path.join(dft.PLOT_DIR, self._name)
        trplt.save_figure(plot_dir,
                          f'{symbol}_{name_range[0]}_{name_range[1]}_3D_{self._position}',
                          extension='png')
        plt.show()


    def plot_buffer_range(self, ticker_object, security, span, n_best):
        '''
        Plots all possible buffers for a given rolling window span
        the range of buffer values is defined in defaults file
        '''
        target  = 'buffer'
        xlabel  = 'buffer size (% around EMA)'
        max_fmt = 'percent'
        fixed = span
        buffer_range = dft.get_buffers()
        buffers = np.linspace(buffer_range[0],
                              buffer_range[1],
                              buffer_range[2])

        emas, _ = self.build_ema_profile(security,
                                          var_name  = target,
                                          variables = buffers,
                                          fixed     = fixed,
                                          )

        dfr = pd.DataFrame(data=[buffers, emas]).T
        dfr.columns = [target, 'ema']
        min_max = [dfr['ema'].min(), dfr['ema'].max()]

        # Plot
        self.build_range_plot(ticker_object = ticker_object,
                              dfr           = dfr,
                              fixed         = fixed,
                              min_max       = min_max,
                              n_best        = n_best,
                              target        = target,
                              xlabel        = xlabel,
                              max_fmt       = max_fmt,
                              )


    def plot_span_range(self, ticker_object, security, buffer, n_best):
        '''
        Plots all possible spans for a given buffer size
        the range of span values is defined in defaults file
        '''
        target  = 'span'
        xlabel  = 'rolling mean span (days)'
        max_fmt = 'integer'
        fixed = buffer
        span_range = dft.get_spans()
        spans = np.arange(span_range[0],
                          span_range[1] + 1,
                          )

        emas, _ = self.build_ema_profile(security,
                                          var_name  = target,
                                          variables = spans,
                                          fixed     = fixed,
                                          )

        dfr = pd.DataFrame(data=[spans, emas]).T
        dfr.columns = [target, 'ema']
        min_max = [dfr['ema'].min(), dfr['ema'].max()]

        # Plot
        self.build_range_plot(ticker_object = ticker_object,
                              dfr           = dfr,
                              fixed         = fixed,
                              min_max       = min_max,
                              n_best        = n_best,
                              target        = target,
                              xlabel        = xlabel,
                              max_fmt       = max_fmt,
                              )


    def build_range_plot(self, ticker_object, dfr, fixed, min_max, n_best, target, xlabel, max_fmt):
        '''
        plotting function common to plot_span_range() & plot_buffer_range()
        '''
        _, axis   = trplt.plot_setup(dfr, target=target)
        axis = trplt.build_range_plot_axes(axis, target=target, xlabel=xlabel)

        largest_idx = trplt.plot_max_values(dfr, axis, n_best, min_max[1], min_max[0], max_fmt)

        symbol = self._name

        axis = trplt.build_title(axis = axis,
                                 ticker = symbol,
                                 ticker_name = ticker_object.get_name(),
                                 position = self._position,
                                 dates = util.dates_to_strings(self._date_range, fmt = '%d-%b-%Y'),
                                 ema = min_max[1],
                                 hold = self._hold,
                                 span = fixed,
                                 buffer = dfr.iloc[largest_idx[0]][0],
                                 buy_sell = None,
                                 )

        dates    = util.dates_to_strings(self._date_range, fmt = '%Y-%m-%d')
        filename = f'{symbol}_{dates[0]}_{dates[1]}_{target}s_{self._position}'
        plot_dir = os.path.join(dft.PLOT_DIR, self._name)
        trplt.save_figure(plot_dir, filename)


    def build_ema_profile(self, security, var_name, variables, fixed):
        ''' Aggregates a 1D numpy array of EMAs as a function of
            the target variable (span or buffer)
            the fixed variable (buffer or span)
            returns the numpy array of EMAs as well as the value for a hold strategy
        '''
        emas  = np.zeros(variables.shape)
        date_range = self.get_date_range()

        if var_name == 'span':
            buffer = fixed
        elif var_name == 'buffer':
            span   = fixed
        else:
            raise ValueError(f'var_name {var_name} should be span or buffer')

        for i, variable in enumerate(variables):
            if var_name == 'span':
                span   = variable
            else:
                buffer = variable

            dfr = self.build_strategy(security.loc[date_range[0]:date_range[1], :].copy(),
                                      span,
                                      buffer,
                                      )
            fee = self.get_fee(dfr,
                               dft.get_actions())
            ema = self.get_cumret(dfr, 'ema', fee)
            emas[i] = ema
            if i == 0:
                hold = self.get_cumret(dfr, 'hold', dft.INIT_WEALTH)

        return emas, hold
