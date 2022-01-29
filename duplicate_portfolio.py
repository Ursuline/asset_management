#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  7 12:54:27 2022

simple portfolio manipulation utility to change either position or strategy in
a portfolio file and save to csv

duplicate_portfolio.py

@author: charly
"""
import sys
from tabulate import tabulate
import pandas as pd


def trim_all_columns(dfr):
    """
    Trim whitespace from ends of each value across all series in dataframe
    """
    trim_strings = lambda x: x.strip() if isinstance(x, str) else x
    return dfr.applymap(trim_strings)


def get_input_file():
    '''Prompts & loads input file as Dataframe'''
    input_file = input('Enter input csv file -> ')
    try:
        dataframe = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f'Cannot find input file "{input_file}"')
        sys.exit(0)
    else:
        dataframe.columns = ['Ticker', 'Position', 'Strategy']
        dataframe = trim_all_columns(dataframe)
        print(tabulate(dataframe, headers="keys"))
    return dataframe


def save_to_csv(dataframe:pd.DataFrame):
    '''Prompts & outputs udated file to csv'''
    output_file = input('Enter output csv file -> ')
    dataframe.to_csv(output_file, index=False)
    print(f'updated dataframe saved as {output_file}')


def get_new_value(column:str, current_value):
    '''Prompts for change in either position or strategy
        column = position or strategy'''
    change_column = ''
    new_column    = ''
    if column == 'position':
        possible_values = ['cash', 'long', 'short']
    else:
        possible_values = ['long', 'short']
    while change_column.lower() not in ['y', 'n']:
        msg = f'Current {column} for portfolio is: {current_value}. Change {column} (y/n) ? -> '
        change_column = input(msg)
        if change_column.lower() == 'y':
            while new_column.lower() not in possible_values:
                new_column = input(f'Enter desired {column} {possible_values} -> ')
        else:
            new_column = input_df.loc[0, column.capitalize()]
    return new_column


def build_updated_dataframe(dataframe:pd.DataFrame, new_pos:str, new_strat:str):
    '''Update dataframe with new values'''
    for column in ['Position', 'Strategy']:
        if column == 'Position':
            replace = [new_pos, new_pos, new_pos]
        elif column == 'Strategy':
            replace = [new_strat, new_strat, new_strat]
        else:
            raise ValueError(f'non existent column {column}')
        dataframe[column] = dataframe[column].replace(['cash', 'long', 'short'],
                                                      replace).reset_index(drop=True)
    return dataframe


if __name__ == '__main__':
    input_df     = get_input_file()
    new_position = get_new_value('position', input_df.loc[0, 'Position'].strip())
    new_strategy = get_new_value('strategy', input_df.loc[0, 'Strategy'].strip())
    print(f'desired output: {new_position=} {new_strategy=}')
    output_df    = build_updated_dataframe(input_df, new_position, new_strategy)
    save_to_csv(output_df)
