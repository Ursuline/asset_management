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

import trading as tra
import trading_defaults as dft


### PLOT SUPPORT FUNCTIONS
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


def build_title(axis, ticker, dates, ema, hold, span, buffer):
    '''
    Build plot title (common to plot_buffer_range() & plot_span_range())
    '''
    # build the title
    title  = f'{ticker} | {dates[0]} - {dates[1]}\n'
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
    Called by plot_buffer_span_contours()
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
            print()

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
    n_buys, n_sells  = 0, 0

    for row in range(data.shape[0]):
        if data.ACTION[row] == actions[0]:  # buy
            y_start = data.loc[data.index[row], 'Close'] + arrow_length
            color = colors[2]
            delta_y = -arrow_length+space
            n_buys += 1
        elif data.ACTION[row] == actions[1]:  # sell
            y_start = data.loc[data.index[row], 'Close'] - arrow_length
            color = colors[3]
            delta_y = arrow_length-space
            n_sells += 1
        else:  # don't draw an arrow
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
    return n_buys, n_sells


def build_1d_emas(secu, date_range, var_name, variables, fixed, fpct):
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

        dfr = tra.build_strategy(secu.loc[date_range[0]:date_range[1], :].copy(),
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


### MAIN PLOT FUNCTIONS
def plot_moving(ticker, date_range, security, span, fee_pct, buffer):
    '''
    Plots security prices with moving average
    span -> rolling window span
    fee_pct -> fee associated with a buy/sell action
    '''
    start = date_range[0]
    end   = date_range[1]
    title_dates = tra.dates_to_strings([start, end], '%d-%b-%Y')
    file_dates  = tra.dates_to_strings([start, end], '%Y-%m-%d')

    # Extract time window
    dfr = tra.build_strategy(security.loc[start:end, :].copy(),
                            span,
                            buffer,
                            dft.INIT_WEALTH,
                           )
    fee  = tra.get_fee(dfr, fee_pct, dft.get_actions())
    hold = tra.get_cumret(dfr, 'hold')  # cumulative returns for hold strategy
    ema  = tra.get_cumret(dfr, 'ema', fee)  # cumulative returns for EMA strategy

    _, axis = plt.subplots(figsize=(14, 8))
    axis.plot(dfr.index, dfr.Close, linewidth=1, label='Price')
    axis.plot(dfr.index, dfr.EMA, linewidth=1, label=f'{span}-days EMA')

    axis.legend(loc='best')
    axis.set_ylabel('Price ($)')
    axis.xaxis.set_major_formatter(dft.get_year_month_format())
    axis.grid(b=None, which='both', axis='both',
             color=dft.GRID_COLOR, linestyle='-', linewidth=1)

    n_buys, n_sells= plot_arrows(axis, dfr, dft.get_actions(), dft.get_color_scheme())

    title  = f'{ticker} | '
    title += f'{title_dates[0]} - {title_dates[1]} | '
    title += f'{n_buys} buys {n_sells} sells\n'
    title += f'EMA payoff={ema:.2%} (Hold={hold:.1%}) | '
    title += f'{span}-day rolling mean | {buffer:.2%} buffer'
    axis.set_title(title, fontsize=dft.TITLE_SIZE, color=dft.TITLE_COLOR)

    save_figure(dft.PLOT_DIR, f'{ticker}_{file_dates[0]}_{file_dates[1]}')
    return dfr


def plot_span_range(ticker, date_range, security, buffer, n_values, fee_pct, extension='png'):
    '''
    Plots all possible spans for a given buffer size
    the range of span values is determined in defaults file
    '''
    #emas = []
    span_range = dft.get_spans()
    spans = np.arange(span_range[0],
                      span_range[1] + 1)

    emas, hold = build_1d_emas(security, date_range,
                               var_name='span', variables=spans, fixed=buffer,
                               fpct=fee_pct)

    dfr = pd.DataFrame(data=[spans, emas]).T
    dfr.columns = ['span', 'ema']

    max_val = dfr['ema'].max()
    min_val = dfr['ema'].min()

    # Plot
    _, axis   = plot_setup(dfr, target='span', xlabel='rolling mean span (days)')
    largest_idx = plot_max_values(dfr, axis, n_values, max_val, min_val, 'integer')

    axis = build_title(axis,
                       ticker,
                       tra.dates_to_strings(date_range, fmt = '%d-%b-%Y'),
                       max_val, hold,
                       dfr.iloc[largest_idx[0]][0], buffer,
                       )

    dates    = tra.dates_to_strings(date_range, fmt = '%Y-%m-%d')
    filename = f'{ticker}_{dates[0]}_{dates[1]}_spans.{extension}'
    pathname = os.path.join(dft.PLOT_DIR, filename)
    try:
        plt.savefig(pathname,
                    dpi=360,
                    transparent=False,
                    orientation='landscape',
                    bbox_inches='tight'
                    )
    except TypeError as ex:
        print(f'Could not save to {pathname}: {ex}')
    except:
        print(f'Error type {sys.exc_info()[0]}')
    else:
        pass


def plot_buffer_range(ticker, security, span, n_values, fee_pct, date_range, extension='png'):
    '''
    Plots all possible buffers for a given rolling window span
    the range of buffer values is determined in defaults file
    '''
    buffer_range = dft.get_buffers()
    buffers = np.linspace(buffer_range[0],
                          buffer_range[1],
                          buffer_range[2])

    emas, hold = build_1d_emas(security, date_range,
                               var_name='buffer', variables=buffers, fixed=span,
                               fpct=fee_pct)

    dfr = pd.DataFrame(data=[buffers, emas]).T
    dfr.columns = ['buffer', 'ema']

    max_val = dfr['ema'].max()
    min_val = dfr['ema'].min()

    # Plot
    _, axis   = plot_setup(dfr, target='buffer', xlabel='buffer size (% around EMA)')
    largest_idx = plot_max_values(dfr, axis, n_values, max_val, min_val, 'percent')

    axis = build_title(axis,
                       ticker,
                       tra.dates_to_strings(date_range, fmt = '%d-%b-%Y'),
                       max_val, hold,
                       span, dfr.iloc[largest_idx[0]][0],
                       )

    dates    = tra.dates_to_strings(date_range, fmt = '%Y-%m-%d')
    filename = f'{ticker}_{dates[0]}_{dates[1]}_buffers.{extension}'
    pathname = os.path.join(dft.PLOT_DIR, filename)
    try:
        plt.savefig(pathname,
                    dpi=360,
                    transparent=False,
                    orientation='landscape',
                    bbox_inches='tight'
                    )
    except TypeError as ex:
        print(f'Could not save to {pathname}: {ex}')
    except:
        print(f'Error type {sys.exc_info()[0]}')
    else:
        pass

def plot_buffer_span_3D(ticker, date_range, spans, buffers, emas, hold):
    '''
    Surface plot of EMA as a function of rolling-window span & buffer
    '''
    def extract_best_ema(spans, buffers, emas, hold, n_best=1):
        best_emas = tra.get_best_emas(spans, buffers, emas, hold, n_best)
        idx_max  = best_emas['ema'].idxmax()
        max_ema  = best_emas['ema'].max()
        hold     = best_emas['hold'].max()
        max_span = best_emas.span.iloc[idx_max]
        max_buff = best_emas.buffer.iloc[idx_max]
        return max_span, max_buff, max_ema, hold

    def format_data(spans, buffers, emas):
        temp = []
        for i, span in enumerate(spans):
            for j, buffer in enumerate(buffers):
                temp.append([span, buffer, emas[i,j]])
        return pd.DataFrame(temp, columns=['span', 'buffer', 'ema'])

    # Get start & end dates in title (%d-%b-%Y) and output file (%Y-%m-%d) formats
    title_range = tra.dates_to_strings([date_range[0],
                                        date_range[1]],
                                       '%d-%b-%Y')
    name_range   = tra.dates_to_strings([date_range[0],
                                         date_range[1]],
                                        '%Y-%m-%d')

    max_span, max_buff, max_ema, hold = extract_best_ema(spans,
                                                         buffers,
                                                         emas,
                                                         hold,
                                                         )

    temp = format_data(spans, buffers, emas)

    # Plot
    fig = plt.figure(figsize=(dft.FIG_WIDTH, dft.FIG_WIDTH))
    axis = fig.gca(projection='3d')
    surf = axis.plot_trisurf(temp['buffer'], temp['span'], temp['ema'],
                             cmap=dft.SURFACE_COLOR_SCHEME,
                             linewidth=0.2)
    fig.colorbar(surf, shrink=.5, aspect=25, label = 'EMA return')
    axis.set_xlabel('buffer')
    axis.set_ylabel('span')
    axis.xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=None, symbol='%', is_latex=False))

    title  = f'{ticker} | {title_range[0]} - {title_range[1]}\n'
    title += f'EMA max payoff={max_ema:.2%} (hold={hold:.2%}) | '
    title += f'{max_span:.0f}-day mean | '
    title += f'opt buffer={max_buff:.2%}'
    axis.set_title(title, fontsize=dft.TITLE_SIZE, color=dft.TITLE_COLOR)

    save_figure(dft.PLOT_DIR, f'{ticker}_{name_range[0]}_{name_range[1]}_3D', extension='png')
    plt.show()


