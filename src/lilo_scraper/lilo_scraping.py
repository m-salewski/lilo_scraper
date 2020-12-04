#!/usr/bin/envthon
# coding: utf-8

import requests
from bs4 import BeautifulSoup
from pandas import DataFrame
import re
import datetime
import argparse
import os, sys
import pandas as pd

from internal_processing import get_job_details, get_name_and_loc, get_posted_and_applicants
from internal_processing import get_job_title, get_job_id, get_job_description
from file_processing import get_files, rename_files_and_dirs, get_paths
from helpers import job_detail_keys, get_job_details_dc, clean_dict, get_deutsch, get_adj_date
from db_processing import get_jobs_wrapper, get_compare_master, update_master

def main(directory, master_db, output_db=None, verbose=False):
    """
    """
    # Get the files to process
    files = get_files(directory)
    
    # rename the files (if needed)
    rename_files_and_dirs(files, directory, verbose)

    pdf_master = pd.DataFrame()
    if master_db:
        if os.path.exists(master_db):
            pdf_master = pd.read_csv(master_db)        
        
    # Process and create the DataFrame
    pdf_new = get_jobs_wrapper(directory,'3 Open', pdf_master, verbose)

    closed_dir = directory+'Closed/'
    pdf_new = get_jobs_wrapper(closed_dir,'2 Closed', pdf_new, verbose)
        
    applied_dir = directory+'Applied/'
    pdf_new = get_jobs_wrapper(applied_dir,'1 Applied', pdf_new, verbose)
                             
    ignored_dir = directory+'Ignored/'
    pdf_new = get_jobs_wrapper(ignored_dir,'0 Ignored', pdf_new, verbose)       
    
    # TODO: change to include master_db as pdf_master  
    if not master_db: master_db = ''
    if os.path.exists(master_db):
        get_compare_master(pdf_new, master_db)
    
    # Update the master DB
    if output_db:
        update_master(pdf_new, output_db, verbose)
    
    return None


if __name__ == '__main__':
    
    # Create the parser
    parser = argparse.ArgumentParser(prog='lilo_scraping',
                                        usage='%(prog)s [options] path',
                                        description='List the content of a folder')
    #parser = argparse.ArgumentParser(fromfile_prefix_chars='@')

    parser.add_argument('-d',
                        '--directory',
                        help='Directory where the html files are stored',
                        type=str, required=True)

    parser.add_argument('-m',
                        '--master',
                        help='Name of master db',
                        type=str)

    parser.add_argument('-o',
                        '--output',
                        help='Name of output db (will overwrite itself & master)',
                        type=str)

    parser.add_argument('-v',
                        '--verbose',
                        action='store_true',                        
                        help='Write processing info to stdio')


    # Execute parse_args()
    args = parser.parse_args()


    # Set up the in/out-put filepaths
    master_db, output_db = get_paths(args.master, args.output)
    
    main(args.directory, master_db, output_db, args.verbose)
    
    
