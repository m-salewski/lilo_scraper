#!/usr/bin/env python
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
from file_processing import get_files, rename_files_and_dirs
from helpers import job_detail_keys, get_job_details_dc, clean_dict, get_deutsch, get_adj_date

def get_jobs_df(files, verbose=False):
    
    # Create empty DF to store results
    pdf_jobs = pd.DataFrame()

    nn=1
    for filename in files:
        
        if verbose:
            print(f'{nn} of {len(files)}')
        
        # Get the creation date of the html
        cdatetime = datetime.datetime.fromtimestamp(os.path.getctime(filename))
        
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

        
        # Create DF-row
        pdf_o = pd.DataFrame(dc, index=[0])
        
        pdate, pdatetime = get_adj_date(dc['Posted Date'],cdatetime)
        
        pdf_o['pdatetime'] = pdatetime
        pdf_o['pdate']     = pdate
        pdf_o['cdatetime'] = cdatetime
        pdf_o['cdate']     = cdatetime.date()


        pdf_o["Job ID"] = get_job_id(soup)
        
        pdf_jobs = pd.concat([pdf_jobs,pdf_o], sort=False).reset_index(drop=True)
        nn+=1

    pdf_jobs_cols = [
        'pdate', 'Job ID', 'Job title', 'Company Name', 'DE', 'Company Location',
        'Seniority Level', 'Industry', 'Employment Type', 'Job Functions', 
        'Number of applicants', 'pdatetime', 'Posted Date', 'cdatetime',
        'cdate'
        ]
    
    pdf_jobs = pdf_jobs[pdf_jobs_cols]
    pdf_jobs = pdf_jobs.sort_values(['pdate','DE','Company Name']).reset_index(drop=True)

    return pdf_jobs

def update_master(pdf_new, verbose=False):

    pdf_new_cols = pdf_new.columns.tolist()
    if 'Open' not in pdf_new_cols:
        pdf_new['Open'] = True
        pdf_new_cols = ['Open'] + pdf_new_cols 
        pdf_new  = pdf_new[pdf_new_cols]

    # Cast the IDs
    pdf_new['Job ID'] = pdf_new['Job ID'].astype(str)    

    pdf_master = pd.read_csv('master.csv')
    pdf_master['Job ID'] = pdf_master['Job ID'].astype(str)

    # Merge on the Job IDs
    pdf_merge = pdf_master[['Job ID', 'Open']].merge(pdf_new[['Job ID', 'Open']], on='Job ID', how='outer', suffixes = ['_old',''])
    
    # Fill the 'Open' NANs with False since they are closed
    pdf_merge['Open'].fillna(value = False, inplace=True)
    
    added = pdf_merge[pdf_merge['Open_old'].isna()]['Job ID'].count()
    open_ = pdf_merge[pdf_merge['Open']==True]['Job ID'].count()
    closed = pdf_merge[pdf_merge['Open']==False]['Job ID'].count()
     
    if verbose:
        print(f'Newly added {added}\nTotal open {open_}\nTotal closed {closed}')
        
    # Get the new Job IDs
    additional_ids = list(set(pdf_new['Job ID'].tolist()).difference(set(pdf_master['Job ID'].tolist())))

    # Set up the cols and conct the DFs
    pdf_master  = pdf_master[pdf_new_cols]
    pdf_new_master = pd.concat([pdf_master, pdf_new[pdf_new['Job ID'].isin(additional_ids)]],sort=False)

    # Remove and replace the 'Open' column
    pdf_new_master = pdf_new_master.drop(columns=['Open'])
    pdf_new_master = pdf_new_master.merge(pdf_merge[['Job ID', 'Open']], on='Job ID', how='inner')

    # De-duplicate the new master DB
    pdf_new_master.drop_duplicates(inplace=True)

    # Resort the new master
    pdf_new_master = pdf_new_master.sort_values(['Open','DE','pdate','Company Name'], ascending=[False,True,True,True]).reset_index(drop=True)
    pdf_new_master  = pdf_new_master[pdf_new_cols]


    return pdf_new_master


def main(args_list, length):
    
    # Get the inputs
    verbose = False
    if length > 2:
        verbose = True
    
    directory = args_list[1]
    
    # Get the files to process
    files = get_files(directory)
    
    # rename the files (if needed)
    rename_files_and_dirs(files, directory, verbose)

    # Process and create the DataFrame
    files = [directory+f for f in files]
    pdf_new = get_jobs_df(files)
    
    # Update the master DB
    pdf_out = update_master(pdf_new, verbose)
    
    # Write to the master DB
    pdf_out.to_csv('master.csv',index=False)
    
    return None


if __name__ == '__main__':
    
    main(sys.argv, len(sys.argv))
