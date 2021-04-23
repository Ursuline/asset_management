#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 14:38:49 2021

trading_plots.py

@author: charles mégnin
"""
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.offsetbox import (TextArea, AnnotationBbox)

import trading_defaults as dft
import utilities as util


### PLOT SUPPORT FUNCTIONS

def plot_setup(data, target):
    '''
    Build line plot structure: dimensions, axes, label & grid
    called by plot_span_range() and plot_buffer_range()
    '''
    fig, axis = plt.subplots(figsize=(dft.FIG_WIDTH, dft.FIG_HEIGHT))
    axis.plot(data[target],
              data.ema,
              linewidth = 1,
              label='EMA return',
              )
    return fig, axis


def build_range_plot_axes(axis, target, xlabel):
    '''Buildsx & y axes and their tickers'''
    axis.legend(loc='best')
    axis.set_xlabel(xlabel)
    if target == 'buffer':
        axis.xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1,
                                                              decimals=None,
                                                              symbol='%',
                                                              is_latex=False,
                                                              )
                                       )
    axis.set_ylabel('return (x)')
    plt.grid(b=None, which='major', axis='both', color=dft.GRID_COLOR)
    return axis


def build_title(axis, ticker, ticker_name, position, dates, ema, hold, span, buffer, buy_sell=None):
    '''
    Build plot title-  common to all plots
    '''
    # build the title
    title  = f'{ticker_name} ({ticker}) | {position.capitalize()} position | '
    title += f'{dates[0]} - {dates[1]}'
    if buy_sell is None:
        title += '\n'
    else: # add number of buys/sells to time series plot
        title += f' | {buy_sell[0]} buys {buy_sell[1]} sells\n'
    title += f'EMA max payoff={ema:.2%} (hold={hold:.2%}) | '
    title += f'{span:.0f}-day mean | '
    title += f'opt buffer={buffer:.2%}'
    #print(f'title step 3={title}\n')
    axis.set_title(title,
                   fontsize = dft.TITLE_SIZE,
                   color    = dft.TITLE_COLOR,
                  )
    return axis


def build_3d_axes_labels(axis):
    '''
    Axes and labels for contour & 3D plots
    '''
    axis.set_xlabel('buffer')
    axis.set_ylabel('span (days)')
    axis.xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1,
                                                          decimals=None,
                                                          symbol='%',
                                                          is_latex=False,
                                                          )
                                   )
    return axis


def plot_maxima(emas, spans, buffers, axis, n_maxima):
    '''
    Called by contour_plot()
    Plots points corresponding to n_maxima largest EMA
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

        # Plot marker at maximum
        axis.plot(buffers[max_idx[1]],
                  spans[max_idx[0]],
                  marker = 'x',
                  color  = dft.MARKER_COLOR,
                  )

        # Anotate marker
        axis.annotate(i,
                      xy  = (buffers[max_idx[1]],
                             spans[max_idx[0]]),
                      textcoords ='data',
                      fontsize   = dft.MAX_LABEL_SIZE,
                      color      = dft.ANNOTATE_COLOR,
                    )

        # set max emas value to arbitrily small number and re-iterate
        _emas[max_idx[0]][max_idx[1]] = - dft.HUGE
    return max_ema, max_span, max_buff


def plot_max_values(data, axis, n_values, max_val, min_val, fmt):
    '''
    Plots maximum values in dataframe as vertical lines
    called by plot_span_range() and plot_buffer_range()
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
            raise ValueError(f'{fmt} should be integer or percent')

        axis.annotate(text=text,
                    xy=(data.iloc[large][0],
                        min_val + np.random.uniform(0, 1)*(max_val-min_val)),
                    color=dft.VLINE_COLOR,
                    )
    return largest_idx


def plot_arrows(axis, data, actions, colors):
    '''Plot arrows '''
    vertical_range = data['Close'].max() - data['Close'].min()
    horizont_range = (data.index[-1] - data.index[0]).days
    arrow_length   = vertical_range/10
    head_width     = horizont_range/100
    head_length    = vertical_range/50
    space          = vertical_range/100  # space bw arrow tip and curve
    lag            = dft.LAG

    def shift_arrow(data, target_date, lag):
        '''Correct for the lag shift on the plot'''
        data_index = data.index.get_loc(target_date) # row number
        y_start = data.iloc[data_index - lag]['Close']
        x_pos   = data.iloc[data_index - lag].name
        return x_pos, y_start

    # filter actions rows
    # buys
    filtered = data[data.ACTION == actions[0]].copy()
    for row in range(filtered.shape[0]):
        x_pos, y_start = shift_arrow(data, filtered.index[row], lag)
        y_pos = y_start + arrow_length

        color = colors[2]
        axis.arrow(x  = x_pos,
                   y  = y_pos,
                   dx = 0,
                   dy = -arrow_length + space,
                   head_width  = head_width,
                   head_length = head_length,
                   length_includes_head = True,
                   linestyle = '-',
                   color = color,
                  )

    # sells
    filtered = data[data.ACTION == actions[1]].copy()
    for row in range(filtered.shape[0]):
        x_pos, y_start = shift_arrow(data, filtered.index[row], lag)
        y_pos = y_start - arrow_length
        color   = colors[3]
        axis.arrow(x  = x_pos,
                   y  = y_pos,
                   dx = 0,
                   dy = arrow_length - space,
                   head_width  = head_width,
                   head_length = head_length,
                   length_includes_head = True,
                   linestyle = '-',
                   color = color,
                  )


def plot_stats(summary_stats, axis):
    '''
    Place a text box with signal statistics
    '''
    xy_pos = (.95, .0075)

    text  = 'Daily returns:\n'
    text += rf'$\mu$={summary_stats["mean"]-1:.2%}\n'
    text += rf'$\sigma$={summary_stats["std"]:.3g}\n'
    text += f'Skewness={summary_stats["skewness"]:.2g}\n'
    text += f'Kurtosis={summary_stats["kurtosis"]:.2g}\n'
    text += f'Gaussian: {summary_stats["jb"]["gaussian"]}\n'
    text += f'({1-summary_stats["jb"]["level"]:.0%} '
    text += f'p-value={summary_stats["jb"]["gaussian"]:.3g})\n'
    offsetbox = TextArea(text)

    anb = AnnotationBbox(offsetbox,
                         xy_pos,
                         xybox=(-20, 40),
                         xycoords='axes fraction',
                         boxcoords="offset points",
                         frameon = False,
                         #arrowprops=dict(arrowstyle="->")
                         )
    axis.add_artist(anb)
    return axis


### MAIN PLOT FUNCTIONS
def build_range_plot(ticker_object, topomap, dfr, fixed, hold, min_max, n_best, target, xlabel, max_fmt):
    '''
    plotting function common to plot_span_range() & plot_buffer_range()
    '''
    _, axis   = plot_setup(dfr, target=target)
    axis = build_range_plot_axes(axis, target=target, xlabel=xlabel)

    date_range = topomap.get_date_range()

    largest_idx = plot_max_values(dfr, axis, n_best, min_max[1], min_max[0], max_fmt)
    if target == 'span':
        buffer = fixed
        span   = dfr.iloc[largest_idx[0]][0]
    else:
        span   = fixed
        buffer = dfr.iloc[largest_idx[0]][0]

    axis = build_title(axis        = axis,
                       ticker      = ticker_object.get_symbol(),
                       ticker_name = ticker_object.get_name(),
                       position = topomap.get_position(),
                       dates    = util.dates_to_strings(date_range, fmt = '%d-%b-%Y'),
                       ema      = min_max[1],
                       hold     = hold,
                       span     = span,
                       buffer   = buffer,
                       buy_sell = None,
                       )

    dates    = util.dates_to_strings(date_range, fmt = '%Y-%m-%d')
    filename = f'{ticker_object.get_symbol()}_{dates[0]}_{dates[1]}_{target}s'
    plot_dir = os.path.join(dft.PLOT_DIR, ticker_object.get_symbol())
    save_figure(plot_dir, filename)


def plot_span_range(ticker_object, topomap, security, buffer, n_best, fee_pct):
    '''
    Plots all possible spans for a given buffer size
    the range of span values is defined in defaults file
    '''
    target  = 'span'
    xlabel  = 'rolling mean span (days)'
    max_fmt = 'integer'
    fixed   = buffer
    span_range = dft.get_spans()
    spans = np.arange(span_range[0],
                      span_range[1] + 1)

    emas, hold = topomap.build_ema_profile(security  = security,
                                           var_name  = target,
                                           variables = spans,
                                           fixed     = fixed,
                                           fpct      = fee_pct,
                                           )

    dfr = pd.DataFrame(data=[spans, emas]).T
    dfr.columns = [target, 'ema']
    min_max = [dfr['ema'].min(), dfr['ema'].max()]

    # Plot
    build_range_plot(ticker_object,
                     topomap,
                     dfr,
                     fixed,
                     hold,
                     min_max,
                     n_best,
                     target,
                     xlabel,
                     max_fmt,
                     )


def plot_buffer_range(ticker_object, topomap, security, span, n_best, fee_pct):
    '''
    Plots all possible buffers for a given rolling window span
    the range of buffer values is defined in defaults file
    '''
    target  = 'buffer'
    xlabel  = 'buffer size (% around EMA)'
    max_fmt = 'percent'
    fixed   = span
    buffer_range = dft.get_buffers()
    buffers = np.linspace(buffer_range[0],
                          buffer_range[1],
                          buffer_range[2])

    emas, hold = topomap.build_ema_profile(security   = security,
                                           var_name   = target,
                                           variables  = buffers,
                                           fixed      = fixed,
                                           fpct       = fee_pct,
                                           )

    dfr = pd.DataFrame(data=[buffers, emas]).T
    dfr.columns = [target, 'ema']
    min_max = [dfr['ema'].min(), dfr['ema'].max()]

    # Plot
    build_range_plot(ticker_object,
                     topomap,
                     dfr,
                     fixed,
                     hold,
                     min_max,
                     n_best,
                     target,
                     xlabel,
                     max_fmt,
                     )

### I/O
def save_figure(plot_dir, prefix, dpi=360, extension='png'):
    '''
    Saves figure to file
    variables:
        plot_dir - directory to plot to
        prefix - filename without its extension
    '''
    os.makedirs(plot_dir, exist_ok = True)
    filename = f'{prefix}.{extension}'
    pathname = os.path.join(plot_dir, filename)
    try:
        plt.savefig(pathname,
                    dpi = dpi,
                    transparent = False,
                    facecolor='white',
                    edgecolor='none',
                    orientation = 'landscape',
                    bbox_inches = 'tight'
                    )
    except TypeError as ex:
        print(f'Could not save to {pathname}: {ex}')
    except:
        print(f'Error type {sys.exc_info()[0]}')
    else:
        pass
