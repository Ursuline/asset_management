#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  7 11:35:29 2022

Simple interactive utility to display the contents of a yaml file

@author: charly
"""
import os
import yaml
import yaml_utilities as util
from urllib.error import HTTPError

# Default path
URL  = 'https://ml-finance.ams3.digitaloceanspaces.com'
DIR  = 'charting/resources'
FILE = 'charting_run.yaml'


if __name__ == '__main__':

    url = input(f'Enter server URL: [{URL}]: ')
    if url == '':
        url = URL
    direc = input(f'Enter directory: [{DIR}]: ')
    if direc == '':
        direc = DIR
    file = input(f'Enter yaml file name: [{FILE}]: ')
    if file == '':
        file = FILE
    path = os.path.join(url, direc, file)
    print()
    try:
        data = util.yaml_load(path=path, remote=True)
    except HTTPError as exception:
        msg = f'{__name__}: Cannot find data at {path}:\n{exception}'
        print(msg)
    except:
        msg = f'{__name__}: Could not load data from {path}'
        print(msg)
    else:
        print(yaml.dump(data, indent=4, default_flow_style=False))
