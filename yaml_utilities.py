#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 29 11:28:30 2022

@author: charly
"""
import yaml
import urllib
from urllib.error import HTTPError

def yaml_load(path, remote:bool=True):
    '''Loader for yaml data. Accepts as path either of:
    1. a URL -> set remote = True
    2. a local file -> set remote = False
    '''
    try:
        if remote:
            data = yaml.safe_load(urllib.request.urlopen(path))
        else:
            data = yaml.safe_load(path)
    except yaml.YAMLError as exception:
        print(f'{__name__}: {exception}')
        raise
    except HTTPError as ex:
        print(f'{__name__}: {ex}')
        raise
    except:
        raise
    return data
