#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 14:38:49 2021

trading_plots.py

@author: charles mégnin
"""
import os
import sys
from datetime import timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.offsetbox import (TextArea, AnnotationBbox)


import trading as tra
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


def build_title(axis, ticker, ticker_name, dates, ema, hold, span, buffer, buy_sell=None):
    '''
    Build plot title-  common to all plots
    '''
    # build the title
    title  = f'{ticker_name} ({ticker}) | {dates[0]} - {dates[1]}'
    if buy_sell == None:
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


def build_3D_axes_labels(axis):
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
    vertical_range = data['Close'].max() - data['Close'].min()
    horizont_range = (data.index[-1] - data.index[0]).days
    arrow_length   = vertical_range/10
    head_width     = horizont_range/100
    head_length    = vertical_range/50
    space          = vertical_range/100  # space bw arrow tip and curve

    # filter actions rows
    # buys
    filtered = data[data.ACTION == actions[0]].copy()
    for row in range(filtered.shape[0]):
        y_start = filtered.loc[filtered.index[row], 'Close']
        color   = colors[2]
        axis.arrow(x  = filtered.index[row],
                   y  = y_start + arrow_length,
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
        y_start = filtered.loc[filtered.index[row], 'Close']
        color   = colors[3]
        axis.arrow(x  = filtered.index[row],
                   y  = y_start - arrow_length,
                   dx = 0,
                   dy = arrow_length - space,
                   head_width  = head_width,
                   head_length = head_length,
                   length_includes_head = True,
                   linestyle = '-',
                   color = color,
                  )


# def plot_arrows_old(axis, data, actions, colors):
#     '''
#     Draws position-switching arrows on axis
#     Called by plot_time_series()
#     '''
#     vertical_range = data['Close'].max() - data['Close'].min()
#     horizont_range = (data.index[-1] - data.index[0]).days
#     arrow_length   = vertical_range/10
#     head_width     = horizont_range/100
#     head_length    = vertical_range/50
#     space          = vertical_range/100  # space bw arrow tip and curve
#     n_buys, n_sells  = 0, 0

#     for row in range(data.shape[0]):
#         if data.ACTION[row] == actions[0]:  # buy
#             y_start = data.loc[data.index[row], 'Close'] + arrow_length
#             color = colors[2]
#             delta_y = -arrow_length+space
#             n_buys += 1
#         elif data.ACTION[row] == actions[1]:  # sell
#             y_start = data.loc[data.index[row], 'Close'] - arrow_length
#             color = colors[3]
#             delta_y = arrow_length-space
#             n_sells += 1
#         else:  # don't draw an arrow
#             continue
#         axis.arrow(x=data.index[row],
#                    y=y_start,
#                    dx=0, dy=delta_y,
#                    head_width=head_width,
#                    head_length=head_length,
#                    length_includes_head=True,
#                    linestyle='-',
#                    color=color,
#                   )
#     return [n_buys, n_sells]

def plot_stats(summary_stats, axis, data, colors):
    '''
    Place a text box with signal statistics
    '''
    xy = (.95, .0075)

    text  = 'Daily returns:\n'
    text += f'$\mu$={summary_stats["mean"]-1:.2%}\n'
    text += f'$\sigma$={summary_stats["std"]:.3g}\n'
    text += f'Skewness={summary_stats["skewness"]:.2g}\n'
    text += f'Kurtosis={summary_stats["kurtosis"]:.2g}\n'
    text += f'Gaussian: {summary_stats["jb"]["gaussian"]}\n'
    text += f'({1-summary_stats["jb"]["level"]:.0%} '
    text += f'p-value={summary_stats["jb"]["gaussian"]:.3g})\n'
    offsetbox = TextArea(text)

    ab = AnnotationBbox(offsetbox,
                        xy,
                        xybox=(-20, 40),
                        xycoords='axes fraction',
                        boxcoords="offset points",
                        frameon = False,
                        #arrowprops=dict(arrowstyle="->")
                        )
    axis.add_artist(ab)
    return axis

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
# def plot_time_series_old(ticker, ticker_name, date_range, security, span, fee_pct, buffer, flags):
#     '''
#     Plots security prices with moving average
#     span -> rolling window span
#     fee_pct -> fee associated with a buy/sell action
#     '''
#     start = date_range[0]
#     end   = date_range[1]
#     title_dates = tra.dates_to_strings([start, end], '%d-%b-%Y')
#     file_dates  = tra.dates_to_strings([start, end], '%Y-%m-%d')

#     # Extract time window
#     dfr = tra.build_strategy(security.loc[start:end, :].copy(),
#                             span,
#                             buffer,
#                             dft.INIT_WEALTH,
#                            )
#     fee  = tra.get_fee(dfr, fee_pct, dft.get_actions())
#     hold = tra.get_cumret(dfr, 'hold')  # cumulative returns for hold strategy
#     ema  = tra.get_cumret(dfr, 'ema', fee)  # cumulative returns for EMA strategy

#     _, axis = plt.subplots(figsize=(dft.FIG_WIDTH, dft.FIG_HEIGHT))
#     axis.plot(dfr.index, dfr.Close, linewidth=1, label='Price')
#     axis.plot(dfr.index, dfr.EMA, linewidth=1, label=f'{span:.0f}-day avg')

#     axis.legend(loc='best')
#     axis.set_ylabel('Price ($)')
#     axis.xaxis.set_major_formatter(dft.get_year_month_format())
#     axis.grid(b=None, which='both', axis='both',
#               color=dft.GRID_COLOR, linestyle='-', linewidth=1)


#     buy_sell = plot_arrows(axis, dfr, dft.get_actions(), dft.get_color_scheme())

#     build_title(axis, ticker, ticker_name, title_dates, ema, hold, span, buffer, buy_sell)
#     save_figure(dft.PLOT_DIR, f'{ticker}_{file_dates[0]}_{file_dates[1]}')
#     return dfr


def plot_time_series(ticker, ticker_name, date_range, display_dates, security, span, fee_pct, buffer, flags):
    '''
    Plots security prices with moving average
    span -> rolling window span
    fee_pct -> fee associated with a buy/sell action
    date_range is entire time series
    display_dates are zoom dates
    flags display -> 0: Price  | 1: EMA  | 2: buffer |
                     3: arrows | 4 : statistics | 5: save
    '''
    timespan = (display_dates[1] - display_dates[0]).days

    title_dates = tra.dates_to_strings([display_dates[0], display_dates[1]], '%d-%b-%Y')
    file_dates  = tra.dates_to_strings([display_dates[0], display_dates[1]], '%Y-%m-%d')

    # Extract time window
    window_start = display_dates[0] - timedelta(days = span + 1)
    dfr = tra.build_strategy(security.loc[window_start:display_dates[1], :].copy(),
                             span,
                             buffer,
                             dft.INIT_WEALTH,
                             )

    fee  = tra.get_fee(dfr, fee_pct, dft.get_actions())
    hold = tra.get_cumret(dfr, 'hold')  # cumulative returns for hold strategy
    ema  = tra.get_cumret(dfr, 'ema', fee)  # cumulative returns for EMA strategy

    _, axis = plt.subplots(figsize=(dft.FIG_WIDTH, dft.FIG_HEIGHT))

    # Display MY for > 180 days and DMY otherwise
    if timespan > 180:
        axis.xaxis.set_major_formatter(dft.get_month_year_format())
    else:
        axis.xaxis.set_major_formatter(dft.get_day_month_year_format())

    axis.grid(b=None, which='both', axis='both',
              color=dft.GRID_COLOR, linestyle='-', linewidth=1)

    # Plot Close
    if flags[0]:
        axis.plot(dfr.loc[display_dates[0]:display_dates[1], :].index,
                  dfr.loc[display_dates[0]:display_dates[1], :].Close,
                  linewidth=1,
                  color = dft.COLOR_SCHEME[0],
                  label='Price')
    # Plot EMA
    if flags[1]:
        axis.plot(dfr.loc[display_dates[0]:display_dates[1], :].index,
                  dfr.loc[display_dates[0]:display_dates[1], :].EMA,
                  linewidth=1,
                  color = dft.COLOR_SCHEME[1],
                  label=f'{span:.0f}-day EMA')
    # Plot EMA +/- buffer
    if flags[2]:
        axis.plot(dfr.loc[display_dates[0]:display_dates[1], :].index,
                  dfr.loc[display_dates[0]:display_dates[1], :].EMA_MINUS,
                  linewidth = 1,
                  linestyle = '--',
                  color = dft.COLOR_SCHEME[2],
                  label=f'EMA - {buffer:.2%}')
        axis.plot(dfr.loc[display_dates[0]:display_dates[1], :].index,
                  dfr.loc[display_dates[0]:display_dates[1], :].EMA_PLUS,
                  linewidth = 1,
                  linestyle = '--',
                  color = dft.COLOR_SCHEME[2],
                  label=f'EMA + {buffer:.2%}')
    axis.legend(loc='best')
    axis.set_ylabel('Price ($)')

    buy_sell = None
    if flags[3]: # plot buy/sell arrows
        def extract_actions(data, actions):
            '''Return a dataframe consisting only of action rows '''
            filtered =  data[(data.ACTION == actions[0]) | (data.ACTION == actions[1])]
            return filtered

        filtered = extract_actions(dfr, dft.get_actions())
        buys  = filtered.loc[display_dates[0]:display_dates[1], 'ACTION'].str.count('buy').sum()
        sells = filtered.loc[display_dates[0]:display_dates[1], 'ACTION'].str.count('sell').sum()
        buy_sell = [buys, sells]
        #buy_sell = [filtered.ACTION.str.count('buy').sum(), filtered.ACTION.str.count('sell').sum()]

        plot_arrows(axis,
                    dfr.loc[display_dates[0]:display_dates[1], :],
                    dft.get_actions(),
                    dft.get_color_scheme(),
                    )

    if flags[4]:
        summary_stats = util.get_summary_stats(dfr.loc[display_dates[0]:display_dates[1], :],
                                               dft.STATS_LEVEL,
                                               'RET')
        axis = plot_stats(summary_stats,
                          axis,
                          dfr.loc[display_dates[0]:display_dates[1], :],
                          dft.get_color_scheme(),
                          )
        #axis, ticker, ticker_name, dates, ema, hold, span, buffer, buy_sell=None
    build_title(axis=axis,
                ticker=ticker,
                ticker_name=ticker_name,
                dates=title_dates,
                span=span,
                buffer=buffer,
                ema=ema,
                hold=hold,
                buy_sell=buy_sell,)
    if flags[5]:
        data_dir = os.path.join(dft.PLOT_DIR, ticker)
        save_figure(data_dir, f'{ticker}_{file_dates[0]}_{file_dates[1]}_tmseries')
        plt.show()

    return dfr


def build_range_plot(ticker, ticker_name, date_range, dfr, fixed, hold, min_max, n_best, target, xlabel, max_fmt):
    '''
    plotting function common to plot_span_range() & plot_buffer_range()
    '''
    _, axis   = plot_setup(dfr, target=target)
    axis = build_range_plot_axes(axis, target=target, xlabel=xlabel)

    largest_idx = plot_max_values(dfr, axis, n_best, min_max[1], min_max[0], max_fmt)

    axis = build_title(axis,
                       ticker,
                       ticker_name,
                       tra.dates_to_strings(date_range, fmt = '%d-%b-%Y'),
                       min_max[1], hold,
                       fixed, dfr.iloc[largest_idx[0]][0],
                       )

    dates    = tra.dates_to_strings(date_range, fmt = '%Y-%m-%d')
    filename = f'{ticker}_{dates[0]}_{dates[1]}_{target}s'
    save_figure(dft.PLOT_DIR, filename)


def plot_span_range(ticker, ticker_name, date_range, security, buffer, n_best, fee_pct, extension='png'):
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
                      span_range[1] + 1)

    emas, hold = build_1d_emas(security, date_range,
                               var_name=target, variables=spans, fixed=fixed,
                               fpct=fee_pct)

    dfr = pd.DataFrame(data=[spans, emas]).T
    dfr.columns = [target, 'ema']
    min_max = [dfr['ema'].min(), dfr['ema'].max()]

    # Plot
    build_range_plot(ticker, ticker_name, date_range, dfr, fixed, hold, min_max, n_best, target, xlabel, max_fmt)


def plot_buffer_range(ticker, ticker_name, security, span, n_best, fee_pct, date_range, extension='png'):
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

    emas, hold = build_1d_emas(security, date_range,
                               var_name  = target,
                               variables = buffers,
                               fixed     = fixed,
                               fpct      = fee_pct,)

    dfr = pd.DataFrame(data=[buffers, emas]).T
    dfr.columns = [target, 'ema']
    min_max = [dfr['ema'].min(), dfr['ema'].max()]

    # Plot
    build_range_plot(ticker, ticker_name, date_range, dfr, fixed, hold, min_max, n_best, target, xlabel, max_fmt)


def plot_buffer_span_3D(ticker, ticker_name, date_range, spans, buffers, emas, hold, colors, elev=None, azim=None, rdist=10):
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

    def re_format_data(spans, buffers, emas):
        temp = []
        for i, span in enumerate(spans):
            for j, buffer in enumerate(buffers):
                temp.append([span, buffer, emas[i,j]])
        return pd.DataFrame(temp, columns=['span', 'buffer', 'ema'])

    def remove_axes_grids(axis):
        # Remove gray panes and axis grid
        axis.xaxis.pane.fill = False
        axis.xaxis.pane.set_edgecolor('white')
        axis.yaxis.pane.fill = False
        axis.yaxis.pane.set_edgecolor('white')
        axis.zaxis.pane.fill = False
        axis.zaxis.pane.set_edgecolor('white')
        axis.grid(False)
        # Remove z-axis
        #axis.w_zaxis.line.set_lw(0.)
        #axis.set_zticks([])
        return axis


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
    temp = re_format_data(spans, buffers, emas)
    # Plot
    fig = plt.figure(figsize=(10, 10))
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

    axis = build_3D_axes_labels(axis)
    #axis.set_zlabel(r'Return', rotation=60)
    axis = remove_axes_grids(axis)
    axis = build_title(axis, ticker, ticker_name, title_range, max_ema, hold, max_span, max_buff)

    save_figure(dft.PLOT_DIR, f'{ticker}_{name_range[0]}_{name_range[1]}_3D', extension='png')
    plt.show()


def plot_buffer_span_contours(ticker, ticker_name, date_range, spans, buffers, emas, hold):
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

    axis = build_3D_axes_labels(axis)

    # Plot maxima points
    max_ema, max_span, max_buff = plot_maxima(emas, spans, buffers, hold,
                                              axis, n_maxima,)

    # Build title
    axis = build_title(axis, ticker, ticker_name, title_range, max_ema, hold, max_span, max_buff)

    plt.grid(b=None, which='major', axis='both', color=dft.GRID_COLOR)
    save_figure(dft.PLOT_DIR, f'{ticker}_{name_range[0]}_{name_range[1]}_contours', extension='png')
    plt.show()


### I/O
def save_figure(plot_dir, prefix, dpi=360, extension='png'):
    '''
    Saves figure to file
    variables:
        plot_dir - directory to plot to
        prefix - filename without its extension
    '''
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
