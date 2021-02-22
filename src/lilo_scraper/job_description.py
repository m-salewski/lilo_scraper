#!/usr/bin/envthon
# coding: utf-8

#import requests
#from bs4 import BeautifulSoup
#from pandas import DataFrame
#import re
#import datetime
import argparse
import os
import pandas as pd
import datetime 

from internal_processing import get_job_details, get_name_and_loc, get_posted_and_applicants
from internal_processing import get_job_title, get_job_id, get_job_description, get_easy_apply
from file_processing import get_files, rename_files_and_dirs, get_paths
from helpers import job_detail_keys, get_job_details_dc, clean_dict, get_deutsch, get_adj_date


def main(directory, job_id, verbose=False):
    """
    """
    
    
    #['Status', 'pdate', 'Job ID', 'Job title', 'Easy', 'Company Name', 'DE',
    #   'Company Location', 'Seniority Level', 'Industry', 'Employment Type',
    #   'Job Functions', 'Number of applicants', 'pdatetime', 'Posted Date',
    #    'cdatetime', 'cdate']
        
    try:
        #if os.path.exists(directory):
        
        import glob

        filename = glob.glob(directory + '*_' + job_id + '.html')[0]
        
    except:
        print('Error: Invalid job-ID or path:', filename)
        return None

    from bs4 import BeautifulSoup
        
    # Open the file and soup it
    f = open(filename,'r')
    soup = BeautifulSoup(f.read(), "lxml")
    f.close()

    # Get the job details
    job_details_list = get_job_details(soup)
    
    # Get the name of the company and the location
    name_and_loc = get_name_and_loc(soup)
    
    # Get the date when job was posted and the number of applicants
    posted_applicants = get_posted_and_applicants(soup)

    # Put all together
    job_details_list = job_details_list+name_and_loc + posted_applicants
    
    
    dc = {}
    dc['Job title'] = get_job_title(soup)        
    dc.update(get_job_details_dc(job_detail_keys)(job_details_list) )
    dc = clean_dict(dc)

    got_de = get_deutsch(get_job_description(soup))
    dc['DE'] = str(got_de)

    easy_apply = get_easy_apply(soup)
    dc['Easy'] = str(easy_apply)
    
    # Get the creation date of the html
    cdatetime = datetime.datetime.fromtimestamp(os.path.getctime(filename))

    pdate, pdatetime = get_adj_date(dc['Posted Date'],cdatetime)

    keys = [ \
        'Date posted', '', 'Job title', 'Seniority Level', '', \
        'Company Name', 'Industry', 'Company Location', '', \
        'Employment Type','Job Functions', '',\
        'DE', 'Easy']
    
    print()
    k=keys[0]
    print(f'{k:50s}', pdate)        
    
    for k in keys[1:]:
        if k != "":
            print(f'{k:50s}',dc[k].strip())
        else:
            print()
            
    print(get_job_description(soup))
    
    return None


if __name__ == '__main__':
    """
    """
    
    # Create the parser
    parser = argparse.ArgumentParser(prog='lilo_read',
                                        usage='%(prog)s [options] path',
                                        description='List the content of a folder')
    #parser = argparse.ArgumentParser(fromfile_prefix_chars='@')

    parser.add_argument('-d',
                        '--directory',
                        default = '/home/sandm/Notebooks/linkedin_local_scraper/saved_webpages_test/Open/',
                        help='Directory where the html files are stored',
                        type=str, required=False)
    'args.master'
    parser.add_argument('-jid',
                        '--job_id',
                        help='Job-ID to view',
                        type=str, required=True)
    
    parser.add_argument('-v',
                        '--verbose',
                        default=False, 
                        action='store_true',                        
                        help='Write processing info to stdio')


    # Execute parse_args()
    args = parser.parse_args()
    
    main(args.directory, args.job_id, args.verbose)
    
    
