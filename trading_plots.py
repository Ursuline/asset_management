#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 14:38:49 2021

trading_plots.py

@author: charles mégnin
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import trading as tra
import trading_defaults as dft

def plot_setup(data, target, xlabel):
    '''
    Build line plot structure: dimensions, axes, label & grid
    '''
    fig, axis = plt.subplots(figsize=(dft.FIG_WIDTH, dft.FIG_HEIGHT))
    axis.plot(data[target],
              data.ema,
              linewidth = 1,
              label='EMA return',
              )
    axis.legend(loc='best')
    axis.set_xlabel(xlabel)
    axis.set_ylabel('return (x)')
    plt.grid(b=None, which='major', axis='both', color='#f1f1f1')
    return fig, axis


def build_title(axis, ticker, start_date, end_date, ema, hold, span, buffer):
    '''
    Build plot title (common to plot_buffer_range() & plot_span_range())
    '''
    title  = f'{ticker} | {start_date} - {end_date}\n'
    title += f'EMA max payoff={ema:.2%} (hold={hold:.2%}) | '
    title += f'{span}-day mean | '
    title += f'opt buffer={buffer:.2%}'
    axis.set_title(title,
                   fontsize = dft.TITLE_SIZE,
                   color    = dft.TITLE_COLOR,
                  )
    return axis


def plot_maxima(emas, spans, buffers, hold, axis, n_maxima):
    '''
    Plot points corresponding to n_maxima largest EMA
    '''
    _emas = emas.copy() # b/c algorithm destroys top n_maxima EMA values
    for i in range(n_maxima):
        # Get coordinates of maximum emas value
        max_idx = np.unravel_index(np.argmax(_emas, axis=None),
                                   _emas.shape)
        if i == 0: # Save best EMA
            max_ema  = np.max(_emas)
            max_span = spans[max_idx[0]]
            max_buff = buffers[max_idx[1]]

        axis.plot(buffers[max_idx[1]], spans[max_idx[0]], marker = 'x')
        axis.annotate(i,
                      xy  = (buffers[max_idx[1]],
                             spans[max_idx[0]]
                            ),
                      textcoords='data',
                      fontsize = dft.MAX_LABEL_SIZE,
                    )
        msg  = f'Max EMA {i}={np.max(_emas):.2%}: '
        msg += f'{spans[max_idx[0]]:.0f}-days buffer={buffers[max_idx[1]]:.2%} '
        msg += f'(hold={hold:.2%})'
        print(msg)

        # set max emas value to arbitrily small number and re-iterate
        _emas[max_idx[0]][max_idx[1]] = - dft.HUGE
    return max_ema, max_span, max_buff


def plot_max_values(data, axis, n_values, max_val, min_val, fmt):
    '''
    Plots maximum values in dataframe as vertical lines
    '''
    largest_idx = pd.Series(data['ema'].nlargest(n_values)).index
    for large in largest_idx:
        axis.axvline(data.iloc[large][0],
                     color     = dft.VLINE_COLOR,
                     linestyle = ':',
                     linewidth = 1,
                    )
        if fmt.lower() == 'integer':
            text = f'{data.iloc[large][0]:.0f}'
        elif fmt.lower() == 'percent':
            text = f'{data.iloc[large][0]:.2%}'
        else:
            raise ValueError(f'{fmt} not implemented / should be integer or percent')

        axis.annotate(text=text,
                    xy=(data.iloc[large][0],
                        min_val + np.random.uniform(0, 1)*(max_val-min_val)),
                    color=dft.VLINE_COLOR,
                    )
    return largest_idx


def plot_arrows(axis, data, actions, colors):
    '''
    Draws position-switching arrows on axis
    '''
    vertical_range = data['Close'].max() - data['Close'].min()
    horizont_range = (data.index[-1] - data.index[0]).days
    arrow_length   = vertical_range/10
    head_width     = horizont_range/100
    head_length    = vertical_range/50
    space          = vertical_range/100  # space bw arrow tip and curve

    for row in range(data.shape[0]):
        if data.ACTION[row] == actions[0]:  # buy
            y_start = data.loc[data.index[row], 'Close'] + arrow_length
            color = colors[2]
            delta_y = -arrow_length+space
        elif data.ACTION[row] == actions[1]:  # sell
            y_start = data.loc[data.index[row], 'Close'] - arrow_length
            color = colors[3]
            delta_y = arrow_length-space
        else:  # don't draw the arrow
            continue
        axis.arrow(x=data.index[row],
                   y=y_start,
                   dx=0, dy=delta_y,
                   head_width=head_width,
                   head_length=head_length,
                   length_includes_head=True,
                   linestyle='-',
                   color=color,
                  )


