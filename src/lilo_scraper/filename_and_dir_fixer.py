#!/usr/bin/envthon
# coding: utf-8

import requests
from bs4 import BeautifulSoup
from pandas import DataFrame
import re
import datetime
import sys
import os
import pandas as pd

# Get the location and local files
def get_files(directory = './saved_webpages/'):
    
    if not os.path.isdir(directory):
        print('Error?')
        
    for path, dirs, files in os.walk(directory):
        
        if path == directory:
            break
    files = sorted(files) # sort all the backup filesb

    files = [directory+f for f in files]
    
    return files
