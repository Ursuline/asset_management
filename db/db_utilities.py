#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 21:37:09 2022

Generic database utilities

@author: charly
"""
import pandas as pd
from tabulate import tabulate
import mysql.connector


### Database utilities ###
def create_database(db_name:str, host:str, user:str, password:str):
    '''Build a database & return connector & cursor as a tuple'''
    try:
        db_cx = mysql.connector.connect(host     = host,
                                        user     = user,
                                        password = password,
                                        )
        cursor = db_cx.cursor(buffered = True)
        sql    = f"CREATE DATABASE {db_name}"
        cursor.execute(sql)
        return (db_cx, cursor)
    except :
        print(f' {__name__} Cannot create database {db_name} for user {user}')
        raise


def list_databases(user:str, host:str, password:str):
    '''Return a list of all databases on the system'''
    try:
        print(f' {__name__} Attempting connecttion to mysql {user} {password}')
        db_cx = mysql.connector.connect(host     = host,
                                        user     = user,
                                        password = password,
                                        )
        cursor = db_cx.cursor()
        sql    = "SHOW DATABASES"
        cursor.execute(sql)
        return [x for x in cursor]
    except:
        print(f' {__name__} User {user } cannot connect to mysql')
        raise


def connect_database(db_name:str, host:str, user:str, password:str):
    '''Connect to an existing database & return connector & cursor as a tuple'''
    try:
        db_cx = mysql.connector.connect(host     = host,
                                        user     = user,
                                        password = password,
                                        database = db_name
                                        )
        cursor = db_cx.cursor(buffered = True)
        return (db_cx, cursor)
    except:
        print(f' {__name__} User {user } cannot connect to mysql')
        raise


### Table utilities ###
def drop_table(db_name:str, table_name:str, cursor):
    '''Destroy table from database'''
    try:
        tables = list_tables(cursor)
        tbls   = []
        for table in tables:
            tbls.append(table[0])
        if table_name not in tbls:
            raise IndexError(f'Failed to drop table "{table_name}" from "{db_name}"')
        sql = f"DROP TABLE {table_name}"
        cursor.execute(sql)
    except Exception as ex:
        print(f'table "{table_name}" does not exist in "{db_name}" {ex}')
        raise
    else:
        msg = f'Table {table_name} dropped'
        print(msg)


def delete_record(table_name:str, cursor, cnx):
    '''Delete record from table'''
    try:
        sql = f'delete from {table_name} where std_id=1 and name=rahul'
        cursor.execute(sql)
        print("Record removed succesfully")
        cnx.commit()
        for row in cursor:
            print(row)
    except Exception as ex:
        print(f"Invalid Query {ex}")


def list_tables(cursor):
    '''Return a list of tables on the db'''
    try:
        sql = 'SHOW TABLES'
        cursor.execute(sql)
        return [x for x in cursor]
    except Exception as ex:
        print(f' {__name__} Failed to list tables: {ex}')
        return [()]


def describe_table(db_name:str, host:str, table_name:str, user:str, password:str):
    '''Outputs to screen a full description of table '''
    headers = ['Field', 'Type', 'Null', 'Key', 'Default', 'Extra']
    (_, cursor) = connect_database(db_name  = db_name,
                                       host     = host,
                                       user     = user,
                                       password = password,
                                       )
    sql = f"DESC {table_name}"
    cursor.execute(sql)
    print(tabulate(cursor.fetchall(), headers=headers, tablefmt='psql'))


def list_table_columns(table_name, cursor):
    '''Lists column names from a tables'''
    sql = f"SELECT * FROM {table_name}"
    cursor.execute(sql)
    return [i[0] for i in cursor.description]


def print_table(table_name:str, cursor, cnx, *args):
    '''Pretty prints table contents to screen args -> sort columns'''
    sql = f"SELECT count(ticker) FROM {table_name}"
    print(sql)
    cursor.execute(sql)
    cnt=cursor.fetchall()
    print(f'{cnt} records in table {table_name}')
    results = list_table_records(table_name, cursor, *args)
    headers = list_table_columns(table_name=table_name, cursor=cursor)
    print(tabulate(results, headers=headers, tablefmt='psql'))


def list_table_records(table_name:str, cursor, *args):
    '''Return all records in a table sorted by args'''
    try:
        sql  = f"SELECT * FROM {table_name} "
        sql += 'ORDER BY '
        sql += (', '.join(str(x) for x in args))
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception as ex:
        print(f' {__name__} Failed to list records from table {table_name}: {ex}')
        return [()]


def db_to_df(table_name:str, db_conn):
    '''build a pandas dataframe from a mySQL table'''
    try:
        sql = f"SELECT * FROM {table_name}"
        dataframe = pd.read_sql(sql, db_conn)
    except Exception as exception:
        print(str(exception))
    finally:
        db_conn.close()
        return dataframe