def build_1d_emas(ticker, secu, date_range, var_name, variables, fixed, fpct):
    ''' Aggregates a 1D numpy array of EMAs as a function of
        the variable (span or buffer)
        the fixed value (buffer or span)
        returns the numpy array of EMAs as well as the value for a hold strategy
    '''
    emas  = np.zeros(variables.shape)

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

        dfr = tra.build_strategy(ticker,
                                 secu.loc[date_range[0]:date_range[1], :].copy(),
                                 span,
                                 buffer,
                                 dft.INIT_WEALTH,
                                 )
        fee = tra.get_fee(dfr, fpct, dft.get_actions())
        ema = tra.get_cumret(dfr, 'ema', fee)
        emas[i] = ema
        if i == 0:
            hold = tra.get_cumret(dfr, 'hold', dft.INIT_WEALTH)

    return emas, hold


def plot_span_range(ticker, security, buffer, n_values, fee_pct, date_range, extension='png'):
    '''
    Plots all possible spans for a given buffer size
    the range of span values is determined in defaults file
    '''
    #emas = []
    span_range = dft.get_spans()
    spans = np.arange(span_range[0],
                      span_range[1] + 1)
    start_string, end_string = tra.dates_to_strings(date_range)
    emas, hold = build_1d_emas(ticker, security, date_range,
                               var_name='span', variables=spans, fixed=buffer,
                               fpct=fee_pct)

    dfr = pd.DataFrame(data=[spans, emas]).T
    dfr.columns = ['span', 'ema']

    max_val = dfr['ema'].max()
    min_val = dfr['ema'].min()

    print(f'\nmax-min ema={max_val}, {min_val}\n')

    # Plot
    _, axis     = plot_setup(dfr, target='span', xlabel='rolling mean span (days)')
    largest_idx = plot_max_values(dfr, axis, n_values, max_val, min_val, 'integer')
    axis = build_title(axis,
                       ticker,
                       start_string, end_string,
                       max_val, hold,
                       dfr.iloc[largest_idx[0]][0], buffer,
                       )

    # save plot to file
    save_figure(dft.PLOT_DIR, f'{ticker}_{start_string}_{end_string}_spans', extension)


def plot_buffer_range(ticker, security, span, n_values, fee_pct, date_range, extension='png'):
    '''
    Plots all possible buffers for a given rolling window span
    the range of buffer values is determined in defaults file
    '''
    buffer_range = dft.get_buffers()
    buffers = np.linspace(buffer_range[0],
                          buffer_range[1],
                          buffer_range[2])
    start_string, end_string = tra.dates_to_strings(date_range)

    emas, hold = build_1d_emas(ticker, security, date_range,
                               var_name='buffer', variables=buffers, fixed=span,
                               fpct=fee_pct)

    dfr = pd.DataFrame(data=[buffers, emas]).T
    dfr.columns = ['buffer', 'ema']

    max_val = dfr['ema'].max()
    min_val = dfr['ema'].min()

    # Plot
    _, axis     = plot_setup(dfr, target='buffer', xlabel='buffer size (% around EMA)')
    largest_idx = plot_max_values(dfr, axis, n_values, max_val, min_val, 'percent')
    axis = build_title(axis,
                       ticker,
                       start_string, end_string,
                       max_val, hold,
                       span, dfr.iloc[largest_idx[0]][0],
                       )

    # save plot to file
    save_figure(dft.PLOT_DIR, f'{ticker}_{start_string}_{end_string}_buffers', extension)

### I/O

def save_figure(plot_dir, p_file, dpi=360, extension='png'):
    '''
    Save figure to file
    '''
    filename = os.path.join(plot_dir, p_file + f'.{extension}')
    plt.savefig(filename,
                dpi=dpi,
                transparent=False,
                orientation='landscape',
                bbox_inches='tight')
