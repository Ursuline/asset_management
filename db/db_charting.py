#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  3 12:36:06 2022

methods specific to charting database

@author: charly
"""
from db import keys
import yahoo_utilities as y_util

USER = "charly"
PASSWORD = keys.LOCAL_CHARLY


def create_company_table(cursor):
    '''
    Create a table for companies with 2 fields:
    - ticker
    - company name
    '''
    try:
        sql  = "CREATE TABLE company (ticker VARCHAR(35), "
        sql += "name VARCHAR(75) NOT NULL)"
        cursor.execute(sql)
        sql = "CREATE UNIQUE INDEX ticker ON company (ticker)"
        cursor.execute(sql)
    except Exception as ex:
        print(f'Could not create company table: {ex}')
    else:
        print('table "company" created')


def create_recommendation_table(cursor):
    '''
    Create a table for recommendations with 8 fields:
    - ticker
    - date
    - strategy
    - position (current)
    - recommendation
    - mean (ie: span in days)
    - buffer
    - portfolio name
    '''
    try:
        sql  = "CREATE TABLE recommendation "
        sql += "(ticker VARCHAR(35) NOT NULL, date DATE NOT NULL, "
        sql += "strategy VARCHAR(5) NOT NULL, position VARCHAR(5) NOT NULL, "
        sql += "recom VARCHAR(5) NOT NULL, mean SMALLINT UNSIGNED NOT NULL, "
        sql += "buffer FLOAT(5,3) NOT NULL, portfolio VARCHAR(35) NOT NULL)"
        cursor.execute(sql)
        sql  = "ALTER TABLE recommendation ADD PRIMARY KEY(ticker, date, strategy, position, portfolio)"
        cursor.execute(sql)
    except Exception as ex:
        print(f'Could not create recommendation table: {ex}')
    else:
        print('table "recommendation" created')


def add_record(company_dict:dict, recom_dict:dict, db_cx, cursor):
    '''
    Add a record to the company & recommendation tables in the database
    expected format for date is YYYY-mm-dd
    '''
    # Add record to company table
    increment_company_table(company_dict=company_dict, cursor=cursor, db_cx=db_cx)
    # Add record to recommendation table
    increment_recommendation_table(recom_dict=recom_dict, cursor=cursor, db_cx=db_cx)


def increment_company_table(company_dict:dict, db_cx, cursor):
    '''Add a record to the company table'''
    ticker = company_dict['ticker']
    try:
        if company_dict['name'] is None: # If no name passed, download it
            name   = company_dict['name']
            y_util.get_names_from_tickers([ticker])
            print(f'{name} ({ticker}) scraped')
        # Add the ticker to the company db if it doesn't already exist
        sql_vars   = "(ticker, name)"
        sql_params = "(%(ticker)s, %(name)s)"
        increment_table(table_name = 'company',
                        ticker     = ticker,
                        sql_vars   = sql_vars,
                        sql_params = sql_params,
                        dictionary = company_dict,
                        db_cx      = db_cx,
                        cursor     = cursor,
                        )
    except Exception as ex:
        print(f'{__name__} failed to increment company table with {ticker}: {ex}')


def increment_recommendation_table(recom_dict:dict, db_cx, cursor):
    '''Add a record to the recommendation table'''
    ticker = recom_dict['ticker']
    try:
        # Add the ticker to the company db if it doesn't already exist
        sql_vars = "(ticker, date, strategy, position, recom, mean, buffer, portfolio) "
        sql_params = "(%(ticker)s, %(date)s, %(strategy)s, %(position)s, %(recom)s, %(mean)s, %(buffer)s, %(portfolio)s)"
        increment_table(table_name = 'recommendation',
                        ticker     = ticker,
                        sql_vars   = sql_vars,
                        sql_params = sql_params,
                        dictionary = recom_dict,
                        db_cx      = db_cx,
                        cursor     = cursor,
                        )
    except Exception as ex:
        print(f'{__name__} failed to increment recommendation table for {ticker} {ex}')


def increment_table(table_name:str, ticker:str, sql_vars:str, sql_params:str, dictionary:dict, db_cx, cursor):
    '''Generic table incrementation method:
        builds the query : INSERT IGNORE INTO table_name sql_vars VALUES sql_params
    '''
    try:
        sql  = f"INSERT IGNORE INTO {table_name} "
        sql += sql_vars
        sql += "VALUES "
        sql += sql_params
        cursor.execute(sql, dictionary)
        db_cx.commit()
        if cursor.rowcount != 0:
            print(f'record {ticker} inserted in table {table_name}')
        else:
            print(f'{ticker} already in db - not inserted in {table_name} table')
    except:
        print(f'Failed to increment {table_name}')
        raise


def get_security_name(ticker:str, cursor):
    '''Return security name from a ticker symbol from company db'''
    try:
        sql = f"SELECT name FROM company where ticker = '{ticker}'"
        cursor.execute(sql)
        name = cursor.fetchall()[0][0]
    except Exception as ex:
        print(f'Cannot retrieve company name for ticker {ticker} {ex}')
        return None
    return name


if __name__ == '__main__':
    pass
