#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  7 18:36:31 2021

I/O for Security, Asset and Portfolio objects

@author: charly
"""
import os
import pandas as pd
import numpy as np

DIR_NAME = 'data'

def load_csv(prefix: str):
    '''Load csv data & return as a dataframe'''
    filename = os.path.join(DIR_NAME, prefix + ".csv")
    return pd.read_csv(filename, sep=';')


def write_portfolio_space(ptf, d_frame: pd.DataFrame, num_ports: int):
    ''' Save dataframe of results to csv'''
    prefx = ptf.data['title']
    perd  = ptf.data['period']
    filename = os.path.join(DIR_NAME, prefx + f"_{perd}_{num_ports}.csv")
    d_frame.to_csv(filename, sep=',', encoding='utf-8')
    print(f'\ndataframe saved as {filename}\n')


def results_to_csv(prefix: str, rvs: np.array, weights: np.array, indices: list):
    ''' Saves results to csv file - WIP NOT FUNCTIONAL'''
    d_frame = pd.DataFrame(rvs)
    filename = os.path.join(DIR_NAME, prefix + ".csv")
    d_frame.to_csv(filename, sep=',', encoding='utf-8')