def plot_buffer_span_contours(ticker, date_range, spans, buffers, emas, hold):
    '''
    Contour plot of EMA as a function of rolling-window span & buffer
    '''
    n_contours = dft.N_CONTOURS # number of contours
    n_maxima   = dft.N_MAXIMA_DISPLAY # number of maximum points to plot

    # Get start & end dates in title (%d-%b-%Y) and output file (%Y-%m-%d) formats
    title_range = tra.dates_to_strings([date_range[0],
                                        date_range[1]],
                                       '%d-%b-%Y')
    name_range   = tra.dates_to_strings([date_range[0],
                                         date_range[1]],
                                        '%Y-%m-%d')

    # Plot
    _, axis = plt.subplots(figsize=(dft.FIG_WIDTH, dft.FIG_WIDTH))
    plt.contourf(buffers, spans, emas,
                 levels=n_contours,
                 cmap=dft.CONTOUR_COLOR_SCHEME,
                 )
    plt.colorbar(label='EMA return')

    # Axis labels
    axis.set_xlabel('buffer')
    axis.set_ylabel('span')

    # Plot maxima points
    max_ema, max_span, max_buff = plot_maxima(emas,
                                              spans,
                                              buffers,
                                              hold,
                                              axis,
                                              n_maxima)

    # Build title
    title  = f'{ticker} | {title_range[0]} - {title_range[1]}\n'
    title += f'EMA max payoff={max_ema:.2%} (hold={hold:.2%}) | '
    title += f'{max_span:.0f}-day mean | '
    title += f'opt buffer={max_buff:.2%}'
    axis.set_title(title, fontsize=dft.TITLE_SIZE, color=dft.TITLE_COLOR)

    plt.grid(b=None, which='major', axis='both', color=dft.GRID_COLOR)
    save_figure(dft.PLOT_DIR, f'{ticker}_{name_range[0]}_{name_range[1]}_contours', extension='png')
    plt.show()

### I/O
def save_figure(plot_dir, p_file, dpi=360, extension='png'):
    '''
    Save figure to file
    '''
    filename = f'{p_file}.{extension}'
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
