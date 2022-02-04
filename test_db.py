#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 31 11:02:55 2022

@author: charly
"""
from datetime import date
from db import db_utility as db_util
from db import db_charting
from db import keys
import yahoo_utilities as y_util

USER = "charly"
PASSWORD = keys.LOCAL_CHARLY

def run_tests():
    '''Checks list of dbs and tables '''
    # Check existing databases
    dbs = db_util.list_databases(user=USER, password=PASSWORD)

    print('Database list:')
    for _db in dbs:
        print(_db)

    # Connect to charting
    db_name = 'charting'
    (db_cx, cursor) = db_util.connect_database(db_name  = db_name,
                                               user     = USER,
                                               password = PASSWORD,
                                               )
    # List tables in database
    tables = db_util.list_tables(cursor)
    print(f'List of tables in {db_name}')
    for table in tables:
        print(f'Database {db_name} | Table {table[0]}:')
        column_names = db_util.list_table_columns(table_name=table[0], cursor=cursor)
        print(f'{__name__} {len(column_names)} columns in table "{table[0]}":\n{column_names}')
        records = db_util.list_table_records(table_name = table[0],
                                             cursor     = cursor,
                                             )
        for record in records:
            print(record)
    db_cx.close()


def run_example(db_cx, cursor):
    '''Adds a record to company & recommendation table'''
    strat     = 'long'
    name      = 'Nikkei 225'
    ticker    = '^N225'
    rec_date  = '2022-01-28'
    recom     = 'buy'
    position  = 'cash'
    span      = 5
    buffer    = .034
    portfolio = 'indices'
    rec_date = rec_date.split('-')
    comp_dict = {'ticker': ticker,
                 'name': name,
                 }
    rec_dict = {'ticker': ticker,
                'date': date(int(rec_date[0]),  # YYYY
                             int(rec_date[1]),  # MM
                             int(rec_date[2])), # DD
                'strategy': strat.lower(),
                'position': position.lower(),
                'recom': recom.lower(),
                'mean': span,
                'buffer': buffer,
                'portfolio': portfolio.lower(),
                }
    db_charting.add_record(company_dict=comp_dict, recom_dict=rec_dict, db_cx=db_cx, cursor=cursor)


def get_security_name(ticker):
    '''Obtain company name from db else from web scraping'''
    try: # first check db
        name = db_charting.get_security_name_from_db(ticker, crs)
    except IndexError:
        try: # next try web scraping
            names = y_util.get_names_from_tickers([ticker])
            name = names[0][1]
        except : # fuck it
            msg = f'Ticker {ticker} not found'
            print(msg)
            name=''
    finally:
        return name


if __name__ == '__main__':
    #run_tests()
    (cnx, crs) = db_util.connect_database(db_name='charting',
                                          user=USER,
                                          password=PASSWORD,
                                          )
    #db_util.drop_table(db_name='charting', table_name='company', cursor=crs)
    #db_util.drop_table(db_name='charting', table_name='recommendation', cursor=crs)
    #db_charting.create_recommendation_table(cursor=crs)
    # run_example(cnx, crs)
    # run_example2(cnx, crs)
    # run_example3(cnx, crs)
    # run_example4(cnx, crs)
    # run_example5(cnx, crs)

    print()
    db_util.describe_table(db_name    = 'charting',
                           table_name ='company',
                           user       = USER,
                           password   = PASSWORD,
                           )
    db_util.print_table('company', crs, cnx, 'ticker')
    print()

    db_util.describe_table(db_name    = 'charting',
                           table_name ='recommendation',
                           user       = USER,
                           password   = PASSWORD,
                           )
    db_util.print_table('recommendation', crs, cnx, 'ticker', 'date')

    TICKER = 'TDOC'
    STRATEGY = 'long'
    print(get_security_name(TICKER), '|' , STRATEGY)
    db_charting.get_security_history(ticker=TICKER, strategy=STRATEGY, cursor=crs)
    portfolio = 'saxo_cycliques'
    db_charting.get_portfolio_history(portfolio=portfolio, cursor=crs)



    cnx.close()
