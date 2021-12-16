#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 16 15:41:32 2021

@author: charly
"""
import os
import pandas as pd
import numpy as np
from bokeh.layouts import gridplot
from bokeh.transform import dodge
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.models import HoverTool, Title, Span, Label, NumeralTickFormatter
from bokeh.models.widgets import Tabs, Panel, Paragraph
from bokeh.plotting import figure, show, output_file, save
from numerize import numerize
import plotter as pltr
import company as cny
import metrics as mtr


class ComparisonPlotter(pltr.Plotter):
    '''Plotter for fundamentals plots'''
    def __init__(self, cie:cny.Company, time_series:pd.DataFrame):
        self._cie = cie
        self._time_series = time_series
        self._cds = None
        self._build_cds()


    def plot_peers_bokeh(self, year:str, metrics:dict, metric_name:str, peers:list, filename:str):
        '''
        Bar plot of sector peers for a given year
        metrics: metric dictionary
        metric_name: human-friendly metric name
        filename = html output file
        '''
        defaults = self.get_plot_defaults()
        title = f"{self._company_name} & peers - {mtr.metrics_set_names[metric_name]} ({year})"

        fig = go.Figure()

        metrics_keys = list(metrics.keys())

        # Add trace from target company
        print(f'Processing base company: {self._ticker}')
        cie_metrics = list(self.load_cie_metrics(year, metrics_keys))
        fig.add_trace(go.Bar(x=metrics_keys,
                             y=cie_metrics,
                             name  = f'{self._company_name} ({self._ticker})',
                             hovertemplate = 'Value: %{y:.2f}<br>',
                             ),
                      )

        # Add traces from peers
        for peer in peers:
            print(f'Processing peer {peer}')
            try:
                peer_cie = Company(peer,
                                   period='annual',
                                   expiration_date=self._expiration_date,
                                   start_date=self._start_date,
                                   end_date=self._end_date
                                   )
                cie_metrics = list(peer_cie.load_cie_metrics(year, metrics_keys).values())
                fig.add_trace(go.Bar(x=metrics_keys,
                                     y=cie_metrics,
                                     name  = f'{peer_cie.get_company_name()} ({peer})',
                                     hovertemplate = 'Value: %{y:.2f}<br>',
                                     ),
                              )
                self._build_caption(fig, metric_name)
            except:
                print(f'Could not include {peer} in plot')
        # For each set of metrics, add benchmark trace
        fig.add_trace(go.Bar(x=metrics_keys,
                             y=list(metrics.values()),
                             name='Benchmark',
                             marker_pattern_shape="x",
                             hovertemplate = 'Value: %{y:.2f}<br>',
                             ),
                      )

        fig.update_layout(
            title = title,
            legend = dict(font = dict(size = 13,
                                      color = "black",
                                      )
                          ),
            xaxis_tickfont_size=14,
            yaxis=dict(title='metric value',
                       titlefont_size=16,
                       tickfont_size=14,
                       linecolor="#BCCCDC",
                       showspikes=True, # Show spike line for Y-axis
                       # Format spike
                       spikethickness=1,
                       spikedash="dot",
                       spikecolor="#999999",
                       spikemode="across",
                       ),
            barmode='group',
            bargap=0.15, # gap between bars of adjacent location coordinates.
            bargroupgap=0.1, # gap between bars of the same location coordinate.
            updatemenus=[self._build_yscale_dropdown()],
        )
        pio.write_html(fig, file=filename, auto_open=True)
