#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  7 19:42:16 2021

General use utilities

@author: charly
"""

def list_to_string(str_list):
    ''' Converts a list of strings to single string '''
    return ', '.join(map(str, str_list))


def annualized_return(rate, ndays):
    ''' Returns annnualized daily return '''
    return ndays * (pow(1. + rate/ndays, ndays) - 1.)


def relative_change(df_column):
    ''' computes relative change bw one column value & the next.
        First value is NaN'''
    return (df_column - df_column.shift(1))/df_column.shift(1)


def absolute_change(df_column):
    ''' computes difference bw one column value & the next.
        First value is NaN'''
    return df_column - df_column.shift(1)
