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

from internal_processing import get_job_details, get_name_and_loc, get_posted_and_applicants
from internal_processing import get_job_title, get_job_id, get_job_description

from helpers import job_detail_keys, get_job_details_dc, clean_dict, get_deutsch, get_adj_date

# Get the location and local files

def get_files(directory = './saved_webpages/'):
    # bookmark backup directory
    if not os.path.isdir(directory):
        print('Error?')
        
    for path, dirs, files in os.walk(directory):
    # If there are any other directory in the backup directory, we need to stop the process and get the backup files only
        if path == directory:
            break
    files = sorted(files) # sort all the backup filesb

    files = [directory+f for f in files]
    
    return files
