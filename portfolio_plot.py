#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 11:11:23 2021

Plotting functions

@author: charles mégnin
"""
import numpy as np
import matplotlib.pyplot as plt
import utilities as util

EXT = 'png' # file extension (png, jpg, gif, etc)

def build_parameters(portfolio):
    ''' constructs dictionary of plot parameters '''
    params = {}
    # markers for max Sharpe, min volatility, max return, portfolio
    params['markers']      = ('o', 's', 'd', '*', 'X')
    params['marker_descr'] = portfolio.descriptions
    params['marker_color'] = 'red'
    params['marker_sz']    = 100
    params['title_sz']     = 18
    params['label_sz']     = 12
    params['caption_sz']   = 12
    params['caption_st']   = 'italic'
    return params


def build_data(ptf, n_p):
    ''' returns a dictionary that encapsulates several portfolio parameters '''
    data = {}
    data['period']    = ptf.data['period']
    data['end_date']  = ptf.data['end_date'].date()
    data['num_ports'] = n_p
    return data


def plot_caption(ptf, parameters, data, fig):
    ''' Add a caption to bottom of plot'''
    caption = util.list_to_string(ptf.get_asset_names()) + '\n'
    caption += f'{data["num_ports"]} '
    caption += f'portfolios (basis: {data["period"]} '
    caption += f'ending on {data["end_date"]})'
    fig.text(.01, -0.05,
             caption,
             ha    = 'left',
             wrap  = True,
             size  = parameters['caption_sz'],
             style = parameters['caption_st'])


def save_plot(title, period):
    ''' Save plot to file '''
    fig_name = f'{title}_{period}'

    plt.savefig(f'{fig_name}.{EXT}')
    plt.show()


def plot_rvs(ptf, rvs, e_front, indices, num_ports, log_plot=False):
    ''' Plot distribution
        rvs = return, volatility, Sharpe ratio array
        indices[0]=Max Sharpe ratio (from grid search)
        indices[1]=Min Volat
        indices[2]=Max Return
        indices[3]=Present portfolio
        indices[4]=Optimal Sharpe ratio (from optimization algo)'''
    parameters = build_parameters(ptf)
    data       = build_data(ptf, num_ports)

    if not log_plot: # linearize returns & convert to relative change
        rvs[:, 0] = np.exp(rvs[:, 0]) - 1.0

    fig, axis = plt.subplots(figsize=(12,8), tight_layout=True)
    axis.set_title('Asset allocation ' + ptf.data['title'],
                   size=parameters['title_sz'])

    # plot all portfolios, axes & colorbar
    scat = axis.scatter(rvs[:, 1], rvs[:, 0], c=rvs[:, 2], cmap='viridis')
    fig.colorbar(scat, label='Sharpe Ratio')

    axis.set_xlabel('Volatility', size=parameters['label_sz'])
    if log_plot:
        axis.set_ylabel('Return (log)',
                        size=parameters['label_sz'])
    else:
        #vals = axis.get_yticks()
        axis.set_yticklabels([f'{x:.0%}' for x in axis.get_yticks()])
        axis.set_ylabel('Return',
                        size=parameters['label_sz'])

    # Plot max sharpe, min volatility and max return portfolios
    x_offset = .0025
    for i, index in enumerate(indices):
        axis.scatter(rvs[index, 1],
                     rvs[index, 0],
                     c      = parameters['marker_color'],
                     s      = parameters['marker_sz'],
                     marker = parameters['markers'][i])
        axis.annotate(parameters['marker_descr'][i],
                      xy = (rvs[index, 1], rvs[index, 0]),
                      xytext = (rvs[index, 1] + x_offset, rvs[index, 0]))

    axis.plot(e_front[:,0], e_front[:,1], 'r--', linewidth=3)

    plot_caption(ptf, parameters, data, fig)
    save_plot(ptf.data["title"], data['period'])
