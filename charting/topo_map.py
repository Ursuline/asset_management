#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 17:13:37 2021

topo_map.py

@author: charles mégnin
"""
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from tqdm import tqdm

from charting import trading_defaults as dft
from charting import trading_plots as trplt
from finance import utilities as util

class Topomap():
    ''' A Topomap encapsulates is the 3d representation of the cumulative ema
    return for all possible combinations of span and buffers
        span, buffer, EMA, hold
    '''
    def __init__(self, ticker_symbol, date_range, strategic_position):
        '''
        name -> identifier / ticker name that corresponds to EMA map
        date_range in datetime format
        spans, buffers, emas -> numpy arrays
        hold -> float
        strategic trading position: strat_pos = 'long' or 'short'
        '''
        self._name       = ticker_symbol
        self._date_range = date_range
        self._strat_pos  = strategic_position.lower()
        self._fee        = dft.FEE_PCT
        self._init_wealth = dft.INIT_WEALTH
        self._strategy   = None
        self._spans      = None
        self._buffers    = None
        self._emas       = None
        self._hold       = None
        self._best_emas  = None
        self._n_best     = None # number of best_emas
        self._ctr_plot_pathname = None
        self._sfc_plot_pathname = None

    ## Setters
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

    ## Getters
    def get_name(self):
        '''Return ticker identifier'''
        return self._name

    def get_strategic_position(self):
        '''Return position '''
        return self._strat_pos

    def get_date_range(self):
        '''Return ticker identifier'''
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

    def get_plot_pathname(self, style:str):
        '''Return a contour or a surface plot defined with style'''
        if style == 'contour':
            return self._ctr_plot_pathname
        if style == 'surface':
            return self._sfc_plot_pathname
        msg = f'style {style} should be contour or surface'
        raise AssertionError(msg)


    def build_ema_map(self, close, dates):
        '''
        Builds a 2D numpy array of EMAs as a function of span and buffer
        This function iteratively calls build_strategy()
        '''
        # define rolling window span range
        span_par = dft.get_spans()
        self._spans = np.arange(span_par['min'],
                                span_par['max'] + 1,
                                step = 1
                                )

        # define buffer range
        buff_par = dft.get_buffers()
        self._buffers = np.linspace(buff_par['min'],
                                    buff_par['max'],
                                    buff_par['number'],
                                    )

        # Initialize EMA returns
        emas = np.zeros((self._spans.shape[0], self._buffers.shape[0]), dtype=np.float64)

        # Fill EMAS for all span/buffer combinations
        desc = f'Building ema map /{span_par["max"] - span_par["min"] + 1}'
        for i, span in tqdm(enumerate(self._spans), desc = desc, ncols=40):
            for j, buffer in enumerate(self._buffers):
                data  = self.build_strategy(close.loc[dates[0]:dates[1], :].copy(),
                                            span,
                                            buffer,
                                            )
                emas[i][j] = self.get_cumret(data,
                                             'ema',
                                             self.get_fee(data, dft.get_actions()),
                                             )
                if i == 0 and j == 0:
                    hold = self.get_cumret(data, 'hold')

        self._emas    = emas
        self.set_hold(hold)


    @staticmethod
    def build_moving_average(dataframe, span, buffer, mean_type):
        '''
        Builds moving average column and its buffers
        mean_type = string either 'EMA' (exponential) or 'SMA' (simple)
        '''
        # Compute exponential weighted mean 'EMA'
        if mean_type == 'EMA':
            dataframe.loc[:, 'EMA'] = dataframe.Close.ewm(span=span, adjust=False).mean()
        elif mean_type == 'SMA':
            dataframe.loc[:, 'SMA'] = dataframe.Close.rolling(window=int(span)).mean()
        else:
            msg  = 'Topomap.build_moving_average(): '
            msg += 'mean_type {mean_type} should be EMA or SMA'
            raise ValueError(msg)
        # Add the buffer boundaries as columns
        dataframe.insert(loc = 1,
                       column = f'{mean_type}_MINUS',
                       value  = dataframe[mean_type]*(1-buffer)
                       )
        dataframe.insert(loc = len(dataframe.columns),
                       column = f'{mean_type}_PLUS',
                       value  = dataframe[mean_type]*(1+buffer)
                       )
        return dataframe


    def build_strategy(self, d_frame, span, buffer):
        '''
        Implements EMA running-mean (aka emw) strategy
        Input dataframe d_frame has date index & security value 'Close'

        Variables:
        span       -> number of rolling days
        buffer     -> % above & below ema to trigger buy/sell

        Returns the 'strategy' consisting of a dataframe with original data +
        following columns:
        EMA -> exponential moving average
        SMA -> Simple moving average
        SIGN -> 1 : above buffer 0: in buffer -1: below buffer
        ACTION -> buy / sell / n/c (no change)
        RET -> 1 + % daily return
        CUMRET_HOLD -> cumulative returns for a hold strategy
        RET2 -> 1 + % daily return when Close > EMA
        CUMRET_EMA -> cumulative returns for the EMA strategy
        '''
        # Build EMA & its buffers
        d_frame = self.build_moving_average(d_frame, span, buffer, 'EMA')

        # Build SMA & its buffers
        d_frame = self.build_moving_average(d_frame, span, buffer, 'SMA')

        # build the SIGN column (above/in/below buffer)
        d_frame = self.build_sign(d_frame, buffer)

        # build the POSITION (long/cash) & ACTION (buy/sell) columns
        d_frame = self.build_positions(d_frame)

        # compute returns from a hold strategy
        d_frame = self.build_hold(d_frame)

        # compute returns from the EMA strategy
        d_frame = self.build_ema(d_frame)

        self._strategy = d_frame

        return d_frame


    @staticmethod
    def build_sign(d_frame, buffer):
        '''
        The SIGN column corresponds to the position wrt ema +/- buffer:
        below buffer: -1 / within buffer: 0 / above buffer: 1
        '''
        d_frame.loc[:, 'SIGN'] = np.where(d_frame.Close - d_frame.EMA*(1 + buffer) > 0,
                                          1,
                                          np.where(d_frame.Close - d_frame.EMA*(1 - buffer) < 0,
                                                      -1, 0)
                                          )
        d_frame.loc[d_frame.index[0], 'SIGN'] = 0.0  # set first value to 0
        return d_frame


    def build_positions(self, d_frame):
        '''
        Builds desired positions & actions for long/short EMA strategies
        POSITION -> cash, long, short
        ACTION -> buy, sell, n/c (no change)
        '''
        def handle_long(prev_pos:str, prev_sign:str, sign:int):
            '''handler for long trading position'''
            # Build the action
            if sign in (0, prev_sign):
                action = 'n/c'
            elif sign == 1: # previous sign is -1 or 0
                if prev_pos == 'cash':
                    action = 'buy'
                elif prev_pos == 'long':
                    action = 'n/c'
                else:
                    action = None
            else: #sign == -1:
                if prev_pos == 'cash':
                    action = 'n/c'
                elif prev_pos == 'long':
                    action = 'sell'
                else:
                    action = None

            # build the position
            if action == 'buy':
                position = 'long'
            elif action == 'sell':
                position = 'cash'
            elif action == 'n/c':
                position = prev_pos
            else:
                msg = f'TopoMap.handle_long position={position} action={action}'
                raise ValueError(msg)
            return [position, action]

        def handle_short(prev_pos:str, prev_sign:str, sign:int):
            '''handler for long trading position'''
            # Build the action
            if sign in (0, prev_sign):
                action = 'n/c'
            elif sign == 1: # previous sign is -1 or 0
                if prev_pos == 'cash':
                    action = 'n/c'
                elif prev_pos == 'short':
                    action = 'buy'
                else:
                    action = None
            else: #sign == -1:
                if prev_pos == 'cash':
                    action = 'sell'
                elif prev_pos == 'short':
                    action = 'n/c'
                else:
                    action = None

            # build the position
            if action == 'buy':
                position = 'cash'
            elif action == 'sell':
                position = 'short'
            elif action == 'n/c':
                position = prev_pos
            else:
                msg = f'TopoMap.handle_short position={position} action={action}'
                raise ValueError(msg)
            return [position, action]


        n_time_steps       = d_frame.shape[0]
        positions, actions = ([] for i in range(2))

        # Set initial value
        positions.append(dft.POSITIONS[2])
        actions.append(dft.ACTIONS[2])

        for step in range(1, n_time_steps):
            sign      = d_frame.loc[d_frame.index[step], 'SIGN']
            prev_sign = d_frame.loc[d_frame.index[step - 1], 'SIGN']
            prev_position = positions[step - 1]
            if self._strat_pos == 'long':
                pos_act = handle_long(prev_position, prev_sign, sign)
            elif self._strat_pos == 'short':
                pos_act = handle_short(prev_position, prev_sign, sign)
            else:
                raise ValueError(f'build_positions: "{self._strat_pos}" long or short positions only')
            positions.append(pos_act[0])
            actions.append(pos_act[1])

        d_frame.insert(loc=len(d_frame.columns), column='POSITION', value=positions)
        d_frame.insert(loc=len(d_frame.columns), column='ACTION', value=actions)
        return d_frame


    def build_ema(self, d_frame):
        '''
        Computes returns, cumulative returns and 'wealth' from initial_wealth
        for EMA strategy
        *** INCORPORATE FEES ***
        '''
        # return: cash=no change. Return only accumulates after LAG days
        d_frame.loc[:, 'RET_EMA'] = np.where(d_frame.POSITION.shift(dft.LAG) == 'cash',
                                             1.0,
                                             d_frame.RET,
                                             )
        # Compute cumulative returns aka 'Wealth'
        d_frame.loc[:, 'CUMRET_EMA'] = d_frame.RET_EMA.cumprod(axis   = None,
                                                               skipna = True) * self._init_wealth
        # Set initial value to init_wealth
        d_frame.loc[d_frame.index[0], 'CUMRET_EMA'] = self._init_wealth

        return d_frame


    def build_hold(self, d_frame):
        '''
        Computes returns, cumulative returns and 'wealth' from initial_wealth
        for hold strategy
        *** MUST INCORPORATE FEES at start/end ***
        '''
        if self._strat_pos == 'long':
            d_frame.loc[:, 'RET'] = 1.0 + d_frame.Close.pct_change()
        else: # short
            d_frame.loc[:, 'RET'] = 1.0 - d_frame.Close.pct_change()
        d_frame.loc[d_frame.index[0], 'RET'] = 1.0  # set first value to 1.0
        d_frame.loc[:, 'CUMRET_HOLD'] = self._init_wealth * d_frame.RET.cumprod(axis   = None,
                                                                                skipna = True)
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
        fee -> $ fee corresponding to self._fee (%)
        '''
        # Add a fee for each movement: mask buys
        fee  = (self._fee * data[data.ACTION == actions[0]].CUMRET_EMA.sum())
        # Mask sells
        fee += (self._fee * data[data.ACTION == actions[1]].CUMRET_EMA.sum())
        return fee


    def get_recom_strategy(self):
        '''Returns the recommended (last row) of the strategy dataframe '''
        current = self._strategy.iloc[-1]
        return current


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
        suffix  = f'{dates[0]}_{dates[1]}_{self._strat_pos}_ema_map'
        suffix = f'{self._name}_{suffix}'
        return suffix

    def load_ema_map(self, ticker_object, refresh, verbose=False):
        '''
        Reads raw EMA data from csv file, reshape and  and returns as a dataframe
        '''
        # Read EMA map values  from file or compute if not saved
        data_dir = os.path.join(dft.DATA_DIR, ticker_object.get_symbol())
        file     = self.get_ema_map_filename() + '.csv'
        map_path = os.path.join(data_dir, file)
        if (os.path.exists(map_path)) & (not refresh):
            if verbose:
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
            if verbose & (not refresh):
                print(f'No EMA map in {map_path}')
            self.build_ema_map(ticker_object.get_close(), self._date_range)
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
        self.save_best_emas() # save to file


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
        suffix = f'{self._name}_{start}_{end}_{self._strat_pos}_results'

        data_dir = os.path.join(dft.DATA_DIR, self._name)
        os.makedirs(data_dir, exist_ok = True)

        self._save_dataframe(self._best_emas, data_dir, suffix, 'csv')


    @staticmethod
    def _save_dataframe(dataframe, data_dir, suffix, extension):
        '''
        Save a dataframe in either csv or pkl format # Implement json save
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
    def surface_plot(self, ticker_object, date_range, style, plot_fmt):
        '''
        plotly surface and contour plots
        style = surface or contour
        '''
        plot_width  = 750
        plot_height = 750
        title_font_sz = 14
        if style not in ['contour', 'surface']:
            msg = f'style {style} should be contour or surface'
            raise AssertionError(msg)
        def extract_best_ema():
            '''
            find highest ema value and corresponding span/buffer
            in _best_emas dataframe
            '''
            idx_max  = self._best_emas['ema'].idxmax()
            max_ema  = self._best_emas['ema'].max()
            max_span = self._best_emas.span.iloc[idx_max]
            max_buff = self._best_emas.buffer.iloc[idx_max]
            return max_span, max_buff, max_ema

        def _build_title(ticker, dates, ema, span, buffer):
            ''' Build plot title '''
            hold     = self._hold
            ticker_name   = ticker.get_name()
            ticker_symbol = ticker.get_symbol()
            title  = f'{ticker_name} ({ticker_symbol}) | '
            title += f'{self._strat_pos.capitalize()} position | '
            title += f'{dates[0]} - {dates[1]}<br>'
            title += f'Max payoff={ema:.2%} (hold={hold:.2%}) | '
            title += f'{span:.0f}-day mean | '
            title += f'buffer={buffer:.2%}'
            return title

        max_span, max_buff, max_ema = extract_best_ema()
        y_values = self._spans
        x_values = self._buffers
        z_values = self._emas

        title_range = util.dates_to_strings([date_range[0],
                                             date_range[1]],
                                            '%d-%b-%Y')
        name_range   = util.dates_to_strings([date_range[0],
                                             date_range[1]],
                                             '%Y-%m-%d')
        # Title
        title = _build_title(ticker = ticker_object,
                             dates  = title_range,
                             ema    = max_ema,
                             span   = max_span,
                             buffer = max_buff,
                             )
        # Axes
        xaxis_title = 'Buffer'
        yaxis_title = 'Span (days)'

        #color bar
        colorbar_dict = dict(title='Return',
                             titleside='top',
                             tickformat='.0%',
                             separatethousands=True,)
        # Hover
        hovertemplate = 'Buffer=%{x:.1%}<br>Span=%{y} days<br>Return=%{z:.1%}<extra></extra>'

        # Default layout
        layout = go.Layout(title           = title,
                           title_font_size = title_font_sz,
                           title_xref = 'paper',
                           title_x  = 0.5,
                           xaxis_title = xaxis_title,
                           yaxis_title = yaxis_title,
                           autosize = True,
                           width  = plot_width,
                           height = plot_height,
                           margin = dict(l=100, r=50, b=100, t=100),
                           xaxis  = dict(tickformat=".0%"),
                           )

        if style == 'surface':
            colorscale = dft.SURFACE_COLOR_SCHEME
            data = [go.Surface(x = x_values,
                               y = y_values,
                               z = z_values,
                               colorscale = colorscale,
                               colorbar   = colorbar_dict,
                               hovertemplate = hovertemplate,
                               )
                    ]
            fig = go.Figure(data=data, layout=layout)

            fig.update_traces(contours_z=dict(show        = True,
                                              usecolormap = True,
                                              highlightcolor = "limegreen",
                                              project_z      = True,
                                              )
                              )

            fig.update_layout(scene = dict(xaxis = dict(nticks=10, tickformat=".0%"),
                                           yaxis = dict(nticks=10),
                                           zaxis = dict(nticks=10, tickformat=".0%"),
                                           xaxis_title = xaxis_title,
                                           yaxis_title = yaxis_title,
                                           zaxis_title = 'return',
                                           )
                              )
        else: # contour plot
            colorscale = dft.SURFACE_COLOR_SCHEME
            data = [go.Contour(x=x_values,
                               y=y_values,
                               z=z_values,
                               colorscale=colorscale,
                               colorbar=colorbar_dict,
                               hovertemplate = hovertemplate,
                               )
                    ]

            fig = go.Figure(data   = data,
                            layout = layout,
                            )

            # Hover
            fig.update_layout(xaxis=dict(hoverformat='.2%'),
                              yaxis=dict(hoverformat='.0f'),)

        os.makedirs(os.path.join(dft.PLOT_DIR, self._name), exist_ok = True)
        filename = self.get_plot_filename(ticker_object, name_range, style, plot_fmt)

        #plotly.offline.plot(fig, filename=filename)
        if plot_fmt == 'html':
            pio.renderers.default = 'browser'
            # To include plotly.js library in file, set include_plotlyjs to True else cdn
            fig.write_html(file=filename, include_plotlyjs='cdn')
        elif plot_fmt == 'png':
            pio.renderers.default = plot_fmt
            fig.write_image(filename)
        else:
            msg = f'plot format {plot_fmt} should be html or png'
            raise AssertionError(msg)
        if style == 'surface':
            self._sfc_plot_pathname = filename
        else:
            self._ctr_plot_pathname = filename
        return fig


    def get_plot_filename(self, ticker, name_range, style, extension):
        ''' Build file name '''
        plot_dir = os.path.join(dft.PLOT_DIR, self._name)
        filename  = f'{ticker.get_symbol()}_'
        filename += f'{name_range[0]}_{name_range[1]}_'
        filename += f'{self._strat_pos}'
        if style == 'surface':
            filename += '_surface'
        else:
            filename += '_contour'
        return f"{plot_dir}/{filename}.{extension}"


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
        buffers = np.linspace(buffer_range['min'],
                              buffer_range['max'],
                              buffer_range['number'])

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
        spans = np.arange(span_range['min'],
                          span_range['max'] + 1,
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
                                 position = self._strat_pos,
                                 dates = util.dates_to_strings(self._date_range, fmt = '%d-%b-%Y'),
                                 ema = min_max[1],
                                 hold = self._hold,
                                 span = fixed,
                                 buffer = dfr.iloc[largest_idx[0]][0],
                                 buy_sell = None,
                                 )

        dates    = util.dates_to_strings(self._date_range, fmt = '%Y-%m-%d')
        filename = f'{symbol}_{dates[0]}_{dates[1]}_{target}s_{self._strat_pos}'
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
