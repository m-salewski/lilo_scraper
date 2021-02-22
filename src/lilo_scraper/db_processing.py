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
from internal_processing import get_job_title, get_job_id, get_job_description, get_easy_apply
from file_processing import get_files, rename_files_and_dirs, get_paths
from helpers import job_detail_keys, get_job_details_dc, clean_dict, get_deutsch, get_adj_date

from utils import verbprint

pdf_jobs_cols = [
    'pdate', 'Job ID', 'Job title', 'Easy', 'Company Name', 'DE', 'Company Location',
    'Seniority Level', 'Industry', 'Employment Type', 'Job Functions', 
    'Number of applicants', 'pdatetime', 'Posted Date', 'cdatetime',
    'cdate'
    ]


def get_master_jobids(master_db):
    """Get the Job-IDs from the master DB

    Args:
      files ([str]): a list of filepaths for the html files
      verbose (bool): a flag for printing info
    """
    
    # Open and cast the master
    return pd.read_csv(master_db)['Job ID'].astype(str).tolist()


def get_jobid_from_filename(filename):
    """
    """
    try:
        return filename.split('__LinkedIn_')[1].replace('.html','')
    except:
        print(filename, 'failed')
        return None


# jobid_list comes from the DataFrame
# filename comes from the directory
check_jobid = lambda jobid_list: lambda filename: get_jobid_from_filename(filename) in jobid_list


def get_jobs_wrapper(directory, status, pdf, verbose=False):
    """
    A wrapper for get_jobs: contains fewer functions for tidyness
    
    1. Get all filenames in the current dir
    2. Get all job IDs from the DF
    3. Get current status job IDs from the DF
    4. Checks
        1. check if files in dir are already processed (ie in the main DF)
        2. check if files in dir are already processed for other status
            - if so, change their status only and do not process _them_
    5. Return DF
    """
    vprint = verbprint(verbose)

    status_str = status.split(' ')[1]
     
    # 1. Get the Job IDs from the files in the current dir 
    # (should only work if already renamed)
    files = get_files(directory)
    
    file_ids = []
    if files != []:
        file_ids = [get_jobid_from_filename(f) for f in files]
    
    # 2. Get all Job IDs from the DataFrame
    # 3. Get current status job IDs from the DF
    old_pdf_ids = []
    all_pdf_ids = []
    if pdf.empty == False:
        pdf_out = pdf.copy()
        all_pdf_ids = pdf['Job ID'].astype(str).unique().tolist()        
        old_pdf_ids = pdf[pdf['Status']==status]['Job ID'].astype(str).tolist()
    else:
        pdf_out = pd.DataFrame()
    
    pdf_new = pd.DataFrame()
        
    # 4. Checks
    # 4.1. Check the Job IDs in the current DataFrame; get the complement
    #    if new files, process; else, ignore
    new_job_ids = list(set(file_ids).difference(set(all_pdf_ids)))
    
    vprint(f"{len(all_pdf_ids):4d} total processed IDs\n" + \
           f"{len(old_pdf_ids):4d} \"{status_str}\" IDs processed\n" + \
           f"{len(file_ids):4d} IDs in \"{status_str}\" directory {directory}\n" + \
           f"{len(new_job_ids):4d} unprocessed files")    
    
    if len(new_job_ids)>0:
            
        #Get the filenames for the new IDs
        ff = [directory+f for f in files if check_jobid(new_job_ids)(f)]
        
        vprint(f'Processing {len(ff)} new {status_str} files')        
        
        pdf_new = get_jobs_df(ff,verbose)
        pdf_new['Status'] = status  
        pdf_out = pd.concat([pdf_out, pdf_new], sort=False)
        
    else: #elif pdf_new.empty:
        vprint(f'No new {status_str} files')
    
    # 4.2. check if files in dir are already processed for other status
    #  Get the processed Job IDs with other status
    # These are in the DF but are not current status
    changed_pdf_ids = []
    if pdf.empty == False:
        changed_pdf_ids = pdf[(pdf['Job ID'].isin(file_ids)) & \
                              (pdf['Status']!=status)]['Job ID'].astype(str).tolist()
        
    #. 4.2.1. If any remaining, change their status only and do not process _them_
    if (len(changed_pdf_ids)>0):
        vprint(f'Swapping status for {len(changed_pdf_ids)} IDs')
        pdf_out.loc[(pdf_out['Job ID'].isin(changed_pdf_ids)), ['Status']]=status        
    
    else: #elif pdf_new.empty:
        vprint(f'No files swapped to {status_str} status')
        
    # 
    if (len(changed_pdf_ids) == 0) & (len(new_job_ids) == 0):
        vprint(f'No changes for {status_str} files')
        return pdf.drop_duplicates()
    else:
        return pdf_out.drop_duplicates()


def get_jobs_df(files, verbose=False):
    """Creates a Pandas DF from the parsed info from saved html files

    Args:
      files ([str]): a list of filepaths for the html files
      verbose (bool): a flag for printing info
    """
    
    vprint = verbprint(verbose)     
    
    # Create empty DF to store results
    pdf_jobs = pd.DataFrame()

    nn=1
    for filename in files:
        
        vprint(f'{nn} of {len(files)}, {filename}')
        
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

        easy_apply = get_easy_apply(soup)
        dc['Easy'] = str(easy_apply)
        
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
    
    pdf_jobs = pdf_jobs[pdf_jobs_cols]
    pdf_jobs = pdf_jobs.sort_values(['pdate','DE','Company Name']).reset_index(drop=True)

    return pdf_jobs


def get_compare_master(pdf_new, master_db):
    """
    """
    # Cast the IDs
    pdf_new['Job ID'] = pdf_new['Job ID'].astype(str)    
    # Measure the jobs per status
    new_open = pdf_new[pdf_new['Status']=='3 Open']['Job ID'].count()
    new_closed = pdf_new[pdf_new['Status']=='2 Closed']['Job ID'].count()
    new_applied = pdf_new[pdf_new['Status']=='1 Applied']['Job ID'].count()
    new_ignored = pdf_new[pdf_new['Status']=='0 Ignored']['Job ID'].count()  


    # Open and cast the master
    # TODO: put this hardcoded dir into an argument
    pdf_master = pd.read_csv(master_db)
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


def update_master(pdf, output_db=None, verbose=False):
    """Update the master DB    
    """    
    
    jobs_cols = [ 'Status'] + pdf_jobs_cols
    
    # Sort the new master
    pdf = pdf.sort_values(['Status','DE','pdate','Company Name'], 
                          ascending=[False,True,True,True]) \
             .reset_index(drop=True)

    pdf = pdf[jobs_cols]
    
    # Write to the master DB
    if output_db:
        pdf.to_csv(output_db, index=False)
    
    return None   
