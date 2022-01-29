#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 21:37:09 2022

@author: charly
"""
import mysql.connector
from db import keys

USER = "charly"
PASSWORD = keys.LOCAL


def create_database(db_name:str):
    '''Build a database'''
    db_cx = mysql.connector.connect(
        host = "localhost",
        user = USER,
        password=PASSWORD
    )
    cursor = db_cx.cursor(buffered=True)
    sql = f"CREATE DATABASE {db_name}"
    cursor.execute(sql)
    return cursor


def list_databases(cursor):
    '''Display all databases on the system'''
    sql = "SHOW DATABASES"
    cursor.execute(sql)
    print(cursor)
    for _db in cursor:
        print(_db)


def connect_database(db_name:str):
    '''Connect to an existing database'''
    db_cx = mysql.connector.connect(
        host = "localhost",
        user = USER,
        password = PASSWORD,
        database = db_name
    )
    cursor = db_cx.cursor(buffered=True)
    return cursor


def list_tables(cursor):
    '''List the tables on the db'''
    sql = 'SHOW TABLES'
    cursor.execute(sql)
    print(cursor)
    for tbl in cursor:
        print(tbl[0])


def list_records(table:str, cursor):
    '''Display all records in a table'''
    sql = f"SELECT * FROM {table}"
    cursor.execute(sql)
    results = cursor.fetchall()
    for result in results:
        print(result)
