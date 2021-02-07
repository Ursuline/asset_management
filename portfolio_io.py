#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  7 18:36:31 2021

I/O for Security, Asset and Portfolio objects

@author: charly
"""
import os
import pandas as pd

DIR_NAME = './'

def load_csv(prefix):
    '''Load csv data & return as a dataframe'''
    filename = os.path.join(DIR_NAME, prefix + ".csv")
    return pd.read_csv(filename, sep=';')


def write_portfolio_space(d_frame, pref, num_ports, perd):
    ''' Save dataframe of results to csv'''
    filename = os.path.join(DIR_NAME, pref + f"_{perd}_{num_ports}.csv")
    d_frame.to_csv(filename, sep=',', encoding='utf-8')
    print(f'\ndataframe saved as {filename}\n')
