#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  3 19:13:48 2022

plotting methods for the db

@author: charly
"""
import pandas as pd
import plotly.graph_objects as go
from db import keys
from db import db_utility as db_util

USER = "charly"
PASSWORD = keys.LOCAL_CHARLY

def plot_mean_buffer(ticker:str, portfolio:str, db_df):
    pass


if __name__ == '__main__':
    try:
        table_name = 'recommendation'
        db_cx, _ = db_util.connect_database(db_name='charting',
                                            user=USER,
                                            password=PASSWORD,
                                            )
        db_df = db_util.db_to_df(table_name = table_name,
                                 db_conn    = db_cx,
                                 )
        print(db_df)
    except Exception as e:
        print(str(e))
