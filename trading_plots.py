#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 14:38:49 2021

@author: charles mégnin
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import trading_defaults as dft

def plot_setup(data, target, xlabel):
    '''
    Build line plot structure: dimensions, axes, label & grid
    '''
    fig, axis = plt.subplots(figsize=(dft.fig_width, dft.fig_height))
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
                   fontsize = dft.title_size,
                   color    = dft.title_color,
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
                      fontsize = dft.max_label_size,
                    )
        print(f'Max EMA {i}={np.max(_emas):.2%}: {spans[max_idx[0]]:.0f}-days buffer={buffers[max_idx[1]]:.2%} (hold={hold:.2%})')

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
                     color     = dft.vline_color,
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
                    color=dft.vline_color,
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
        #arrow_start = data.loc[data.index[row], 'Close']
        axis.arrow(x=data.index[row],
                   y=y_start,
                   dx=0, dy=delta_y,
                   head_width=head_width,
                   head_length=head_length,
                   length_includes_head=True,
                   linestyle='-',
                   color=color,
                  )


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
