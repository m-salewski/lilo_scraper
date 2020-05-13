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
from file_processing import get_files, rename_files_and_dirs
from helpers import job_detail_keys, get_job_details_dc, clean_dict, get_deutsch, get_adj_date


def get_jobs_wrapper(directory, status, pdf=None, verbose=False):
    """
    A wrapper for get_jobs: contains a few functions for tidyness
    """
    files = get_files(directory)
    
    pdf_new = pd.DataFrame()
    if len(files)>0:
        files = [directory+f for f in files]
        pdf_new = get_jobs_df(files,verbose)
        pdf_new['Status'] = status
    
    if (pdf is not None) & (pdf_new.empty == False):
        return pd.concat([pdf, pdf_new])
    elif pdf_new.empty:
        return pdf
    else:
        return pdf_new


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

def get_compare_master(pdf_new):
    
    # Cast the IDs
    pdf_new['Job ID'] = pdf_new['Job ID'].astype(str)    
    # Measure the jobs per status
    new_open = pdf_new[pdf_new['Status']=='3 Open']['Job ID'].count()
    new_closed = pdf_new[pdf_new['Status']=='2 Closed']['Job ID'].count()
    new_applied = pdf_new[pdf_new['Status']=='1 Applied']['Job ID'].count()
    new_ignored = pdf_new[pdf_new['Status']=='0 Ignored']['Job ID'].count()  

    # Open and cast the master
    # TODO: put this hardcoded dir into an argument
    pdf_master = pd.read_csv('../../data/master.csv')
    pdf_master['Job ID'] = pdf_master['Job ID'].astype(str)
    # Measure the jobs per status in the master
    master_open = pdf_master[pdf_master['Status']=='3 Open']['Job ID'].count()
    master_closed = pdf_master[pdf_master['Status']=='2 Closed']['Job ID'].count()
    master_applied = pdf_master[pdf_master['Status']=='1 Applied']['Job ID'].count()
    master_ignored = pdf_master[pdf_master['Status']=='0 Ignored']['Job ID'].count()    

    # Merge on the Job IDs
    pdf_merge = pdf_master[['Job ID', 'Status']].merge(pdf_new[['Job ID', 'Status']], on='Job ID', how='outer', suffixes = ['_old',''])
    
    # Fill the 'Status' NANs with False since they are closed
    added = pdf_merge[pdf_merge['Status_old'].isna()]['Job ID'].count() 
    
    print(f'Newly added {added}')
        
    # Get the new Job IDs
    pdf_master_count = pdf_master.groupby('Status').agg({'Job ID':'count'}).reset_index().rename(columns={'Job ID':'counts_master'})
    pdf_new_count = pdf_new.groupby('Status').agg({'Job ID':'count'}).reset_index().rename(columns={'Job ID':'counts_new'})

    # Get the difference in counts 
    # TODO: update this to show what changes to what
    pdf_merge = pdf_new_count.merge(pdf_master_count, on='Status', how='outer')
    pdf_merge.fillna(value = 0, inplace=True)
    pdf_merge = pdf_merge.astype({"counts_new": int, "counts_master": int})
    
    pdf_merge['Status'] = pdf_merge['Status'].apply(lambda s: s.split(' ')[1]) 
    
    print(pdf_merge)
    
    return None


def update_master(pdf, master_filename=None, verbose=False):

    pdf_jobs_cols = [ 'Status',
        'pdate', 'Job ID', 'Job title', 'Company Name', 'DE', 'Company Location',
        'Seniority Level', 'Industry', 'Employment Type', 'Job Functions', 
        'Number of applicants', 'pdatetime', 'Posted Date', 'cdatetime',
        'cdate'
        ]
    
    # Resort the new master
    pdf = pdf.sort_values(['Status','DE','pdate','Company Name'], ascending=[False,True,True,True]).reset_index(drop=True)

    pdf = pdf[pdf_jobs_cols]
    
    # Write to the master DB
    if master_filename:
        pdf.to_csv(master_filename, index=False)
    else:
        pdf.to_csv('../data/master.csv',index=False)
    
    return None


def main(directory, master_filename, verbose):
    
    # Get the inputs
    '''
    verbose = False
    if length > 3:
        verbose = True
        update_master = True
    elif length > 2:
        verbose = True
        update_master = False
    '''
        
    # Get the files to process
    files = get_files(directory)
    
    # rename the files (if needed)
    rename_files_and_dirs(files, directory, verbose)

    # Process and create the DataFrame
    pdf_new = get_jobs_wrapper(directory,'3 Open', None, verbose)

    closed_dir = directory+'Closed/'
    pdf_new = get_jobs_wrapper(closed_dir,'2 Closed', pdf_new, verbose)
        
    applied_dir = directory+'Applied/'
    pdf_new = get_jobs_wrapper(applied_dir,'1 Applied', pdf_new, verbose)
                             
    ignored_dir = directory+'Ignored/'
    pdf_new = get_jobs_wrapper(ignored_dir,'0 Ignored', pdf_new, verbose)       
    
    #if verbose: 
    get_compare_master(pdf_new)
    
    # Update the master DB
    if master_filename:
        update_master(pdf_new, master_filename, verbose)
    
    return None


if __name__ == '__main__':
    
    # Create the parser
    parser = argparse.ArgumentParser(prog='loli_scraping',
                                        usage='%(prog)s [options] path',
                                        description='List the content of a folder')
    #parser = argparse.ArgumentParser(fromfile_prefix_chars='@')

    parser.add_argument('-d',
                        '--directory',
                        help='Directory where the html files are stored',
                        type=str, required=True)

    parser.add_argument('-m',
                        '--master',
                        help='Name of master db (will overwrite)',
                        type=str)

    parser.add_argument('-v',
                        '--verbose',
                        action='store_true',                        
                        help='Write processing info to stdio')


    # Execute parse_args()
    args = parser.parse_args()

    main(args.directory, args.master, args.verbose)
    
    
