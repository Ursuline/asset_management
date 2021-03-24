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

HUGE = 1000000


def plot_setup(df, target, xlabel, width, height):
    fig, ax = plt.subplots(figsize=(width, height))
    ax.plot(df[target],
            df.ema,
            linewidth=1,
            label='EMA return',
           )
    ax.legend(loc='best')
    ax.set_xlabel(xlabel)
    ax.set_ylabel('return (x)')
    plt.grid(b=None, which='major', axis='both', color='#f1f1f1')
    return fig, ax


def plot_maxima(emas, spans, buffers, hold, ax, n_maxima):
        '''
        Plot points corresponding to n_maxima largest EMA
        '''
        _emas = emas.copy() # algorithm destroys top n_maxima EMA values
        for i in range(n_maxima):
            # Get coordinates of maximum emas value
            max_idx = np.unravel_index(np.argmax(_emas, axis=None),
                                       _emas.shape)
            if i == 0: # Save best EMA
                max_ema  = np.max(_emas)
                max_span = spans[max_idx[0]]
                max_buff = buffers[max_idx[1]]

            ax.plot(buffers[max_idx[1]], spans[max_idx[0]], marker = 'x')
            ax.annotate(i, xy=(buffers[max_idx[1]],
                               spans[max_idx[0]]),
                           textcoords='data',
                           fontsize=8,
                        )
            print(f'Max EMA {i}={np.max(_emas):.2%}: {spans[max_idx[0]]:.0f}-days buffer={buffers[max_idx[1]]:.2%} (hold={hold:.2%})')

            # set max emas value to arbitrily small number and re-iterate
            _emas[max_idx[0]][max_idx[1]] = - HUGE
        return max_ema, max_span, max_buff

def plot_max_values(df, ax, n_values, max_val, min_val, fmt, line_color):
    '''
    Plots maximum values in dataframe as vertical lines
    '''
    largest_idx = pd.Series(df['ema'].nlargest(n_values)).index
    for large in largest_idx:
        ax.axvline(df.iloc[large][0],
                   color=line_color,
                   linestyle=':',
                   linewidth=1)
        if fmt.lower() == 'integer':
            text = f'{df.iloc[large][0]:.0f}'
        elif fmt.lower() == 'percent':
            text = f'{df.iloc[large][0]:.2%}'
        else:
            raise ValueError(f'{fmt} not implemented / should be integer or percent')

        ax.annotate(text=text,
                    xy=(df.iloc[large][0],
                        min_val + np.random.uniform(0, 1)*(max_val-min_val)),
                    color=line_color,
                    )
    return largest_idx


def plot_arrows(axis, data, switches, colors):
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
        if data.SWITCH[row] == switches[0]:  # buy
            y_start = data.loc[data.index[row], 'Close'] + arrow_length
            color = colors[2]
            dy = -arrow_length+space
        elif data.SWITCH[row] == switches[1]:  # sell
            y_start = data.loc[data.index[row], 'Close'] - arrow_length
            color = colors[3]
            dy = arrow_length-space
        else:  # don't draw the arrow
            continue
        #arrow_start = data.loc[data.index[row], 'Close']
        axis.arrow(x=data.index[row],
                   y=y_start,
                   dx=0, dy=dy,
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